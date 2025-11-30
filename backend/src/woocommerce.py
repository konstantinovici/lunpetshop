"""WooCommerce Store API client for fetching product data."""

import os
import time
import httpx
from typing import List, Dict, Optional
from urllib.parse import urlencode


class WooCommerceClient:
    """Client for interacting with WooCommerce Store API."""
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        cache_ttl: int = 300,
        timeout: int = 10
    ):
        """Initialize WooCommerce client.
        
        Args:
            base_url: Base URL for WooCommerce API (defaults to env var or production)
            cache_ttl: Cache TTL in seconds (default: 300)
            timeout: Request timeout in seconds (default: 10)
        """
        self.base_url = base_url or os.getenv(
            "WOOCOMMERCE_API_BASE_URL",
            "https://lunpetshop.com/wp-json/wc/store/v1"
        )
        self.cache_ttl = cache_ttl
        self.timeout = timeout
        self._cache: Dict[str, tuple] = {}  # {cache_key: (data, timestamp)}
        self._categories_cache: Optional[List[Dict]] = None
        self._categories_cache_time: float = 0
    
    def _get_cache_key(self, endpoint: str, params: Dict) -> str:
        """Generate cache key from endpoint and parameters."""
        sorted_params = sorted(params.items())
        param_str = urlencode(sorted_params)
        return f"{endpoint}?{param_str}"
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cache entry is still valid."""
        if cache_key not in self._cache:
            return False
        _, timestamp = self._cache[cache_key]
        return (time.time() - timestamp) < self.cache_ttl
    
    def _get_from_cache(self, cache_key: str) -> Optional[any]:
        """Get data from cache if valid."""
        if self._is_cache_valid(cache_key):
            data, _ = self._cache[cache_key]
            return data
        return None
    
    def _set_cache(self, cache_key: str, data: any):
        """Store data in cache."""
        self._cache[cache_key] = (data, time.time())
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> any:
        """Make HTTP request to WooCommerce API.
        
        Args:
            endpoint: API endpoint (e.g., '/products')
            params: Query parameters
            
        Returns:
            JSON response data
            
        Raises:
            httpx.HTTPError: On HTTP errors
            httpx.TimeoutException: On timeout
        """
        url = f"{self.base_url}{endpoint}"
        if params:
            url += "?" + urlencode(params)
        
        # Use httpx with SSL verification and proper headers
        with httpx.Client(
            timeout=self.timeout,
            verify=True,  # SSL verification
            follow_redirects=True,
            headers={
                "User-Agent": "LunPetShop-Chatbot/1.0",
                "Accept": "application/json"
            }
        ) as client:
            response = client.get(url)
            response.raise_for_status()
            return response.json()
    
    def search_products(self, query: str, per_page: int = 10) -> List[Dict]:
        """Search products by name or description.
        
        Args:
            query: Search query string
            per_page: Number of results per page
            
        Returns:
            List of product dictionaries
        """
        cache_key = self._get_cache_key("/products", {"search": query, "per_page": per_page})
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return cached
        
        params = {"search": query, "per_page": per_page}
        results = self._make_request("/products", params)
        self._set_cache(cache_key, results)
        return results
    
    def get_products_by_category(self, category_id: int, per_page: int = 10) -> List[Dict]:
        """Get products in a specific category by ID.
        
        Args:
            category_id: Category ID
            per_page: Number of results per page
            
        Returns:
            List of product dictionaries
        """
        cache_key = self._get_cache_key("/products", {"category": str(category_id), "per_page": per_page})
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return cached
        
        params = {"category": category_id, "per_page": per_page}
        results = self._make_request("/products", params)
        self._set_cache(cache_key, results)
        return results
    
    def get_products_by_category_name(self, category_name: str, per_page: int = 10) -> List[Dict]:
        """Get products by category name (supports Vietnamese and English).
        
        Args:
            category_name: Category name in Vietnamese or English
            per_page: Number of results per page
            
        Returns:
            List of product dictionaries
        """
        # Get categories if not cached or cache expired
        if (self._categories_cache is None or 
            (time.time() - self._categories_cache_time) > self.cache_ttl):
            self._categories_cache = self.get_categories()
            self._categories_cache_time = time.time()
        
        # Find matching category
        category_id = None
        for category in self._categories_cache:
            # Check exact match (case-insensitive)
            if category["name"].lower() == category_name.lower():
                category_id = category["id"]
                break
            # Check slug match
            if category.get("slug", "").lower() == category_name.lower().replace(" ", "-"):
                category_id = category["id"]
                break
        
        if category_id is None:
            # Try fuzzy matching - check if category name contains the search term
            for category in self._categories_cache:
                if category_name.lower() in category["name"].lower():
                    category_id = category["id"]
                    break
        
        if category_id is None:
            return []  # Category not found
        
        return self.get_products_by_category(category_id, per_page)
    
    def get_all_products(self, per_page: int = 100) -> List[Dict]:
        """Get all products with pagination.
        
        Args:
            per_page: Number of results per page
            
        Returns:
            List of all product dictionaries
        """
        all_products = []
        page = 1
        
        while True:
            cache_key = self._get_cache_key("/products", {"page": page, "per_page": per_page})
            cached = self._get_from_cache(cache_key)
            
            if cached is not None:
                products = cached
            else:
                params = {"page": page, "per_page": per_page}
                products = self._make_request("/products", params)
                self._set_cache(cache_key, products)
            
            if not products:
                break
            
            all_products.extend(products)
            
            # If we got fewer results than per_page, we're done
            if len(products) < per_page:
                break
            
            page += 1
        
        return all_products
    
    def get_product_by_id(self, product_id: int) -> Dict:
        """Get single product by ID.
        
        Args:
            product_id: Product ID
            
        Returns:
            Product dictionary
        """
        cache_key = self._get_cache_key(f"/products/{product_id}", {})
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return cached
        
        result = self._make_request(f"/products/{product_id}")
        self._set_cache(cache_key, result)
        return result
    
    def get_product_by_name(self, product_name: str) -> Dict:
        """Get product by name using fuzzy matching.
        
        Args:
            product_name: Product name to search for
            
        Returns:
            Product dictionary (first match)
        """
        # Use search to find products
        results = self.search_products(product_name, per_page=10)
        
        if not results:
            raise ValueError(f"Product '{product_name}' not found")
        
        # Return first match
        return results[0]
    
    def get_categories(self) -> List[Dict]:
        """Get all product categories.
        
        Returns:
            List of category dictionaries
        """
        # Categories are cached separately with longer TTL
        if (self._categories_cache is not None and 
            (time.time() - self._categories_cache_time) < self.cache_ttl):
            return self._categories_cache
        
        cache_key = self._get_cache_key("/products/categories", {})
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            self._categories_cache = cached
            self._categories_cache_time = time.time()
            return cached
        
        results = self._make_request("/products/categories")
        self._set_cache(cache_key, results)
        self._categories_cache = results
        self._categories_cache_time = time.time()
        return results

