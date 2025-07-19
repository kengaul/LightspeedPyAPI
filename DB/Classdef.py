from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import DeclarativeBase, relationship, sessionmaker
from typing import List, Optional
from datetime import datetime
import os, requests

class Base(DeclarativeBase):
    pass

# ---------------- SUPPLIERS ----------------
class Supplier(Base):
    """General Supplier entity from the 'listSuppliers' API"""
    __tablename__ = "suppliers"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    source = Column(String, nullable=True)
    description = Column(String, nullable=True)
    deleted_at = Column(DateTime, nullable=True)
    version = Column(Integer, nullable=False)
    
    contact_first_name = Column(String, nullable=True)
    contact_last_name = Column(String, nullable=True)
    company_name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    mobile = Column(String, nullable=True)
    fax = Column(String, nullable=True)
    website = Column(String, nullable=True)
    email = Column(String, nullable=True)
    twitter = Column(String, nullable=True)
    
    postal_address1 = Column(String, nullable=True)
    postal_address2 = Column(String, nullable=True)
    postal_suburb = Column(String, nullable=True)
    postal_postcode = Column(String, nullable=True)
    postal_city = Column(String, nullable=True)
    postal_state = Column(String, nullable=True)
    postal_country_id = Column(String, nullable=True)
    
    physical_address1 = Column(String, nullable=True)
    physical_address2 = Column(String, nullable=True)
    physical_suburb = Column(String, nullable=True)
    physical_postcode = Column(String, nullable=True)
    physical_city = Column(String, nullable=True)
    physical_state = Column(String, nullable=True)
    physical_country_id = Column(String, nullable=True)

# ---------------- PRODUCT SUPPLIERS ----------------
class ProductSupplier(Base):
    """Represents a supplier relationship for a specific product"""
    __tablename__ = "product_suppliers"

    id = Column(String, primary_key=True)
    product_id = Column(String, ForeignKey("products.id"))
    supplier_id = Column(String, ForeignKey("suppliers.id"))
    price = Column(Float)

    product = relationship("Product", back_populates="suppliers")
    supplier = relationship("Supplier")

# ---------------- PRODUCTS ----------------
class Product(Base):
    __tablename__ = "products"

    id = Column(String, primary_key=True)
    parent_id = Column(String, ForeignKey("products.id"), nullable=True)  # Recursive for variants
    name = Column(String, nullable=False)
    sku = Column(String, nullable=False)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    supplier_id = Column(String, nullable=False)
    has_inventory = Column(Boolean)
    saleaccountcode = Column(Integer)
    purchaseaccountcode = Column(Integer)

    suppliers = relationship("ProductSupplier", back_populates="product")
    product_codes = relationship("ProductCode", back_populates="product")
    variant_options = relationship("VariantOption", back_populates="product")
    images = relationship("ProductImage", back_populates="product")
    inventory = relationship("Inventory", back_populates="product")

# ---------------- PRODUCT CODES ----------------
class ProductCode(Base):
    __tablename__ = "product_codes"

    id = Column(String, primary_key=True)
    product_id = Column(String, ForeignKey("products.id"))
    type = Column(String, nullable=False)
    code = Column(String, nullable=False)

    product = relationship("Product", back_populates="product_codes")

# ---------------- VARIANT OPTIONS ----------------
class VariantOption(Base):
    __tablename__ = "variant_options"

    id = Column(String, primary_key=True)
    product_id = Column(String, ForeignKey("products.id"))
    name = Column(String, nullable=False)
    value = Column(String, nullable=False)

    product = relationship("Product", back_populates="variant_options")

# ---------------- PRODUCT IMAGES ----------------
class ProductImage(Base):
    __tablename__ = "product_images"

    id = Column(String, primary_key=True)
    product_id = Column(String, ForeignKey("products.id"))
    url = Column(String, nullable=False)
    original_url = Column(String, nullable=False)

    product = relationship("Product", back_populates="images")

# ---------------- SALES ----------------
class Sale(Base):
    __tablename__ = "sales"

    id = Column(String, primary_key=True)
    outlet_id = Column(String, ForeignKey("outlets.id"))
    invoice_number = Column(String)  # Unique only within an outlet
    sale_date = Column(DateTime)
    total_price = Column(Float)
    total_tax = Column(Float)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    line_items = relationship("SaleLineItem", back_populates="sale")
    payments = relationship("Payment", back_populates="sale")

class SaleLineItem(Base):
    __tablename__ = "sale_line_items"

    id = Column(String, primary_key=True)
    sale_id = Column(String, ForeignKey("sales.id"))
    product_id = Column(String, ForeignKey("products.id"))
    quantity = Column(Integer)
    price = Column(Float)
    cost = Column(Float)
    total_price = Column(Float)
    total_tax = Column(Float)
    created_at = Column(DateTime)

    sale = relationship("Sale", back_populates="line_items")
    product = relationship("Product")

class Payment(Base):
    __tablename__ = "payments"

    id = Column(String, primary_key=True)
    sale_id = Column(String, ForeignKey("sales.id"))
    payment_type = Column(String)
    amount = Column(Float)
    payment_date = Column(DateTime)
    created_at = Column(DateTime)

    sale = relationship("Sale", back_populates="payments")

# ---------------- CONSIGNMENTS ----------------
class Consignment(Base):
    __tablename__ = "consignments"

    id = Column(String, primary_key=True)
    outlet_id = Column(String, ForeignKey("outlets.id"))
    name = Column(String, nullable=True)
    type = Column(String)  # STOCKTAKE, SUPPLIER, RETURN
    status = Column(String)
    consignment_date = Column(DateTime)
    received_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    products = relationship("ConsignmentProduct", back_populates="consignment")

class ConsignmentProduct(Base):
    __tablename__ = "consignment_products"

    id = Column(String, primary_key=True)
    consignment_id = Column(String, ForeignKey("consignments.id"))
    product_id = Column(String, ForeignKey("products.id"))
    count = Column(Integer)
    received = Column(Integer)
    cost = Column(Float)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    consignment = relationship("Consignment", back_populates="products")
    product = relationship("Product")

# ---------------- OUTLETS ----------------
class Outlet(Base):
    __tablename__ = "outlets"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(String, primary_key=True)
    outlet_id = Column(String, ForeignKey("outlets.id"))
    product_id = Column(String, ForeignKey("products.id"))
    inventory_level = Column(Integer, nullable=False, default=0)
    current_amount = Column(Integer, nullable=False, default=0)
    version = Column(Integer, nullable=False)
    deleted_at = Column(DateTime, nullable=True)
    average_cost = Column(Float, nullable=True)
    reorder_point = Column(Integer, nullable=True)
    reorder_amount = Column(Integer, nullable=True)

    # Relationships
    product = relationship("Product", back_populates="inventory")
    #outlet = relationship("Outlet", back_populates="inventory")

# ---------------- LATEST VERSION TRACKING ----------------
class LatestVersion(Base):
    __tablename__ = "latest_version"
    
    entity = Column(String, primary_key=True)  # e.g., "sales", "consignments"
    max_version = Column(Integer, nullable=False)

# ---------------- DATABASE SETUP ----------------
DATABASE_URL = "sqlite:///retail_data.db"  # Change to PostgreSQL if needed
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# Initialize Database
Base.metadata.create_all(engine)

def get_session():
    return SessionLocal()