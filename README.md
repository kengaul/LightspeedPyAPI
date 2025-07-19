# LightspeedPyAPI

This repository contains a collection of scripts and modules for working with the **Lightspeed Retail X-Series** API. The code is focused on downloading product data, validating existing items, uploading images, and storing information in a local SQLite database.

## Repository overview

```
LightspeedPyAPI/
├── DB/                      # Database models and sync logic
│   ├── Classdef.py          # SQLAlchemy ORM definitions
│   └── Sync.py              # Fetches Lightspeed data and stores in DB
├── new_api/                 # Experimental client/models
│   ├── api_client.py        # Minimal API wrapper
│   ├── lookups.py           # Lookup classes for names ↔ IDs
│   ├── lookups_runtime.py   # Runtime lookup initialization
│   ├── main.py              # Example product creation script
│   └── models.py            # Pydantic models for Product/Variant
├── CheckExisting.py, OrderProduct.py, etc.
└── README.md
```

Most scripts rely on **two environment variables** for authentication and store selection:

```python
class LightspeedAPIClient:
    API_BASE_URL = f"https://{os.environ.get('LIGHTSPEED_STORE')}.retail.api.lightspeedapp.app/api"
    API_KEY = os.environ.get('LIGHTSPEED_TOKEN')
```

### Key modules

1. **DB/**
   - `Classdef.py` defines SQLAlchemy models for suppliers, products, consignment records, inventory, and a version tracker.
   - `Sync.py` contains `sync_data()` which fetches paginated data from Lightspeed, processes it, and updates the local DB.

2. **new_api/**
   - `models.py` uses Pydantic to model product data and to convert friendly names to IDs via lookup tables. Lookups are loaded at runtime by `lookups_runtime.setup()`.
   - `api_client.py` is a lightweight wrapper around Lightspeed endpoints.
   - `main.py` demonstrates loading lookups and creating a product with variants.

3. **Utility scripts**
   - Scripts such as `CheckExisting.py`, `OrderProduct.py`, and `imageupdate.py` parse CSV files, compare product data, and upload images. Many of these are ad-hoc command line tools.
   - `productanalysis.py` loads product JSON, analyzes variant images, and downloads images with matching logic.

## Important concepts

- **Environment variables** `LIGHTSPEED_TOKEN` and `LIGHTSPEED_STORE` must be set for the API client.
- **CSV workflows** are used to process supplier order files and determine which products need creation or updates.
- **Database sync** via `DB/Sync.py` fetches suppliers, products, sales, consignments, and inventory from Lightspeed into a local SQLite database.

## Learning paths

If you're new to the repository, consider exploring the following topics:

1. **Lightspeed API** – Review the official documentation to understand available endpoints for products, suppliers, and variants.
2. **SQLAlchemy ORM basics** – `DB/Classdef.py` defines relationships between products, suppliers, inventory, and sales. Understanding SQLAlchemy sessions will help you extend or query the local DB.
3. **Pydantic for data validation** – `new_api/models.py` uses Pydantic models to prepare product data before sending it to the API.
4. **Script usage patterns** – Many scripts operate as command-line tools expecting CSV files or directories of images. Reading through `imageupdate.py` or `CheckOrderAndCreate.py` provides examples.
5. **Potential refactoring** – The project is primarily a set of standalone scripts. If you plan to extend it, consider organizing it into a Python package, consolidating API wrappers, and adding automated tests.

This overview should help you navigate the repository and identify areas for further exploration.

