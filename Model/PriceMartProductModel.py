from .ProductModel import ProductModel
# from .ProductModel import ProductModel


class PriceMartProductModel(ProductModel):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        data_source = 'PriceMart'
        search_key = 'product_name'
        super().__init__(data_source, search_key)


# model = PriceMartProductModel('127.0.0.1', 8090)
# model.add_product("Members Selection Shredded Mozzarella Cheese 2.26 kg / 5 lb", 'Groceries, Groceries, Groceries', 'https://pricemart.com/Members-Selection-Shredded-Mozzarella-Cheese-2-26-kg-5-lb-99908', 'https://d31f1ehqijlcua.cloudfront.net/n/b/6/a/0/b6a0b16b60e3cfad6902848355b484acbf590008_Dairy_99908_01.jpg')
# {'product_name': "Member's Selection Shredded Mozzarella Cheese 2.26 kg / 5 lb", 'categories': 'Groceries, Groceries, Groceries', 'link_to_product': 'Members-Selection-Shredded-Mozzarella-Cheese-2-26-kg-5-lb-99908', 'image_source': 'https://d31f1ehqijlcua.cloudfront.net/n/b/6/a/0/b6a0b16b60e3cfad6902848355b484acbf590008_Dairy_99908_01.jpg', 'source': 'PriceMart'}

# print(model.product_collection)