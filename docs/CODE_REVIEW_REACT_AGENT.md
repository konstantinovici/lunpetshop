# Code Review: LùnPetShop ReAct Agent

## Overall Assessment: 7.5/10

The implementation follows the ReAct pattern correctly. There are several improvements that would bring it to production-grade quality.

---

## ✅ What's Good

### 1. ReAct Pattern Implementation (chatbot.py)
```python
# Tools always bound - LLM decides when to use them ✅
tools = [search_products_tool, get_products_by_category_tool, get_product_details_tool]
llm = get_llm(tools=tools)
```

### 2. Tool Design (woocommerce_tools.py)
- Good docstrings with examples ✅
- Clear argument descriptions ✅
- Graceful error handling ✅

### 3. WooCommerce Client (woocommerce.py)
- Retry logic with exponential backoff ✅
- Caching strategy ✅
- Multiple URL sources (proxy, internal, direct) ✅

### 4. Bilingual Support
- Vietnamese and English prompts ✅
- Language detection ✅

---

## ⚠️ Issues & Improvements

### Issue 1: Temperature Too High for Tool Calling

**Current:**
```python
temperature=0.7,  # Too creative for tool decisions
```

**Recommended:**
```python
temperature=0.3,  # More deterministic for tool calling
```

**Why:** Lower temperature = more reliable tool selection.

---

### Issue 2: Max Tokens Too Low

**Current:**
```python
max_tokens=500,  # May truncate product lists
```

**Recommended:**
```python
max_tokens=1500,  # Room for product lists
```

---

### Issue 3: Tool Names Not Following Conventions

**Current:**
```python
@tool
def search_products_tool(query: str) -> str:
```

**Better (snake_case without _tool suffix):**
```python
@tool
def search_products(query: str) -> str:
```

LangChain convention: tool name is the function name, no need for `_tool` suffix.

---

### Issue 4: System Prompt Too Long

The current prompt is ~50 lines. LLMs work better with concise prompts.

**Recommended Concise Prompt:**
```python
def get_system_prompt(language: str) -> str:
    if language == "vi":
        return f"""Bạn là KittyCat 🐱, trợ lý bán hàng AI của {BUSINESS_INFO['name']}.

**Công cụ:**
- search_products: Tìm sản phẩm theo từ khóa
- get_products_by_category: Lấy sản phẩm theo danh mục
- get_product_details: Thông tin chi tiết sản phẩm

**Quy tắc:**
1. LUÔN dùng công cụ khi khách hỏi về sản phẩm, giá, số lượng, tồn kho
2. Trình bày kết quả tự nhiên, ngắn gọn
3. Nếu không tìm thấy, hướng dẫn liên hệ Zalo: {BUSINESS_INFO['zalo']}

**Thông tin cửa hàng:** {BUSINESS_INFO['address']} | Zalo: {BUSINESS_INFO['zalo']} | Giờ: {BUSINESS_INFO['hours']}
"""
```

---

### Issue 5: Missing Price Filter Tool

Common e-commerce query: "products under 100k"

**Add this tool:**
```python
@tool
def search_products_by_price(max_price: int, category: str = None) -> str:
    """Search products under a maximum price.
    
    Use when customer asks for products under a certain price.
    
    Args:
        max_price: Maximum price in VND (e.g., 100000 for 100k)
        category: Optional category to filter (e.g., "cat food")
    
    Returns:
        Products under the specified price
    """
    client = get_client()
    # Filter by price from WooCommerce
    products = client.search_products_by_price(max_price, category)
    return format_products_list(products)
```

---

### Issue 6: Dead Code - Intent Classification Imports

**Current (chatbot.py):**
```python
from .utils import detect_language, classify_intent  # classify_intent unused
```

**Clean up:**
```python
from .utils import detect_language  # Only what's needed
```

The `classify_intent` is only used in fallback (no LLM). Consider removing entirely or keeping minimal.

---

### Issue 7: No Parallel Tool Call Handling

Current code handles tool calls sequentially. For better UX, handle parallel calls:

```python
if tool_calls:
    # Execute tools in parallel
    import asyncio
    
    async def execute_tool(tool_call):
        tool_name = getattr(tool_call, "name", None)
        tool_args = getattr(tool_call, "args", {})
        return tool_map[tool_name].invoke(tool_args)
    
    # Run all tool calls concurrently
    results = await asyncio.gather(*[execute_tool(tc) for tc in tool_calls])
```

---

### Issue 8: Consider Using `tool_choice` for Forcing Tool Use

When you KNOW tools should be used (e.g., product queries), force it:

```python
# Force tool use for product-related queries
llm_with_forced_tools = llm.bind_tools(
    tools,
    tool_choice="auto"  # or "required" to always use tools
)
```

---

### Issue 9: Missing Structured Output for Tools

**Current:** Tools return markdown strings.

**Better:** Use Pydantic for structured output:

```python
from pydantic import BaseModel
from typing import List

class Product(BaseModel):
    name: str
    price: str
    stock_status: str
    url: str

class ProductSearchResult(BaseModel):
    total_found: int
    products: List[Product]
    
@tool
def search_products(query: str) -> ProductSearchResult:
    """..."""
    # Returns structured data that LLM can reason about better
```

---

### Issue 10: Add Logging for Debugging

**Add to chatbot.py:**
```python
import logging
logger = logging.getLogger(__name__)

def chatbot_node(state):
    # ...
    logger.info(f"User query: {user_text}")
    logger.info(f"Language detected: {language}")
    
    if tool_calls:
        logger.info(f"Tool calls requested: {[tc.name for tc in tool_calls]}")
    
    logger.info(f"Response length: {len(response)}")
```

---

## 🚀 Recommended Improvements (Priority Order)

### Priority 1: Critical for Production

1. **Lower temperature to 0.3** - More reliable tool calling
2. **Increase max_tokens to 1500** - Room for product lists
3. **Add logging** - Debugging in production

### Priority 2: Better UX

4. **Simplify system prompt** - More reliable behavior
5. **Add price filter tool** - Common e-commerce query
6. **Clean up dead code** - Remove unused imports

### Priority 3: Advanced

7. **Parallel tool execution** - Faster responses
8. **Structured output** - Better LLM reasoning
9. **Tool choice forcing** - Guaranteed tool use when needed

---

## 📊 Comparison: Current vs Cutting-Edge

| Feature | Current | Best Practice | Status |
|---------|---------|--------------|--------|
| ReAct Pattern | ✅ | ✅ | Good |
| Tools Always Bound | ✅ | ✅ | Good |
| Temperature | 0.7 | 0.3 | ⚠️ Too high |
| Max Tokens | 500 | 1500+ | ⚠️ Too low |
| System Prompt | 50 lines | 15-20 lines | ⚠️ Too long |
| Tool Docstrings | Good | Good | ✅ |
| Error Handling | Good | Good | ✅ |
| Caching | Yes | Yes | ✅ |
| Retry Logic | Yes | Yes | ✅ |
| Logging | Minimal | Comprehensive | ⚠️ |
| Parallel Tools | No | Yes | ❌ |
| Structured Output | No | Yes | ❌ |
| Price Filter Tool | No | Yes | ❌ |

---

## 🔧 Quick Fixes (Apply Now)

### Fix 1: Temperature & Max Tokens

```python
# In chatbot.py, get_llm function
llm = ChatOpenAI(
    model="grok-4-1-fast-non-reasoning",
    api_key=api_key,
    base_url="https://api.x.ai/v1",
    temperature=0.3,      # Changed from 0.7
    max_tokens=1500,      # Changed from 500
)
```

### Fix 2: Cleaner Tool Names

```python
# In woocommerce_tools.py
@tool
def search_products(query: str) -> str:      # Removed _tool suffix
    """Search for products by name or description.
    ...
    """

@tool  
def get_products_by_category(category_name: str) -> str:  # Removed _tool suffix
    """Get products in a specific category.
    ...
    """

@tool
def get_product_details(product_name: str) -> str:  # Removed _tool suffix
    """Get detailed information about a specific product.
    ...
    """
```

---

## Conclusion

The implementation is solid and follows ReAct correctly. The main improvements needed are:

1. **Configuration tweaks** (temperature, max_tokens) - 5 minutes
2. **System prompt simplification** - 15 minutes
3. **Adding logging** - 10 minutes
4. **Price filter tool** - 30 minutes

Total estimated time for Priority 1 & 2 improvements: **~1 hour**

The code is production-ready for an MVP. Apply the quick fixes for better reliability.

