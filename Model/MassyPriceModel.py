from pocketbase import PocketBase
from datetime import datetime, timedelta


class MassyPriceModel:
    HOST = '127.0.0.1'
    PORT = 8090
    COLLECTION_NAME = 'price_history'
    DATA_SOURCE = 'MASSYSTORES'

    def __init__(self, host=HOST, port=PORT):
        self.host = host
        self.port = port
        self.address = self.host + ':' + str(self.port)
        self.url = 'http://' + self.address
        self.url_s = 'https://' + self.address
        self.client = PocketBase(base_url=self.url)
        self.price_collection = self.client.collection(self.COLLECTION_NAME)

    def add_product_price(self, product_id, price, datestamp_utc):
        product_data = {
            'product_id': product_id,
            'price': price,
            'datestamp': datestamp_utc,
        }
        self.price_collection.create(product_data)

    def getPriceHistory(self, id, page=1, per_page=30):
        filter_str = {"filter": f'product_id = "{id}" '}
        result = self.price_collection.get_list(page, per_page, filter_str)
        return result.items

    def wasProductUpdated(self, product_id, date):
        # Get current date and time
        # now = datetime.datetime.utcnow().date()

        # Get start of today
        start_of_day = datetime(date.year, date.month, date.day)

        # Get start of tomorrow by adding one day to start of today
        start_of_next_day = start_of_day + timedelta(days=1)

        # Get one second before tomorrow
        one_second_before_next_day = start_of_next_day - timedelta(seconds=1)
        filter_str = {"filter": f' product_id = "{product_id}" && datestamp >= "{str(start_of_day)}" && datestamp <= "{str(one_second_before_next_day)}" '}
        result = self.price_collection.get_list(page=1, per_page=30, query_params=filter_str)
        return len(result.items) > 0

    def update_product_price(self, id, price, datestamp):
        # self.price_collection.update(id, )
        pass

    # def update_product_price_by_name(self, product_name, price):
    #     result = self.getProducts(product_name) this will cause an error
    #     self.update_product_price(result[0].collection_id['id'], price)

    # def remove_all(self):
    #     self.price_collection.delete


# model = MassyPriceModel()
# print(model.wasProductUpdated("0z2gtxov6t2p3zx", datetime.utcnow().date()))
# model.add_product_price('w2136gsbltn9tg9', 5.75, '2024-02-07 01:39:56.713604')
