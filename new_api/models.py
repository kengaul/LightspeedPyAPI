from pydantic import BaseModel, model_validator
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

    @model_validator(mode='before')
    def convert_names_to_ids(cls, values):
        from new_api.main import brands_lookup, suppliers_lookup, categories_lookup
        if isinstance(values.get('brand'), str):
            values['brand'] = brands_lookup.get_id(values['brand'])
        if isinstance(values.get('supplier'), str):
            values['supplier'] = suppliers_lookup.get_id(values['supplier'])
        if isinstance(values.get('category'), str):
            values['category'] = categories_lookup.get_id(values.get('category'))
        return values

    class Config:
        orm_mode = True