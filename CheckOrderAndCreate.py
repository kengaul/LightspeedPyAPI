import sys
import csv
import requests
import os
import logging
import math

""" try: # for Python 3
    from http.client import HTTPConnection
except ImportError:
    from httplib import HTTPConnection
HTTPConnection.debuglevel = 1

logging.basicConfig() # you need to initialize logging, otherwise you will not see anything from requests
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True """


class OrderedProduct:
    def __init__(self, sku, name, supply_price, supplier_code=None, is_variant=False, variant_list=[]):
        self.sku = sku
        self.name = name.capitalize()
        self.supply_price = supply_price
        self.supplier_code=supplier_code
        self.is_variant = is_variant
        self.variant_list = variant_list
    def __repr__(self):
        return f'Product: {self.sku} - {self.name} - Variants: {len(self.variant_list)}'

class Product:
    def __init__(self, sku, name, supply_price, supplier_id=None, supplier_code=None, product_category_id=None, brand_id=None, tag_ids=None):
        self.sku = sku
        self.name = name.capitalize()
        self.supply_price = supply_price
        self.is_active = True
        self.price_including_tax = float(supply_price)*2.5
        if supplier_id is None:
            self.supplier_id=1
        else:
            self.supplier_id=supplier_id
        self.supplier_code=supplier_code
        if product_category_id is None:
            self.product_category_id='29e62e5c-3b33-43e1-a3d4-4c2514cd81fd'
        else:
            self.product_category_id=product_category_id
        self.brand_id = brand_id
        if tag_ids is None:
            self.tag_ids = []
        else:
            self.tag_ids=tag_ids
        self.account_code_sale=200
        self.account_code_purchase=631
        self.tax_id='02dcd191-ae2b-11e8-ed44-5b640bf36da8'
    def __repr__(self):
        return f'Product: {self.sku} - {self.name}'

def saleprice(cost_price:float):
     return math.ceil((cost_price)*100/25)*25/100

class LightspeedAPI:

    def __init__(self, token, store):
        self.token = token
        self.store = store     
    
    def get_variants(self):
        try:
            url = f"https://{self.store}.retail.lightspeed.app/api/2.0/variant_attributes"
            headers={
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/json"
            }
            response = requests.get(url=url, headers=headers)
            variant_attributes_dict = {variant["name"]: variant for variant in response.json()["data"] if not variant['is_deprecated']}
            #print (f'Variant: {response.json()["data"]}')
            return variant_attributes_dict
            
        except requests.exceptions.RequestException:
            print('HTTP Request failed')
            return None

    def search_products_by_sku(self, skus):
        try:
            url = f"https://{self.store}.retail.lightspeed.app/api/2.0/search"
            params = [("type", "products")]
            for sku in skus:
                params.append(("sku", sku))
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/json"
            }
            response = requests.get(url=url, headers=headers, params=params)
            if response.status_code == 200:
                lightspeed_products_dict = {product["sku"]: product for product in response.json()["data"]}
                return lightspeed_products_dict
            else:
                return None
        except requests.exceptions.JSONDecodeError:
            print("Failed to parse JSON from response ", response.content)
        except requests.exceptions.RequestException as e:
            print("HTTP Request failed with ", e)
        

    def upload_image(self, product_id, image_path):
        url = f"https://{self.store}.retail.lightspeed.app/api/2.0/products/{product_id}/actions/image_upload"
        headers = {
            "Authorization": f"Bearer {self.token}"
        }
        files = {'image': open(image_path, 'rb')}
        try:
            response = requests.post(url, files=files, headers=headers)
            if response.status_code == 200:
                return "Image Updated"
            else:
                return "Image Update Failed"
        except requests.exceptions.JSONDecodeError:
            print("Failed to parse JSON from response ", response.content)
        except requests.exceptions.RequestException as e:
            print("HTTP Request failed with ", e)


    def create_product(self, product):
        try:
            url = f"https://{self.store}.retail.lightspeed.app/api/2.0/products"
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/json"
            }
            response = requests.post(url=url, headers=headers, json=product.__dict__)
            if response.status_code == 200:
                return response.json()
            else:
                print(response)
        except requests.exceptions.JSONDecodeError:
            print("Failed to parse JSON from response ", response.content)
        except requests.exceptions.RequestException as e:
            print("HTTP Request failed with ", e)
        
def csv_to_products(csv_file, key_column):
    products = []
    variant_types = lightspeed_api.get_variants()
    variant_products = {}
    try:
        with open(csv_file, 'r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            for row in reader:
                sku = row[key_column]
                if row["VARIANTNAME"] is None or row["VARIANTNAME"]=="" :
                    name = row["DESCRIPTION"]  # Assuming there's a column "NAME" in the CSV file for product name
                    is_variant = False
                    variant_type_id = None
                else:
                    name = row["VARIANTNAME"]
                    is_variant = True
                    variant_type_id = variant_types[row["VARIANTTYPE"]]['id']
                    variant_value = row["VARIANTVALUE"]
                supply_price = row["COST"]  # Assuming there's a column "COST" in the CSV file for product cost
                supplier_code = row["CODE"]
                supply_price = float(row["COST"])
                retail_price = saleprice(supply_price*2.5)
                exvat_retail_price = round(saleprice(supply_price*2.5)/1.2,2)
                #print(f"parse: {name} - {retail_price} {is_variant}")
                if is_variant:
                    tempvariant = {'variant_definitions': {'attribute_id': variant_type_id, 'value': variant_value}, 'sku': sku, 'price_including_tax': retail_price, 'price_excluding_tax': exvat_retail_price, 'supply_price': supply_price, 'supplier_code': supplier_code}
                    if name in variant_products.keys():
                        variant_products[name].append(tempvariant)
                        print(f"Add to existing variant {name} {variant_products}")
                    else:
                        variant_products[name]=[]
                        variant_products[name].append(tempvariant)
                        product = OrderedProduct(sku, name, supply_price, supplier_code=supplier_code, is_variant=is_variant, variant_list=[])
                        products.append(product)
                        keylist=list(variant_products.keys())
                        print(f"New Variant so create a top product for it {name} {variant_products}")
                else:
                    product = OrderedProduct(sku, name, supply_price, supplier_code=supplier_code, is_variant=is_variant, variant_list=[])
                    products.append(product)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        products=None
    for index, item in enumerate(products):
        print(f"{index} - {item} - {len(variant_products)}")
        #products[index]["variants"] = variant_products[products[index]["name"]]
    return products

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <csv_file> <key_column>")
        sys.exit(1)

    csv_file = sys.argv[1]
    key_column = sys.argv[2]
    token = os.environ.get('LIGHTSPEED_TOKEN')
    store = os.environ.get('LIGHTSPEED_STORE')

    try:
        lightspeed_api = LightspeedAPI(token, store)
        products = csv_to_products(csv_file, key_column)
        print(f'Data extracted successfully: ')
        skus = [product.sku for product in products]
        lightspeed_products_dict = lightspeed_api.search_products_by_sku(skus)
        if lightspeed_products_dict:
            for product in products:
                if product.sku in lightspeed_products_dict:
                    lightspeed_product = lightspeed_products_dict[product.sku]
                    print(f"Product '{product.sku}' exists in Lightspeed: {lightspeed_product['id']} at {lightspeed_product['supply_price']} before {product.supply_price}")
                    if lightspeed_product['has_variants']:
                        print(f'Warning top level product that has variants')
                    if lightspeed_product['variant_parent_id'] is None:
                        productid_for_image=lightspeed_product['id']
                        if product.is_variant:
                            print(f"Danger!! Existing product is basic but you want variants!!")
                    else:
                        productid_for_image=lightspeed_product['variant_parent_id']
                else:
                    print(f"Product '{product.sku}' does not exist in Lightspeed and needs to be created.")
                    # lightspeed_api.create_product(product)
                    print (f'New peoduct details - {product}')
                pathname, extension = os.path.splitext(csv_file)
                image_path = os.path.join(pathname, f"{product.sku}.png")
                exists = os.path.isfile(image_path)
                if exists:
                    print("Adding image:", image_path)
                    # lightspeed_api.upload_image(productid_for_image, image_path)
                else:
                    print("No image at:", image_path)
        else:
            print("No product information received from Lightspeed")
    except FileNotFoundError:
        print(f"Error: File '{csv_file}' not found.")
    except KeyError:
        print(f"Error: Column '{key_column}' not found in the CSV file.")
    except Exception as e:
        print("An error occurred:", e)