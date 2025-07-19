import sys
import csv
import requests,os
#
# USAGE: /Users/kgaul/.pyenv/versions/3.9.7/bin/python /Users/kgaul/Documents/Lightspeed/PythonAPI/Checkexistsfromorder.py /Users/kgaul/Documents/DaisyCheynes/HeavenSends/403929.csv BARCODES
#
#import requests
#import logging

# Enabling debugging at http.client level (requests->urllib3->http.client)
# you will see the REQUEST, including HEADERS and DATA, and RESPONSE with HEADERS but without DATA.
# the only thing missing will be the response.body which is not logged.
""" try: # for Python 3
    from http.client import HTTPConnection
except ImportError:
    from httplib import HTTPConnection
HTTPConnection.debuglevel = 1

logging.basicConfig() # you need to initialize logging, otherwise you will not see anything from requests
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True
 """

authtoken=os.environ.get('LIGHTSPEED_TOKEN')
storeurl=os.environ.get('LIGHTSPEED_STORE')

def csv_to_dict(csv_file, key_column):
    data_dict = {}
    with open(csv_file, 'r',encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        for row in reader:
            key = row[key_column]
            data_dict[key] = row
    return data_dict

def get_products_bysku(skulist):
    # Request Search
    # GET https://daisycheynes.retail.lightspeed.app/api/2.0/search

    try:
        url=f"https://{storeurl}.retail.lightspeed.app/api/2.0/search"
        params = [("type", "products")]
        for key in skulist:
            params.append(("sku", key))
        headers={
                "Authorization": f"Bearer {authtoken}",
                "Accept": "application/json"
                }
        response = requests.get(url=url,headers=headers,params=params)
        if response.status_code == 200:
            return response.json()
        else:
            return None

    except requests.exceptions.RequestException as e:
        print("HTTP Request failed with ",e)
    except requests.exceptions.JSONDecodeError:
        print("Failed to parse json from response ",{response.content})

    def upload_image(productid,imagepath):
        url=f"https://{storeurl}.retail.lightspeed.app/api/2.0/products/{productid}/actions/image_upload"
        headers={
                "Authorization": f"Bearer {authtoken}"
        }
        files = {'image': open(imagepath, 'rb')}  
        try:        
            response = requests.post( url, files=files, headers=headers)
            if response.status_code == 200:
                return "Image Updated"
            else:
                return "Image Update Failed"

        except requests.exceptions.RequestException as e:
            print("HTTP Request failed with ",e)
        except requests.exceptions.JSONDecodeError:
            print("Failed to parse json from response ",{response.content})

def create_product(product):
    # Request Search
    # GET https://daisycheynes.retail.lightspeed.app/api/2.0/search

    try:
        url=f"https://{storeurl}.retail.lightspeed.app/api/2.0/products"
        params = [("type", "products")]
        headers={
                "Authorization": f"Bearer {authtoken}",
                "Accept": "application/json"
                }
        response = requests.post(url=url,headers=headers,params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print (response)
            return

    except requests.exceptions.RequestException as e:
        print("HTTP Request failed with ",e)
    except requests.exceptions.JSONDecodeError:
        print("Failed to parse json from response ",{response.content})

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <csv_file> <key_column>")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    key_column = sys.argv[2]

    try:
        data_dict = csv_to_dict(csv_file, key_column)
        print("Data extracted successfully:")
        product_info=get_products_bysku(data_dict.keys())
        #print ("Products: ", product_info)
        lightspeed_products = {item["sku"]: item for item in product_info['data']}
        #print ("Products: ",lightspeed_products)
        for key, row in data_dict.items():
            #print ("Key:",key)
            if key in lightspeed_products:
                print(f"Product '{key}' exists in Lightspeed: {lightspeed_products[key]['id']} at {lightspeed_products[key]['supply_price']} before {row['COST']}")
                pathname, extension = os.path.splitext(csv_file)
                imagepath = os.path.join(pathname, f"{key}.png")
                exists = os.path.isfile(imagepath)
                if exists:
                    print ("adding image: ",imagepath)
                    # upload_image(lightspeed_products[key]['id'],imagepath)
                else:
                    print ("no image at: ",imagepath)
                    #     
            else:
                print(f"Product '{key}' does not exist in Lightspeed and needs to be created.")

    except FileNotFoundError:
        print(f"Error: File '{csv_file}' not found.")
    except KeyError:
        print(f"Error: Column '{key_column}' not found in the CSV file.")
    except Exception as e:
        print("An error occurred:", e)