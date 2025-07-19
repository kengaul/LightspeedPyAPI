import sys
import csv
import requests
import os
import logging
import math
import json
import pathlib

class LightspeedAPI:

    def __init__(self, token, store):
        self.token = token
        self.store = store
    
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
                return None
        except requests.exceptions.JSONDecodeError:
            print("Failed to parse JSON from response ", response.content if response else "")
        except requests.exceptions.RequestException as e:
            print("HTTP Request failed with ", e)

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
                return lightspeed_products_dict
            else:
                return None
        except requests.exceptions.JSONDecodeError:
            print("Failed to parse JSON from response ", response.content if response else "")
        except requests.exceptions.RequestException as e:
            print("HTTP Request failed with ", e)

    def upload_image(self, image_path):
        sku=[os.path.splitext(os.path.basename(image_path))[0]]
        response = None
        try:
            products=self.search_products_by_sku(sku)
            imagecount=0
            #print(f"Got {image_path} and extracted {sku}")
            #print(products)
            if len(products) >0:
                print(f"Found product {products[sku[0]]['sku']}")
                
                if products[sku[0]]['variant_parent_id'] is None:
                    target_product_id=products[sku[0]]["id"]
                else:
                    target_product_id=products[sku[0]]['variant_parent_id']
                    isvariant_flag="*"
                    imagecount=len(products[sku[0]]['skuImages'])

                url = f"https://{self.store}.retail.lightspeed.app/api/2.0/products/{target_product_id}/actions/image_upload"
                headers = {
                    "Authorization": f"Bearer {self.token}"
                }
                files = {'image': open(image_path, 'rb')}
                if imagecount == 0:
                    response = requests.post(url, files=files, headers=headers)
                    if response.status_code == 200:
                        return "Image Updated"
                    else:
                        return "Image Update Failed"
                else:
                    print(f"Skipping {image_path} as product already has {imagecount} images")
            
            else:
                print(f"No product found {sku} from {image_path}")
        except requests.exceptions.JSONDecodeError:
            print("Failed to parse JSON from response ", response.content if response else "")
        except requests.exceptions.RequestException as e:
            print("HTTP Request failed with ", e)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)

def loadskus(fname):
        content_array = []
        with open(fname) as f:
                #Content_list is the list that contains the read lines.     
                for line in f:
                        content_array.append(line.strip())
                return content_array

if __name__ == "__main__":
    # Handle different argument scenarios
    if len(sys.argv) > 5 or len(sys.argv) < 2:
        print(f"{len(sys.argv)} - Usage: python imageupdate.py <prefix> <skulist> <imageext> [--new-only] [--norename]")
        sys.exit(1)
    elif len(sys.argv) == 5 and sys.argv[4] == "--new-only":
        prefix = sys.argv[2]
        skulist = sys.argv[3]
        extenstion = sys.argv[1]
        dorename = False  # In this case, filenames are already SKUs
        upload_only_new = True  # We want to upload only new products
    elif len(sys.argv) == 4:
        prefix = sys.argv[2]
        skulist = sys.argv[3]
        extenstion = sys.argv[1]
        dorename = True  # We will rename files to match SKUs
        upload_only_new = False  # We are renaming files
    else:
        print("Usage error: Missing required parameters")
        sys.exit(1)

    # Load necessary environment variables and SKU list
    token = os.environ.get('LIGHTSPEED_TOKEN')
    store = os.environ.get('LIGHTSPEED_STORE')
    directory = pathlib.Path.cwd()
    
    # Load the SKU list if provided
    skuary = loadskus(skulist)
    lightspeed_api = LightspeedAPI(token, store)

    # Get all files that match the prefix and extension
    files = sorted(pathlib.Path(directory).glob(f"{prefix}*.{extenstion}"))
    
    iterator = 0

    for file in files:
        current_filename_without_extension = os.path.splitext(file.name)[0]  # Get the current filename (no extension)

        if dorename:
            # Rename case: We are renaming files to match SKUs
            sku_from_list = skuary[iterator]  # Get the SKU from the list
            if current_filename_without_extension != sku_from_list:
                new_f_name = file.rename(f"{sku_from_list}.{extenstion}")  # Rename to match the SKU
                print(f"Renamed {file.name} to {new_f_name.name}")
            else:
                new_f_name = file  # No renaming if already matches
        elif upload_only_new:
            # New product upload case: Files must be named as the SKU
            if current_filename_without_extension in skuary:
                new_f_name = file  # File is already correctly named
                print(f"Uploading new product image: {new_f_name.name}")
            else:
                # Skip the file if not part of the new SKU list
                print(f"Skipping {file.name}, not in the new SKU list")
                iterator += 1
                continue

        # Upload the image to Lightspeed
        lightspeed_api.upload_image(new_f_name.name)
        iterator += 1