import importlib

import pytest

@pytest.mark.parametrize('module_name', ['requests', 'yaml', 'pydantic', 'openpyxl'])
def test_import(module_name):
    importlib.import_module(module_name)
