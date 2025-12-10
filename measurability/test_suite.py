"""
Agent Measurability Framework - Test Suite Definitions

Gold standard test cases for evaluating agent reliability.
Includes the failure case from production and comprehensive coverage.

Reference: docs/knowledge/agents measurability, reliability .md
"""

from evaluation_framework import TestCase, QueryType


# =============================================================================
# TEST SUITE: Product Search Queries
# =============================================================================

PRODUCT_SEARCH_TESTS = [
    # The failure case from image (critical)
    TestCase(
        query_id="prod_search_001",
        query="ok , what cat products you have total ?",
        language="en",
        query_type=QueryType.PRODUCT_SEARCH,
        expected_tool="search_products_tool",
        expected_tool_params={"query": "cat"},
        expected_response_contains=["product", "cat"],
        expected_response_not_contains=["Oops", "no cat products", "popped up"],
        should_use_tool=True,
        min_product_count=1,
    ),
    
    # Vietnamese product search
    TestCase(
        query_id="prod_search_002",
        query="Bạn có sản phẩm gì cho mèo?",
        language="vi",
        query_type=QueryType.PRODUCT_SEARCH,
        expected_tool="search_products_tool",
        expected_tool_params={"query": "mèo"},
        expected_response_contains=["sản phẩm", "mèo"],
        expected_response_not_contains=["không tìm thấy", "Xin lỗi"],
        should_use_tool=True,
    ),
    
    # Dog products search (English)
    TestCase(
        query_id="prod_search_003",
        query="What products do you have for my dog?",
        language="en",
        query_type=QueryType.PRODUCT_SEARCH,
        expected_tool="search_products_tool",
        expected_tool_params={"query": "dog"},
        expected_response_contains=["product", "dog"],
        expected_response_not_contains=["Oops", "no products"],
        should_use_tool=True,
    ),
    
    # Dog products search (Vietnamese)
    TestCase(
        query_id="prod_search_004",
        query="Bạn có sản phẩm gì cho chó của tôi?",
        language="vi",
        query_type=QueryType.PRODUCT_SEARCH,
        expected_tool="search_products_tool",
        expected_tool_params={"query": "chó"},
        expected_response_contains=["sản phẩm", "chó"],
        expected_response_not_contains=["không tìm thấy"],
        should_use_tool=True,
    ),
    
    # Generic product search
    TestCase(
        query_id="prod_search_005",
        query="show me all products",
        language="en",
        query_type=QueryType.PRODUCT_SEARCH,
        expected_tool="search_products_tool",
        expected_tool_params={"query": ""},
        expected_response_contains=["product"],
        expected_response_not_contains=["Oops", "error"],
        should_use_tool=True,
    ),
    
    # Pate search
    TestCase(
        query_id="prod_search_006",
        query="Do you have any pate?",
        language="en",
        query_type=QueryType.PRODUCT_SEARCH,
        expected_tool="search_products_tool",
        expected_tool_params={"query": "pate"},
        expected_response_contains=["pate"],
        expected_response_not_contains=["Oops", "not found"],
        should_use_tool=True,
    ),
    
    # Vietnamese pate search
    TestCase(
        query_id="prod_search_007",
        query="Có pate không?",
        language="vi",
        query_type=QueryType.PRODUCT_SEARCH,
        expected_tool="search_products_tool",
        expected_tool_params={"query": "pate"},
        expected_response_contains=["pate"],
        expected_response_not_contains=["không có"],
        should_use_tool=True,
    ),
    
    # Price-constrained search
    TestCase(
        query_id="prod_search_008",
        query="What cat food do you have under 50000 VND?",
        language="en",
        query_type=QueryType.PRODUCT_SEARCH,
        expected_tool="search_products_tool",
        expected_tool_params={"query": "cat food"},
        expected_response_contains=["cat", "food"],
        expected_response_not_contains=["Oops"],
        should_use_tool=True,
    ),
]


# =============================================================================
# TEST SUITE: Category Browse Queries
# =============================================================================

CATEGORY_BROWSE_TESTS = [
    # Browse cat food category
    TestCase(
        query_id="cat_browse_001",
        query="Show me cat food category",
        language="en",
        query_type=QueryType.CATEGORY_BROWSE,
        expected_tool="get_products_by_category_tool",
        expected_tool_params={"category_name": "Thức ăn cho Mèo"},
        expected_response_contains=["cat", "food"],
        expected_response_not_contains=["Oops"],
        should_use_tool=True,
    ),
    
    # Browse dog food category (Vietnamese)
    TestCase(
        query_id="cat_browse_002",
        query="Cho tôi xem danh mục thức ăn cho chó",
        language="vi",
        query_type=QueryType.CATEGORY_BROWSE,
        expected_tool="get_products_by_category_tool",
        expected_tool_params={"category_name": "Thức ăn cho Chó"},
        expected_response_contains=["chó", "thức ăn"],
        expected_response_not_contains=["không tìm thấy"],
        should_use_tool=True,
    ),
    
    # List all categories
    TestCase(
        query_id="cat_browse_003",
        query="What categories do you have?",
        language="en",
        query_type=QueryType.CATEGORY_BROWSE,
        expected_tool="get_products_by_category_tool",
        expected_tool_params={},
        expected_response_contains=["category"],
        expected_response_not_contains=["Oops"],
        should_use_tool=True,
    ),
]


# =============================================================================
# TEST SUITE: Product Details Queries
# =============================================================================

PRODUCT_DETAILS_TESTS = [
    # Get specific product details
    TestCase(
        query_id="prod_detail_001",
        query="Tell me more about Pate Nekko",
        language="en",
        query_type=QueryType.PRODUCT_DETAILS,
        expected_tool="get_product_details_tool",
        expected_tool_params={"product_id": None},  # Product ID varies
        expected_response_contains=["pate", "nekko"],
        expected_response_not_contains=["Oops", "not found"],
        should_use_tool=True,
    ),
    
    # Price inquiry
    TestCase(
        query_id="prod_detail_002",
        query="How much is the Whiskas cat food?",
        language="en",
        query_type=QueryType.PRODUCT_DETAILS,
        expected_tool="search_products_tool",  # Search first to find
        expected_tool_params={"query": "Whiskas"},
        expected_response_contains=["price", "whiskas"],
        expected_response_not_contains=["Oops"],
        should_use_tool=True,
    ),
]


# =============================================================================
# TEST SUITE: Business Information Queries
# =============================================================================

BUSINESS_INFO_TESTS = [
    # Store info (English)
    TestCase(
        query_id="biz_info_001",
        query="What can you tell me about the business?",
        language="en",
        query_type=QueryType.BUSINESS_INFO,
        expected_tool=None,  # Rule-based, no tool needed
        expected_tool_params=None,
        expected_response_contains=["LùnPetShop", "pet"],
        expected_response_not_contains=["Oops", "error"],
        should_use_tool=False,
    ),
    
    # Store info (Vietnamese)
    TestCase(
        query_id="biz_info_002",
        query="Cho tôi biết về cửa hàng của bạn?",
        language="vi",
        query_type=QueryType.BUSINESS_INFO,
        expected_tool=None,
        expected_tool_params=None,
        expected_response_contains=["LùnPetShop", "cửa hàng"],
        expected_response_not_contains=["Xin lỗi", "lỗi"],
        should_use_tool=False,
    ),
]


# =============================================================================
# TEST SUITE: Contact Information Queries
# =============================================================================

CONTACT_INFO_TESTS = [
    # Address query (English)
    TestCase(
        query_id="contact_001",
        query="What's your address?",
        language="en",
        query_type=QueryType.CONTACT_INFO,
        expected_tool=None,
        expected_tool_params=None,
        expected_response_contains=["address", "đường"],
        expected_response_not_contains=["Oops"],
        should_use_tool=False,
    ),
    
    # Address query (Vietnamese)
    TestCase(
        query_id="contact_002",
        query="Địa chỉ của bạn ở đâu?",
        language="vi",
        query_type=QueryType.CONTACT_INFO,
        expected_tool=None,
        expected_tool_params=None,
        expected_response_contains=["địa chỉ"],
        expected_response_not_contains=["Xin lỗi"],
        should_use_tool=False,
    ),
    
    # Zalo contact (English)
    TestCase(
        query_id="contact_003",
        query="How can I reach you on Zalo?",
        language="en",
        query_type=QueryType.CONTACT_INFO,
        expected_tool=None,
        expected_tool_params=None,
        expected_response_contains=["Zalo", "0935005762"],
        expected_response_not_contains=["Oops"],
        should_use_tool=False,
    ),
    
    # Zalo contact (Vietnamese)
    TestCase(
        query_id="contact_004",
        query="Làm thế nào để liên hệ với bạn qua Zalo?",
        language="vi",
        query_type=QueryType.CONTACT_INFO,
        expected_tool=None,
        expected_tool_params=None,
        expected_response_contains=["Zalo", "0935005762"],
        expected_response_not_contains=["Xin lỗi"],
        should_use_tool=False,
    ),
]


# =============================================================================
# TEST SUITE: Edge Cases / Ambiguous Queries
# =============================================================================

EDGE_CASE_TESTS = [
    # Ambiguous query (could be search or general)
    TestCase(
        query_id="edge_001",
        query="What do you have?",
        language="en",
        query_type=QueryType.PRODUCT_SEARCH,
        expected_tool="search_products_tool",
        expected_tool_params={"query": ""},
        expected_response_contains=["product"],
        expected_response_not_contains=["Oops"],
        should_use_tool=True,
    ),
    
    # Typo in query
    TestCase(
        query_id="edge_002",
        query="cat fod for sale",  # "fod" instead of "food"
        language="en",
        query_type=QueryType.PRODUCT_SEARCH,
        expected_tool="search_products_tool",
        expected_tool_params={"query": "cat food"},
        expected_response_contains=["cat"],
        expected_response_not_contains=["Oops"],
        should_use_tool=True,
    ),
    
    # Mixed language query
    TestCase(
        query_id="edge_003",
        query="Show me pate cho mèo",
        language="vi",  # Defaults to Vietnamese due to "mèo"
        query_type=QueryType.PRODUCT_SEARCH,
        expected_tool="search_products_tool",
        expected_tool_params={"query": "pate mèo"},
        expected_response_contains=["pate"],
        expected_response_not_contains=["Oops"],
        should_use_tool=True,
    ),
    
    # Empty-ish query
    TestCase(
        query_id="edge_004",
        query="products?",
        language="en",
        query_type=QueryType.PRODUCT_SEARCH,
        expected_tool="search_products_tool",
        expected_tool_params={"query": ""},
        expected_response_contains=["product"],
        expected_response_not_contains=["Oops"],
        should_use_tool=True,
    ),
]


# =============================================================================
# TEST SUITE: General Conversation (LLM required)
# =============================================================================

GENERAL_CONVERSATION_TESTS = [
    # Pet advice
    TestCase(
        query_id="general_001",
        query="My pet won't eat, do you have any advice?",
        language="en",
        query_type=QueryType.GENERAL,
        expected_tool=None,
        expected_tool_params=None,
        expected_response_contains=[],  # LLM-generated, flexible
        expected_response_not_contains=["Oops", "error"],
        should_use_tool=False,
    ),
    
    # First-time pet owner
    TestCase(
        query_id="general_002",
        query="I want to adopt a pet for the first time, can you help?",
        language="en",
        query_type=QueryType.GENERAL,
        expected_tool=None,
        expected_tool_params=None,
        expected_response_contains=[],
        expected_response_not_contains=["Oops"],
        should_use_tool=False,
    ),
    
    # Greeting
    TestCase(
        query_id="general_003",
        query="Hello!",
        language="en",
        query_type=QueryType.GENERAL,
        expected_tool=None,
        expected_tool_params=None,
        expected_response_contains=["hello", "hi", "welcome"],
        expected_response_not_contains=["Oops"],
        should_use_tool=False,
    ),
    
    # Vietnamese greeting
    TestCase(
        query_id="general_004",
        query="Xin chào!",
        language="vi",
        query_type=QueryType.GENERAL,
        expected_tool=None,
        expected_tool_params=None,
        expected_response_contains=["xin chào", "chào"],
        expected_response_not_contains=["Xin lỗi"],
        should_use_tool=False,
    ),
]


# =============================================================================
# COMBINED TEST SUITE
# =============================================================================

TEST_SUITE = (
    PRODUCT_SEARCH_TESTS +
    CATEGORY_BROWSE_TESTS +
    PRODUCT_DETAILS_TESTS +
    BUSINESS_INFO_TESTS +
    CONTACT_INFO_TESTS +
    EDGE_CASE_TESTS +
    GENERAL_CONVERSATION_TESTS
)

# Critical tests that must pass (high priority)
CRITICAL_TESTS = [
    test for test in TEST_SUITE 
    if test.query_id in [
        "prod_search_001",  # The failure case from image
        "prod_search_002",  # Vietnamese cat search
        "prod_search_003",  # English dog search
        "prod_search_004",  # Vietnamese dog search
    ]
]

# Tool-calling tests only (for measuring tool reliability)
TOOL_CALLING_TESTS = [
    test for test in TEST_SUITE 
    if test.should_use_tool
]

# Rule-based tests only (no tool needed)
RULE_BASED_TESTS = [
    test for test in TEST_SUITE 
    if not test.should_use_tool
]


def get_test_suite(suite_name: str = "all") -> list[TestCase]:
    """
    Get a specific test suite by name.
    
    Args:
        suite_name: One of "all", "critical", "tool_calling", "rule_based",
                   "product_search", "category", "details", "business", 
                   "contact", "edge", "general"
                   
    Returns:
        List of TestCase objects
    """
    suites = {
        "all": TEST_SUITE,
        "critical": CRITICAL_TESTS,
        "tool_calling": TOOL_CALLING_TESTS,
        "rule_based": RULE_BASED_TESTS,
        "product_search": PRODUCT_SEARCH_TESTS,
        "category": CATEGORY_BROWSE_TESTS,
        "details": PRODUCT_DETAILS_TESTS,
        "business": BUSINESS_INFO_TESTS,
        "contact": CONTACT_INFO_TESTS,
        "edge": EDGE_CASE_TESTS,
        "general": GENERAL_CONVERSATION_TESTS,
    }
    
    return suites.get(suite_name, TEST_SUITE)


def get_test_by_id(query_id: str) -> TestCase | None:
    """Get a specific test case by ID."""
    for test in TEST_SUITE:
        if test.query_id == query_id:
            return test
    return None


if __name__ == "__main__":
    # Print test suite summary
    print(f"Total test cases: {len(TEST_SUITE)}")
    print(f"  - Product Search: {len(PRODUCT_SEARCH_TESTS)}")
    print(f"  - Category Browse: {len(CATEGORY_BROWSE_TESTS)}")
    print(f"  - Product Details: {len(PRODUCT_DETAILS_TESTS)}")
    print(f"  - Business Info: {len(BUSINESS_INFO_TESTS)}")
    print(f"  - Contact Info: {len(CONTACT_INFO_TESTS)}")
    print(f"  - Edge Cases: {len(EDGE_CASE_TESTS)}")
    print(f"  - General: {len(GENERAL_CONVERSATION_TESTS)}")
    print()
    print(f"Critical tests: {len(CRITICAL_TESTS)}")
    print(f"Tool-calling tests: {len(TOOL_CALLING_TESTS)}")
    print(f"Rule-based tests: {len(RULE_BASED_TESTS)}")








