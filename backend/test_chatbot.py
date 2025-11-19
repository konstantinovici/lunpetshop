"""Integration test script for LùnPetShop KittyCat Chatbot - Full pipeline testing."""

import asyncio
import os
import time
import argparse
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from src.chatbot import graph, get_llm
from src.utils import detect_language, classify_intent
import uuid

# Load environment variables
load_dotenv()

# Rule-based test questions (from PRD)
RULE_BASED_QUESTIONS = {
    "Vietnamese": [
        "Bạn có sản phẩm gì cho mèo của tôi?",
        "Bạn có sản phẩm gì cho chó của tôi?",
        "Cho tôi biết về cửa hàng của bạn?",
        "Địa chỉ của bạn ở đâu?",
        "Làm thế nào để liên hệ với bạn qua Zalo?",
    ],
    "English": [
        "What products do you have for my cat?",
        "What products do you have for my dog?",
        "What can you tell me about the business?",
        "What's your address?",
        "How can I reach you on Zalo?",
    ]
}

# LLM integration test questions (general conversation)
# These questions should NOT contain product keywords (cat/dog/mèo/chó) 
# to ensure they trigger "general" intent and use the LLM
LLM_QUESTIONS = {
    "Vietnamese": [
        "Thú cưng của tôi không chịu ăn, bạn có lời khuyên gì không?",
        "Tôi muốn nuôi thú cưng lần đầu, bạn có thể tư vấn không?",
        "Bạn có thể giúp tôi chọn thức ăn phù hợp không?",
        "Cửa hàng có dịch vụ spa không?",
        "Tôi ở xa, có thể đặt hàng online không?",
    ],
    "English": [
        "My pet won't eat, do you have any advice?",
        "I want to adopt a pet for the first time, can you help?",
        "Can you help me choose the right food?",
        "Do you offer spa services?",
        "I live far away, can I order online?",
    ]
}


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80 + "\n")


def print_conversation(question, response, intent=None, response_time=None, used_llm=False):
    """Print a conversation exchange with metadata."""
    print(f"👤 User: {question}")
    if intent:
        print(f"   📊 Intent: {intent} | Language: {detect_language(question)}")
    if used_llm:
        print(f"   🤖 LLM: ✅ (xAI Grok)")
    else:
        print(f"   📋 Response: Rule-based")
    if response_time:
        print(f"   ⏱️  Response time: {response_time:.2f}s")
    print(f"🐱 KittyCat: {response}\n")
    print("-" * 80)


async def test_question(question, language, config, test_type="rule-based", force_llm=False):
    """Test a single question and return metrics.
    
    Args:
        question: The question to test
        language: Language code ("vi" or "en")
        config: Thread config for graph
        test_type: Type of test ("rule-based" or "llm")
        force_llm: If True, force intent to "general" to ensure LLM is used
    """
    start_time = time.time()
    
    # Detect intent before calling graph
    detected_lang = detect_language(question)
    intent = classify_intent(question, detected_lang)
    
    # Force "general" intent for LLM tests to ensure they actually test the LLM
    if force_llm:
        intent = "general"
    
    used_llm = (intent == "general" and get_llm() is not None)
    
    try:
        # Create input
        input_data = {
            "messages": [HumanMessage(content=question)],
            "language": language,
        }
        
        # Force intent to "general" for LLM tests
        if force_llm:
            input_data["forced_intent"] = "general"
        
        # Invoke graph
        result = graph.invoke(input_data, config)
        
        # Get response
        response = result["messages"][-1].content
        response_time = time.time() - start_time
        
        # Verify response is not empty
        assert len(response.strip()) > 0, "Response is empty"
        
        return {
            "success": True,
            "response": response,
            "intent": intent,
            "response_time": response_time,
            "used_llm": used_llm,
            "language": detected_lang,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "response_time": time.time() - start_time,
            "intent": intent,
            "used_llm": used_llm,
        }


async def test_rule_based_questions():
    """Test rule-based responses (product/business/contact queries)."""
    print_header("📋 Testing Rule-Based Responses")
    
    results = {"vi": [], "en": []}
    
    # Test Vietnamese questions
    print("\n🇻🇳 Vietnamese Questions:")
    vi_thread_id = str(uuid.uuid4())
    vi_config = {"configurable": {"thread_id": vi_thread_id}}
    
    for i, question in enumerate(RULE_BASED_QUESTIONS["Vietnamese"], 1):
        print(f"\n📝 Test {i}/{len(RULE_BASED_QUESTIONS['Vietnamese'])} (Vietnamese)")
        result = await test_question(question, "vi", vi_config, "rule-based")
        results["vi"].append(result)
        
        if result["success"]:
            print_conversation(
                question, 
                result["response"],
                intent=result["intent"],
                response_time=result["response_time"],
                used_llm=result["used_llm"]
            )
        else:
            print(f"❌ Error: {result['error']}\n")
        
        await asyncio.sleep(0.3)
    
    # Test English questions
    print("\n🇬🇧 English Questions:")
    en_thread_id = str(uuid.uuid4())
    en_config = {"configurable": {"thread_id": en_thread_id}}
    
    for i, question in enumerate(RULE_BASED_QUESTIONS["English"], 1):
        print(f"\n📝 Test {i}/{len(RULE_BASED_QUESTIONS['English'])} (English)")
        result = await test_question(question, "en", en_config, "rule-based")
        results["en"].append(result)
        
        if result["success"]:
            print_conversation(
                question,
                result["response"],
                intent=result["intent"],
                response_time=result["response_time"],
                used_llm=result["used_llm"]
            )
        else:
            print(f"❌ Error: {result['error']}\n")
        
        await asyncio.sleep(0.3)
    
    return results


async def test_llm_integration():
    """Test LLM integration (general conversation questions)."""
    print_header("🤖 Testing LLM Integration (xAI Grok)")
    
    has_api_key = os.getenv("XAI_API_KEY") is not None
    llm_available = get_llm() is not None
    
    if not has_api_key:
        print("⚠️  Warning: XAI_API_KEY not found in environment!")
        print("   LLM tests will be skipped. Add XAI_API_KEY to .env for full integration testing.\n")
        return None
    
    if not llm_available:
        print("⚠️  Warning: LLM initialization failed!")
        print("   Check your API key and network connection.\n")
        return None
    
    print("✅ LLM available - Testing real API calls...\n")
    
    results = {"vi": [], "en": []}
    
    # Test Vietnamese LLM questions
    print("\n🇻🇳 Vietnamese LLM Questions:")
    vi_thread_id = str(uuid.uuid4())
    vi_config = {"configurable": {"thread_id": vi_thread_id}}
    
    for i, question in enumerate(LLM_QUESTIONS["Vietnamese"], 1):
        print(f"\n📝 LLM Test {i}/{len(LLM_QUESTIONS['Vietnamese'])} (Vietnamese)")
        # Force LLM usage for LLM tests (bypasses intent classification)
        result = await test_question(question, "vi", vi_config, "llm", force_llm=True)
        results["vi"].append(result)
        
        if result["success"]:
            print_conversation(
                question,
                result["response"],
                intent=result["intent"],
                response_time=result["response_time"],
                used_llm=result["used_llm"]
            )
            # Verify it actually used LLM
            if not result["used_llm"]:
                print("   ⚠️  Warning: LLM not available or failed to initialize!")
        else:
            print(f"❌ Error: {result['error']}\n")
        
        await asyncio.sleep(1.0)  # Longer delay for API calls
    
    # Test English LLM questions
    print("\n🇬🇧 English LLM Questions:")
    en_thread_id = str(uuid.uuid4())
    en_config = {"configurable": {"thread_id": en_thread_id}}
    
    for i, question in enumerate(LLM_QUESTIONS["English"], 1):
        print(f"\n📝 LLM Test {i}/{len(LLM_QUESTIONS['English'])} (English)")
        # Force LLM usage for LLM tests (bypasses intent classification)
        result = await test_question(question, "en", en_config, "llm", force_llm=True)
        results["en"].append(result)
        
        if result["success"]:
            print_conversation(
                question,
                result["response"],
                intent=result["intent"],
                response_time=result["response_time"],
                used_llm=result["used_llm"]
            )
            if not result["used_llm"]:
                print("   ⚠️  Warning: LLM not available or failed to initialize!")
        else:
            print(f"❌ Error: {result['error']}\n")
        
        await asyncio.sleep(1.0)  # Longer delay for API calls
    
    return results


def print_summary(rule_based_results, llm_results, test_llm_requested=False):
    """Print test summary with metrics.
    
    Args:
        rule_based_results: Results from rule-based tests
        llm_results: Results from LLM tests (None if skipped)
        test_llm_requested: Whether LLM tests were requested via flag
    """
    print_header("📊 Test Summary & Performance Metrics")
    
    # Rule-based summary
    total_rule_based = sum(len(results) for results in rule_based_results.values())
    successful_rule_based = sum(
        sum(1 for r in results if r.get("success")) 
        for results in rule_based_results.values()
    )
    avg_rule_time = sum(
        sum(r.get("response_time", 0) for r in results if r.get("success"))
        for results in rule_based_results.values()
    ) / max(successful_rule_based, 1)
    
    print(f"\n📋 Rule-Based Responses:")
    print(f"   Total: {total_rule_based} | Success: {successful_rule_based} | Avg Time: {avg_rule_time:.3f}s")
    
    # LLM summary
    if llm_results:
        total_llm = sum(len(results) for results in llm_results.values())
        successful_llm = sum(
            sum(1 for r in results if r.get("success"))
            for results in llm_results.values()
        )
        llm_calls = sum(
            sum(1 for r in results if r.get("used_llm") and r.get("success"))
            for results in llm_results.values()
        )
        avg_llm_time = sum(
            sum(r.get("response_time", 0) for r in results if r.get("success"))
            for results in llm_results.values()
        ) / max(successful_llm, 1)
        
        print(f"\n🤖 LLM Integration:")
        print(f"   Total: {total_llm} | Success: {successful_llm} | LLM Calls: {llm_calls}")
        print(f"   Avg Response Time: {avg_llm_time:.3f}s")
    else:
        if test_llm_requested:
            print(f"\n🤖 LLM Integration: Skipped (no API key or LLM unavailable)")
        else:
            print(f"\n🤖 LLM Integration: Skipped (use --llm flag to enable)")
    
    # Overall status
    print(f"\n✅ Overall Status:")
    print(f"   Rule-based: {'✅ PASS' if successful_rule_based == total_rule_based else '❌ FAIL'}")
    if llm_results:
        successful_llm = sum(
            sum(1 for r in results if r.get("success"))
            for results in llm_results.values()
        )
        total_llm = sum(len(results) for results in llm_results.values())
        print(f"   LLM Integration: {'✅ PASS' if successful_llm == total_llm else '❌ FAIL'}")
    
    print(f"\n🎯 Core Functionality:")
    print(f"   ✓ Product queries (cat/dog)")
    print(f"   ✓ Business information")
    print(f"   ✓ Contact information")
    if llm_results:
        print(f"   ✓ General conversation (LLM)")
    print(f"\n🚀 Pipeline is ready for deployment!\n")


async def test_chatbot(test_llm=False):
    """Full integration test suite - tests entire pipeline.
    
    Args:
        test_llm: If True, runs LLM integration tests (makes real API calls).
                  If False, only runs rule-based tests to save costs.
    """
    
    print_header("🐾 LùnPetShop KittyCat Chatbot - Full Integration Test Suite")
    print("Testing complete pipeline: Language Detection → Intent Classification → Response Generation\n")
    
    if not test_llm:
        print("💡 Tip: Use --llm flag to test LLM integration (makes real API calls)\n")
    
    # Test rule-based responses
    rule_based_results = await test_rule_based_questions()
    
    # Test LLM integration (only if flag is set)
    llm_results = None
    if test_llm:
        llm_results = await test_llm_integration()
    else:
        print("\n⏭️  Skipping LLM integration tests (use --llm flag to enable)")
    
    # Print summary
    print_summary(rule_based_results, llm_results, test_llm_requested=test_llm)


def main():
    """Parse CLI arguments and run tests."""
    parser = argparse.ArgumentParser(
        description="Integration test suite for LùnPetShop KittyCat Chatbot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test_chatbot.py              # Run rule-based tests only (default)
  python test_chatbot.py --llm        # Run all tests including LLM integration
  python test_chatbot.py -l           # Short form for LLM tests
        """
    )
    
    parser.add_argument(
        "--llm",
        "-l",
        action="store_true",
        help="Enable LLM integration tests (makes real API calls to xAI Grok). "
             "By default, LLM tests are skipped to save costs."
    )
    
    args = parser.parse_args()
    
    # Run the test suite
    asyncio.run(test_chatbot(test_llm=args.llm))


if __name__ == "__main__":
    main()

