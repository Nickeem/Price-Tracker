import datetime

import pytz

from Model.MassyProductModel import MassyProductModel
from Model.MassyPriceModel import MassyPriceModel
from Scrapers.MassyScraper import MassyScraper


class App:
    timezone = 'America/Barbados'
    barbados_timezone = pytz.timezone(timezone)

    def run(self):
        product_model = MassyProductModel()
        price_model = MassyPriceModel()
        # product_model.remove_all()
        scraper = MassyScraper()
        main_menu_info, submenu_info = scraper.get_sources()
        total_sources = 0
        failed_scraped = 0
        for menu_item in submenu_info:
            '''
            ISSUES:
                products with discounts gives and error when the price is scraped
                products with no images give errors
            '''
            product_link = menu_item['link']
            product_sources = scraper.get_product_sources(product_link)
            for source in product_sources:
                total_sources += 1
                try:

                    info = scraper.get_product_info(source)
                    info = scraper.add_categories(info, (menu_item['name'], menu_item['parent']))

                    utc_now = datetime.datetime.utcnow()
                    utc_now_s = str(utc_now)
                    # datestamp = str(utc_now.replace(tzinfo=pytz.utc).astimezone(self.barbados_timezone))
                    # info['DATESTAMP'] = datestamp

                    info['link_to_product'] = source

                    print(f"added product {info['product_name']} ")
                    product_model.add_product(info['product_name'], info['categories'], info['link_to_product'], info['img_source'])
                    product_id = product_model.getProducts(info['product_name'])[0].collection_id['id']
                    price_model.add_product_price(product_id, info['price'], utc_now_s)

                except:
                    failed_scraped += 1
                    print(f'Error parsing product info {source}')
                # print(info)

        print(
            f'Stats:\nTotal products: {total_sources}\nFailed to Scrape: {failed_scraped}\nScrape %:{((total_sources - failed_scraped) / total_sources) * 100}% ')

    def print_sources(self):
        scraper = MassyScraper()
        product_sources = scraper.get_sources()
        for source in product_sources:
            print(source)

app = App()
app.run()


