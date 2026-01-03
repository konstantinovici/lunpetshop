# Building a ReAct Agent for E-Commerce: A Complete Guide

> How we built an AI chatbot for LùnPetShop that actually searches products instead of making things up

---

## 📚 TABLE OF CONTENTS

1. [Full Blog Post](#full-blog-post) - Comprehensive technical guide
2. [Facebook Version](#facebook-version) - Community-friendly format
3. [X/Twitter Thread](#xtwitter-thread) - Bite-sized thread
4. [Quick Reference Card](#quick-reference-card) - Future agent building

---

# FULL BLOG POST

## Building a ReAct Agent for E-Commerce: Why Your Chatbot Needs to Think Before It Speaks

### The Problem: Chatbots That Make Things Up

You've probably experienced this: you ask an AI chatbot "how many products do you have?" and it confidently responds with made-up numbers. Or you ask "show me cat food products" and it gives you generic advice instead of actual product listings.

This happens because most chatbots are built with **intent classification** — a pattern where the system tries to categorize your question first, then decides what to do. The problem? Intent classification is brittle, requires constant tuning, and often gates tool usage incorrectly.

### The Solution: ReAct Pattern

**ReAct (Reasoning + Acting)** is a paradigm where the AI agent:
1. Always has access to tools
2. Reasons about whether to use them
3. Acts by calling tools when needed
4. Reflects on the results

The key insight: **Don't classify intent. Let the LLM decide.**

### Our Journey: LùnPetShop KittyCat Chatbot

LùnPetShop is a Vietnamese pet store. They needed a chatbot that could:
- Answer questions about products (cats, dogs, accessories)
- Search actual inventory from WooCommerce
- Provide real prices and stock information
- Work in both Vietnamese and English

#### What We Tried First (The Wrong Way)

```python
# ❌ WRONG: Intent-based tool gating
intent = classify_intent(user_text, language)

if intent == "cat_products":
    response = get_cat_products_text(language)  # Static text
elif intent == "product_search":
    # Only NOW do we use tools
    tools = [search_products_tool, ...]
    llm = get_llm(tools=tools)
```

**Problems with this approach:**
- "show me cat food" → classified as `cat_products` → returned static text, no actual search
- "how many snacks do you have" → classified as `general` → no tools, made up answer
- Intent classification requires constant keyword tuning
- Edge cases fall through the cracks

#### What Actually Works (ReAct Pattern)

```python
# ✅ RIGHT: ReAct pattern - tools always available
def chatbot_node(state):
    """ReAct: Tools always available, LLM decides when to use them."""
    
    # Always import and bind tools
    tools = [
        search_products_tool,
        get_products_by_category_tool,
        get_product_details_tool
    ]
    
    # LLM has tools bound - it will decide when to use them
    llm = get_llm(tools=tools)
    
    # Let LLM reason and act
    response = llm.invoke(messages)
    
    # If LLM decided to use tools, execute them
    if response.tool_calls:
        tool_results = execute_tools(response.tool_calls)
        final_response = llm.invoke([...messages, response, tool_results])
        return final_response
    
    return response
```

**Why this works:**
- LLM sees the tools and their descriptions
- LLM reasons: "User wants cat food products → I should use `get_products_by_category_tool`"
- LLM acts: Calls the tool with appropriate arguments
- LLM reflects: Uses tool results to craft a helpful response

### The System Prompt: Guiding the Agent

The system prompt is crucial. Here's what works:

```python
system_prompt = """You are KittyCat 🐱, the AI assistant for LùnPetShop.

Product Search Tools:
You have access to tools to search for real products from the store:
- search_products_tool: Search for products by name or description
- get_products_by_category_tool: Get products by category
- get_product_details_tool: Get detailed information about a specific product

Guidelines:
- Use tools when you need specific product information from the store
- No tools needed for general questions about store info, address, hours
- Decide yourself when you need to search for actual products

Store information:
- Name: LùnPetShop
- Address: 70 Đường Số 3, Quận 2, TP.HCM
- Zalo: 0935005762
"""
```

**Key principles:**
1. **List the tools clearly** — The LLM needs to know what's available
2. **Explain when to use them** — But don't be too restrictive
3. **Trust the LLM** — "Decide yourself when you need to search"
4. **Provide static context** — Store info that doesn't need tools

### The Tools: LangChain Implementation

```python
from langchain_core.tools import tool

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
    client = WooCommerceClient()
    products = client.search_products(query, per_page=20)
    return format_products_list(products)


@tool
def get_products_by_category_tool(category_name: str) -> str:
    """Get products in a specific category.
    
    Use this tool when the user asks about products in a category.
    Supports both Vietnamese and English category names.
    
    Args:
        category_name: Category name (e.g., 'cat food', 'Pate mèo')
        
    Returns:
        Formatted markdown string with products in that category
    """
    client = WooCommerceClient()
    products = client.get_products_by_category_name(category_name)
    return format_products_list(products)
```

**Tool design principles:**
1. **Clear docstrings** — The LLM reads these to understand when to use each tool
2. **Specific use cases** — Examples help the LLM match user queries to tools
3. **Simple return format** — Markdown or plain text the LLM can interpret

### Binding Tools to the LLM

```python
from langchain_openai import ChatOpenAI 

def get_llm(tools):
    llm = ChatOpenAI(
        model="grok-4-1-fast-non-reasoning",  # or "gpt-4", "claude-3", etc.
        api_key=api_key,
        base_url="https://api.x.ai/v1",  # xAI endpoint
        temperature=0.7,
    )
    
    # This is the key: bind_tools makes tools available to the LLM
    llm = llm.bind_tools(tools)
    
    return llm
```

### Handling Tool Calls

```python
def process_with_tools(llm, messages, tools):
    # First LLM call - might include tool calls
    response = llm.invoke(messages)
    
    # Check if LLM decided to use tools
    tool_calls = getattr(response, 'tool_calls', [])
    
    if not tool_calls:
        # LLM answered directly - no tools needed
        return response.content
    
    # Execute each tool the LLM requested
    tool_results = []
    tool_map = {tool.name: tool for tool in tools}
    
    for tool_call in tool_calls:
        tool_name = tool_call.name
        tool_args = tool_call.args
        
        # Execute the tool
        result = tool_map[tool_name].invoke(tool_args)
        
        # Create tool message for LLM
        tool_results.append(ToolMessage(
            content=str(result),
            tool_call_id=tool_call.id
        ))
    
    # Second LLM call - process tool results
    updated_messages = messages + [response] + tool_results
    final_response = llm.invoke(updated_messages)
    
    return final_response.content
```

### Real-World Challenge: WooCommerce Connection

We hit a snag: the backend couldn't connect directly to WooCommerce API due to firewall rules blocking external connections during TLS handshake.

**Solution: WordPress Proxy**

```php
// WordPress plugin creates a proxy endpoint
register_rest_route('lunpetshop/v1', '/woocommerce-proxy/(?P<endpoint>.*)', [
    'methods' => 'GET',
    'callback' => function($request) {
        $endpoint = $request->get_param('endpoint');
        
        // WordPress makes INTERNAL request to WooCommerce
        $wc_url = home_url('/wp-json/wc/store/v1/' . $endpoint);
        $response = wp_remote_get($wc_url, ['sslverify' => false]);
        
        return new WP_REST_Response(json_decode($body), $status);
    },
    'permission_callback' => '__return_true'
]);
```

**Why this works:**
- Backend calls WordPress proxy (external request, allowed)
- WordPress calls WooCommerce internally (same server, no firewall)
- Data flows: Backend → WordPress → WooCommerce → WordPress → Backend

### Results

Before (Intent Classification):
```
User: "show me cat food products"
Bot: "We have a wide variety of cat foods... contact us for details!"
```

After (ReAct Pattern):
```
User: "show me cat food products"
Bot: "Found 30 products in Thức ăn cho Mèo:

1. **Hạt Royal Canin cho mèo 2kg** - 450.000 ₫
   Stock: Còn 15 trong kho
   [View Product](https://lunpetshop.com/...)

2. **Pate Whiskas vị cá 85g** - 18.000 ₫
   Stock: Còn 42 trong kho
   [View Product](https://lunpetshop.com/...)
..."
```

### Key Lessons

1. **Don't over-engineer intent classification** — Let the LLM decide
2. **Tools should always be available** — ReAct pattern
3. **Tool docstrings matter** — The LLM reads them
4. **System prompts should guide, not restrict** — "Decide yourself"
5. **Real integrations have real problems** — Firewalls, TLS, CORS
6. **Proxy patterns solve connection issues** — WordPress as middleman

### Architecture Summary

```
┌─────────────────────────────────────────────────────────────┐
│                     User (Browser)                          │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                 Chat Widget (JavaScript)                    │
│                 Embedded in WordPress                       │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                 Backend API (FastAPI)                       │
│                 localhost:8000 via tunnel                   │
│  ┌───────────────────────────────────────────────────────┐ │
│  │               LangGraph + LangChain                    │ │
│  │  ┌─────────────────────────────────────────────────┐  │ │
│  │  │           ReAct Agent (Grok/GPT-4)              │  │ │
│  │  │  - Tools always bound                           │  │ │
│  │  │  - LLM reasons about tool usage                 │  │ │
│  │  │  - Executes tools, processes results            │  │ │
│  │  └─────────────────────────────────────────────────┘  │ │
│  │                        │                               │ │
│  │  ┌─────────────────────┴─────────────────────────┐    │ │
│  │  │              WooCommerce Tools                │    │ │
│  │  │  - search_products_tool                       │    │ │
│  │  │  - get_products_by_category_tool              │    │ │
│  │  │  - get_product_details_tool                   │    │ │
│  │  └───────────────────────────────────────────────┘    │ │
│  └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│            WordPress Proxy Endpoint                         │
│            /wp-json/lunpetshop/v1/woocommerce-proxy/       │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│            WooCommerce Store API (Internal)                 │
│            /wp-json/wc/store/v1/                           │
└─────────────────────────────────────────────────────────────┘
```

### Code Repository Structure

```
lunpetshop/
├── backend/
│   ├── src/
│   │   ├── api.py              # FastAPI endpoints
│   │   ├── chatbot.py          # ReAct agent logic
│   │   ├── prompts.py          # System prompts
│   │   ├── woocommerce.py      # WooCommerce client
│   │   └── woocommerce_tools.py # LangChain tools
│   └── main.py
├── wordpress-plugin/
│   └── lunpetshop-chatbot/
│       ├── lunpetshop-chatbot.php  # Plugin with proxy
│       └── assets/
└── widget/
    └── assets/js/chat-widget.js
```

---

# FACEBOOK VERSION

## 🤖 How We Built an AI Chatbot That Actually Searches Products (Not Makes Things Up)

Hey everyone! Just finished building a ReAct AI agent for LùnPetShop (Vietnamese pet store) and wanted to share what I learned.

### The Problem
Most chatbots do this:
- User: "show me cat food"
- Bot: "We have various cat foods! Contact us for details!" 🙄

They make things up instead of actually searching.

### The Solution: ReAct Pattern
Instead of classifying user intent, let the AI decide when to use tools.

**Before (Intent Classification):**
```
if intent == "product_search":
    use_tools()  # Only sometimes
else:
    make_stuff_up()  # Most of the time
```

**After (ReAct):**
```
tools = [search_tool, category_tool, details_tool]
llm = get_llm(tools=tools)  # Always available
response = llm.invoke(messages)  # LLM decides
```

### Results
Now when someone asks "show me cat food":
- LLM thinks: "I should search for cat food products"
- LLM calls: `get_products_by_category_tool("cat food")`
- LLM responds with REAL products, prices, and stock

### Key Takeaways
1. Don't over-engineer intent classification
2. Let the LLM decide when to use tools
3. Write clear tool docstrings (LLM reads them!)
4. System prompt should guide, not restrict

### Tech Stack
- LangChain + LangGraph
- xAI Grok (or GPT-4, Claude)
- WooCommerce Store API
- FastAPI backend
- WordPress plugin

Full technical writeup on my blog: [link]

Anyone else building e-commerce agents? Would love to hear your approaches! 👇

---

# X/TWITTER THREAD

**Thread: How to build a ReAct AI agent that actually works 🧵**

---

**1/**
Just shipped a ReAct agent for an e-commerce store.

The #1 mistake I made: using intent classification to decide when to use tools.

Here's what actually works 👇

---

**2/**
❌ WRONG approach:

```python
if intent == "product_search":
    use_tools()
else:
    make_stuff_up()
```

This is brittle. Edge cases everywhere.

---

**3/**
✅ RIGHT approach (ReAct):

```python
tools = [search, category, details]
llm.bind_tools(tools)  # Always available
response = llm.invoke(messages)  # LLM decides
```

Let the LLM reason about tool usage.

---

**4/**
The magic is in `bind_tools()`.

LLM sees the tools + their docstrings.
LLM reasons: "User wants cat food → I should search"
LLM acts: Calls the tool.
LLM reflects: Uses results to respond.

---

**5/**
Your system prompt should guide, not restrict:

❌ "Only use tools when user asks for specific products"
✅ "Decide yourself when you need to search for actual products"

Trust the LLM.

---

**6/**
Tool docstrings matter A LOT.

The LLM reads them to understand when to use each tool.

Clear examples in docstrings = better tool selection.

---

**7/**
Real-world problem we hit:

Backend couldn't connect to WooCommerce API (firewall blocking TLS).

Solution: WordPress proxy endpoint.

Backend → WordPress (allowed) → WooCommerce (internal) ✅

---

**8/**
Results:

Before: "We have various products, contact us!"
After: "Found 30 products: Royal Canin 450k₫, Whiskas 18k₫..." with real stock info.

---

**9/**
TL;DR for building ReAct agents:

1. Tools always available
2. LLM decides when to use them
3. Clear tool docstrings
4. Guiding (not restrictive) system prompts
5. Proxy patterns for tricky integrations

---

**10/**
Tech stack:
- LangChain + LangGraph
- xAI Grok / GPT-4 / Claude
- WooCommerce API
- FastAPI + WordPress

Full code walkthrough on my blog: [link]

What agents are you building? 🤖

---

# QUICK REFERENCE CARD

## ReAct Agent Cheat Sheet

### Pattern
```python
# 1. Define tools
@tool
def search_tool(query: str) -> str:
    """Clear docstring - LLM reads this."""
    return execute_search(query)

# 2. Always bind tools
tools = [tool1, tool2, tool3]
llm = llm.bind_tools(tools)

# 3. Let LLM decide
response = llm.invoke(messages)

# 4. Execute tool calls if any
if response.tool_calls:
    results = [execute(tc) for tc in response.tool_calls]
    final = llm.invoke([...messages, response, results])
```

### System Prompt Template
```
You are [Agent Name], assistant for [Company].

Available Tools:
- tool_1: Description and when to use
- tool_2: Description and when to use

Guidelines:
- Use tools when you need specific information
- Decide yourself when tools are needed
- [Static context like business info]
```

### Common Mistakes
| ❌ Wrong | ✅ Right |
|----------|----------|
| Intent classification gates tools | Tools always available |
| "Only use tools when..." | "Decide yourself when..." |
| Sparse tool docstrings | Detailed docstrings with examples |
| Direct API calls | Proxy for firewall issues |

### Architecture
```
User → Widget → Backend → LLM (tools bound) → Tool execution → Response
                              ↓
                    External APIs (via proxy if needed)
```

### Debugging Checklist
- [ ] Tools are bound to LLM
- [ ] Tool docstrings are clear
- [ ] System prompt lists tools
- [ ] API connections work (check proxy)
- [ ] LLM response has `tool_calls` attribute

---

## License & Attribution

This guide is based on the LùnPetShop KittyCat Chatbot project.

Feel free to use, adapt, and share with attribution.

Built with: LangChain, LangGraph, xAI Grok, WooCommerce, FastAPI, WordPress.

