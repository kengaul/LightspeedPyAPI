import json,os,requests
from datetime import datetime
from typing import List, Optional, Dict


class Image:
    """Represents an image with multiple sizes."""
    def __init__(self, url: str, sizes: Dict[str, str]):
        self.url = url
        self.sizes = sizes

    @property
    def original_url(self) -> str:
        """Return the original size URL for matching purposes."""
        return self.sizes.get("original", self.url)

    def __str__(self):
        return f"Image Original URL: {self.original_url}"


class Supplier:
    """Represents a supplier associated with the product."""
    def __init__(self, supplier_id: str, name: str, code: str, price: float):
        self.supplier_id = supplier_id
        self.name = name
        self.code = code
        self.price = float(price)

    def __str__(self):
        return f"Supplier(Name: {self.name}, Price: {self.price:.2f}, Code: {self.code})"


class ProductCode:
    """Represents different codes (e.g., SKU, custom codes) for the product."""
    def __init__(self, code_id: str, code_type: str, code: str):
        self.code_id = code_id
        self.code_type = code_type
        self.code = code

    def __str__(self):
        return f"{self.code_type}: {self.code}"


class VariantOption:
    """Represents a variant option (e.g., color, size)."""
    def __init__(self, option_id: str, name: str, value: str):
        self.option_id = option_id
        self.name = name
        self.value = value

    def __str__(self):
        return f"{self.name}: {self.value}"


class Product:
    """Represents a product, supporting variants and image analysis."""
    def __init__(self, product_id: str, name: str, sku: str, active: bool, supplier: Supplier,
                 created_at: str, updated_at: str, product_codes: List[ProductCode],
                 images: List[Image], sku_images: List[Image], variant_options: List[VariantOption],
                 has_variants: bool = False, variants: Optional[List['Product']] = None,
                 parent_id: Optional[str] = None):

        self.product_id = product_id
        self.parent_id = parent_id
        self.name = name
        self.sku = sku
        self.active = active
        self.supplier = supplier
        self.created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        self.updated_at = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
        self.product_codes = product_codes
        self.images = images  # Parent images
        self.sku_images = sku_images  # SKU-specific images
        self.variant_options = variant_options
        self.has_variants = has_variants
        self.variants = variants if variants else []

    def add_variant(self, variant: 'Product'):
        """Add a variant to the parent product."""
        if self.has_variants:
            self.variants.append(variant)

    def get_combined_variant_options(self) -> str:
        """Return a concatenated string of all variant option values."""
        return " ".join(option.value.lower() for option in self.variant_options)

    def get_all_variant_original_urls(self) -> set:
        """Get all original image URLs used by variants and the parent SKU."""
        all_urls = {img.original_url for img in self.sku_images}
        for variant in self.variants:
            all_urls.update({img.original_url for img in variant.sku_images})
        return all_urls
    
    def match_image_to_variant(self, image: Image) -> str:
        """
        Match an image to a variant using the following priority:
        1. If the image filename starts with the supplier code, use the supplier code.
        2. If the image filename starts with the SKU, use the SKU.
        3. Otherwise, attempt word matching based on variant name.
        4. If no match, return 'unknown'.
        """
        image_name = os.path.basename(image.original_url).lower()
        best_match = None
        best_score = 0
        for variant in self.variants:
            if variant.supplier.code:
                suppliercode=variant.supplier.code
            else:
                suppliercode="No Suuplier Code"
            print(f"\n[DEBUG] Current Image: {image_name} code {suppliercode.lower()} and sku {variant.sku}")
            # 0. Check if the image is already allocated to the variant
            if image.original_url in variant.get_all_variant_original_urls():
                print(f"\n[DEBUG] Already Allocated Image")
                return variant.sku

            # 1. Check if the filename starts with SKU
            if image_name.startswith(variant.sku.lower()):
                print(f"\n[DEBUG] Matched by SKU")
                return variant.sku
            
            # 2. Check if the filename starts with supplier code
            if variant.supplier.code and image_name.startswith(variant.supplier.code.lower()):
                print(f"\n[DEBUG] Matched by Supplier Code")
                return variant.sku
            # 3. Word Matching with a Confidence Score

            variant_option_words = set(variant.get_combined_variant_options().split())
            matched_words = [word for word in variant_option_words if word in image_name]
            match_count = len(matched_words)
            total_words = len(variant_option_words)
            
            confidence_score = match_count / total_words if total_words > 0 else 0
            print(f"[DEBUG] Variant: {variant.variant_options[0].value}, Matched Words: {matched_words}, Confidence: {confidence_score:.2f}")
            # Keep track of the best match
            if confidence_score > best_score:
                best_score = confidence_score
                best_match = variant.sku or variant.supplier.code

            # 4. If confidence is high enough, use best match; otherwise, return 'unknown'
            chosen_match = best_match if best_score >= 0.5 else self.sku
        if best_match:    
            print(f"[DEBUG] Chosen Match: {chosen_match}, Confidence: {best_score:.2f}")
            return chosen_match
        
        print(f"\n[DEBUG] Just Return by SKU not variant or is top level variant")
        return self.sku

    
    def save_images(self, base_dir="images"):
        """Download and save images into supplier-based directories with appropriate naming."""
        supplier_name = self.supplier.name.replace(" ", "_") if self.supplier else "Unknown_Supplier"
        supplier_dir = os.path.join(base_dir, supplier_name)
        os.makedirs(supplier_dir, exist_ok=True)
        
        sequence_counter = 1
        for img in self.images:
            filename_base = self.match_image_to_variant(img) or self.supplier.code or self.sku
            if sequence_counter>1: filename_base += f"_{sequence_counter}"
            sequence_counter += 1
            filename = f"{filename_base}.jpg"
            filepath = os.path.join(supplier_dir, filename)
            self.download_image(img.original_url, filepath)

    @staticmethod
    def download_image(url: str, path: str):
        """Download and save an image from a URL."""
        try:
            response = requests.get(url)
            if response.status_code == 200:
                with open(path, 'wb') as f:
                    f.write(response.content)
                print(f"Image saved to {path}")
            else:
                print(f"Failed to download image from {url} - Status code: {response.status_code}")
        except Exception as e:
            print(f"Error downloading image from {url}: {e}")

    def get_unassigned_images(self) -> List[Image]:
        """Identify images on the parent that are not assigned to any variant using original URL."""
        assigned_urls = self.get_all_variant_original_urls()
        return [img for img in self.images if img.original_url not in assigned_urls]

    def __str__(self):
        return (f"Product: {self.name} (SKU: {self.sku})\\n"
                f"Variants: {len(self.variants)}\\n"
                f"Unassigned Images: {[img.original_url for img in self.get_unassigned_images()]}")


# ------------------- JSON Loader & Analysis -------------------

def load_products_from_json(file_path: str) -> List[Product]:
    """Load products from a JSON file and organize variant families."""
    with open(file_path, 'r') as f:
        data = json.load(f)["data"]

    products = {}
    for item in data:
        supplier_data = item.get("supplier") or {}
        supplier = Supplier(
            supplier_id=supplier_data.get("id", "unknown"),
            name=supplier_data.get("name", "Unknown"),
            code=item.get("supplier_code", ""),
            price=item.get("supply_price", 0.0)
        )
        product = Product(
            product_id=item["id"],
            parent_id=item.get("variant_parent_id"),
            name=item["name"],
            sku=item["sku"],
            supplier=supplier,
            active=item["active"],
            created_at=item["created_at"],
            updated_at=item["updated_at"],
            product_codes=[ProductCode(pc["id"], pc["type"], pc["code"]) for pc in item.get("product_codes", [])],
            images=[Image(img["url"], img.get("sizes", {})) for img in item.get("images", [])],
            sku_images=[Image(img["url"], img.get("sizes", {})) for img in item.get("skuImages", [])],
            variant_options=[VariantOption(opt["id"], opt["name"], opt["value"]) for opt in item.get("variant_options", [])],
            has_variants=item.get("has_variants", False)
        )
        products[product.product_id] = product

    # Associate variants with their parents
    for product in products.values():
        if product.parent_id and product.parent_id in products:
            products[product.parent_id].add_variant(product)

    return list(products.values())


def find_unassigned_images(products: List[Product]) -> Dict[str, List[Image]]:
    """Find products with unassigned images."""
    unassigned = {}
    for product in products:
        if product.has_variants:
            unassigned_images = product.get_unassigned_images()
            if unassigned_images:
                unassigned[product.name] = unassigned_images
    return unassigned


# ------------------- Example Execution -------------------

if __name__ == "__main__":
    # Example: Load products and find unassigned images
    products = load_products_from_json("allproduct.json")
    unassigned_images_map = find_unassigned_images(products)

    for product_name, images in unassigned_images_map.items():
        print(f"Product: {product_name}")
        for img in images:
            print(f"  - Unassigned Image Original URL: {img.original_url}")
    for product in products:
        if not product.parent_id:  # Only process simple products and variant parents
            product.save_images("downloaded_images")
    print("Image processing complete.")
