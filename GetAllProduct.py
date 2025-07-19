import requests,os
import json,logging

authtoken=os.environ.get('LIGHTSPEED_TOKEN')
storeurl=os.environ.get('LIGHTSPEED_STORE')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def saveimage(products):
     """Save the Image to file - Alert if there are images on parent but not assigned"""
     return {
                 product["supplier_code"].upper(): product for product in products
                 if product.get("supplier_code") is not None
            }

def fetch_all_products():
    after = 0
    all_products = []

    while True:
        try:
            products = get_products(after)
            if not products or not products.get("data"):
                break  # Exit loop if no more products

            logging.info(f"Retrieved {len(products['data'])} products from version {after}")
            all_products.extend(products["data"])  # ✅ Append product data

            after = products["version"]["max"]
            logging.info(f"Moving to version {after}")
        except KeyError as e:
            logging.error(f"KeyError encountered: {e}", exc_info=True)
            break
        except TypeError as e:
            logging.error(f"TypeError encountered: {e}", exc_info=True)
            break
        except Exception as e:
            logging.error(f"Unexpected error occurred: {e}", exc_info=True)
            break

    return {"data": all_products}  # ✅ Return wrapped in \"data\" key to match original structure

def save_products_to_file(products_dict, filename='products.json'):
    """Save products dictionary to a JSON file."""
    with open(filename, 'w') as file:
        json.dump(products_dict, file, indent=4)  # Indented for readability

def get_products(after):
    # Request Search
    # GET https://daisycheynes.retail.lightspeed.app/api/2.0/search

    try:
        url=f"https://{storeurl}.retail.lightspeed.app/api/2.0/products"
        params={
            "deleted": "false",
            "after": after
        }
        headers={
            "Authorization": f"Bearer {authtoken}",
            "Accept": "application/json"
        }
        response = requests.get(url=url, headers=headers, params=params)
        print('Response HTTP Status Code: {status_code}'.format(
            status_code=response.status_code))
        #print('Response HTTP Response Body: {content}'.format(
        #    content=response.content))
        if response.status_code == 200:
                print(f"Got a page")
                return response.json()
        else:
                print(response)
                return None
    except requests.exceptions.RequestException as e:
        print("HTTP Request failed with ",e)
    except requests.exceptions.JSONDecodeError:
        logging.error(f"Failed to parse json from response: {e} - {response.content}")

if __name__ == "__main__":
    try:
        products_dict = fetch_all_products()
        save_products_to_file(products_dict, "allproduct.json")
        logging.info(f"Products successfully saved to file with total: {len(products_dict['data'])}")
    except Exception as e:
        logging.error(f"An error occurred: {e}", exc_info=True)
