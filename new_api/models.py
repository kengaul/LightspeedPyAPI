from typing import List, Optional, Union

from pydantic import BaseModel, ConfigDict, model_validator

from .lookups_runtime import brand_lookup, supplier_lookup, category_lookup


class VariantAttributes(BaseModel):
    """Optional attributes for a product variant."""

    size: Optional[str] = None
    color: Optional[str] = None
    material: Optional[str] = None


class Variant(BaseModel):
    """Representation of a variant row."""

    id: Optional[str] = None
    sku: Optional[str] = None
    price: Optional[float] = None
    inventory_level: int = 0
    attributes: VariantAttributes


class Product(BaseModel):
    """Simplified product model used for order imports."""

    id: Optional[str] = None
    name: str
    sku: Optional[str] = None
    description: Optional[str] = None
    category: Union[str, None] = None
    brand: Union[str, None] = None
    supplier: Union[str, None] = None
    price: Optional[float] = None
    tags: Optional[List[str]] = None
    supplier_code: Optional[str] = None
    custom_fields: Optional[dict] = None
    variants: List[Variant] = []

    @model_validator(mode="before")
    def convert_names_to_ids(cls, values):
        brands_lookup = values.pop("brands_lookup", brand_lookup)
        suppliers_lookup = values.pop("suppliers_lookup", supplier_lookup)
        categories_lookup = values.pop("categories_lookup", category_lookup)

        if isinstance(values.get("brand"), str) and brands_lookup is not None:
            resolved = brands_lookup.get_id(values["brand"])
            if resolved is not None:
                values["brand"] = resolved
        if isinstance(values.get("supplier"), str) and suppliers_lookup is not None:
            resolved = suppliers_lookup.get_id(values["supplier"])
            if resolved is not None:
                values["supplier"] = resolved
        if isinstance(values.get("category"), str) and categories_lookup is not None:
            resolved = categories_lookup.get_id(values.get("category"))
            if resolved is not None:
                values["category"] = resolved
        return values

    model_config = ConfigDict(from_attributes=True)
