"""LangGraph chatbot for LùnPetShop with bilingual support.

SIMPLIFIED VERSION: Uses cached product data instead of live WooCommerce API.
Product data is synced daily via sync_products.py script.
"""

from typing import Optional
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
import os
import logging

from .knowledge_base import (
    get_cat_products_text,
    get_dog_products_text,
    get_business_info_text,
    get_contact_info_text,
    get_knowledge_base_context,
    get_cache_status,
    BUSINESS_INFO,
)
from .prompts import get_system_prompt_simple
from .utils import detect_language, classify_intent

logger = logging.getLogger(__name__)


# Extended State with language tracking
class ChatbotState(MessagesState):
    """State for the chatbot with language tracking."""
    language: str = "vi"  # Default to Vietnamese
    forced_intent: Optional[str] = None  # For testing: force a specific intent


def chatbot_node(state: ChatbotState) -> ChatbotState:
    """Main chatbot node that processes user messages.
    
    SIMPLIFIED: No tool calling. Product data comes from cached knowledge base.
    LLM has full product context in system prompt.
    """
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
    
    try:
        logger.info(f"Processing query: '{user_text[:50]}...' | Language: {language}")
        
        llm = get_llm()
        
        if llm is None:
            # Fallback: Use simple intent classification if no LLM available
            intent = classify_intent(user_text, language)
            if intent == "cat_products":
                response = get_cat_products_text(language)
            elif intent == "dog_products":
                response = get_dog_products_text(language)
            elif intent == "business":
                response = get_business_info_text(language)
            elif intent == "contact":
                response = get_contact_info_text(language)
            else:
                if language == "vi":
                    response = "Xin lỗi, tôi không thể xử lý câu hỏi này ngay bây giờ. Vui lòng liên hệ với chúng tôi qua Zalo: 0935005762 🐾"
                else:
                    response = "Sorry, I can't process that question right now. Please contact us on Zalo: 0935005762 🐾"
        else:
            # Get system prompt with full knowledge base context
            system_prompt = get_system_prompt_simple(language)
            llm_messages = [SystemMessage(content=system_prompt)] + messages
            
            # Get LLM response (no tools - all data in context)
            llm_response = llm.invoke(llm_messages)
            response = llm_response.content
                
    except Exception as e:
        # Log the error for debugging
        import traceback
        logger.error(f"Error in chatbot_node: {str(e)}")
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
    """Get the configured LLM (xAI Grok).
    
    Returns:
        LLM instance, or None if API key not configured
    """
    api_key = os.getenv("XAI_API_KEY")
    
    if not api_key:
        # If no API key, return None - will use rule-based responses
        return None
    
    try:
        # xAI uses OpenAI-compatible API
        llm = ChatOpenAI(
            model="grok-4-1-fast-non-reasoning",
            api_key=api_key,
            base_url="https://api.x.ai/v1",
            temperature=0.3,
            max_tokens=1500,
        )
        return llm
    except Exception as e:
        logger.warning(f"Failed to initialize LLM: {e}")
        logger.warning("Will use rule-based responses only")
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


# Create the graph instance
graph = create_graph()
