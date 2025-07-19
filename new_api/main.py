"""Example script demonstrating usage of the API client."""

from new_api.api_client import LightspeedAPIClient
from new_api.lookups import BrandLookup, SupplierLookup, CategoryLookup
from new_api.models import Product
import requests

if __name__ == "__main__":
    try:
        # Create the API client using the token from the environment by default
        client = LightspeedAPIClient()

        # Initialize lookup tables
        brands_data = client.get_brands()
        suppliers_data = client.get_suppliers()
        categories_data = client.get_categories()

        brands_lookup = BrandLookup(brands_data)
        suppliers_lookup = SupplierLookup(suppliers_data)
        categories_lookup = CategoryLookup(categories_data)
        
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
        
        product = Product(
            **product_data,
            brands_lookup=brands_lookup,
            suppliers_lookup=suppliers_lookup,
            categories_lookup=categories_lookup,
        )
        created_product = client.create_product(product.dict())
        print("Product created successfully:", created_product)
        
    except requests.HTTPError as e:
        print(f"HTTP error occurred: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")