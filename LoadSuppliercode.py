import requests,os
import json,logging

authtoken=os.environ.get('LIGHTSPEED_TOKEN')
storeurl=os.environ.get('LIGHTSPEED_STORE')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_products_from_file(filename='products.json'):
    """Save products dictionary to a JSON file."""
    with open(filename, 'r') as file:
        return json.load(file)
    


if __name__ == "__main__":
    try:
        products_dict = load_products_from_file()
        logging.info(f"Got product {products_dict["TPX52"]["id"]}")
    except Exception as e:
        logging.error(f"An error occurred: {e}",exc_info=True)
