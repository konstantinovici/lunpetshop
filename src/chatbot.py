"""LangGraph chatbot for LùnPetShop with bilingual support."""

from typing import Annotated, Literal
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
import os
import re

from .knowledge_base import (
    get_cat_products_text,
    get_dog_products_text,
    get_business_info_text,
    get_contact_info_text,
    BUSINESS_INFO,
)


# Extended State with language tracking
class ChatbotState(MessagesState):
    """State for the chatbot with language tracking."""
    language: str = "vi"  # Default to Vietnamese


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


def get_system_prompt(language: str) -> str:
    """Get the system prompt for the chatbot based on language."""
    if language == "vi":
        return f"""Bạn là KittyCat 🐱, trợ lý AI thân thiện của {BUSINESS_INFO['name']}.

Về bạn:
- Tên: KittyCat
- Vai trò: Trợ lý AI cá nhân cho {BUSINESS_INFO['name']}
- Tính cách: Thân thiện, nhiệt tình, am hiểu về thú cưng

Nhiệm vụ của bạn:
1. Trả lời câu hỏi về sản phẩm cho mèo và chó
2. Cung cấp thông tin về cửa hàng
3. Hỗ trợ khách hàng tìm sản phẩm phù hợp
4. Cung cấp thông tin liên hệ

Hướng dẫn:
- Luôn thân thiện và hữu ích
- Trả lời ngắn gọn, dễ hiểu
- Sử dụng emoji 🐱 🐕 🐾 khi phù hợp
- Nếu không chắc chắn, gợi ý khách hàng liên hệ qua Zalo: {BUSINESS_INFO['zalo']}

Thông tin cửa hàng:
- Tên: {BUSINESS_INFO['name']}
- Địa chỉ: {BUSINESS_INFO['address']}
- Zalo/Phone: {BUSINESS_INFO['zalo']}
- Facebook: {BUSINESS_INFO['facebook']}
- Giờ mở cửa: {BUSINESS_INFO['hours']}
- Dịch vụ: {BUSINESS_INFO['tagline']}
"""
    else:
        return f"""You are KittyCat 🐱, the friendly AI assistant for {BUSINESS_INFO['name']}.

About you:
- Name: KittyCat
- Role: Personal AI assistant for {BUSINESS_INFO['name']}
- Personality: Friendly, helpful, knowledgeable about pets

Your tasks:
1. Answer questions about cat and dog products
2. Provide business information
3. Help customers find suitable products
4. Provide contact information

Guidelines:
- Always be friendly and helpful
- Keep responses concise and clear
- Use emojis 🐱 🐕 🐾 when appropriate
- If unsure, suggest customers contact via Zalo: {BUSINESS_INFO['zalo']}

Store information:
- Name: {BUSINESS_INFO['name']}
- Address: {BUSINESS_INFO['address']}
- Zalo/Phone: {BUSINESS_INFO['zalo']}
- Facebook: {BUSINESS_INFO['facebook']}
- Hours: {BUSINESS_INFO['hours']}
- Services: {BUSINESS_INFO['tagline_en']}
"""


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


def chatbot_node(state: ChatbotState) -> ChatbotState:
    """Main chatbot node that processes user messages."""
    messages = state["messages"]
    
    # Get the last user message
    if not messages:
        return state
    
    last_message = messages[-1]
    if not isinstance(last_message, HumanMessage):
        return state
    
    user_text = last_message.content
    
    # Detect language
    language = detect_language(user_text)
    
    # Classify intent
    intent = classify_intent(user_text, language)
    
    # Generate response based on intent
    try:
        if intent == "cat_products":
            response = get_cat_products_text(language)
        elif intent == "dog_products":
            response = get_dog_products_text(language)
        elif intent == "business":
            response = get_business_info_text(language)
        elif intent == "contact":
            response = get_contact_info_text(language)
        else:
            # Use LLM for general conversation
            llm = get_llm()
            
            if llm is None:
                # Fallback to friendly message if no LLM
                if language == "vi":
                    response = "Xin lỗi, tôi không thể xử lý câu hỏi này ngay bây giờ. Vui lòng liên hệ với chúng tôi qua Zalo: 0935005762 🐾"
                else:
                    response = "Sorry, I can't process that question right now. Please contact us on Zalo: 0935005762 🐾"
            else:
                system_prompt = get_system_prompt(language)
                
                # Prepare messages for LLM
                llm_messages = [SystemMessage(content=system_prompt)] + messages
                
                # Get LLM response
                llm_response = llm.invoke(llm_messages)
                response = llm_response.content
    except Exception as e:
        # Log the error for debugging
        import traceback
        print(f"Error in chatbot_node: {str(e)}")
        traceback.print_exc()
        
        # Return friendly error message
        if language == "vi":
            response = "Xin lỗi, đã có lỗi xảy ra. Vui lòng thử lại sau. 😔"
        else:
            response = "Sorry, an error occurred. Please try again later. 😔"
    
    # Add response to messages
    return {
        "messages": [AIMessage(content=response)],
        "language": language,
    }


def get_llm():
    """Get the configured LLM (xAI Grok)."""
    api_key = os.getenv("XAI_API_KEY")
    
    if not api_key:
        # If no API key, return None - will use rule-based responses
        return None
    
    try:
        # xAI uses OpenAI-compatible API
        # Latest model: Grok 4 Fast with 2M context window
        llm = ChatOpenAI(
            model="grok-4-fast",  # Latest xAI model (2M context window)
            api_key=api_key,
            base_url="https://api.x.ai/v1",
            temperature=0.7,
            max_tokens=500,
        )
        return llm
    except Exception as e:
        print(f"Warning: Failed to initialize LLM: {e}")
        print("Will use rule-based responses only")
        return None


def create_graph():
    """Create the LangGraph chatbot graph."""
    # Initialize the graph with state
    workflow = StateGraph(ChatbotState)
    
    # Add nodes
    workflow.add_node("chatbot", chatbot_node)
    
    # Define edges
    workflow.add_edge(START, "chatbot")
    workflow.add_edge("chatbot", END)
    
    # Compile with memory
    memory = MemorySaver()
    graph = workflow.compile(checkpointer=memory)
    
    return graph


def get_greeting(language: str = "vi") -> str:
    """Get greeting message based on language."""
    if language == "vi":
        return f"""Xin chào! 🐱 Mình là KittyCat, trợ lý AI của {BUSINESS_INFO['name']}. 

Mình có thể giúp bạn:
• Tìm sản phẩm cho mèo 🐱
• Tìm sản phẩm cho chó 🐕
• Thông tin về cửa hàng 🏪
• Thông tin liên hệ 📞

Bạn cần mình hỗ trợ gì nào? 🐾"""
    else:
        return f"""Hello! 🐱 I'm KittyCat, your personal AI assistant for {BUSINESS_INFO['name']}. 

I can help you with:
• Cat products 🐱
• Dog products 🐕
• Store information 🏪
• Contact information 📞

How can I help you today? 🐾"""


# Create the graph instance
graph = create_graph()

