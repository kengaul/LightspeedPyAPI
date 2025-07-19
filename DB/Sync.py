import requests
import os
import logging
from sqlalchemy.orm import Session
from datetime import datetime
from Classdef import Inventory, get_session, Sale, SaleLineItem, Payment, Consignment, ConsignmentProduct, Outlet, LatestVersion, Product, ProductSupplier, Supplier, ProductCode, ProductImage, VariantOption

# API Configuration
authtoken = os.environ.get("LIGHTSPEED_TOKEN")
storeurl = os.environ.get("LIGHTSPEED_STORE")

web_session = requests.Session()
web_session.headers.update({
    "Authorization": f"Bearer {authtoken}",
    "Accept": "application/json"
})

HEADERS = {
    "Authorization": f"Bearer {authtoken}",
    "Accept": "application/json"
}

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def parse_datetime(date_str):
    if date_str:
        try:
            return datetime.fromisoformat(date_str.rstrip("Z"))
        except ValueError:
            logging.error(f"Invalid datetime format: {date_str}")
    return None

# Fetch latest version for an entity
def get_latest_version(db_session: Session, entity: str, session: requests.session) -> int:
    record = db_session.query(LatestVersion).filter_by(entity=entity).first()
    return record.max_version if record else 0

# Update latest version for an entity
def update_latest_version(db_session: Session, entity: str, max_version: int, session: requests.session):
    record = db_session.query(LatestVersion).filter_by(entity=entity).first()
    if record:
        record.max_version = max_version
    else:
        db_session.add(LatestVersion(entity=entity, max_version=max_version))
    db_session.commit()

# Fetch paginated data from API
def fetch_paginated_data(endpoint: str, entity: str, db_session: Session, session: requests.session):
    after = get_latest_version(db_session, entity, session)
    url = f"https://{storeurl}.retail.lightspeed.app/api/2.0/{endpoint}"
    max_version = after

    while True:
        params = {
            "after": after,
            "page_size": 100 }
        response = session.get(url, params=params)

        if response.status_code != 200:
            logging.error(f"Failed to fetch {entity} - Status {response.status_code}")
            return

        data = response.json()
        if not data.get("data"):
            break

        process_data(data["data"], entity, db_session,session)
        max_version = max(max_version, data["version"]["max"])
        after = data["version"]["max"]

    update_latest_version(db_session, entity, max_version, session)

# Process API data and store in DB
def process_data(data, entity, db_session: Session, session: requests.session):
    try:
        if entity == "sales":
            for sale in data:
                sale_record = Sale(
                    id=sale["id"],
                    outlet_id=sale["outlet_id"],
                    invoice_number=sale["invoice_number"],
                    sale_date=parse_datetime(sale["sale_date"]),
                    total_price=sale["total_price"],
                    total_tax=sale["total_tax"],
                    created_at=parse_datetime(sale["created_at"]),
                    updated_at=parse_datetime(sale["updated_at"])
                )
                db_session.merge(sale_record)

                for item in sale["line_items"]:
                    line_item = SaleLineItem(
                        id=item["id"],
                        sale_id=sale["id"],
                        product_id=item["product_id"],
                        quantity=item["quantity"],
                        price=item["price"],
                        cost=item["cost"],
                        total_price=item["total_price"],
                        total_tax=item["total_tax"],
                        created_at=parse_datetime(sale["created_at"])
                    )
                    db_session.merge(line_item)

                for payment in sale["payments"]:
                    payment_record = Payment(
                        id=payment["id"],
                        sale_id=sale["id"],
                        payment_type=payment["name"],
                        amount=payment["amount"],
                        payment_date=parse_datetime(payment["payment_date"]),
                        created_at=parse_datetime(sale["created_at"])
                    )
                    db_session.merge(payment_record)
            db_session.commit()

        elif entity == "suppliers":
            for supplier in data:
                contact = supplier.get("contact", {})
                supplier_record = Supplier(
                    id=supplier["id"],
                    name=supplier["name"],
                    source=supplier.get("source"),
                    description=supplier.get("description"),
                    deleted_at=parse_datetime(supplier.get("deleted_at")),
                    version=supplier["version"],
                    company_name=contact.get("company_name"),
                    phone=contact.get("phone"),
                    mobile=contact.get("mobile"),
                    fax=contact.get("fax"),
                    website=contact.get("website"),
                    email=contact.get("email"),
                    twitter=contact.get("twitter"),
                    postal_address1=contact.get("postal_address1"),
                    postal_address2=contact.get("postal_address2"),
                    postal_suburb=contact.get("postal_suburb"),
                    postal_postcode=contact.get("postal_postcode"),
                    postal_city=contact.get("postal_city"),
                    postal_state=contact.get("postal_state"),
                    postal_country_id=contact.get("postal_country_id"),
                    physical_address1=contact.get("physical_address1"),
                    physical_address2=contact.get("physical_address2"),
                    physical_suburb=contact.get("physical_suburb"),
                    physical_postcode=contact.get("physical_postcode"),
                    physical_city=contact.get("physical_city"),
                    physical_state=contact.get("physical_state"),
                    physical_country_id=contact.get("physical_country_id")
                )
                db_session.merge(supplier_record)
            db_session.commit()

        elif entity == "products":
            for product in data:
                logging.info(f"Processing Product {product['name']}")
                supplier_data = product.get("supplier", {})
                if supplier_data:
                    logging.info(f"Found Supplier: {supplier_data.get('name', 'Unknown')}")
                    supplier = db_session.query(ProductSupplier).filter_by(id=supplier_data.get("id")).first()
                    if not supplier and supplier_data:
                        supplier = ProductSupplier(
                            id=supplier_data.get("id"),
                            price=supplier_data.get("price", 0.0)
                        )
                        db_session.add(supplier)
                        logging.debug(f"Supplier product added {supplier.id}")
                else:
                    logging.warning(f"No supplier found for product {product['name']}")
                    

                product_record = Product(
                    id=product["id"],
                    parent_id=product.get("variant_parent_id"),
                    name = product["variant_name"] if product.get("variant_parent_id") else product["name"],
                    sku=product["sku"],
                    active=product["is_active"],
                    has_inventory=product["has_inventory"],
                    supplier_id = product.get("supplier_id") or "631dfd2-32c7-2a4e-3d07-1156033616fc",
                    saleaccountcode = product.get("account_code"),
                    purchaseaccountcode = product.get("account_code_purchase"),
                    created_at=parse_datetime(product["created_at"]),
                    updated_at=parse_datetime(product["updated_at"])
                )
                db_session.merge(product_record)
                logging.debug(f"Added Product {product['name']}")

                # Process Product Codes
                for code in product.get("product_codes", []):
                    product_code = ProductCode(
                        id=code["id"],
                        type=code["type"],
                        code=code["code"]
                    )
                    db_session.merge(product_code)
                    logging.debug(f"Added Product Code {product_code.code}")

                # Process Images
                for img in product.get("images", []):
                    image_record = ProductImage(
                        id=img["id"],
                        url=img["url"],
                        original_url=img["sizes"].get("original", img["url"])
                    )
                    db_session.merge(image_record)
                    logging.debug(f"Ading Iamge {image_record.url}")

                for img in product.get("skuImages", []):
                    sku_image_record = ProductImage(
                        id=img["id"],
                        url=img["url"],
                        original_url=img["sizes"].get("original", img["url"])
                    )
                    db_session.merge(sku_image_record)

                # Process Variant Options
                for option in product.get("variant_options", []):
                    variant_option = VariantOption(
                        id=option["id"],
                        product_id=product["id"],
                        name=option["name"],
                        value=option["value"]
                    )
                    db_session.merge(variant_option)
                    logging.debug(f"Variant Added {variant_option.value}")
            db_session.commit()

        elif entity == "consignments":
            for consignment in data:
                consignment_record = Consignment(
                    id=consignment["id"],
                    outlet_id=consignment["outlet_id"],
                    name=consignment.get("reference") or consignment.get("name"),
                    type=consignment["type"],  # STOCKTAKE, SUPPLIER, RETURN
                    status=consignment["status"],
                    consignment_date=parse_datetime(consignment["consignment_date"]),
                    received_at=parse_datetime(consignment["received_at"]),
                    created_at=parse_datetime(consignment["created_at"]),
                    updated_at=parse_datetime(consignment["updated_at"])
                )
                db_session.merge(consignment_record)
                logging.debug(f"Consignment {consignment['id']} merged into session")

                # Process Consignment Products
                url = f"https://{storeurl}.retail.lightspeed.app/api/2.0/consignments/{consignment['id']}/products?page_size=300"

                response = session.get(url)

                if response.status_code == 200:
                    consignment_products = response.json().get("data", [])
                    for product in consignment_products:
                        consignment_product_record = ConsignmentProduct(
                            id=product["product_id"],  # Assuming product_id is unique per consignment
                            consignment_id=consignment["id"],
                            product_id=product["product_id"],
                            count=product["count"],
                            received=product["received"],
                            cost=float(product["cost"]),
                            created_at=parse_datetime(product["created_at"]),
                            updated_at=parse_datetime(product["updated_at"])
                        )
                        db_session.merge(consignment_product_record)
                        logging.debug(f"Consignment product {consignment['id']} {consignment_product_record.id} merged into session")
                    db_session.commit()
                else:
                    logging.error(f"Failed to fetch consignment products for {consignment['id']} - Status {response.status_code}")
            db_session.commit()
            
        elif entity == "inventory":
            for inv in data:
                inventory_record = Inventory(
                    id=inv["id"],
                    outlet_id=inv["outlet_id"],
                    product_id=inv["product_id"],
                    inventory_level=inv.get("inventory_level", 0),
                    current_amount=inv.get("current_amount", 0),
                    version=inv["version"],
                    deleted_at=parse_datetime(inv.get("deleted_at")),
                    average_cost=inv.get("average_cost"),
                    reorder_point=inv.get("reorder_point"),
                    reorder_amount=inv.get("reorder_amount"),
                )
                db_session.merge(inventory_record)
            db_session.commit()
        logging.info(f"Committed {entity} to the database")
    except Exception as e:
        logging.error(f"Error processing {entity}: {e}", exc_info=True)
        session.rollback()  # 🔥 Rollback if something fails

# Fetch and sync all data
def sync_data():
    db_session = get_session()
    fetch_paginated_data("suppliers", "suppliers", db_session, web_session)
    fetch_paginated_data("products", "products", db_session, web_session)
    fetch_paginated_data("sales", "sales", db_session, web_session)
    fetch_paginated_data("consignments", "consignments", db_session, web_session)
    fetch_paginated_data("inventory", "inventory", db_session, web_session)
    db_session.close()

if __name__ == "__main__":
    sync_data()
    logging.info("Data sync complete.")
