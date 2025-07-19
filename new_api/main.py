from api_client import get_brands, get_suppliers, get_categories, create_product
from lookups import BrandLookup, SupplierLookup, CategoryLookup
from models import Product
import requests

if __name__ == "__main__":
    try:
        # Initialize lookup tables
        brands_data = get_brands()
        suppliers_data = get_suppliers()
        categories_data = get_categories()

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
        
        product = Product(**product_data)
        created_product = create_product(product.dict())
        print("Product created successfully:", created_product)
        
    except requests.HTTPError as e:
        print(f"HTTP error occurred: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")