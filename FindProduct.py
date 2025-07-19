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

    def search_products_by_id(self, id):
        try:
            url = f"https://{self.store}.retail.lightspeed.app/api/2.0/search"
            params = [("type", "products")]
            params.append(("sku", id))
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


def loadskus(fname):
        content_array = []
        with open(fname) as f:
                #Content_list is the list that contains the read lines.     
                for line in f:
                        content_array.append(line.strip())
                return content_array

checkdgt = lambda n: "" if n=="10" else n
isbn1310 = lambda n:n[3:12]+checkdgt(str(-sum(i*int(n[13-i])for i in range(2,11))%11))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"{len(sys.argv)} - Usage: python lookupproduct.py <skulist>")
        sys.exit(1)
    
    token = os.environ.get('LIGHTSPEED_TOKEN')
    store = os.environ.get('LIGHTSPEED_STORE')
    
    lightspeed_api = LightspeedAPI(token, store)
    skulist = sys.argv[1]
    skuary=loadskus(skulist)
    #products=lightspeed_api.search_products_by_id(skuary)
    #print(products)
    for sku in skuary:
        #print(file)
        product=lightspeed_api.search_products_by_id(sku)
        if len(product)>0:
            print(sku)
        else:
            sku10=isbn1310(sku)
            isbn8product=lightspeed_api.search_products_by_id(sku10)
            if len(isbn8product)>0:
                  print(sku10)
            else:
                print(f"No product found for sku {sku} or {sku10}")