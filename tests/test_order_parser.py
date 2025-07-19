import pathlib
import sys

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from order_parser import parse_csv, load_definition


def test_parse_csv_basic(tmp_path):
    csv_path = tmp_path / "orders.csv"
    csv_path.write_text(
        "DESCRIPTION,BRAND,CATEGORY,SUPPLIER,SKU,COST,QTY,SIZE,COLOR,MATERIAL\n"
        "Test Product,BrandA,CatA,SupA,SKU001,1.23,10,L,Red,Cotton\n",
        encoding="utf-8",
    )

    mapping = load_definition(pathlib.Path("supplier_definitions/example_supplier.yaml"))
    products = parse_csv(csv_path, mapping)

    assert len(products) == 1
    prod = products[0]
    assert prod.name == "Test Product"
    assert prod.brand == "BrandA"
    assert prod.category == "CatA"
    assert prod.supplier == "SupA"
    var = prod.variants[0]
    assert var.sku == "SKU001"
    assert var.price == 1.23
    assert var.inventory_level == 10
    assert var.attributes.size == "L"
    assert var.attributes.color == "Red"
    assert var.attributes.material == "Cotton"
