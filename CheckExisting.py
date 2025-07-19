import sys
import csv
import requests
import os
import logging
import math
import json
import string

""" try: # for Python 3
    from http.client import HTTPConnection
except ImportError:
    from httplib import HTTPConnection
HTTPConnection.debuglevel = 1

logging.basicConfig() # you need to initialize logging, otherwise you will not see anything from requests
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True  """

class Product:
    def __init__(self, sku: str, id: str, name: str, supply_price: float, is_variant: bool=False, supplier: str=None, supplier_code: str=None, product_category: str=None, brand_id: str=None, tag_ids: list[str]=None, variant_type: str=None, variant_type_value: str=None):
        try:
            #print(f'Initializing Product {sku}')
            self.sku = sku
            if id is None:
                self.id=""
            else:
                self.id=id
            self.name = string.capwords(name)
            self.supply_price = supply_price
            self.is_active = True
            self.price_including_tax: float= self.saleprice()
            if supplier is None:
                print(f'Warning: No supplier which should be impossible')
                self.supplier_id=1
            else:
                try:
                    self.supplier_id=lightspeed_api.get_supplier_id(supplier)
                    self.supplier_name=supplier
                except KeyError:
                    print(f'Error bailing out: No supplier found for {supplier}')
                    exit(100)
            self.supplier_code=supplier_code
            #print(f'Supplier set: {self.supplier_id}')
            if product_category is None:
                self.product_category_id='29e62e5c-3b33-43e1-a3d4-4c2514cd81fd'
                self.product_category="Undefined"
            else:
                self.product_category_id=lightspeed_api.get_category_id(product_category)
                self.product_category=product_category
            self.brand_id = brand_id
            #print(f'Category Set: {self.product_category_id}')
            if tag_ids is None:
                self.tag_ids = []
            else:
                self.tag_ids=tag_ids
            self.account_code_sale=200
            self.account_code_purchase=631
            self.tax_id='02dcd191-ae2b-11e8-ed44-5b640bf36da8'
            if is_variant:
                self.is_variant=True
                self.variant_type=variant_type
                self.variant_type_id=lightspeed_api.get_variant_type_id(variant_type)
                self.variant_type_value=variant_type_value
            else:
                self.variant_type=None
                self.variant_type_value=None
                self.is_variant=False
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)

    def __repr__(self):
        return f'Product: {self.sku} - {self.name} - Variant: {self.is_variant}'

    def saleprice(self):
        sale_price=math.ceil((self.supply_price*2.5)*100/25)*25/100
        #print(f'Calculating Sale price from {self.supply_price}-{sale_price}')
        return sale_price
    
    def isvariant(self):
        return self.is_variant
    
    def set_category(self,category):
        self.product_category_id=lightspeed_api.get_category_id(category)
        self.product_category=category
        #print(f"category set - {self.product_category}")        
        return
    
    def set_costprice(self,costprice):
        self.supply_price=costprice
        self.sale_price=self.saleprice()
        return
    
    def getvariantdata(self):
        print(f'Calculating variant clause for use by parent {self.sku}')
        if self.is_variant:
            return {'variant_definitions': {'attribute_id': self.variant_type_id, 'value': self.variant_type_value}, 'sku': self.sku, 'price_including_tax': self.price_including_tax, 'price_excluding_tax': self.price_including_tax, 'supply_price': self.supply_price, 'supplier_code': self.supplier_code}
            #return json.dumps(variant_data)
        else:
            return None

class LightspeedAPI:

    def __init__(self, token, store):
        self.token = token
        self.store = store
        try:
            print("Initializing lookup tables...")
            self.supplier_lookup = self.load_lookup("suppliers")
            self.brand_lookup = self.load_lookup("brands")
            self.variant_type_lookup = self.load_lookup("variants")    
            self.product_catagories = self.load_lookup("catagories")
            print("Lookup tables initialized...")
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)

    def load_lookup(self, lookup_type):
        # Load lookup tables for suppliers, brands, and variant types
        #print(f'Loading lookup {lookup_type}')
        lookup = {}
        try:
            headers={
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/json"
            }
            if lookup_type == "variants":
                url = f"https://{self.store}.retail.lightspeed.app/api/2.0/variant_attributes"
                #lookup = {variant["name"]: variant for variant in response.json()["data"] if not variant['is_deprecated']}
                response = requests.get(url=url, headers=headers)
                lookup = {item["name"]: item for item in response.json()["data"] if not item['is_deprecated']}
            elif lookup_type == "suppliers":
                url = f"https://{self.store}.retail.lightspeed.app/api/2.0/suppliers"
                response = requests.get(url=url, headers=headers)
                lookup = {item["name"]: item for item in response.json()["data"] if not item['deleted_at']}
            elif lookup_type == "brands":
                url = f"https://{self.store}.retail.lightspeed.app/api/2.0/brands"
                response = requests.get(url=url, headers=headers)
                lookup = {item["name"]: item for item in response.json()["data"] if not item['deleted_at']}
            elif lookup_type == "catagories":
                url = f"https://{self.store}.retail.lightspeed.app/api/2.0/product_categories"
                response = requests.get(url=url, headers=headers)
                lookup = {item["name"]: item for item in response.json()["data"]["data"]["categories"]}
            return lookup 
        except requests.exceptions.RequestException:
                print('HTTP Request failed')
                return None
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno,response.json()["data"]["data"] )
        
    def get_supplier_id(self, supplier_name):
        return self.supplier_lookup[supplier_name]["id"]

    def get_brand_id(self, brand_name):
        return self.brand_lookup[brand_name]["id"]

    def get_variant_type_id(self, variant_type_name):
        return self.variant_type_lookup[variant_type_name]["id"]
    
    def get_category_id(self, category_name):
         return self.product_catagories[category_name]["id"]

    
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
        except requests.exceptions.RequestException as e:
            print("HTTP Request failed with ", e)
        except requests.exceptions.JSONDecodeError:
            print("Failed to parse JSON from response ", response.content)

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
        except requests.exceptions.RequestException as e:
            print("HTTP Request failed with ", e)
        except requests.exceptions.JSONDecodeError:
            print("Failed to parse JSON from response ", response.content)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)

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
        except requests.exceptions.RequestException as e:
            print("HTTP Request failed with ", e)
        except requests.exceptions.JSONDecodeError:
            print("Failed to parse JSON from response ", response.content)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)

 
def csv_to_products(csv_file, key_column, supplier_name: str):
    products = []
    variant_products = {}
    try:
        with open(csv_file, 'r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file,quotechar='"', delimiter=',')
            for row in reader:
                sku: str = row[key_column]
                name: str = row["DESCRIPTION"]  # Assuming there's a column "NAME" in the CSV file for product name
                if row["VARIANTNAME"] is None or row["VARIANTNAME"]=="" :
                    is_variant: bool = False
                    variant_type_name: str = None
                    variant_value: str = None
                else:
                    name = row["VARIANTNAME"]
                    is_variant: bool = True
                    variant_type_name: str=row["VARIANTTYPE"]
                    variant_type_id: str = lightspeed_api.get_variant_type_id(variant_type_name)
                    variant_value: str = row["VARIANTVALUE"]
                supply_price: float = float(row["COST"])  # Assuming there's a column "COST" in the CSV file for product cost
                supplier_code: str = row["CODE"]
                #print(f"parse: {name} - {supply_price} {is_variant}")
                #print(f"SKU: {sku}, Varianttype:  {variant_type_id}")
                product = Product(sku, id, name, supply_price, is_variant=is_variant, supplier=supplier_name, supplier_code=supplier_code, variant_type=variant_type_name,variant_type_value=variant_value)
                products.append(product)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        products=None
    #for index, item in enumerate(products):
    #    print(f"{index} - {item}")
        #products[index]["variants"] = variant_products[products[index]["name"]]
    return products

def create_csv(products: Product,filetype: str):
    if filetype == "new":
        with open('newproducts.csv', 'w', newline='') as ofile:
            writer = csv.writer(ofile)
            fields = ["sku","name","variant_option_one_name","variant_option_one_value","product_category","supply_price","retail_price","tax_name","account_code","account_code_purchase","brand_name","supplier_name","supplier_code","active","track_inventory"]
        
            writer.writerow(fields)
            for oproduct in products:
                writer.writerow([f"{oproduct.sku}", oproduct.name,oproduct.variant_type,oproduct.variant_type_value,oproduct.product_category,oproduct.supply_price,oproduct.price_including_tax,"VAT",oproduct.account_code_sale,oproduct.account_code_purchase,oproduct.supplier_name,oproduct.supplier_name,oproduct.supplier_code,"1","1"])
                # oproduct.product_category, oproduct.supply_price,oproduct.price_including_tax,"VAT",oproduct.account_code_sale,oproduct.account_code_purchase,oproduct.brand,oproduct.supplier_name,oproduct.supplier_code,
    else: 
        with open('updateproducts.csv', 'w', newline='') as ufile:
            uwriter = csv.writer(ufile)
            fields = ["product_id","sku","name","variant_option_one_name","variant_option_one_value","product_category","supply_price","retail_price","tax_name","account_code","account_code_purchase","brand_name","supplier_name","supplier_code","active","track_inventory"]
        
            uwriter.writerow(fields)
            for oproduct in products:
                uwriter.writerow([oproduct.id,f"{oproduct.sku}", oproduct.name,oproduct.variant_type,oproduct.variant_type_value,oproduct.product_category,oproduct.supply_price,oproduct.price_including_tax,"VAT",oproduct.account_code_sale,oproduct.account_code_purchase,oproduct.supplier_name,oproduct.supplier_name,oproduct.supplier_code,"1","1"])

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python script.py <csv_file> <key_column> <supplier name")
        sys.exit(1)

    csv_file = sys.argv[1]
    key_column = sys.argv[2]
    token = os.environ.get('LIGHTSPEED_TOKEN')
    store = os.environ.get('LIGHTSPEED_STORE')
    supplier_name = sys.argv[3]
    newproduct :Product = []
    updateproduct :Product = []

    try:
        lightspeed_api = LightspeedAPI(token, store)
        products = csv_to_products(csv_file, key_column, supplier_name)
        skus = [product.sku for product in products]
        print(f'Data extracted successfully: {skus} found')
        lightspeed_products_dict = lightspeed_api.search_products_by_sku(skus)
        if lightspeed_products_dict:
            print(f'Lightspeed  initializied')
        else:
            print("No product information received from Lightspeed all new products")
            lightspeed_products_dict={}
        for product in products:
            #print(f'Entering Loop Product')
            if product.sku in lightspeed_products_dict:
                #print(f'product found')
                lightspeed_product = lightspeed_products_dict[product.sku]
                product.id=lightspeed_product['id']
                product.name=lightspeed_product['name']
                #product.variant_value=lightspeed_product['variant_option_one_value']
                #print(f"{product.sku} - loading Variant: '{product.is_variant}' exists as parent if:{lightspeed_product['has_variants']} or is child if {lightspeed_product['variant_parent_id']} is populated")
                updateproduct.append(product)
            else:
                #print(f"Create product: '{product.sku}'")
                # lightspeed_api.create_product(product)
                #print (f'New peoduct details - {product}')
                newproduct.append(product)
            create_csv(newproduct,"new")
            create_csv(updateproduct,"existing")
    except FileNotFoundError:
        print(f"Error: File '{csv_file}' not found.")
    except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)