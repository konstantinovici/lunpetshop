#!/usr/bin/env python3
"""
Product Sync Script for LùnPetShop

Syncs products from WooCommerce API to local cache file.
Run daily via cron or manually when products change.

Usage:
    python scripts/sync_products.py
    
Or via wrapper:
    ./scripts/trigger_sync.sh
"""

import os
import sys
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.woocommerce import WooCommerceClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Paths
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "data"
CACHE_FILE = DATA_DIR / "products_cache.json"

# Category mappings (WooCommerce category slugs/names to our structure)
# These map WooCommerce categories to our cat/dog/general classification
CATEGORY_MAPPINGS = {
    # Cat-specific categories
    "cat": ["thuc-an-cho-meo", "cat-food", "pate-meo", "cat-pate", "cat-ve-sinh", "cat-litter"],
    # Dog-specific categories  
    "dog": ["thuc-an-cho-cho", "dog-food", "pate-cho", "dog-pate", "vong-co-day-dat", "leash"],
    # Shared categories (both cat and dog)
    "shared": ["do-choi", "toys", "quan-ao", "clothing", "nem-lot", "beds", "sua-tam", "shampoo", 
               "an-vat-banh-thuong", "treats", "tp-chuc-nang", "supplements", "bat-an-binh-nuoc", 
               "bowls", "dung-cu-ve-sinh", "hygiene", "ve-ran", "flea-tick", "loa-vong-chong-liem", "cones"]
}

# Category type detection keywords
CAT_KEYWORDS = ["mèo", "meo", "cat", "kitten"]
DOG_KEYWORDS = ["chó", "cho", "dog", "puppy", "cún", "cun"]


def detect_pet_type(product: Dict) -> str:
    """Detect if product is for cat, dog, or both based on name/categories."""
    name = product.get("name", "").lower()
    categories = [c.get("name", "").lower() for c in product.get("categories", [])]
    all_text = name + " " + " ".join(categories)
    
    is_cat = any(kw in all_text for kw in CAT_KEYWORDS)
    is_dog = any(kw in all_text for kw in DOG_KEYWORDS)
    
    if is_cat and not is_dog:
        return "cat"
    elif is_dog and not is_cat:
        return "dog"
    else:
        return "general"  # Both or neither


def categorize_product(product: Dict) -> str:
    """Categorize product into our category structure."""
    categories = product.get("categories", [])
    category_slugs = [c.get("slug", "").lower() for c in categories]
    category_names = [c.get("name", "").lower() for c in categories]
    
    # Try to match to our categories
    name = product.get("name", "").lower()
    
    # Food detection
    if any(kw in name for kw in ["thức ăn", "hạt", "food", "dry food"]):
        return "food"
    if any(kw in name for kw in ["pate", "pâté", "wet food"]):
        return "pate"
    if any(kw in name for kw in ["ăn vặt", "bánh thưởng", "treat", "snack"]):
        return "treats"
    if any(kw in name for kw in ["sữa tắm", "shampoo", "dầu gội"]):
        return "shampoo"
    if any(kw in name for kw in ["cát vệ sinh", "litter", "cát mèo"]):
        return "litter"
    if any(kw in name for kw in ["đồ chơi", "toy", "banh", "ball"]):
        return "toys"
    if any(kw in name for kw in ["quần áo", "áo", "clothing", "sweater", "shirt"]):
        return "clothing"
    if any(kw in name for kw in ["nệm", "bed", "giường", "lót"]):
        return "beds"
    if any(kw in name for kw in ["vòng cổ", "dây dắt", "leash", "collar"]):
        return "leashes"
    if any(kw in name for kw in ["chức năng", "supplement", "vitamin"]):
        return "supplements"
    if any(kw in name for kw in ["bát", "bowl", "bình nước", "feeder"]):
        return "bowls"
    if any(kw in name for kw in ["vệ sinh", "hygiene", "dụng cụ"]):
        return "hygiene"
    if any(kw in name for kw in ["ve", "rận", "flea", "tick"]):
        return "flea_tick"
    if any(kw in name for kw in ["loa", "cone", "chống liếm"]):
        return "cones"
    
    return "other"


def format_price(price: str) -> str:
    """Format price to Vietnamese dong format."""
    try:
        # WooCommerce returns price as string like "80000"
        price_num = float(price)
        return f"{price_num:,.0f} ₫".replace(",", ".")
    except (ValueError, TypeError):
        return price or "Liên hệ"


def extract_product_info(product: Dict) -> Dict:
    """Extract relevant product information."""
    return {
        "id": product.get("id"),
        "name": product.get("name", ""),
        "price": format_price(product.get("prices", {}).get("price", "")),
        "regular_price": format_price(product.get("prices", {}).get("regular_price", "")),
        "description": product.get("short_description", "")[:200] if product.get("short_description") else "",
        "url": product.get("permalink", ""),
        "in_stock": product.get("is_in_stock", True),
        "image": product.get("images", [{}])[0].get("src", "") if product.get("images") else ""
    }


def sync_products() -> Dict[str, Any]:
    """
    Fetch all products from WooCommerce and organize into cache structure.
    
    Returns:
        Dict with sync results and product data
    """
    logger.info("Starting product sync from WooCommerce...")
    
    # Initialize client
    client = WooCommerceClient(
        cache_ttl=0,  # No caching for sync
        timeout=30,
        max_retries=3
    )
    
    # Fetch all products
    try:
        all_products = client.get_all_products(per_page=100)
        logger.info(f"Fetched {len(all_products)} products from WooCommerce")
    except Exception as e:
        logger.error(f"Failed to fetch products: {e}")
        raise
    
    # Organize products by pet type and category
    cache_data = {
        "last_sync": datetime.now(timezone.utc).isoformat(),
        "total_products": len(all_products),
        "sync_status": "success",
        "categories": {
            "cat": {},
            "dog": {},
            "general": {}
        }
    }
    
    # Process each product
    for product in all_products:
        pet_type = detect_pet_type(product)
        category = categorize_product(product)
        product_info = extract_product_info(product)
        
        # Initialize category if needed
        if category not in cache_data["categories"][pet_type]:
            cache_data["categories"][pet_type][category] = {
                "count": 0,
                "products": []
            }
        
        # Add product
        cache_data["categories"][pet_type][category]["products"].append(product_info)
        cache_data["categories"][pet_type][category]["count"] += 1
    
    # Log summary
    for pet_type in ["cat", "dog", "general"]:
        total = sum(cat["count"] for cat in cache_data["categories"][pet_type].values())
        logger.info(f"  {pet_type.upper()}: {total} products in {len(cache_data['categories'][pet_type])} categories")
    
    return cache_data


def save_cache(data: Dict[str, Any]) -> None:
    """Save cache data to JSON file."""
    # Ensure data directory exists
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # Write cache file
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Cache saved to {CACHE_FILE}")


def main():
    """Main entry point for sync script."""
    logger.info("=" * 60)
    logger.info("LùnPetShop Product Sync")
    logger.info("=" * 60)
    
    try:
        # Sync products
        cache_data = sync_products()
        
        # Save to cache file
        save_cache(cache_data)
        
        # Print summary
        logger.info("=" * 60)
        logger.info("SYNC COMPLETE")
        logger.info(f"Total products: {cache_data['total_products']}")
        logger.info(f"Last sync: {cache_data['last_sync']}")
        logger.info(f"Cache file: {CACHE_FILE}")
        logger.info("=" * 60)
        
        return 0
        
    except Exception as e:
        logger.error(f"Sync failed: {e}")
        
        # Save error state to cache
        error_data = {
            "last_sync": datetime.now(timezone.utc).isoformat(),
            "total_products": 0,
            "sync_status": "error",
            "error_message": str(e),
            "categories": {"cat": {}, "dog": {}, "general": {}}
        }
        
        # Try to save error state
        try:
            save_cache(error_data)
        except Exception:
            pass
        
        return 1


if __name__ == "__main__":
    sys.exit(main())


