"""LangGraph chatbot for LùnPetShop with bilingual support."""

from typing import Annotated, Literal, Optional, List
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
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
from .prompts import get_system_prompt
from .utils import detect_language, classify_intent  # classify_intent for fallback only
import logging

logger = logging.getLogger(__name__)


# Extended State with language tracking
class ChatbotState(MessagesState):
    """State for the chatbot with language tracking."""
    language: str = "vi"  # Default to Vietnamese
    forced_intent: Optional[str] = None  # For testing: force a specific intent


def chatbot_node(state: ChatbotState) -> ChatbotState:
    """Main chatbot node that processes user messages using ReAct pattern.
    
    ReAct (Reasoning + Acting): Tools are always available, LLM decides when to use them.
    No intent classification needed - the LLM reasons about tool usage dynamically.
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
        # ReAct Pattern: Always import and bind tools
        # The LLM will decide when to use them based on the conversation
        from .woocommerce_tools import (
            search_products_tool,
            get_products_by_category_tool,
            get_product_details_tool
        )
        
        # Always bind tools - let LLM decide when to use them
        tools = [
            search_products_tool,
            get_products_by_category_tool,
            get_product_details_tool
        ]
        
        logger.info(f"Processing query: '{user_text[:50]}...' | Language: {language}")
        
        llm = get_llm(tools=tools)
        
        if llm is None:
            # Fallback: Use simple intent classification only if no LLM available
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
            # ReAct: LLM reasons about when to use tools
            system_prompt = get_system_prompt(language)
            llm_messages = [SystemMessage(content=system_prompt)] + messages
            
            # Get LLM response (with tools available)
            llm_response = llm.invoke(llm_messages)
            
            # Check if LLM decided to use tools
            tool_calls = getattr(llm_response, 'tool_calls', None) or []
            
            if tool_calls:
                logger.info(f"Tool calls requested: {[getattr(tc, 'name', tc.get('name') if isinstance(tc, dict) else 'unknown') for tc in tool_calls]}")
                # Execute tools that LLM requested
                tool_messages = []
                tool_map = {tool.name: tool for tool in tools}
                
                for tool_call in tool_calls:
                    # Handle different tool_call formats
                    if isinstance(tool_call, dict):
                        tool_name = tool_call.get("name")
                        tool_args = tool_call.get("args", {})
                        tool_call_id = tool_call.get("id")
                    else:
                        tool_name = getattr(tool_call, "name", None)
                        tool_args = getattr(tool_call, "args", {})
                        tool_call_id = getattr(tool_call, "id", None)
                    
                    if tool_name and tool_name in tool_map:
                        try:
                            # Execute tool
                            tool_result = tool_map[tool_name].invoke(tool_args)
                            tool_messages.append(ToolMessage(
                                content=str(tool_result),
                                tool_call_id=tool_call_id or f"call_{tool_name}"
                            ))
                        except Exception as e:
                            # Handle tool execution errors
                            import traceback
                            error_msg = f"Error executing tool {tool_name}: {str(e)}"
                            print(f"Tool execution error: {error_msg}")
                            traceback.print_exc()
                            tool_messages.append(ToolMessage(
                                content=error_msg,
                                tool_call_id=tool_call_id or f"call_{tool_name}"
                            ))
                
                # LLM processes tool results and generates final response
                updated_messages = llm_messages + [llm_response] + tool_messages
                final_response = llm.invoke(updated_messages)
                response = final_response.content
            else:
                # No tool calls - LLM responded directly
                logger.info("No tool calls - LLM responded directly")
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


def get_llm(tools: Optional[List] = None):
    """Get the configured LLM (xAI Grok), optionally with tools bound.
    
    Args:
        tools: Optional list of LangChain tools to bind to the LLM
        
    Returns:
        LLM instance with tools bound (if provided), or None if API key not configured
    """
    api_key = os.getenv("XAI_API_KEY")
    
    if not api_key:
        # If no API key, return None - will use rule-based responses
        return None
    
    try:
        # xAI uses OpenAI-compatible API
        # Latest model: Grok 4 Fast with 2M context window
        llm = ChatOpenAI(
            model="grok-4-1-fast-non-reasoning",  # Latest xAI model (2M context window)
            api_key=api_key,
            base_url="https://api.x.ai/v1",
            temperature=0.3,   # Lower for reliable tool calling
            max_tokens=1500,   # Room for product lists
        )
        
        # Bind tools if provided
        if tools:
            llm = llm.bind_tools(tools)
        
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


# Create the graph instance
graph = create_graph()
