"""Runtime lookup initialization for converting names to IDs."""

from typing import Optional
from .lookups import BrandLookup, SupplierLookup, CategoryLookup
from .api_client import LightspeedAPIClient

# Module-level lookup instances; may remain ``None`` if setup() hasn't been called
brand_lookup: Optional[BrandLookup] = None
supplier_lookup: Optional[SupplierLookup] = None
category_lookup: Optional[CategoryLookup] = None


def setup(client: LightspeedAPIClient) -> None:
    """Populate lookup tables using the given API client."""
    global brand_lookup, supplier_lookup, category_lookup

    brands_data = client.get_brands()
    suppliers_data = client.get_suppliers()
    categories_data = client.get_categories()

    brand_lookup = BrandLookup(brands_data)
    supplier_lookup = SupplierLookup(suppliers_data)
    category_lookup = CategoryLookup(categories_data)

