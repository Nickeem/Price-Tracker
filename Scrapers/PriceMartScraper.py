import bs4
import requests
from bs4 import BeautifulSoup

from playwright.sync_api import sync_playwright


class PriceMartScraper:
    BASEURL = 'https://www.pricesmart.com'
    HOMEURL = 'https://www.pricesmart.com/en-BB'
    CATEGORYURL = 'https://www.pricesmart.com/en-BB/categories'
    USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML,' \
                 + ' like Gecko) Chrome/106.0.0.0 Safari/537.36 OPR/92.0.0.0'

    DRIVER_PATH = "/Users/vacat/Documents/chromedriver-win64/"

    def __clean_text(self, text):
        return text.replace('\n', '').strip()

    def get_html_soup(self, source, extensive=False, wait_on_element=None):
        # soup = BeautifulSoup()
        if extensive: # load js
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(source)

                if wait_on_element is not None:
                    # Wait for the dynamic content to load
                    page.wait_for_selector(wait_on_element)

                # Get the content of the page
                html = page.content()

                soup = BeautifulSoup(html, 'html.parser')

                # Close the browser
                browser.close()

        else:
            headers = {'User-Agent': self.USER_AGENT}
            response = requests.get(source, headers=headers)
            html_content = response.content
            soup = BeautifulSoup(html_content, 'html.parser')
        return soup

    def get_category_info(self, tag: bs4.Tag):
        link = self.BASEURL + tag['href']  # concat site pah with relative path
        # div_tag = tag.find('span', recursive=False, class_='sf-menu-item__label')
        # get and clean name text
        name = self.__clean_text(tag.text)
        return {
            'name': name,
            'link': link
        }

    def get_category_sources(self) -> []:
        menu_items_div_class = "categories-container"

        soup = self.get_html_soup(self.CATEGORYURL)

        menu_content = soup.find('div', class_=menu_items_div_class)
        menu_list_items = menu_content.find_all('a', class_="sf-link")
        # print(menu_items_div)
        main_menu_info = []

        for a_tag in menu_list_items:
            # for each category within an "a" tag get its info
            info = self.get_category_info(a_tag)
            main_menu_info.append(info)

        return main_menu_info

    def get_product_sources(self, category_source):
        product_sources = []

        # wait on custom navigation element to load to start scraping
        wait_on_element = '.custom-pagination'

        soup = self.get_html_soup(category_source,extensive=True, wait_on_element=wait_on_element)
        page_info = soup
        next_page = True

        while next_page:
            products_container = page_info.find('div', '.results-listing')
            products = products_container.find_all('div', class_='sf-button--pure')
            for product in products:
                product_sources.append(self.BASEURL + product['href'])
                if len(page_info.find_all('li', id='next')) > 0:
                    print(1)
                    next_page_source_element = page_info.find('li', id='next')
                    next_page_source = next_page_source_element.find('a', class_='page-link')['href']
                    next_page_source = self.BASEURL + next_page_source
                    print(next_page_source)
                    page_info = self.get_html_soup(next_page_source)
                else:
                    print(2)
                    next_page = False

        return product_sources

    def get_product_info(self, product_source):
        image_source = ''
        price = 0
        process_price = lambda x: float(x.replace('$', '').replace(',', ''))

        wait_on_element = '.product-description__container'

        soup = self.get_html_soup(product_source, extensive=True, wait_on_element=wait_on_element)
        product_info = soup.find('div', class_='product__info')

        image_div = soup.find('div', class_='sf-gallery__stage')
        image_source = image_div.find('img', class_='sf-image')['src']

        brand = product_info.find('h3', class_='sf-heading__title')
        if brand is None:
            # Member's selection is an exclusive brand to pricesmart and there is a special class that indicates this
            brand = "Member's Selection"
        else:
            brand = brand.text

        brand = self.__clean_text(brand)
        price = soup.find('span', class_='sf-price__regular').text
        price = process_price(price)
        product = soup.find('h2', class_='sf-heading__title').text
        product = self.__clean_text(product)

        description = soup.find('div', class_='product-description__container').find('p', class_='items-data').text
        description = self.__clean_text(description)

        return {
            'img_source': image_source,
            'price': price,
            'product': product,
            'brand': brand,
            'description': description,
        }


scraper = PriceMartScraper()
# soup = scraper.get_html_soup(scraper.HOMEURL)
# print(soup)
category_sources = scraper.get_category_sources()
# print(category_sources)

# product_source = 'https://www.pricesmart.com/en-BB/product/Pampers-Cruisers-Diapers-Size-5-104-Units-344776/344776'
# print(scraper.get_product_info(product_source))

# for category_source in category_sources:
#     print(scraper.get_product_sources(category_source['link']))
# print(category_sources)
