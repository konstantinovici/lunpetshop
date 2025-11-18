"""Knowledge base for LùnPetShop chatbot containing product and business information."""

# Business Information
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

# Product Categories for Cats
CAT_PRODUCTS = {
    "food": {
        "vi": "Thức ăn cho Mèo",
        "en": "Cat Food",
        "count": 31,
        "examples": [
            {"name": "Thức ăn hạt GV trộn siêu cấp cho mèo – Mix 9 loại 500g", "price": "80,000 ₫"}
        ]
    },
    "pate": {
        "vi": "Pate mèo",
        "en": "Cat Pâté",
        "count": 29,
        "examples": [
            {"name": "Pate Nekko cho mèo 70g", "price": "16,000 ₫"}
        ]
    },
    "treats": {
        "vi": "Ăn vặt Bánh Thưởng",
        "en": "Treats & Snacks",
        "count": 25,
    },
    "shampoo": {
        "vi": "Sữa tắm",
        "en": "Shampoo",
        "count": 26,
        "examples": [
            {"name": "Sữa tắm cho chó mèo SENTEE 500ml", "price": "80,000 ₫"}
        ]
    },
    "litter": {
        "vi": "Cát vệ sinh",
        "en": "Litter",
        "count": 15,
    },
    "toys": {
        "vi": "Đồ chơi chó mèo",
        "en": "Toys",
        "count": 34,
    },
    "clothing": {
        "vi": "Quần áo",
        "en": "Clothing",
        "count": 35,
    },
    "beds": {
        "vi": "Nệm Lót",
        "en": "Beds",
        "count": 15,
    },
}

# Product Categories for Dogs
DOG_PRODUCTS = {
    "food": {
        "vi": "Thức ăn cho Chó",
        "en": "Dog Food",
        "count": 8,
    },
    "pate": {
        "vi": "Pate chó",
        "en": "Dog Pâté",
        "count": 5,
    },
    "treats": {
        "vi": "Ăn vặt Bánh Thưởng",
        "en": "Treats & Snacks",
        "count": 25,
        "examples": [
            {"name": "Gà viên mix việt quất sấy lạnh 100g", "price": "40,000 ₫"},
            {"name": "Gà viên mix việt quất sấy lạnh 500g", "price": "160,000 ₫"},
            {"name": "Cá hồi viên sấy lạnh 200g", "price": "110,000 ₫"},
            {"name": "Bánh Thưởng cho Cún JerHigh Thái Lan", "price": "55,000 ₫"},
        ]
    },
    "shampoo": {
        "vi": "Sữa tắm",
        "en": "Shampoo",
        "count": 26,
    },
    "toys": {
        "vi": "Đồ chơi chó mèo",
        "en": "Toys",
        "count": 34,
    },
    "clothing": {
        "vi": "Quần áo",
        "en": "Clothing",
        "count": 35,
        "examples": [
            {"name": "XL Smiling Face Floral Sweater", "price": "90,000 ₫"},
            {"name": "Áo 4 chân có mũ adidog", "price": "70,000 ₫"},
        ]
    },
    "beds": {
        "vi": "Nệm Lót",
        "en": "Beds",
        "count": 15,
    },
    "leashes": {
        "vi": "Vòng Cổ Dây Dắt",
        "en": "Leashes & Collars",
        "count": 56,
    },
}

# General Product Categories
GENERAL_PRODUCTS = {
    "supplements": {
        "vi": "TP chức năng",
        "en": "Supplements",
        "count": 16,
    },
    "bowls": {
        "vi": "Bát ăn Bình Nước",
        "en": "Bowls & Feeders",
        "count": 29,
    },
    "hygiene": {
        "vi": "Dụng cụ vệ sinh",
        "en": "Hygiene Tools",
        "count": 7,
    },
    "flea_tick": {
        "vi": "Ve Rận",
        "en": "Flea & Tick Prevention",
        "count": 14,
    },
    "cones": {
        "vi": "Loa Vòng chống liếm",
        "en": "Protective Cones",
        "count": 9,
    },
}


def get_cat_products_text(language="vi"):
    """Generate text description of cat products."""
    if language == "vi":
        text = "🐱 **Sản phẩm cho Mèo:**\n\n"
        for category in CAT_PRODUCTS.values():
            text += f"• **{category['vi']}** - {category['count']} sản phẩm\n"
            if "examples" in category:
                for example in category["examples"]:
                    text += f"  - {example['name']}: {example['price']}\n"
        text += f"\n📞 Liên hệ: {BUSINESS_INFO['zalo']} (Zalo) để biết thêm chi tiết!"
    else:
        text = "🐱 **Cat Products:**\n\n"
        for category in CAT_PRODUCTS.values():
            text += f"• **{category['en']}** - {category['count']} products\n"
            if "examples" in category:
                for example in category["examples"]:
                    text += f"  - {example['name']}: {example['price']}\n"
        text += f"\n📞 Contact: {BUSINESS_INFO['zalo']} (Zalo) for more details!"
    return text


def get_dog_products_text(language="vi"):
    """Generate text description of dog products."""
    if language == "vi":
        text = "🐕 **Sản phẩm cho Chó:**\n\n"
        for category in DOG_PRODUCTS.values():
            text += f"• **{category['vi']}** - {category['count']} sản phẩm\n"
            if "examples" in category:
                for example in category["examples"]:
                    text += f"  - {example['name']}: {example['price']}\n"
        text += f"\n📞 Liên hệ: {BUSINESS_INFO['zalo']} (Zalo) để biết thêm chi tiết!"
    else:
        text = "🐕 **Dog Products:**\n\n"
        for category in DOG_PRODUCTS.values():
            text += f"• **{category['en']}** - {category['count']} products\n"
            if "examples" in category:
                for example in category["examples"]:
                    text += f"  - {example['name']}: {example['price']}\n"
        text += f"\n📞 Contact: {BUSINESS_INFO['zalo']} (Zalo) for more details!"
    return text


def get_business_info_text(language="vi"):
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


def get_contact_info_text(language="vi"):
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

