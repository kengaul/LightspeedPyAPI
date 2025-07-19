import csv
import json
import yaml
from pathlib import Path
from typing import List, Dict, Any

from new_api.models import Product, Variant, VariantAttributes


def load_definition(path: str | Path) -> Dict[str, Any]:
    """Load a supplier definition from JSON or YAML."""
    path = Path(path)
    with open(path, "r", encoding="utf-8") as f:
        if path.suffix in {".yaml", ".yml"}:
            return yaml.safe_load(f)
        return json.load(f)


def _row_to_product(row: Dict[str, str], mapping: Dict[str, Any]) -> Product:
    prod_map = mapping.get("product", {})
    var_map = mapping.get("variants", {})

    product_data = {
        key: row.get(col, "") for key, col in prod_map.items()
    }

    attr_map = var_map.get("attributes", {})
    attributes = {
        attr: row.get(col, "") for attr, col in attr_map.items()
    }

    variant = Variant(
        sku=row.get(var_map.get("sku", "sku"), ""),
        price=float(row.get(var_map.get("price", "0"), 0) or 0),
        inventory_level=int(row.get(var_map.get("inventory_level", "0"), 0) or 0),
        attributes=VariantAttributes(**attributes),
    )

    product = Product(variants=[variant], **product_data)
    return product


def parse_csv(path: str | Path, mapping: Dict[str, Any]) -> List[Product]:
    products: List[Product] = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            products.append(_row_to_product(row, mapping))
    return products


def parse_text(text: str, mapping: Dict[str, Any], delimiter: str = ",") -> List[Product]:
    """Parse lines of delimited text (e.g., from pdftotext)."""
    lines = [l for l in text.splitlines() if l.strip()]
    reader = csv.DictReader(lines, delimiter=delimiter)
    return [_row_to_product(row, mapping) for row in reader]
