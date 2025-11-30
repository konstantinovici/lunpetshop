"""TDD tests for chatbot integration with WooCommerce tools - Phase 3.

All tests written BEFORE implementation (TDD Red phase).
Run with: python test_chatbot_with_tools.py
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from src.chatbot import get_llm, chatbot_node, ChatbotState
from src.woocommerce_tools import (
    search_products_tool,
    get_products_by_category_tool,
    get_product_details_tool
)


class TestChatbotWithTools(unittest.TestCase):
    """Test suite for chatbot integration with WooCommerce tools."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.tools = [
            search_products_tool,
            get_products_by_category_tool,
            get_product_details_tool
        ]
    
    @patch('src.chatbot.ChatOpenAI')
    def test_llm_binds_tools(self, mock_chat_openai):
        """Test verify tools are bound to LLM."""
        # Setup mock LLM
        mock_llm_instance = Mock()
        mock_llm_instance.bind_tools = Mock(return_value=mock_llm_instance)
        mock_chat_openai.return_value = mock_llm_instance
        
        # Execute
        llm = get_llm(tools=self.tools)
        
        # Assert
        self.assertIsNotNone(llm)
        # Should have called bind_tools
        mock_llm_instance.bind_tools.assert_called_once()
        # Should have passed the tools
        call_args = mock_llm_instance.bind_tools.call_args[0][0]
        self.assertEqual(len(call_args), len(self.tools))
    
    @patch('src.chatbot.get_llm')
    @patch('src.woocommerce_tools.WooCommerceClient')
    def test_chatbot_calls_tool_for_product_query(self, mock_client_class, mock_get_llm):
        """Test LLM invokes tool when needed."""
        # Setup mock LLM with tool calling
        mock_llm = Mock()
        mock_tool_call = Mock()
        mock_tool_call.name = "search_products_tool"
        mock_tool_call.args = {"query": "cat food"}
        mock_tool_call.get = Mock(return_value="tool_call_id_123")
        
        mock_ai_message = Mock()
        mock_ai_message.tool_calls = [mock_tool_call]
        mock_ai_message.content = ""
        
        mock_llm.invoke = Mock(side_effect=[
            mock_ai_message,  # First call returns tool call
            Mock(content="Here are some cat food products...")  # Second call returns final response
        ])
        mock_get_llm.return_value = mock_llm
        
        # Setup mock client
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.search_products.return_value = []
        
        # Create state
        state = ChatbotState(
            messages=[HumanMessage(content="What cat food do you have?")],
            language="en"
        )
        
        # Execute
        result = chatbot_node(state)
        
        # Assert
        self.assertIsNotNone(result)
        # Should have invoked LLM
        self.assertGreater(mock_llm.invoke.call_count, 0)
        # Final response should be in messages
        messages = result.get("messages", [])
        self.assertGreater(len(messages), 0)
    
    @patch('src.chatbot.get_llm')
    @patch('src.woocommerce_tools.WooCommerceClient')
    def test_chatbot_tool_execution_flow(self, mock_client_class, mock_get_llm):
        """Test tool call -> execution -> final response."""
        # Setup mock LLM
        mock_llm = Mock()
        
        # First call: LLM decides to use tool
        mock_tool_call = Mock()
        mock_tool_call.name = "search_products_tool"
        mock_tool_call.args = {"query": "pate"}
        mock_tool_call.get = Mock(return_value="tool_call_id_123")
        
        mock_ai_message_1 = Mock()
        mock_ai_message_1.tool_calls = [mock_tool_call]
        mock_ai_message_1.content = ""
        
        # Second call: LLM generates final response with tool results
        mock_ai_message_2 = Mock()
        mock_ai_message_2.content = "Here are some pate products for your cat..."
        mock_ai_message_2.tool_calls = []
        
        mock_llm.invoke = Mock(side_effect=[mock_ai_message_1, mock_ai_message_2])
        mock_get_llm.return_value = mock_llm
        
        # Setup mock client
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.search_products.return_value = [{"name": "Pate Nekko", "prices": {"price": "16000"}}]
        
        # Create state
        state = ChatbotState(
            messages=[HumanMessage(content="Show me pate for cats")],
            language="en"
        )
        
        # Execute
        result = chatbot_node(state)
        
        # Assert
        messages = result.get("messages", [])
        # Should have tool message in conversation
        tool_messages = [msg for msg in messages if isinstance(msg, ToolMessage)]
        self.assertGreater(len(tool_messages), 0)
        # Final response should be from LLM
        final_message = messages[-1]
        self.assertIsInstance(final_message, AIMessage)
        self.assertIn("pate", final_message.content.lower())
    
    @patch('src.chatbot.get_llm')
    def test_chatbot_multiple_tool_calls(self, mock_get_llm):
        """Test handles multiple tool calls in one response."""
        # Setup mock LLM
        mock_llm = Mock()
        
        # First call: LLM decides to use multiple tools
        mock_tool_call_1 = Mock()
        mock_tool_call_1.name = "search_products_tool"
        mock_tool_call_1.args = {"query": "cat food"}
        mock_tool_call_1.get = Mock(return_value="tool_call_id_1")
        
        mock_tool_call_2 = Mock()
        mock_tool_call_2.name = "get_products_by_category_tool"
        mock_tool_call_2.args = {"category_name": "Thức ăn cho Mèo"}
        mock_tool_call_2.get = Mock(return_value="tool_call_id_2")
        
        mock_ai_message_1 = Mock()
        mock_ai_message_1.tool_calls = [mock_tool_call_1, mock_tool_call_2]
        mock_ai_message_1.content = ""
        
        # Second call: Final response
        mock_ai_message_2 = Mock()
        mock_ai_message_2.content = "Here are cat food products..."
        mock_ai_message_2.tool_calls = []
        
        mock_llm.invoke = Mock(side_effect=[mock_ai_message_1, mock_ai_message_2])
        mock_get_llm.return_value = mock_llm
        
        # Create state
        state = ChatbotState(
            messages=[HumanMessage(content="Show me cat food products")],
            language="en"
        )
        
        # Execute
        result = chatbot_node(state)
        
        # Assert
        messages = result.get("messages", [])
        # Should have multiple tool messages
        tool_messages = [msg for msg in messages if isinstance(msg, ToolMessage)]
        self.assertGreaterEqual(len(tool_messages), 1)
    
    @patch('src.chatbot.get_llm')
    def test_chatbot_no_tools_for_general_query(self, mock_get_llm):
        """Test doesn't use tools unnecessarily."""
        # Setup mock LLM
        mock_llm = Mock()
        mock_ai_message = Mock()
        mock_ai_message.content = "Hello! How can I help you?"
        mock_ai_message.tool_calls = []  # No tool calls
        
        mock_llm.invoke = Mock(return_value=mock_ai_message)
        mock_get_llm.return_value = mock_llm
        
        # Create state
        state = ChatbotState(
            messages=[HumanMessage(content="Hello")],
            language="en"
        )
        
        # Execute
        result = chatbot_node(state)
        
        # Assert
        messages = result.get("messages", [])
        # Should not have tool messages
        tool_messages = [msg for msg in messages if isinstance(msg, ToolMessage)]
        self.assertEqual(len(tool_messages), 0)
        # Should have direct response
        final_message = messages[-1]
        self.assertIsInstance(final_message, AIMessage)
    
    @patch('src.chatbot.get_llm')
    @patch('src.woocommerce_tools.WooCommerceClient')
    def test_chatbot_fallback_on_tool_error(self, mock_client_class, mock_get_llm):
        """Test graceful degradation when tools fail."""
        # Setup mock LLM
        mock_llm = Mock()
        mock_tool_call = Mock()
        mock_tool_call.name = "search_products_tool"
        mock_tool_call.args = {"query": "pate"}
        mock_tool_call.get = Mock(return_value="tool_call_id_123")
        
        mock_ai_message_1 = Mock()
        mock_ai_message_1.tool_calls = [mock_tool_call]
        mock_ai_message_1.content = ""
        
        # Second call: LLM handles error gracefully
        mock_ai_message_2 = Mock()
        mock_ai_message_2.content = "I'm sorry, I couldn't find products right now. Please contact us via Zalo."
        mock_ai_message_2.tool_calls = []
        
        mock_llm.invoke = Mock(side_effect=[mock_ai_message_1, mock_ai_message_2])
        mock_get_llm.return_value = mock_llm
        
        # Setup mock client to raise error
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.search_products.side_effect = Exception("API Error")
        
        # Create state
        state = ChatbotState(
            messages=[HumanMessage(content="Show me pate")],
            language="en"
        )
        
        # Execute
        result = chatbot_node(state)
        
        # Assert
        messages = result.get("messages", [])
        # Should still have a response (graceful degradation)
        final_message = messages[-1]
        self.assertIsInstance(final_message, AIMessage)
        self.assertIsNotNone(final_message.content)
    
    @patch('src.chatbot.get_llm')
    def test_product_search_intent_uses_tools(self, mock_get_llm):
        """Test product_search intent routes to tools."""
        # Setup mock LLM
        mock_llm = Mock()
        mock_tool_call = Mock()
        mock_tool_call.name = "search_products_tool"
        mock_tool_call.args = {"query": "cat food"}
        mock_tool_call.get = Mock(return_value="tool_call_id_123")
        
        mock_ai_message_1 = Mock()
        mock_ai_message_1.tool_calls = [mock_tool_call]
        mock_ai_message_1.content = ""
        
        mock_ai_message_2 = Mock()
        mock_ai_message_2.content = "Here are cat food products..."
        mock_ai_message_2.tool_calls = []
        
        mock_llm.invoke = Mock(side_effect=[mock_ai_message_1, mock_ai_message_2])
        mock_get_llm.return_value = mock_llm
        
        # Create state with product_search intent
        state = ChatbotState(
            messages=[HumanMessage(content="What cat food do you have?")],
            language="en",
            forced_intent="product_search"
        )
        
        # Execute
        result = chatbot_node(state)
        
        # Assert
        # Should have used LLM with tools (not rule-based)
        self.assertGreater(mock_llm.invoke.call_count, 0)
    
    def test_existing_intents_still_work(self):
        """Test backward compatibility - existing intents still work."""
        # Create state with cat_products intent (should use rule-based)
        state = ChatbotState(
            messages=[HumanMessage(content="What products for my cat?")],
            language="en",
            forced_intent="cat_products"
        )
        
        # Execute
        result = chatbot_node(state)
        
        # Assert
        messages = result.get("messages", [])
        self.assertGreater(len(messages), 0)
        # Should have response (rule-based, not tool-based)
        final_message = messages[-1]
        self.assertIsInstance(final_message, AIMessage)
        self.assertIn("cat", final_message.content.lower() or "mèo", final_message.content.lower())
    
    def test_chatbot_without_llm_fallback(self):
        """Test works when LLM unavailable."""
        # Create state
        state = ChatbotState(
            messages=[HumanMessage(content="Hello")],
            language="en"
        )
        
        # Mock get_llm to return None (no LLM available)
        with patch('src.chatbot.get_llm', return_value=None):
            # Execute
            result = chatbot_node(state)
            
            # Assert
            messages = result.get("messages", [])
            self.assertGreater(len(messages), 0)
            # Should have fallback response
            final_message = messages[-1]
            self.assertIsInstance(final_message, AIMessage)
            self.assertIsNotNone(final_message.content)


if __name__ == "__main__":
    unittest.main()

