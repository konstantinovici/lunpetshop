"""LangChain tools for WooCommerce product search."""

from langchain_core.tools import tool
from typing import List, Dict
from .woocommerce import WooCommerceClient
import os

# Initialize WooCommerce client (singleton pattern)
_client = None

def get_client() -> WooCommerceClient:
    """Get or create WooCommerce client instance."""
    global _client
    if _client is None:
        _client = WooCommerceClient()
    return _client


def format_price(price_str: str) -> str:
    """Format price string with thousand separators.
    
    Args:
        price_str: Price as string (e.g., "16000")
        
    Returns:
        Formatted price (e.g., "16.000 ₫")
    """
    try:
        price = int(price_str)
        # Format with thousand separators
        formatted = f"{price:,}".replace(",", ".")
        return formatted
    except (ValueError, TypeError):
        return price_str


def format_product(product: Dict) -> str:
    """Format a single product as markdown string.
    
    Args:
        product: Product dictionary from WooCommerce API
        
    Returns:
        Formatted markdown string
    """
    name = product.get("name", "Unknown Product")
    prices = product.get("prices", {})
    price = prices.get("price", "0")
    currency_symbol = prices.get("currency_symbol", "₫")
    
    # Format price
    formatted_price = format_price(price)
    
    # Stock information
    stock_info = product.get("stock_availability", {})
    stock_text = stock_info.get("text", "")
    is_in_stock = product.get("is_in_stock", False)
    low_stock = product.get("low_stock_remaining")
    
    # Build stock status
    if not is_in_stock:
        stock_status = "Out of stock"
    elif low_stock is not None and low_stock <= 5:
        stock_status = f"Low stock ({low_stock} remaining)"
    else:
        stock_status = stock_text if stock_text else "In stock"
    
    # Permalink
    permalink = product.get("permalink", "")
    
    # Build formatted string
    lines = [
        f"**{name}** - Price: {formatted_price} {currency_symbol}",
        f"Stock: {stock_status}"
    ]
    
    if permalink:
        lines.append(f"[View Product]({permalink})")
    
    return "\n".join(lines)


def format_products_list(products: List[Dict], max_results: int = 20) -> str:
    """Format a list of products as markdown string.
    
    Args:
        products: List of product dictionaries
        max_results: Maximum number of products to show
        
    Returns:
        Formatted markdown string
    """
    if not products:
        return "No products found. Please contact us via Zalo: 0935005762 for assistance."
    
    # Limit results
    display_products = products[:max_results]
    total_found = len(products)
    
    # Build header
    if total_found > max_results:
        header = f"Found {total_found} products. Showing first {max_results}:\n\n"
    else:
        header = f"Found {total_found} product{'s' if total_found > 1 else ''}:\n\n"
    
    # Format each product
    product_lines = []
    for i, product in enumerate(display_products, 1):
        product_lines.append(f"{i}. {format_product(product)}")
    
    return header + "\n\n".join(product_lines)


@tool
def search_products_tool(query: str) -> str:
    """Search for products by name or description.
    
    Use this tool when the user asks about specific products, product types,
    or wants to find products matching certain criteria.
    
    Args:
        query: Search query string (product name, type, description, etc.)
        
    Returns:
        Formatted markdown string with product list
    """
    try:
        client = get_client()
        max_results = int(os.getenv("WOOCOMMERCE_MAX_PRODUCTS", "20"))
        products = client.search_products(query, per_page=max_results)
        return format_products_list(products, max_results)
    except Exception as e:
        error_msg = str(e)
        # Check if it's a connection error
        if "Connection" in error_msg or "connection" in error_msg.lower():
            return "Xin lỗi, hiện tại không thể kết nối đến hệ thống sản phẩm. Vui lòng thử lại sau hoặc liên hệ trực tiếp qua Zalo: 0935005762 để được hỗ trợ."
        return f"Xin lỗi, đã có lỗi xảy ra khi tìm kiếm sản phẩm: {error_msg}. Vui lòng liên hệ qua Zalo: 0935005762 để được hỗ trợ."


@tool
def get_products_by_category_tool(category_name: str) -> str:
    """Get products in a specific category.
    
    Use this tool when the user asks about products in a category.
    Supports both Vietnamese and English category names.
    Examples: 'Thức ăn cho Mèo', 'Cat Food', 'Pate mèo', 'Quần áo', etc.
    
    Args:
        category_name: Category name in Vietnamese or English
        
    Returns:
        Formatted markdown string with products in that category
    """
    try:
        client = get_client()
        max_results = int(os.getenv("WOOCOMMERCE_MAX_PRODUCTS", "20"))
        products = client.get_products_by_category_name(category_name, per_page=max_results)
        return format_products_list(products, max_results)
    except Exception as e:
        error_msg = str(e)
        # Check if it's a connection error
        if "Connection" in error_msg or "connection" in error_msg.lower():
            return f"Xin lỗi, hiện tại không thể kết nối đến hệ thống sản phẩm để lấy danh mục '{category_name}'. Vui lòng thử lại sau hoặc liên hệ trực tiếp qua Zalo: 0935005762 để được hỗ trợ."
        return f"Xin lỗi, đã có lỗi xảy ra khi lấy sản phẩm từ danh mục '{category_name}': {error_msg}. Vui lòng liên hệ qua Zalo: 0935005762 để được hỗ trợ."


@tool
def get_product_details_tool(product_name: str) -> str:
    """Get detailed information about a specific product by name.
    
    Use this tool when the user asks about a specific product's price,
    stock availability, or other details.
    
    Args:
        product_name: Name of the product to look up
        
    Returns:
        Formatted markdown string with product details
    """
    try:
        client = get_client()
        product = client.get_product_by_name(product_name)
        
        # Format detailed product information
        name = product.get("name", "Unknown Product")
        prices = product.get("prices", {})
        price = prices.get("price", "0")
        currency_symbol = prices.get("currency_symbol", "₫")
        formatted_price = format_price(price)
        
        # Stock information
        stock_info = product.get("stock_availability", {})
        stock_text = stock_info.get("text", "")
        is_in_stock = product.get("is_in_stock", False)
        low_stock = product.get("low_stock_remaining")
        
        # Description
        description = product.get("description", "")
        short_description = product.get("short_description", "")
        
        # Permalink
        permalink = product.get("permalink", "")
        
        # Build detailed response
        lines = [
            f"**{name}**",
            f"",
            f"Price: {formatted_price} {currency_symbol}"
        ]
        
        # Stock status
        if not is_in_stock:
            lines.append("Stock: Out of stock")
        elif low_stock is not None and low_stock <= 5:
            lines.append(f"Stock: Low stock ({low_stock} remaining)")
        else:
            lines.append(f"Stock: {stock_text if stock_text else 'In stock'}")
        
        # Description
        if short_description:
            # Strip HTML tags if present
            import re
            clean_desc = re.sub(r'<[^>]+>', '', short_description)
            if clean_desc.strip():
                lines.append("")
                lines.append(f"Description: {clean_desc.strip()}")
        elif description:
            import re
            clean_desc = re.sub(r'<[^>]+>', '', description)
            if clean_desc.strip():
                lines.append("")
                lines.append(f"Description: {clean_desc.strip()[:200]}...")  # Limit length
        
        # Link
        if permalink:
            lines.append("")
            lines.append(f"[View Product on Website]({permalink})")
        
        return "\n".join(lines)
    except ValueError as e:
        return f"Không tìm thấy sản phẩm '{product_name}'. Vui lòng thử tìm kiếm với từ khóa khác hoặc liên hệ qua Zalo: 0935005762."
    except Exception as e:
        error_msg = str(e)
        # Check if it's a connection error
        if "Connection" in error_msg or "connection" in error_msg.lower():
            return f"Xin lỗi, hiện tại không thể kết nối đến hệ thống sản phẩm để lấy thông tin chi tiết. Vui lòng thử lại sau hoặc liên hệ trực tiếp qua Zalo: 0935005762 để được hỗ trợ."
        return f"Xin lỗi, đã có lỗi xảy ra khi lấy thông tin sản phẩm: {error_msg}. Vui lòng liên hệ qua Zalo: 0935005762 để được hỗ trợ."

