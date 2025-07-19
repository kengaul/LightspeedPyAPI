from typing import Dict

class LookupTable:
    def __init__(self, data: Dict[str, str]):
        self.data = data

    def get_id(self, name: str) -> str:
        return self.data.get(name)
    
    def get_name(self, id: str) -> str:
        return {v: k for k, v in self.data.items()}.get(id)

class BrandLookup(LookupTable):
    pass

class SupplierLookup(LookupTable):
    pass

class CategoryLookup(LookupTable):
    pass