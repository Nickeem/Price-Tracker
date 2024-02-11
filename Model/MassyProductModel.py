from pocketbase import PocketBase

class MassyProductModel:

    HOST = '127.0.0.1'
    PORT = 8090
    COLLECTION_NAME = 'products'
    DATA_SOURCE = 'MASSYSTORES'

    def __init__(self, host=HOST, port=PORT):
        self.host = host
        self.port = port
        self.address = self.host + ':' + str(self.port)
        self.url = 'http://' + self.address
        self.url_s = 'https://' + self.address
        self.client = PocketBase(base_url=self.url)
        self.product_collection = self.client.collection(self.COLLECTION_NAME)

    def add_product(self, product_name,  categories, link_to_product, img_source):
        if self.productExists(product_name):
            print('Item already exists')
            pass
        else:
            product_data = {
                'product_name': product_name,
                'categories': categories,
                'link_to_product': link_to_product,
                'image_source': img_source,
                'source': self.DATA_SOURCE,
            }
            self.product_collection.create(product_data)

    def productExists(self, product_name):
        return len(self.getProducts(product_name)) > 0

    def getProducts(self, product_name, page=1, per_page=30):
        filter_str = {"filter": f'product_name = "{product_name}" && source = "{self.DATA_SOURCE}" '}
        result = self.product_collection.get_list(page, per_page, filter_str)
        return result.items

    def get_product_byid(self,  product_id, page=1, per_page=30):
        filter_str = {"filter": f'id = "{product_id}"'}
        res = self.product_collection.get_list(page, per_page,query_params=filter_str)
        return res

    # def update_product(self, product_id, new_price, datestamp):
    #     new_data = {
    #         'current_price': new_price,
    #         'Last_Update': datestamp
    #     }
    #     self.product_collection.update(product_id, new_data)
    #
    # def update_product_price_by_name(self, product_name, new_data={}):
    #     result = self.getProducts(product_name)
    #     self.update_product(result[0].collection_id['id'], new_data)


    def remove_all(self):
        self.product_collection.delete()


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
