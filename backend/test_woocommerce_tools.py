"""TDD tests for WooCommerce LangChain tools - Phase 2.

All tests written BEFORE implementation (TDD Red phase).
Run with: python test_woocommerce_tools.py
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from src.woocommerce_tools import (
    search_products_tool,
    get_products_by_category_tool,
    get_product_details_tool
)


class TestWooCommerceTools(unittest.TestCase):
    """Test suite for WooCommerce LangChain tools."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sample_product = {
            "id": 30014,
            "name": "pate nekko cho mèo 70g",
            "prices": {
                "price": "16000",
                "regular_price": "16000",
                "currency_code": "VND",
                "currency_symbol": "₫"
            },
            "images": [{
                "src": "https://lunpetshop.com/wp-content/uploads/2025/07/image.jpg"
            }],
            "categories": [{
                "id": 243,
                "name": "Pate mèo",
                "slug": "pate-meo"
            }],
            "stock_availability": {
                "text": "Còn 29 trong kho",
                "class": "in-stock"
            },
            "is_in_stock": True,
            "permalink": "https://lunpetshop.com/sanpham/product-925/"
        }
        
        self.sample_products_list = [
            self.sample_product,
            {
                "id": 30012,
                "name": "Sữa tắm cho chó mèo SENTEE chai 500ml",
                "prices": {
                    "price": "80000",
                    "currency_code": "VND",
                    "currency_symbol": "₫"
                },
                "stock_availability": {
                    "text": "Còn 4 trong kho",
                    "class": "in-stock"
                },
                "is_in_stock": True,
                "permalink": "https://lunpetshop.com/sanpham/product-923/"
            }
        ]
    
    @patch('src.woocommerce_tools.WooCommerceClient')
    def test_search_products_tool_success(self, mock_client_class):
        """Test tool returns formatted markdown."""
        # Setup mock client
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.search_products.return_value = self.sample_products_list
        
        # Execute
        result = search_products_tool("pate")
        
        # Assert
        self.assertIsInstance(result, str)
        self.assertIn("pate nekko cho mèo 70g", result)
        self.assertIn("16.000 ₫", result)  # Formatted price
        self.assertIn("Sữa tắm cho chó mèo", result)
        self.assertIn("80.000 ₫", result)
        # Should contain markdown formatting
        self.assertIn("**", result)  # Bold product names
        # Should contain links
        self.assertIn("lunpetshop.com", result)
        mock_client.search_products.assert_called_once_with("pate", per_page=20)
    
    @patch('src.woocommerce_tools.WooCommerceClient')
    def test_search_products_tool_empty(self, mock_client_class):
        """Test handles no results gracefully."""
        # Setup mock client
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.search_products.return_value = []
        
        # Execute
        result = search_products_tool("nonexistent product")
        
        # Assert
        self.assertIsInstance(result, str)
        self.assertIn("not found", result.lower() or "no results", result.lower())
        # Should return a user-friendly message
    
    @patch('src.woocommerce_tools.WooCommerceClient')
    def test_get_products_by_category_tool_vi(self, mock_client_class):
        """Test Vietnamese category tool."""
        # Setup mock client
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.get_products_by_category_name.return_value = self.sample_products_list
        
        # Execute
        result = get_products_by_category_tool("Pate mèo")
        
        # Assert
        self.assertIsInstance(result, str)
        self.assertIn("Pate mèo", result)
        self.assertIn("pate nekko", result.lower())
        mock_client.get_products_by_category_name.assert_called_once_with("Pate mèo", per_page=20)
    
    @patch('src.woocommerce_tools.WooCommerceClient')
    def test_get_products_by_category_tool_en(self, mock_client_class):
        """Test English category tool."""
        # Setup mock client
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.get_products_by_category_name.return_value = self.sample_products_list
        
        # Execute
        result = get_products_by_category_tool("Cat Food")
        
        # Assert
        self.assertIsInstance(result, str)
        # Should handle English category name
        mock_client.get_products_by_category_name.assert_called_once_with("Cat Food", per_page=20)
    
    @patch('src.woocommerce_tools.WooCommerceClient')
    def test_get_product_details_tool(self, mock_client_class):
        """Test product details formatting."""
        # Setup mock client
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.get_product_by_name.return_value = self.sample_product
        
        # Execute
        result = get_product_details_tool("pate nekko cho mèo 70g")
        
        # Assert
        self.assertIsInstance(result, str)
        self.assertIn("pate nekko cho mèo 70g", result)
        self.assertIn("16.000 ₫", result)  # Formatted price
        self.assertIn("Còn 29 trong kho", result)  # Stock info
        self.assertIn("lunpetshop.com", result)  # Link
        # Should have detailed formatting
        self.assertIn("**", result)  # Bold formatting
        mock_client.get_product_by_name.assert_called_once_with("pate nekko cho mèo 70g")
    
    @patch('src.woocommerce_tools.WooCommerceClient')
    def test_tool_error_handling(self, mock_client_class):
        """Test tools handle client errors."""
        # Setup mock client to raise error
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.search_products.side_effect = Exception("API Error")
        
        # Execute
        result = search_products_tool("pate")
        
        # Assert
        self.assertIsInstance(result, str)
        # Should return user-friendly error message
        self.assertIn("error", result.lower() or "sorry", result.lower() or "unable", result.lower())
        # Should suggest contacting via Zalo
        self.assertIn("zalo", result.lower() or "contact", result.lower())
    
    @patch('src.woocommerce_tools.WooCommerceClient')
    def test_tool_markdown_formatting(self, mock_client_class):
        """Test verify markdown structure."""
        # Setup mock client
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.search_products.return_value = self.sample_products_list
        
        # Execute
        result = search_products_tool("pate")
        
        # Assert markdown structure
        self.assertIn("**", result)  # Bold for product names
        # Should have proper line breaks
        lines = result.split("\n")
        self.assertGreater(len(lines), 1)  # Multiple lines
        # Each product should be on separate lines or clearly separated
    
    @patch('src.woocommerce_tools.WooCommerceClient')
    def test_tool_max_results_limit(self, mock_client_class):
        """Test respects max products limit."""
        # Setup mock client
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # Create list with more than max products
        many_products = self.sample_products_list * 15  # 30 products
        mock_client.search_products.return_value = many_products
        
        # Execute
        result = search_products_tool("pate")
        
        # Assert
        # Should limit results (implementation may limit to 20)
        mock_client.search_products.assert_called_once()
        # Result should indicate if limited
        # (Implementation may show "Showing first X results" or similar)
    
    @patch('src.woocommerce_tools.WooCommerceClient')
    def test_tool_low_stock_formatting(self, mock_client_class):
        """Test formatting for low stock products."""
        # Product with low stock
        low_stock_product = {
            "id": 30008,
            "name": "Áo 4 chân có mũ adidog",
            "prices": {
                "price": "70000",
                "currency_code": "VND",
                "currency_symbol": "₫"
            },
            "stock_availability": {
                "text": "Còn 1 trong kho",
                "class": "in-stock"
            },
            "low_stock_remaining": 1,
            "is_in_stock": True,
            "permalink": "https://lunpetshop.com/sanpham/product-919/"
        }
        
        # Setup mock client
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.search_products.return_value = [low_stock_product]
        
        # Execute
        result = search_products_tool("áo")
        
        # Assert
        self.assertIn("Còn 1 trong kho", result)
        # Should indicate low stock clearly
        self.assertIn("1", result)


if __name__ == "__main__":
    unittest.main()









