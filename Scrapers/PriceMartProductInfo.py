class PriceMartProductInfo:
    def __init__(self, info):
        self.base_url = 'https://www.pricesmart.com/en-BB/product/'
        self.currency = info.get('currency', '')
        self.sku = info.get('master_sku', '')

        self.fractionDigits = info.get('fractionDigits', '')
        self.price_bb = info.get('price_BB', '')
        self.price_bb = int(self.price_bb) / (1 * 10**self.fractionDigits)
        self.product_uri = info.get('slug', '')
        self.availablility = info.get('availability_BB', '')
        self.inventory = info.get('inventory_BB', '')
        self.pid = info.get('pid', '')
        self.title = info.get('title', '')
        self.title = self.title.replace('"', '\\"') # escape quotes in string
        self.brand = info.get('brand', '')
        self.image = info.get('thumb_image', '')
        self.description: str = info.get('description', '')
        self.categories: list = []

    def add_categories(self, categories: list):
        self.categories = categories

    def print_product(self,):
        print(f'{self.title}, {self.price_bb}')

    def getCategories_str(self) -> str:
        return ', '.join(self.categories)

    def getProudctLink(self):
        return self.base_url + self.product_uri + '/' + self.sku


    def get_info(self) -> dict:
        return {
            'price_bb': self.price_bb,
            'product_name': self.title,
            'categories': ', '.join(self.categories),
            'link_to_product': self.product_uri,
            'img_source': self.image,
            'description': self.description
        }


