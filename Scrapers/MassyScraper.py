import bs4
import requests
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime

'''
ISSUES:
    products with discounts gives and error when the price is scraped: FIXED
    products with no images give errors: FIXED
'''


class MassyScraper:
    BASEURL = 'https://www.shopmassystoresbb.com'
    USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML,' \
                 + ' like Gecko) Chrome/106.0.0.0 Safari/537.36 OPR/92.0.0.0'


    def __init__(self):
        pass


    def get_html_soup(self, source):
        headers = {'User-Agent': self.USER_AGENT}
        response = requests.get(source, headers=headers)
        html_content = response.content
        soup = BeautifulSoup(html_content, 'html.parser')
        return soup

    def get_sources(self) -> [[dict], [dict]]:
        '''
        :return: list of main menu info and submenu info
        '''
        menu_items_div_id = 'menuItems'

        headers = {'User-Agent': self.USER_AGENT}
        response = requests.get(self.BASEURL, headers=headers)
        html_content = response.content
        soup = BeautifulSoup(html_content, 'html.parser')

        menu_content = soup.find('div', id=menu_items_div_id)
        menu_items_ul = menu_content.find('ul', class_='quadmenu-navbar-nav')
        menu_list_items = menu_items_ul.find_all('li', recursive=False)

        main_menu_info = []
        sub_menu_info = []
        for li in menu_list_items:
            info = self.get_list_info(li)
            main_menu_info.append(info)
            sub_info = self.get_all_li_info(li, submenu=True)
            for si in sub_info:
                si['parent'] = info['name']
            sub_menu_info += sub_info

        return [main_menu_info, sub_menu_info]

    def get_list_info(self, tag: bs4.Tag):
        a_tag = tag.find('a', recursive=False)
        link = a_tag['href']
        name = a_tag.find('span', class_='quadmenu-text').text
        return {
            'name': name,
            'link': link
        }

    def parse_list(self, li_tag: bs4.Tag):
        t = {}
        info = self.get_list_info(li_tag)

    def get_all_li_info(self, li_tag: bs4.Tag, submenu=False):
        tags = li_tag.find_all('li', recursive=submenu)
        tags_info = []
        for tag in tags:
            info = self.get_list_info(tag)
            tags_info.append(info)

        return tags_info

    def get_product_sources(self, source):
        """
        TODO: create code to ensure source param meets specific format else raise exception
        """
        soup = self.get_html_soup(source)
        list_section = soup.find('section', class_='shop-list')
        list_container = list_section.find('div', class_='container')
        products = list_container.find_all('div', class_='product-header', recursive=True)
        product_sources = []
        for product in products:
            a_tag = product.find('a')
            product_sources.append(a_tag['href'])

        return product_sources

    def get_product_info(self, source):
        """
            TODO: create code to ensure source param meets specific format else raise exception
        """
        # default variables
        img_source = ''
        price = 0
        discounted_price = 0
        discount = 0

        process_price = lambda x: float(x.replace('$', '').replace(',', ''))
        soup = self.get_html_soup(source)

        # get image of product. They are cases where the product uses a default image
        figure = soup.find('figure')
        img_source_a = figure.find('a')
        if img_source_a is not None:
            img_source = img_source_a['href']
        elif figure.find('img'):
            img_source = figure.find('img')['src']  # default image

        details_container = soup.find('div', class_='shop-detail-right')
        product = details_container.find('h1', class_='product_title').text
        product.replace('\n', '').replace('\t', '')
        price_container = details_container.find('p', class_='price')

        if price_container.find('bdi') is not None:
            # case when product has a discount
            price = process_price(price_container.find('del').find('bdi').text)
            discounted_price = process_price(price_container.find('ins').find('bdi').text)
            discount = round((price - discounted_price) / price, 2)
        else:
            price = process_price(price_container.text)

        # except:
        #     print(f'Error occurred while parsing source: {source}')

        # additional info
        info_tag = soup.find('span', class_='posted_in').find_all('a')
        categories = []
        for info in info_tag:
            categories.append(info.text)

        sku = soup.find('span', class_='sku').text
        return {
            'img_source': img_source,
            'product_name': self.clean_item_info(product),
            'price': price,
            'categories': ','.join(categories),
            'discount': discount,
            'discounted_price': discounted_price,
            'sku': sku
        }

    def add_categories(self, info, additional_categories: tuple):
        for category in additional_categories:
            if category not in info['categories']:
                info['categories'] += f', {category}'
        return info

    def clean_item_info(self, text: str):
        return text.replace('\t', '').replace('\n', '')


# scraper = MassyScraper()
# info = scraper.get_product_info("https://www.shopmassystoresbb.com/product/whirlpool-electric-stove-30-copy/")
# print(info)
# details_container = soup.find('div', class_='shop-detail-right')
# price_container = details_container.find('p', class_='price')
# parse = price_container.find('del').find('bdi').text
# print(parse)

# info_dump = scraper.get_product_info('https://www.shopmassystoresbb.com/product/magnum-magnum-fryers-air-3-5qt/')
#
# print(info_dump)
#
# print('Next:')
# scraper.run()

