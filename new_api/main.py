"""Example script demonstrating usage of the API client."""

from new_api.api_client import LightspeedAPIClient
from new_api.models import Product
from new_api.lookups_runtime import setup
import requests

if __name__ == "__main__":
    try:
        # Create the API client using the token from the environment by default
        client = LightspeedAPIClient()

        # Initialize lookup tables for runtime conversion
        setup(client)
        
        # Example product data
        product_data = {
            "name": "T-Shirt",
            "description": "A comfortable cotton t-shirt",
            "category": "Apparel",
            "brand": "BrandName",
            "supplier": "SupplierName",
            "variants": [
                {"sku": "TSHIRT-S", "price": 19.99, "inventory_level": 100, "attributes": {"size": "S", "color": "Red", "material": "cotton"}},
                {"sku": "TSHIRT-M", "price": 19.99, "inventory_level": 150, "attributes": {"size": "M", "color": "Red", "material": "cotton"}},
            ],
            "tags": ["clothing", "tshirt"],
            "custom_fields": {"material": "cotton"}
        }
        
        product = Product(**product_data)
        created_product = client.create_product(product.dict())
        print("Product created successfully:", created_product)
        
    except requests.HTTPError as e:
        print(f"HTTP error occurred: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
