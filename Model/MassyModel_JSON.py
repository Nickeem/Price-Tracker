import json

class MassyModel:

    FILE = '//massy_data.json'

    def __init__(self):
        pass

    def add_product(self, product_name, price, categories, img_source):
        # some validation could be done
        try:
            with open(self.FILE, 'r') as file:
                product_data = json.load(file)
        except FileNotFoundError:
            # If the file doesn't exist, create an empty dictionary
            product_data = {'data': []}

        # Step 2: Append new information to the data
        new_data = {
                        'product_name': product_name,
                        'price': price,
                        'categories': categories,
                        'img_source': img_source
                    }
        product_data['data'].append(new_data)

        # Step 3: Write the modified data back to the JSON file
        with open(self.FILE, 'w') as file:
            json.dump(product_data, file, indent=2)

    def remove_all(self):
        try:
            with open(self.FILE, 'r') as file:
                product_data = json.load(file)
        except FileNotFoundError:
            # If the file doesn't exist, create an empty dictionary
            product_data = {'data': []}

        # Step 2: Append new information to the data

        product_data['data'].clear()

        # Step 3: Write the modified data back to the JSON file
        with open(self.FILE, 'w') as file:
            json.dump(product_data, file, indent=2)




