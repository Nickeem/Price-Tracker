from pocketbase import PocketBase
from abc import ABC, abstractmethod


class ProductModel(ABC):
    HOST = '127.0.0.1'
    PORT = 8090
    COLLECTION_NAME = 'products'
    DATA_SOURCE = ''
    SEARCH_KEY = ''

    def __init__(self, data_source, search_key, host=HOST, port=PORT):
        self.host = host
        self.port = port
        self.DATA_SOURCE = data_source
        self.SEARCH_KEY = search_key
        self.address = self.host + ':' + str(self.port)
        self.url = 'http://' + self.address
        self.url_s = 'https://' + self.address
        self.client = PocketBase(base_url=self.url)
        self.product_collection = self.client.collection(self.COLLECTION_NAME)

    def set_data_source(self, data_source):
        self.DATA_SOURCE = data_source

    def add_product(self, product_name, categories, link_to_product, img_source):
        if self.productExists(product_name):
            print(f'Item already exists: {product_name}')
            return False
        else:
            product_data = {
                'product_name': product_name,
                'categories': categories,
                'link_to_product': link_to_product,
                'image_source': img_source,
                'source': self.DATA_SOURCE,
            }
            self.product_collection.create(product_data)
            return True

    def productExists(self, search_product):
        return len(self.getProducts(search_product)) > 0

    def getProducts(self, product_name, page=1, per_page=30):
        filter_str = {"filter": f'{self.SEARCH_KEY} = "{product_name}" && source = "{self.DATA_SOURCE}" '}
        result = self.product_collection.get_list(page, per_page, filter_str)
        return result.items

    def get_product_byid(self, product_id, page=1, per_page=30):
        filter_str = {"filter": f'id = "{product_id}"'}
        res = self.product_collection.get_list(page, per_page, query_params=filter_str)
        return res

    def remove_product(self, product_id):
        self.product_collection.delete(product_id)

# def update_product(self, product_id, new_price, datestamp):
#     new_data = {
#         'Last_Update': datestamp
#     }
#     self.product_collection.update(product_id, new_data)
#
# def update_product_price_by_name(self, product_name, new_data={}):
#     result = self.getProducts(product_name)
#     self.update_product(result[0].collection_id['id'], new_data)

#         'current_price': new_price,

# model = MassyProductModel()
# model.add_product('Kraft Mac & Cheese Three Cheese 206g',
#                   'Boxed Meals,Boxed/Canned Meals,Kraft Competiton,Pastas, Grains & Rice, Grocery',
#                   'https://www.shopmassystoresbb.com/wp-content/uploads/2021/01/Kraft-Three-Cheese.jpg',
#                   'https://www.shopmassystoresbb.com/wp-content/uploads/2021/01/Kraft-Three-Cheese.jpg'
#                   )
# records = model.getProducts('Kraft Mac & Cheese Three Cheese 206g')
# print((records[0].collection_id))
# # for record in records:
# #     print(f"Results: {}")
#
# x = {
#     "product_name": "Kraft Mac & Cheese Three Cheese 206g",
#     "price": 5.75,
#     "categories": "Boxed Meals,Boxed/Canned Meals,Kraft Competiton,Pastas, Grains & Rice, Grocery",
#     "img_source": "https://www.shopmassystoresbb.com/wp-content/uploads/2021/01/Kraft-Three-Cheese.jpg"
# }
#
