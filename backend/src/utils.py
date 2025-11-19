def detect_language(text: str) -> str:
    """Detect if the message is in Vietnamese or English."""
    # Simple heuristic: check for Vietnamese-specific characters
    vietnamese_chars = ["ă", "â", "đ", "ê", "ô", "ơ", "ư", "à", "á", "ạ", "ả", "ã"]
    vietnamese_words = ["xin", "chào", "sản phẩm", "mèo", "chó", "gì", "của", "có", "thể", "cho"]
    
    text_lower = text.lower()
    
    # Check for Vietnamese characters
    for char in vietnamese_chars:
        if char in text_lower:
            return "vi"
    
    # Check for Vietnamese words
    for word in vietnamese_words:
        if word in text_lower:
            return "vi"
    
    # Default to English if no Vietnamese markers found
    return "en"


def classify_intent(text: str, language: str) -> str:
    """Classify user intent based on message content."""
    text_lower = text.lower()
    
    # Cat product keywords
    cat_keywords_vi = ["mèo", "cat", "kitty", "kitten", "cho mèo"]
    cat_keywords_en = ["cat", "kitty", "kitten", "feline"]
    
    # Dog product keywords
    dog_keywords_vi = ["chó", "dog", "cún", "puppy", "cho chó"]
    dog_keywords_en = ["dog", "puppy", "canine", "pup"]
    
    # Business info keywords
    business_keywords_vi = ["cửa hàng", "shop", "giới thiệu", "về", "business", "dịch vụ"]
    business_keywords_en = ["about", "business", "store", "shop", "service"]
    
    # Contact keywords
    contact_keywords_vi = ["liên hệ", "địa chỉ", "zalo", "phone", "facebook", "contact", "address"]
    contact_keywords_en = ["contact", "address", "phone", "zalo", "facebook", "reach"]
    
    # Check for cat products
    cat_keywords = cat_keywords_vi if language == "vi" else cat_keywords_en
    if any(keyword in text_lower for keyword in cat_keywords):
        return "cat_products"
    
    # Check for dog products
    dog_keywords = dog_keywords_vi if language == "vi" else dog_keywords_en
    if any(keyword in text_lower for keyword in dog_keywords):
        return "dog_products"
    
    # Check for contact info
    contact_keywords = contact_keywords_vi + contact_keywords_en
    if any(keyword in text_lower for keyword in contact_keywords):
        return "contact"
    
    # Check for business info
    business_keywords = business_keywords_vi + business_keywords_en
    if any(keyword in text_lower for keyword in business_keywords):
        return "business"
    
    return "general"

