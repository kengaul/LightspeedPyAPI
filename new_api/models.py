from pydantic import BaseModel, root_validator
from typing import List, Optional, Union

class VariantAttributes(BaseModel):
    size: Optional[str]
    color: Optional[str]
    material: Optional[str]

class Variant(BaseModel):
    id: Optional[str]
    sku: str
    price: float
    inventory_level: int
    attributes: VariantAttributes

class Product(BaseModel):
    id: Optional[str]
    name: str
    description: Optional[str] = None
    category: Union[str, Optional[str]] = None
    brand: Union[str, Optional[str]] = None
    supplier: Union[str, Optional[str]] = None
    variants: List[Variant]
    tags: Optional[List[str]] = None
    custom_fields: Optional[dict] = None

    @root_validator(pre=True)
    def convert_names_to_ids(cls, values):
        brands_lookup = values.pop('brands_lookup', None)
        suppliers_lookup = values.pop('suppliers_lookup', None)
        categories_lookup = values.pop('categories_lookup', None)

        if isinstance(values.get('brand'), str) and brands_lookup is not None:
            values['brand'] = brands_lookup.get_id(values['brand'])
        if isinstance(values.get('supplier'), str) and suppliers_lookup is not None:
            values['supplier'] = suppliers_lookup.get_id(values['supplier'])
        if isinstance(values.get('category'), str) and categories_lookup is not None:
            values['category'] = categories_lookup.get_id(values.get('category'))
        return values

    class Config:
        orm_mode = True