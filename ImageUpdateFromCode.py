import sys
import csv
import requests
import os
import logging
import math
import json,logging
import pathlib
import re
from collections import Counter

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class LightspeedAPI:

    def __init__(self, token, store):
        self.token = token
        self.store = store

    def load_suppliers(self):
        response = None
        try:
            url = f"https://{self.store}.retail.lightspeed.app/api/2.0/suppliers"
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/json"
            }
            response = requests.get(url=url, headers=headers)
            if response.status_code == 200:
                return response.json()["data"]
            else:
                logging.info(f"No Suppliers Found")
                return None
        except requests.exceptions.JSONDecodeError:
            logging.error(
                f"Failed to parse json from response: {e} - {response.content if response else ''}"
            )
        except requests.exceptions.RequestException as e:
            logging.error(f"HTTP Request exception: {e}")
    
    def search_products_by_sku(self, skus):
        response = None
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
                logging.info(f"No product found for {skus}")
                return None
        except requests.exceptions.JSONDecodeError:
            logging.error(
                f"Failed to parse json from response: {e} - {response.content if response else ''}"
            )
        except requests.exceptions.RequestException as e:
            logging.error(f"HTTP Request exception: {e}")

    def search_products_by_id(self, ids):
        response = None
        try:
            url = f"https://{self.store}.retail.lightspeed.app/api/2.0/search"
            params = [("type", "products")]
            for id in ids:
                params.append(("product_id", id))
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/json"
            }
            response = requests.get(url=url, headers=headers, params=params)
            if response.status_code == 200:
                lightspeed_products_dict = {product["sku"]: product for product in response.json()["data"]}
                #print(response.status_code)
                return lightspeed_products_dict
            else:
                logging.info(f"No product found for {ids}")
                return None
        except requests.exceptions.JSONDecodeError:
            logging.error(
                f"Failed to parse json from response: {e} - {response.content if response else ''}"
            )
        except requests.exceptions.RequestException as e:
            logging.error(f"HTTP Request exception: {e}")

    def upload_image(self, product: dict, image_path: str) -> str | None:
        """Upload ``image_path`` to the given product in Lightspeed."""
        response = None
        try:
            if product['variant_parent_id'] is None:
                target_product_id=product["id"]
                isvariant_flag=""
                imagecount=len(product['images'])
            else:
                target_product_id=product['variant_parent_id']
                #target_product_id=product['id']
                isvariant_flag="*"
                imagecount=len(product['skuImages'])

            url = f"https://{self.store}.retail.lightspeed.app/api/2.0/products/{target_product_id}/actions/image_upload"
            headers = {
                "Authorization": f"Bearer {self.token}"
            }
            files = {'image': open(image_path, 'rb')}
            print(f"Uploading {image_path} to {product['sku']}{isvariant_flag}")
            if imagecount == 0:
                response = requests.post(url, files=files, headers=headers)
                if response.status_code == 200:
                    return "Image Updated"
                else:
                    return "Image Update Failed"
            else:
                print(f"Skipping {image_path} as product already has {imagecount} images")
        except requests.exceptions.JSONDecodeError:
            print("Failed to parse JSON from response ", response.content if response else "")
        except requests.exceptions.RequestException as e:
            print("HTTP Request failed with ", e)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
        
def load_products_from_file(filename='products.json'):
    """Save products dictionary to a JSON file."""
    with open(filename, 'r') as file:
        return json.load(file)

def get_product_id_supplier_code(products_dict, supplier_code):
    """
    Check if ``supplier_code`` exists in ``products_dict`` and return the
    product ID if found.

    :param products_dict: Dictionary of products keyed by supplier code.
    :param supplier_code: The supplier code to look up in ``products_dict``.
    :return: The product ID if found, otherwise ``None``.
    """
    if supplier_code in products_dict:
        product = products_dict[supplier_code]
        #a_upper= {k.upper():v for k,v in products_dict.items()}
        #product = a_upper[supplier_code.upper()]
        #return product.get("id")  # Assuming the product data has an 'id' field
        return product
    else:
        return None
    
def get_code_from_filename(filename_stem):
    """Return the supplier code portion of a filename stem.

    ``filename_stem`` may include a numeric suffix separated by either an
    underscore or hyphen.  This helper strips that suffix so that both
    ``"ABC123_1"`` and ``"ABC123-1"`` yield ``"ABC123"``.

    Parameters
    ----------
    filename_stem : str
        The stem of the filename (without extension).

    Returns
    -------
    str
        The extracted supplier code.
    """

    # Split on the first underscore or hyphen and return the leading portion.
    return re.split(r"[-_]", filename_stem)[0]

if __name__ == "__main__":
    if len(sys.argv) > 4 or len(sys.argv) <3:
        print(f"{len(sys.argv)} - Usage: python imageupdate.py <extenstion> <imagedir> <suppliername")
        sys.exit(1)
    else:
        imagedir = sys.argv[2]
        extenstion = sys.argv[1]
        supplier = sys.argv[3]

    token = os.environ.get('LIGHTSPEED_TOKEN')
    store = os.environ.get('LIGHTSPEED_STORE')


    directory= pathlib.Path(imagedir)
    #skuary=loadskus(skulist)
    #print(skuary)
    lightspeed_api = LightspeedAPI(token, store)
    #product=lightspeed_api.search_products_by_sku(skuary)
    product = load_products_from_file()
    supplier_json = lightspeed_api.load_suppliers()
    suppliername_dict = {supplier["name"]: supplier for supplier in supplier_json}
    supplierid_dict = {supplier["id"]: supplier for supplier in supplier_json}
            
    inscope_supplier = suppliername_dict[supplier]["id"]
    #files = sorted(pathlib.Path(directory).glob(f"{prefix}*.{extenstion}"))
    files = directory.rglob(f"*.{extenstion}")
    #print(directory)
    iterator=0
    #file_dict = {item.name: item for item in files}
    for file in files:
        supplier_code = get_code_from_filename(file.stem)
        item = get_product_id_supplier_code(product,supplier_code)
        if item is not None:
            if item["supplier_id"] != inscope_supplier:
                logging.info(f"Supplier code found but not inscope supplier {file.name} - {item['sku']} - {supplierid_dict[item['supplier_id']]['name']} ignoring")
            else:
                lightspeed_api.upload_image(item,file)
        else:
            # Checking for slash replacements
            supplier_code = supplier_code.replace("_","/").upper()
            item = get_product_id_supplier_code(product,supplier_code)
            if item is not None:
                if item["supplier_id"] != inscope_supplier:
                    logging.info(f"Supplier code found but not inscope supplier {file.name} - {item['sku']} - {supplierid_dict[item['supplier_id']]['name']} ignoring")
                else:
                    #lightspeed_api.upload_image(item,file)
                    logging.info(f"Sku Images present {len(item['skuImages'])} {file.name} - {item['sku']} ")
            else:
                logging.info(f"While processing {file.name} no product found {supplier_code}")
