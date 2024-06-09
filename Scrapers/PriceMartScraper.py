import json
import math
import time

import bs4
import requests
from bs4 import BeautifulSoup

from playwright.sync_api import sync_playwright
from PriceMartProductInfo import PriceMartProductInfo

# class does full scra;e in ~619 seconds
class PriceMartScraper:
    BASEURL = 'https://www.pricesmart.com'
    HOMEURL = 'https://www.pricesmart.com/en-BB'
    PRODUCTS_API_URL = 'https://www.pricesmart.com/api/br_discovery/getProductsByKeyword'
    PRODUCT_API_URL = 'https://www.pricesmart.com/api/ct/getProduct'
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
                page.goto(source, referer=self.BASEURL)

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
        page_number = 1  # page to render
        num_per_page = 12
        start = 0  # 0 or multiple of 12
        category_id = category_source.split('/')[-1]

        headers = {
            "User-Agent": self.USER_AGENT,
            "Content-Type": "application/json; charset=utf-8",
            "Accept-Encoding": "gzip, deflate, br"
        }
        current_url = str(category_source)  # + f"?page={page_number}"
        ref_url = self.HOMEURL
        payload = {
          "url": current_url,
          "start": start,
          "q": category_id,
          "fq": [],
          "search_type": "category",
          "rows": 12,
          "ref_url": ref_url,
          "account_id": "7024",
          "auth_key": "ev7libhybjg5h1d1",
          # "request_id": 1717260546250,
          "domain_key": "pricesmart_bloomreach_io_en",
          "fl": "pid,title,price,thumb_image,brand,slug,skuid,currency,fractionDigits,master_sku,availability_BB,price_BB,inventory_BB,inventory_BB,promoid_BB",
          "view_id": "BB"
        }

        response = requests.post(self.PRODUCTS_API_URL, data=json.dumps(payload), headers=headers)
        response = response.json()
        response = response['response']

        products = response['docs']
        num_in_category = response['numFound']
        max_page = math.ceil( num_in_category / num_per_page )
        for page in range(2,max_page+1):
            current_url = str(category_source) + f"?page={page_number}"
            ref_url = str(category_source) + f"?page={page_number-1}"
            start = num_per_page * page
            payload['start'] = start
            payload['url'] = current_url
            payload['ref_url'] = ref_url

            response = requests.post(self.PRODUCTS_API_URL, data=json.dumps(payload), headers=headers)
            response = response.json()
            response = response['response']

            products += response['docs']
        for index in range(len(products)):
            products[index] = PriceMartProductInfo(products[index])
        return products

        """
        # wait on custom navigation element to load to start scraping
        wait_on_element = '.results-listing .sf-button--pure'
        
        category_source_page = str(category_source)

        soup = self.get_html_soup(category_source_page, extensive=True, wait_on_element=wait_on_element)
        page_info = soup
        next_page = True

        while next_page:
            products_container = page_info.find('div', class_='results-listing')
            products = products_container.find_all('div', class_='sf-button--pure')
            for product in products:
                product_sources.append(self.BASEURL + product['href'])

            # load next page and check if it is a valid page
            page_number += 1
            category_source_page = category_source + '?page=' + str(page_number)
            try:
                soup = self.get_html_soup(category_source_page, extensive=True, wait_on_element=wait_on_element)
            except Exception as e:
                print(f'When trying to navigate to {category_source_page}, an error occurred. Error: {e}')
                break

            page_info = soup
            """

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
    def get_additonal_product_info_simplified(self, sku):
        # api_url = self.PRODUCT_API_URL  #+ product_uri
        payload = [
            {
                "skus": [sku]
            },
            {
                "products": "getProductBySKU"
            }
        ]
        headers = {
            "User-Agent": self.USER_AGENT,
            "Content-Type": "application/json; charset=utf-8",
            "Accept-Encoding": "gzip, deflate, br"
        }

        response = requests.post(self.PRODUCT_API_URL, data=json.dumps(payload), headers=headers)
        response = response.json()
        # response = response['response']

        element_name = response['data']['products']['results'][0]['masterData']['current']['masterVariant']['attributesRaw'][1]['name']
        description = response['data']['products']['results'][0]['masterData']['current']['masterVariant']['attributesRaw'][1]['value']['en-CR']
        return description

    def get_product_additional_info(self, product_info: PriceMartProductInfo):
        api_url = self.PRODUCT_API_URL + product_info.product_uri
        description = self.get_additonal_product_info_simplified(product_info.sku)
        product_info.description = description
        return product_info


start_time = time.time()
scraper = PriceMartScraper()
# soup = scraper.get_html_soup(scraper.HOMEURL)
# print(soup)
#
# # print(category_sources)
# category_product_info = {}
# for category_source in category_sources:
#     response = scraper.get_product_sources(category_source['link'])
#     info = response['response']
#     name = category_source['name']
#     # print(f"{name}: {response}")
#     # product_info = PriceMartProductInfo(info)
#     category_product_info[name] = info
#
# print(category_product_info)
category_sources = scraper.get_category_sources()
for category in category_sources:
    category_link = category['link']
    products = scraper.get_product_sources(category_link)
    for product in products:
        product_modified = scraper.get_product_additional_info(product)

# products = scraper.get_product_sources("https://www.pricesmart.com/en-BB/category/Groceries/G10D03")
# while True:
#     index = int(input('Enter index number: '))
#     product_description = scraper.get_product_additional_info(products[index])
# print(product_description)
# print(products)
# products[0].print_product()




# product_source = 'https://www.pricesmart.com/en-BB/product/Kale-450-g-15-8-oz-447156/447156'
# print(scraper.get_product_info(product_source))

# category_source = 'https://www.pricesmart.com/en-BB/category/Liquor-Beer-Wine/G10D08014'
# product_sources = scraper.get_product_sources(category_source)
# print(product_sources)
# for category_source in category_sources:
#     print(scraper.get_product_sources(category_source['link']))
# print(category_sources)

print("--- %s seconds ---" % (time.time() - start_time))