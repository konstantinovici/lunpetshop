"""Knowledge base for LùnPetShop chatbot containing product and business information.

This module provides:
1. Static business information (address, hours, contact)
2. Product data loaded from daily cache (synced from WooCommerce)
3. Helper functions to generate text descriptions for the chatbot
"""

import json
import logging
from pathlib import Path
from typing import Dict, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# Paths
DATA_DIR = Path(__file__).parent.parent / "data"
CACHE_FILE = DATA_DIR / "products_cache.json"

# Business Information (static, rarely changes)
BUSINESS_INFO = {
    "name": "Lùn PetShop",
    "tagline": "Thức ăn, phụ kiện, spa, lưu trú",
    "tagline_en": "Food, accessories, spa, accommodation",
    "website": "https://lunpetshop.com/",
    "address": "46 Văn Cận, Khuê Trung, Cẩm Lệ, Đà Nẵng 550000, Vietnam",
    "phone": "0935005762",
    "zalo": "0935005762",
    "facebook": "https://www.facebook.com/lunpetshop",
    "hours": "8:00 AM – 9:30 PM",
}

# Category name mappings (for display)
CATEGORY_NAMES = {
    "food": {"vi": "Thức ăn", "en": "Food"},
    "pate": {"vi": "Pate", "en": "Pâté"},
    "treats": {"vi": "Ăn vặt Bánh Thưởng", "en": "Treats & Snacks"},
    "shampoo": {"vi": "Sữa tắm", "en": "Shampoo"},
    "litter": {"vi": "Cát vệ sinh", "en": "Litter"},
    "toys": {"vi": "Đồ chơi", "en": "Toys"},
    "clothing": {"vi": "Quần áo", "en": "Clothing"},
    "beds": {"vi": "Nệm Lót", "en": "Beds"},
    "leashes": {"vi": "Vòng Cổ Dây Dắt", "en": "Leashes & Collars"},
    "supplements": {"vi": "TP chức năng", "en": "Supplements"},
    "bowls": {"vi": "Bát ăn Bình Nước", "en": "Bowls & Feeders"},
    "hygiene": {"vi": "Dụng cụ vệ sinh", "en": "Hygiene Tools"},
    "flea_tick": {"vi": "Ve Rận", "en": "Flea & Tick Prevention"},
    "cones": {"vi": "Loa Vòng chống liếm", "en": "Protective Cones"},
    "other": {"vi": "Khác", "en": "Other"},
}

# Fallback product data (used if cache is missing or invalid)
FALLBACK_CAT_PRODUCTS = {
    "food": {"count": 31, "products": [{"name": "Thức ăn hạt GV trộn siêu cấp cho mèo", "price": "80.000 ₫"}]},
    "pate": {"count": 29, "products": [{"name": "Pate Nekko cho mèo 70g", "price": "16.000 ₫"}]},
    "treats": {"count": 25, "products": []},
    "shampoo": {"count": 26, "products": []},
    "litter": {"count": 15, "products": []},
    "toys": {"count": 34, "products": []},
    "clothing": {"count": 35, "products": []},
    "beds": {"count": 15, "products": []},
}

FALLBACK_DOG_PRODUCTS = {
    "food": {"count": 8, "products": []},
    "pate": {"count": 5, "products": []},
    "treats": {"count": 25, "products": [{"name": "Gà viên mix việt quất sấy lạnh 100g", "price": "40.000 ₫"}]},
    "shampoo": {"count": 26, "products": []},
    "toys": {"count": 34, "products": []},
    "clothing": {"count": 35, "products": []},
    "beds": {"count": 15, "products": []},
    "leashes": {"count": 56, "products": []},
}

FALLBACK_GENERAL_PRODUCTS = {
    "supplements": {"count": 16, "products": []},
    "bowls": {"count": 29, "products": []},
    "hygiene": {"count": 7, "products": []},
    "flea_tick": {"count": 14, "products": []},
    "cones": {"count": 9, "products": []},
}

# Cache for loaded product data
_products_cache: Optional[Dict[str, Any]] = None
_cache_load_time: Optional[datetime] = None


def load_products_cache(force_reload: bool = False) -> Dict[str, Any]:
    """
    Load products from cache file.
    
    Args:
        force_reload: Force reload from file even if already cached in memory
        
    Returns:
        Dict with product categories and metadata
    """
    global _products_cache, _cache_load_time
    
    # Return memory cache if available and not forcing reload
    if _products_cache is not None and not force_reload:
        return _products_cache
    
    # Try to load from file
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validate cache structure
            if "categories" in data and "last_sync" in data:
                _products_cache = data
                _cache_load_time = datetime.now()
                logger.info(f"Loaded product cache from {CACHE_FILE} (synced: {data.get('last_sync', 'unknown')})")
                return _products_cache
            else:
                logger.warning("Cache file has invalid structure, using fallback data")
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse cache file: {e}")
        except Exception as e:
            logger.error(f"Failed to load cache file: {e}")
    else:
        logger.warning(f"Cache file not found at {CACHE_FILE}, using fallback data")
    
    # Return fallback data
    _products_cache = {
        "last_sync": None,
        "total_products": 0,
        "sync_status": "fallback",
        "categories": {
            "cat": FALLBACK_CAT_PRODUCTS,
            "dog": FALLBACK_DOG_PRODUCTS,
            "general": FALLBACK_GENERAL_PRODUCTS,
        }
    }
    return _products_cache


def get_cache_status() -> Dict[str, Any]:
    """Get information about the current cache status."""
    cache = load_products_cache()
    return {
        "last_sync": cache.get("last_sync"),
        "total_products": cache.get("total_products", 0),
        "sync_status": cache.get("sync_status", "unknown"),
        "cache_file_exists": CACHE_FILE.exists(),
    }


def get_products_by_pet(pet_type: str) -> Dict[str, Any]:
    """
    Get products for a specific pet type.
    
    Args:
        pet_type: "cat", "dog", or "general"
        
    Returns:
        Dict of categories with products
    """
    cache = load_products_cache()
    return cache.get("categories", {}).get(pet_type, {})


def get_cat_products_text(language: str = "vi") -> str:
    """Generate text description of cat products."""
    cache = load_products_cache()
    cat_products = cache.get("categories", {}).get("cat", {})
    
    if language == "vi":
        text = "🐱 **Sản phẩm cho Mèo:**\n\n"
        for category_key, category_data in cat_products.items():
            category_name = CATEGORY_NAMES.get(category_key, {}).get("vi", category_key)
            count = category_data.get("count", 0)
            text += f"• **{category_name}** - {count} sản phẩm\n"
            
            # Show up to 3 example products
            products = category_data.get("products", [])[:3]
            for product in products:
                name = product.get("name", "")
                price = product.get("price", "")
                if name and price:
                    text += f"  - {name}: {price}\n"
        
        text += f"\n📞 Liên hệ: {BUSINESS_INFO['zalo']} (Zalo) để biết thêm chi tiết!"
    else:
        text = "🐱 **Cat Products:**\n\n"
        for category_key, category_data in cat_products.items():
            category_name = CATEGORY_NAMES.get(category_key, {}).get("en", category_key)
            count = category_data.get("count", 0)
            text += f"• **{category_name}** - {count} products\n"
            
            products = category_data.get("products", [])[:3]
            for product in products:
                name = product.get("name", "")
                price = product.get("price", "")
                if name and price:
                    text += f"  - {name}: {price}\n"
        
        text += f"\n📞 Contact: {BUSINESS_INFO['zalo']} (Zalo) for more details!"
    
    return text


def get_dog_products_text(language: str = "vi") -> str:
    """Generate text description of dog products."""
    cache = load_products_cache()
    dog_products = cache.get("categories", {}).get("dog", {})
    
    if language == "vi":
        text = "🐕 **Sản phẩm cho Chó:**\n\n"
        for category_key, category_data in dog_products.items():
            category_name = CATEGORY_NAMES.get(category_key, {}).get("vi", category_key)
            count = category_data.get("count", 0)
            text += f"• **{category_name}** - {count} sản phẩm\n"
            
            products = category_data.get("products", [])[:3]
            for product in products:
                name = product.get("name", "")
                price = product.get("price", "")
                if name and price:
                    text += f"  - {name}: {price}\n"
        
        text += f"\n📞 Liên hệ: {BUSINESS_INFO['zalo']} (Zalo) để biết thêm chi tiết!"
    else:
        text = "🐕 **Dog Products:**\n\n"
        for category_key, category_data in dog_products.items():
            category_name = CATEGORY_NAMES.get(category_key, {}).get("en", category_key)
            count = category_data.get("count", 0)
            text += f"• **{category_name}** - {count} products\n"
            
            products = category_data.get("products", [])[:3]
            for product in products:
                name = product.get("name", "")
                price = product.get("price", "")
                if name and price:
                    text += f"  - {name}: {price}\n"
        
        text += f"\n📞 Contact: {BUSINESS_INFO['zalo']} (Zalo) for more details!"
    
    return text


def get_all_products_summary(language: str = "vi") -> str:
    """Generate a summary of all products."""
    cache = load_products_cache()
    categories = cache.get("categories", {})
    
    cat_total = sum(c.get("count", 0) for c in categories.get("cat", {}).values())
    dog_total = sum(c.get("count", 0) for c in categories.get("dog", {}).values())
    general_total = sum(c.get("count", 0) for c in categories.get("general", {}).values())
    
    if language == "vi":
        return f"""
🐾 **Tổng quan sản phẩm tại {BUSINESS_INFO['name']}:**

🐱 Sản phẩm cho Mèo: {cat_total} sản phẩm
🐕 Sản phẩm cho Chó: {dog_total} sản phẩm
🎁 Sản phẩm chung: {general_total} sản phẩm

📞 Liên hệ: {BUSINESS_INFO['zalo']} (Zalo)
📍 Địa chỉ: {BUSINESS_INFO['address']}
"""
    else:
        return f"""
🐾 **Product Overview at {BUSINESS_INFO['name']}:**

🐱 Cat Products: {cat_total} products
🐕 Dog Products: {dog_total} products
🎁 General Products: {general_total} products

📞 Contact: {BUSINESS_INFO['zalo']} (Zalo)
📍 Address: {BUSINESS_INFO['address']}
"""


def get_business_info_text(language: str = "vi") -> str:
    """Generate text description of business information."""
    if language == "vi":
        return f"""
🏪 **Thông tin về {BUSINESS_INFO['name']}**

📍 **Địa chỉ:** {BUSINESS_INFO['address']}

📞 **Liên hệ:**
• Phone/Zalo: {BUSINESS_INFO['zalo']}
• Facebook: {BUSINESS_INFO['facebook']}

🕐 **Giờ mở cửa:** {BUSINESS_INFO['hours']}

🐾 **Dịch vụ:** {BUSINESS_INFO['tagline']}

🌐 **Website:** {BUSINESS_INFO['website']}
"""
    else:
        return f"""
🏪 **About {BUSINESS_INFO['name']}**

📍 **Address:** {BUSINESS_INFO['address']}

📞 **Contact:**
• Phone/Zalo: {BUSINESS_INFO['zalo']}
• Facebook: {BUSINESS_INFO['facebook']}

🕐 **Hours:** {BUSINESS_INFO['hours']}

🐾 **Services:** {BUSINESS_INFO['tagline_en']}

🌐 **Website:** {BUSINESS_INFO['website']}
"""


def get_contact_info_text(language: str = "vi") -> str:
    """Generate contact information text."""
    if language == "vi":
        return f"""
📱 **Thông tin Liên hệ:**

• **Zalo:** {BUSINESS_INFO['zalo']}
• **Phone:** {BUSINESS_INFO['phone']}
• **Facebook:** {BUSINESS_INFO['facebook']}
• **Địa chỉ:** {BUSINESS_INFO['address']}

Chúng tôi sẵn sàng hỗ trợ bạn từ {BUSINESS_INFO['hours']} mỗi ngày! 🐾
"""
    else:
        return f"""
📱 **Contact Information:**

• **Zalo:** {BUSINESS_INFO['zalo']}
• **Phone:** {BUSINESS_INFO['phone']}
• **Facebook:** {BUSINESS_INFO['facebook']}
• **Address:** {BUSINESS_INFO['address']}

We're here to help you from {BUSINESS_INFO['hours']} every day! 🐾
"""


def get_knowledge_base_context(language: str = "vi") -> str:
    """
    Get full knowledge base context for the chatbot.
    This is injected into the system prompt so the LLM has all product info.
    """
    cache = load_products_cache()
    sync_info = f"(Data synced: {cache.get('last_sync', 'unknown')})"
    
    context = f"""
=== LÙN PETSHOP KNOWLEDGE BASE ===
{sync_info}

{get_business_info_text(language)}

{get_all_products_summary(language)}

--- CAT PRODUCTS ---
{get_cat_products_text(language)}

--- DOG PRODUCTS ---
{get_dog_products_text(language)}
"""
    return context


# Legacy compatibility - keep old variable names as aliases
CAT_PRODUCTS = FALLBACK_CAT_PRODUCTS
DOG_PRODUCTS = FALLBACK_DOG_PRODUCTS
GENERAL_PRODUCTS = FALLBACK_GENERAL_PRODUCTS
