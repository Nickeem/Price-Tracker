class PriceMartProductInfo:
    def __init__(self, info):
        self.price_bb = info.get('price_BB', '')
        self.currency = info.get('currency', '')
        self.sku = info.get('master_sku', '')
        self.fractionDigits = info.get('fractionDigits', '')
        self.product_uri = info.get('slug', '')
        self.availablility = info.get('availability_BB', '')
        self.inventory = info.get('inventory_BB', '')
        self.pid = info.get('pid', '')
        self.title = info.get('title', '')
        self.brand = info.get('brand', '')
        self.image = info.get('thumb_image', '')
        self.description = info.get('description', '')

    def print_product(self,):
        print(f'{self.title}, {self.price_bb}')


