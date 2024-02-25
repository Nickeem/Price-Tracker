from pocketbase import PocketBase


class ImportsModel:
    HOST = '127.0.0.1'
    PORT = 8090
    COLLECTION_NAME = 'imports'

    def __init__(self, host=HOST, port=PORT):
        self.host = host
        self.port = port
        self.address = self.host + ':' + str(self.port)
        self.url = 'http://' + self.address
        self.url_s = 'https://' + self.address
        self.client = PocketBase(base_url=self.url)
        self.price_collection = self.client.collection(self.COLLECTION_NAME)

    def add_import_info(self, start_time, end_time, new_imports, imports_failed, imports_skipped,
                        price_updated, price_update_skipped, total_imports, source):
        product_data = {
            'start_time': start_time,
            'end_time': end_time,
            'new_imports': new_imports,
            'imports_failed': imports_failed,
            'imports_skipped': imports_skipped,
            'price_updated': price_updated,
            'price_update_skipped': price_update_skipped,
            'total_imports': total_imports,
            'source': source,
        }
        self.price_collection.create(product_data)


# model = ImportsModel()
#
# model.add_import_info('2024-02-07 01:39:56.713604', '2024-02-25 01:39:56.713604', 500, 25, 525, 'MASSYSTORES')
