import datetime

import pytz

from Model.PriceModel import PriceModel
from Model.ProductModel import ProductModel
from Model.PriceMartProductModel import PriceMartProductModel
from Model.MassyProductModel import MassyProductModel
from Model.MassyPriceModel import MassyPriceModel
from Model.ImportsModel import ImportsModel
from Scrapers.PriceMartScraper import PriceMartScraper
from Scrapers.MassyScraper import MassyScraper
from Scrapers.PriceMartProductInfo import PriceMartProductInfo
from Handlers.Logger import Logger
from Handlers.Config import Config


class App:
    timezone = 'America/Barbados'
    barbados_timezone = pytz.timezone(timezone)

    LOGS_PATH = './Logs'
    CONFIG_FILE = 'config.json'

    def __init__(self):
        datestamp = str(datetime.datetime.utcnow().date())
        massy_error_log_name = 'MASSY_IMPORTS_ERRORS_'
        massy_import_log_name = 'MASSY_IMPORTS_'
        massy_error_log_file_name = massy_error_log_name + datestamp
        massy_import_log_file_name = massy_import_log_name + datestamp

        #
        pm_error_log_name = 'PM_IMPORTS_ERRORS_'
        pm_import_log_name = 'PM_IMPORTS_'
        pm_error_log_file_name = pm_error_log_name + datestamp
        pm_import_log_file_name = pm_import_log_name + datestamp

        self.MASSY_ERROR_LOGGER = Logger(self.LOGS_PATH, massy_error_log_file_name)
        self.MASSY_IMPORT_LOGGER = Logger(self.LOGS_PATH, massy_import_log_file_name)

        self.PM_ERROR_LOGGER = Logger(self.LOGS_PATH, pm_error_log_file_name)
        self.PM_IMPORT_LOGGER = Logger(self.LOGS_PATH, pm_import_log_file_name)

        self.config = Config(self.CONFIG_FILE)

    def run_massy(self):
        HOST = self.config.get_database_host()
        PORT = self.config.get_database_port()

        # initiate models
        product_model = MassyProductModel(HOST, PORT)
        price_model = PriceModel(HOST, PORT)
        imports_model = ImportsModel(HOST, PORT)

        # initiate Scraper
        scraper = MassyScraper()

        # initiate process stats
        total_sources = 0
        # total_products = 0
        new_products_scraped = 0
        price_updated = 0
        price_update_skipped = 0
        products_skipped = 0
        failed_scraped = 0
        start_time = str(datetime.datetime.utcnow())

        # Start Scraping
        main_menu_info, submenu_info = scraper.get_sources()

        for menu_item in submenu_info:

            # dev mode check to determine process
            if total_sources >= self.config.get_dev_import_limit() and self.config.isDev():
                break
            product_link = menu_item['link']

            # get product sources
            product_sources = scraper.get_product_sources(product_link)
            for source in product_sources:  # scrape
                # dev mode check to determine process
                if total_sources >= self.config.get_dev_import_limit() and self.config.isDev():
                    break

                # parse product info into dict
                try:

                    info = scraper.get_product_info(source)

                    info = scraper.add_categories(info, (menu_item['name'], menu_item['parent']))

                    # get current time
                    utc_now = datetime.datetime.utcnow()
                    utc_now_s = str(utc_now)
                    # datestamp = str(utc_now.replace(tzinfo=pytz.utc).astimezone(self.barbados_timezone))
                    # info['DATESTAMP'] = datestamp

                    # get link to product
                    info['link_to_product'] = source

                    # add product to database
                    product_was_added = product_model.add_product(info['product_name'], info['categories'],
                                                                  info['link_to_product'], info['img_source'])

                    # check if status of product importation and log
                    if product_was_added:
                        self.MASSY_IMPORT_LOGGER.log(f"added product {info['product_name']}. {info['link_to_product']}")
                        new_products_scraped += 1
                    else:
                        self.MASSY_IMPORT_LOGGER.log(f"Product already exists and was not added: {info['product_name']}. {info['link_to_product']}")
                        products_skipped += 1

                    product_id = product_model.getProducts(info['product_name'], )[0].collection_id['id']

                    # check if product price was updated
                    was_price_updated = price_model.wasProductUpdated(product_id, utc_now)

                    # add product price update
                    if not was_price_updated:
                        price_model.add_product_price(product_id, info['price'], utc_now_s)
                        price_updated += 1
                    else:
                        price_update_skipped += 1

                except Exception as err:
                    if type(err).__name__ == 'ClientResponseError':
                        message = \
                            f'Failed to make database connection.Type of Error: {type(err).__name__}. Error:  {err}'
                        self.MASSY_ERROR_LOGGER.log(message)
                        exit(2)  # exit code of 2 means ClientResponseError
                    failed_scraped += 1
                    message = \
                        f'Error parsing product info for {source}. Type of Error: {type(err).__name__}. Error:  {err}'
                    self.MASSY_ERROR_LOGGER.log(message)
                finally:
                    total_sources += 1
                # print(info)
        end_time = str(datetime.datetime.utcnow())

        # log import job stats
        imports_model.add_import_info(start_time, end_time, new_products_scraped, failed_scraped,
                                      products_skipped, price_updated, price_update_skipped, total_sources,
                                      product_model.DATA_SOURCE)

        print(
            f'Stats:\n'
            f'Total products: {total_sources}\n'
            f'Failed to Scrape: {failed_scraped}\n'
            f'Scrape %:{((total_sources - failed_scraped) / total_sources) * 100}% ')

    def run_price_mart(self):
        HOST = self.config.get_database_host()
        PORT = self.config.get_database_port()

        product_model = PriceMartProductModel(HOST, PORT)
        price_model = PriceModel(HOST, PORT)
        imports_model = ImportsModel(HOST, PORT)
        # product_model.remove_all()
        scraper = PriceMartScraper()

        # scraping stats
        total_sources = 0
        # total_products = 0
        new_products_scraped = 0
        price_updated = 0
        price_update_skipped = 0
        products_skipped = 0

        failed_scraped = 0
        start_time = str(datetime.datetime.utcnow())

        # get category sources
        category_sources = scraper.get_category_sources()

        # get products in each category
        for category in category_sources:
            category_link = category['link']
            products = scraper.get_product_sources(category_link)
            categories = scraper.process_categories_from_text(category['name'])
            for product in products:

                try:

                    product_modified: PriceMartProductInfo = scraper.get_product_additional_info(product)

                    product_modified.add_categories(categories)

                    # get current time
                    utc_now = datetime.datetime.utcnow()
                    utc_now_s = str(utc_now)

                    # info = product_modified.get_info()
                    # add product to database
                    product_was_added = product_model.add_product(product_modified.title, product_modified.categories,
                                                                  product_modified.product_uri, product_modified.image)

                    # check if status of product importation and log
                    if product_was_added:
                        self.PM_IMPORT_LOGGER.log(f"added product {product_modified.title}. {product_modified.product_uri}")
                        new_products_scraped += 1
                    else:
                        self.PM_IMPORT_LOGGER.log(
                            f"Product already exists and was not added: {product_modified.title}. {product_modified.product_uri}")
                        products_skipped += 1

                    product_id = product_model.getProducts(product_modified.title, )[0].collection_id['id']

                    # check if product price was updated
                    was_price_updated = price_model.wasProductUpdated(product_id, utc_now)

                    # add product price update
                    if not was_price_updated:
                        price_model.add_product_price(product_id, product_modified.price_bb, utc_now_s)
                        price_updated += 1
                    else:
                        price_update_skipped += 1

                except Exception as err:
                    if type(err).__name__ == 'ClientResponseError':
                        message = f'Failed to make database connection.Type of Error: {type(err).__name__}. Error:  {err}'
                        self.MASSY_ERROR_LOGGER.log(message)
                        exit(2)  # exit code of 2 means ClientResponseError
                    failed_scraped += 1
                    message = f'Error parsing product info for {product.product_uri}. Type of Error: {type(err).__name__}. Error:  {err}'
                    self.MASSY_ERROR_LOGGER.log(message)
                finally:
                    total_sources += 1

        end_time = str(datetime.datetime.utcnow())

        # log import job stats
        imports_model.add_import_info(start_time, end_time, new_products_scraped, failed_scraped,
                                      products_skipped, price_updated, price_update_skipped, total_sources,
                                      product_model.DATA_SOURCE)

        print(
            f'Stats:\n'
            f'Total products: {total_sources}\n'
            f'Failed to Scrape: {failed_scraped}\n'
            f'Scrape %:{((total_sources - failed_scraped) / total_sources) * 100}% ')

    def run(self):
        self.run_massy()
        self.run_price_mart()
    def print_sources(self):
        scraper = MassyScraper()
        product_sources = scraper.get_sources()
        for source in product_sources:
            print(source)


app = App()
app.run()
