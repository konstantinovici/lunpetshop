"""TDD tests for WooCommerce API client - Phase 1.

All tests written BEFORE implementation (TDD Red phase).
Run with: python test_woocommerce.py
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import time
from src.woocommerce import WooCommerceClient


class TestWooCommerceClient(unittest.TestCase):
    """Test suite for WooCommerceClient class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.base_url = "https://lunpetshop.com/wp-json/wc/store/v1"
        self.client = WooCommerceClient(base_url=self.base_url)
        
        # Sample product data matching WooCommerce API structure
        self.sample_product = {
            "id": 30014,
            "name": "pate nekko cho mèo 70g",
            "slug": "product-925",
            "prices": {
                "price": "16000",
                "regular_price": "16000",
                "currency_code": "VND",
                "currency_symbol": "₫"
            },
            "images": [{
                "src": "https://lunpetshop.com/wp-content/uploads/2025/07/image.jpg",
                "thumbnail": "https://lunpetshop.com/wp-content/uploads/2025/07/image-300x300.jpg"
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
        
        self.sample_category = {
            "id": 243,
            "name": "Pate mèo",
            "slug": "pate-meo",
            "count": 29
        }
    
    @patch('src.woocommerce.httpx.get')
    def test_search_products_success(self, mock_get):
        """Test successful product search returns list."""
        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [self.sample_product]
        mock_get.return_value = mock_response
        
        # Execute
        results = self.client.search_products("pate", per_page=10)
        
        # Assert
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], 30014)
        self.assertEqual(results[0]["name"], "pate nekko cho mèo 70g")
        mock_get.assert_called_once()
        # Verify correct URL was called
        call_args = mock_get.call_args[0][0]
        self.assertIn("search=pate", call_args)
        self.assertIn("per_page=10", call_args)
    
    @patch('src.woocommerce.httpx.get')
    def test_search_products_no_results(self, mock_get):
        """Test empty list when no matches."""
        # Mock API response with empty list
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response
        
        # Execute
        results = self.client.search_products("nonexistent", per_page=10)
        
        # Assert
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 0)
    
    @patch('src.woocommerce.httpx.get')
    def test_search_products_api_error(self, mock_get):
        """Test handles HTTP errors gracefully."""
        # Mock API error
        mock_get.side_effect = Exception("Connection error")
        
        # Execute and assert
        with self.assertRaises(Exception):
            self.client.search_products("pate", per_page=10)
    
    @patch('src.woocommerce.httpx.get')
    def test_get_products_by_category_id(self, mock_get):
        """Test get products by category ID."""
        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [self.sample_product]
        mock_get.return_value = mock_response
        
        # Execute
        results = self.client.get_products_by_category(category_id=243, per_page=10)
        
        # Assert
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 1)
        mock_get.assert_called_once()
        # Verify correct URL was called
        call_args = mock_get.call_args[0][0]
        self.assertIn("category=243", call_args)
    
    @patch('src.woocommerce.httpx.get')
    def test_get_products_by_category_name_vi(self, mock_get):
        """Test Vietnamese category name lookup."""
        # First call: get categories to find ID
        categories_response = Mock()
        categories_response.status_code = 200
        categories_response.json.return_value = [self.sample_category]
        
        # Second call: get products
        products_response = Mock()
        products_response.status_code = 200
        products_response.json.return_value = [self.sample_product]
        
        mock_get.side_effect = [categories_response, products_response]
        
        # Execute
        results = self.client.get_products_by_category_name("Pate mèo", per_page=10)
        
        # Assert
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 1)
        # Should have called API twice (categories, then products)
        self.assertEqual(mock_get.call_count, 2)
    
    @patch('src.woocommerce.httpx.get')
    def test_get_products_by_category_name_en(self, mock_get):
        """Test English category name lookup."""
        # Mock category with English name
        en_category = {
            "id": 240,
            "name": "Thức ăn cho Mèo",
            "slug": "thuc-an-cho-meo",
            "count": 31
        }
        
        # First call: get categories
        categories_response = Mock()
        categories_response.status_code = 200
        categories_response.json.return_value = [en_category]
        
        # Second call: get products
        products_response = Mock()
        products_response.status_code = 200
        products_response.json.return_value = [self.sample_product]
        
        mock_get.side_effect = [categories_response, products_response]
        
        # Execute - should handle English category name
        # Note: This test assumes the client can match English names
        # Implementation may need a mapping or fuzzy matching
        results = self.client.get_products_by_category_name("Cat Food", per_page=10)
        
        # Assert
        self.assertIsInstance(results, list)
        # Should have attempted to find category
        self.assertGreaterEqual(mock_get.call_count, 1)
    
    @patch('src.woocommerce.httpx.get')
    def test_get_product_by_id(self, mock_get):
        """Test get single product by ID."""
        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.sample_product
        mock_get.return_value = mock_response
        
        # Execute
        product = self.client.get_product_by_id(30014)
        
        # Assert
        self.assertIsInstance(product, dict)
        self.assertEqual(product["id"], 30014)
        self.assertEqual(product["name"], "pate nekko cho mèo 70g")
        mock_get.assert_called_once()
        # Verify correct URL was called
        call_args = mock_get.call_args[0][0]
        self.assertIn("/products/30014", call_args)
    
    @patch('src.woocommerce.httpx.get')
    def test_get_product_by_name(self, mock_get):
        """Test fuzzy match product by name."""
        # Mock search response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [self.sample_product]
        mock_get.return_value = mock_response
        
        # Execute
        product = self.client.get_product_by_name("pate nekko")
        
        # Assert
        self.assertIsInstance(product, dict)
        self.assertEqual(product["id"], 30014)
        # Should have used search endpoint
        call_args = mock_get.call_args[0][0]
        self.assertIn("search=pate nekko", call_args)
    
    @patch('src.woocommerce.httpx.get')
    def test_get_categories(self, mock_get):
        """Test get all categories."""
        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [self.sample_category]
        mock_get.return_value = mock_response
        
        # Execute
        categories = self.client.get_categories()
        
        # Assert
        self.assertIsInstance(categories, list)
        self.assertEqual(len(categories), 1)
        self.assertEqual(categories[0]["id"], 243)
        self.assertEqual(categories[0]["name"], "Pate mèo")
        mock_get.assert_called_once()
        # Verify correct URL was called
        call_args = mock_get.call_args[0][0]
        self.assertIn("/products/categories", call_args)
    
    @patch('src.woocommerce.httpx.get')
    def test_cache_hit(self, mock_get):
        """Test cache returns cached data."""
        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [self.sample_product]
        mock_get.return_value = mock_response
        
        # First call - should hit API
        results1 = self.client.search_products("pate", per_page=10)
        
        # Second call - should use cache (no additional API call)
        results2 = self.client.search_products("pate", per_page=10)
        
        # Assert
        self.assertEqual(results1, results2)
        # Should only call API once due to caching
        self.assertEqual(mock_get.call_count, 1)
    
    @patch('src.woocommerce.httpx.get')
    def test_cache_expiry(self, mock_get):
        """Test cache expires after TTL."""
        # Create client with short TTL for testing
        client = WooCommerceClient(base_url=self.base_url, cache_ttl=1)  # 1 second TTL
        
        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [self.sample_product]
        mock_get.return_value = mock_response
        
        # First call
        client.search_products("pate", per_page=10)
        
        # Wait for cache to expire
        time.sleep(1.1)
        
        # Second call - should hit API again (cache expired)
        client.search_products("pate", per_page=10)
        
        # Assert - should have called API twice
        self.assertEqual(mock_get.call_count, 2)
    
    @patch('src.woocommerce.httpx.get')
    def test_pagination(self, mock_get):
        """Test handles paginated results."""
        # Mock first page
        page1_response = Mock()
        page1_response.status_code = 200
        page1_response.json.return_value = [self.sample_product]
        
        # Mock second page
        page2_response = Mock()
        page2_response.status_code = 200
        page2_response.json.return_value = []
        
        mock_get.side_effect = [page1_response, page2_response]
        
        # Execute - get all products (should handle pagination)
        results = self.client.get_all_products(per_page=100)
        
        # Assert
        self.assertIsInstance(results, list)
        # Should have called API at least once
        self.assertGreaterEqual(mock_get.call_count, 1)
    
    @patch('src.woocommerce.httpx.get')
    def test_timeout_handling(self, mock_get):
        """Test handles request timeouts."""
        # Mock timeout error
        import httpx
        mock_get.side_effect = httpx.TimeoutException("Request timeout")
        
        # Execute and assert
        with self.assertRaises(httpx.TimeoutException):
            self.client.search_products("pate", per_page=10)


if __name__ == "__main__":
    unittest.main()












