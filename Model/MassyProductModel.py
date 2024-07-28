from .ProductModel import ProductModel


class MassyProductModel(ProductModel):
    def __init__(self, host, port):
        data_source = 'MASSYSTORES'
        search_key = 'product_name'
        self.HOST = host
        self.PORT = port
        super().__init__(data_source, search_key)

