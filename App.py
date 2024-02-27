import datetime

import pytz

from Model.MassyProductModel import MassyProductModel
from Model.MassyPriceModel import MassyPriceModel
from Model.ImportsModel import ImportsModel
from Scrapers.MassyScraper import MassyScraper
from Handlers.Logger import Logger
from Handlers.Config import Config


class App:
    timezone = 'America/Barbados'
    barbados_timezone = pytz.timezone(timezone)

    LOGS_PATH = './Logs'
    CONFIG_FILE = 'config.json'

    def __init__(self):
        datestamp = str(datetime.datetime.utcnow().date())
        error_log_name = 'MASSY_IMPORTS_ERRORS_'
        import_log_name = 'MASSY_IMPORTS_'
        error_log_file_name = error_log_name + datestamp
        import_log_file_name = import_log_name + datestamp

        self.ERROR_LOGGER = Logger(self.LOGS_PATH, error_log_file_name)
        self.IMPORT_LOGGER = Logger(self.LOGS_PATH, import_log_file_name)
        self.config = Config(self.CONFIG_FILE)

    def run(self):
        HOST = self.config.get_database_host()
        PORT = self.config.get_database_port()

        product_model = MassyProductModel(HOST, PORT)
        price_model = MassyPriceModel(HOST, PORT)
        imports_model = ImportsModel(HOST, PORT)
        # product_model.remove_all()
        scraper = MassyScraper()
        main_menu_info, submenu_info = scraper.get_sources()

        # scraping stats
        total_sources = 0
        # total_products = 0
        new_products_scraped = 0
        price_updated = 0
        price_update_skipped = 0
        products_skipped = 0

        failed_scraped = 0
        start_time = str(datetime.datetime.utcnow())

        for menu_item in submenu_info:
            if total_sources >= 50:
                break
            product_link = menu_item['link']
            product_sources = scraper.get_product_sources(product_link)
            for source in product_sources:
                # dev clause
                if total_sources >= 50:
                    break

                try:

                    info = scraper.get_product_info(source)
                    info = scraper.add_categories(info, (menu_item['name'], menu_item['parent']))

                    utc_now = datetime.datetime.utcnow()
                    utc_now_s = str(utc_now)
                    # datestamp = str(utc_now.replace(tzinfo=pytz.utc).astimezone(self.barbados_timezone))
                    # info['DATESTAMP'] = datestamp

                    info['link_to_product'] = source

                    product_was_added = product_model.add_product(info['product_name'], info['categories'],
                                                                  info['link_to_product'], info['img_source'])
                    if product_was_added:
                        self.IMPORT_LOGGER.log(f"added product {info['product_name']}. {info['link_to_product']}")
                        new_products_scraped += 1
                    else:
                        self.IMPORT_LOGGER.log(f"Product already exists and was not added: {info['product_name']}. {info['link_to_product']}")
                        products_skipped += 1

                    product_id = product_model.getProducts(info['product_name'])[0].collection_id['id']

                    was_price_updated = price_model.wasProductUpdated(product_id, utc_now)
                    if not was_price_updated:
                        price_model.add_product_price(product_id, info['price'], utc_now_s)
                        price_updated += 1
                    else:
                        price_update_skipped += 1

                except Exception as err:
                    failed_scraped += 1
                    message = f'Error parsing product info for {source}. Error: {err}'
                    self.ERROR_LOGGER.log(message)
                    # print(f'Error parsing product info {source}')
                finally:
                    total_sources += 1
                # print(info)
        end_time = str(datetime.datetime.utcnow())

        # log import job stats
        imports_model.add_import_info(start_time, end_time, new_products_scraped, failed_scraped,
                                      products_skipped, price_updated, price_update_skipped, total_sources,
                                      product_model.DATA_SOURCE)

        print(
            f'Stats:\nTotal products: {total_sources}\nFailed to Scrape: {failed_scraped}\nScrape %:{((total_sources - failed_scraped) / total_sources) * 100}% ')

    def print_sources(self):
        scraper = MassyScraper()
        product_sources = scraper.get_sources()
        for source in product_sources:
            print(source)


app = App()
app.run()
