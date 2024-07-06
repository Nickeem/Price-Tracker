from ProductModel import ProductModel


class PriceMartProductModel(ProductModel):
    def __init__(self, host, port):
        self.HOST = host
        self.PORT = port
        data_source = 'PriceMart'
        search_key = 'internal_product_id'
        super().__init__(data_source, search_key)

