import requests
import os

class LightspeedAPIClient:
    API_BASE_URL = f"https://{os.environ.get('LIGHTSPEED_STORE')}.retail.api.lightspeedapp.app/api"
    API_KEY = os.environ.get('LIGHTSPEED_TOKEN')

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

    def _get(self, endpoint: str):
        url = f'{self.API_BASE_URL}/{endpoint}'
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def _post(self, endpoint: str, data: dict):
        url = f'{self.API_BASE_URL}/{endpoint}'
        response = requests.post(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()

    def get_brands(self) -> dict:
        data = self._get('/2.0/brands')
        brands = {brand['name']: brand['brandID'] for brand in data['Brand']}
        return brands

    def get_suppliers(self) -> dict:
        data = self._get('/2.0/suppliers')
        suppliers = {supplier['name']: supplier['supplierID'] for supplier in data['Supplier']}
        return suppliers

    def get_categories(self) -> dict:
        data = self._get('/2.0/product_categories')
        categories = {category['name']: category['categoryID'] for category in data['Category']}
        return categories

    def create_product(self, product: dict):
        return self._post('/2.0/products',product)