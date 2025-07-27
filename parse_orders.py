import argparse
import csv
import os
from pathlib import Path
from typing import List

from order_parser import load_definition, parse_csv, parse_text
from image_extractor import pdf_to_text, extract_images


def products_to_rows(products) -> List[dict]:
    rows = []
    for p in products:
        for v in p.variants:
            rows.append({
                "id": p.id,
                "sku": p.sku,
                "description": p.description,	
                "product_category": p.category,	
                "variant_option_one_name": v.variant.attributes[0].name if v.variant.attributes else None,	
                "variant_option_one_value": v.variant.attributes[0].value if v.variant.attributes else None,
                "variant_option_two_name": v.variant.attributes[1].name if len(v.variant.attributes) > 1 else None,
                "variant_option_two_value": v.variant.attributes[1].value if len(v.variant.attributes) > 1 else None,
                "tags": p.tags,
                "supply_price": p.supplier_price,	
                "retail_price": float(p.supply_price)*2.5,
                "tax_name": "VAT" if p.vat>0 or p.vat is None else "Exempt",
                "account_code": 200,
                "account_code_purchase": 631,
                "brand_name": p.brand,	
                "supplier_name": p.supplier,
                "supplier_code": p.supplier_code,
                "name": p.name,
                "sku": p.sku,
                "price": p.price,
                "size": v.attributes.size,
                "color": v.attributes.color,
                "material": v.attributes.material,
                "brand": p.brand,
                "supplier": p.supplier,
                "category": p.category,
            })
    return rows


def write_output(rows: List[dict], out_path: Path) -> None:
    """Write parsed rows to a text CSV file."""

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse supplier orders")
    parser.add_argument("definition", help="Path to supplier definition YAML/JSON")
    parser.add_argument("order_file", help="CSV or PDF file")
    parser.add_argument("--output", default="parsed_orders.csv", help="Output CSV/Excel file")
    parser.add_argument("--extract-images", action="store_true", help="Extract images from PDF if provided")
    parser.add_argument("--upload-images", action="store_true", help="Upload images using ImageUpdateFromCode")
    args = parser.parse_args()

    mapping = load_definition(args.definition)
    order_path = Path(args.order_file)

    if order_path.suffix.lower() == ".pdf":
        text = pdf_to_text(order_path)
        products = parse_text(text, mapping)
        if args.extract_images:
            extract_images(order_path, order_path.parent / "images")
    else:
        products = parse_csv(order_path, mapping)

    rows = products_to_rows(products)
    write_output(rows, Path(args.output))

    if args.upload_images:
        from ImageUpdateFromCode import LightspeedAPI, load_products_from_file, get_code_from_filename, get_product_id_supplier_code
        token = os.environ.get("LIGHTSPEED_TOKEN")
        store = os.environ.get("LIGHTSPEED_STORE")
        api = LightspeedAPI(token, store)
        product_lookup = load_products_from_file()
        image_dir = Path(args.output).with_suffix("").parent / "images"
        for img_path in image_dir.glob("*.jpg"):
            code = get_code_from_filename(img_path.stem)
            prod = get_product_id_supplier_code(product_lookup, code)
            if prod:
                api.upload_image(prod, img_path)


if __name__ == "__main__":
    main()
