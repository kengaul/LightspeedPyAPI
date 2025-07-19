import pathlib
import sys

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from parse_orders import write_output

rows = [{
    "name": "A",
    "sku": "1",
    "price": 2.5,
    "inventory": 3,
    "size": "L",
    "color": "Red",
    "material": "Cotton",
    "brand": "B",
    "supplier": "S",
    "category": "C",
}]


def test_write_output_csv(tmp_path):
    out = tmp_path / "out.csv"
    write_output(rows, out)
    content = out.read_text(encoding="utf-8").splitlines()
    assert content[0].split(',') == list(rows[0].keys())
    assert content[1].split(',')[0] == "A"


def test_write_output_xlsx(tmp_path, monkeypatch):
    out = tmp_path / "out.xlsx"
    write_output(rows, out)
    saved = out.read_text(encoding="utf-8").splitlines()
    assert saved[0].split(',')[0] == "name"
    assert saved[1].split(',')[0] == "A"
