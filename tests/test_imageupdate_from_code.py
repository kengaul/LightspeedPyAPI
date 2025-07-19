import pathlib
import sys
import types
import pytest

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
sys.modules.setdefault("requests", types.ModuleType("requests"))
from ImageUpdateFromCode import get_code_from_filename


def test_get_code_standard_case():
    # filename without any suffix
    assert get_code_from_filename(pathlib.Path("ABC123.jpg").stem) == "ABC123"


def test_get_code_with_suffix():
    # filename with underscore suffix
    assert get_code_from_filename(pathlib.Path("ABC123_1.png").stem) == "ABC123"


def test_get_code_hyphen_suffix():
    # filename with hyphen suffix should also be handled
    assert get_code_from_filename(pathlib.Path("ABC123-2.jpeg").stem) == "ABC123"


