#!/usr/bin/env python3
"""
Agent Measurability Framework - Main Runner Script

Connects to the chatbot graph and runs evaluation test suite.
Outputs results to console and saves to JSON for tracking.

Usage:
    python measurability/run_evaluation.py              # Run all tests
    python measurability/run_evaluation.py --baseline   # Save as baseline
    python measurability/run_evaluation.py --compare    # Compare to baseline
    python measurability/run_evaluation.py --suite critical  # Run critical tests only
    python measurability/run_evaluation.py --test prod_search_001  # Run single test

Reference: docs/knowledge/agents measurability, reliability .md
"""

import argparse
import asyncio
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "backend"))
sys.path.insert(0, str(project_root / "measurability"))

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

# Load environment variables
# Try both locations: project root and backend directory
load_dotenv(project_root / ".env")
load_dotenv(project_root / "backend" / ".env")

from evaluation_framework import (
    AgentEvaluator,
    TestCase,
    TestResult,
    EvaluationMetrics,
    QueryType,
)
from test_suite import (
    TEST_SUITE,
    CRITICAL_TESTS,
    TOOL_CALLING_TESTS,
    get_test_suite,
    get_test_by_id,
)


# Results file path
RESULTS_FILE = Path(__file__).parent / "evaluation_results.json"


def load_chatbot_graph():
    """
    Load the chatbot graph from backend.
    
    Returns:
        The compiled LangGraph graph
    """
    try:
        from src.chatbot import graph
        return graph
    except ImportError as e:
        print(f"Error importing chatbot graph: {e}")
        print("Make sure the backend is properly set up.")
        sys.exit(1)


def extract_tool_call_info(messages: List[Any]) -> tuple[bool, Optional[str], Optional[Dict]]:
    """
    Extract tool call information from LangGraph messages.
    
    Handles both dict and object formats for tool calls.
    
    Args:
        messages: List of messages from graph result
        
    Returns:
        Tuple of (tool_called, tool_name, tool_params)
    """
    tool_called = False
    tool_name = None
    tool_params = None
    
    for msg in messages:
        # Check for tool calls in AIMessage
        if isinstance(msg, AIMessage):
            tool_calls = getattr(msg, 'tool_calls', None) or []
            
            if tool_calls:
                tool_called = True
                # Get first tool call
                tc = tool_calls[0]
                
                # Handle dict format
                if isinstance(tc, dict):
                    tool_name = tc.get("name")
                    tool_params = tc.get("args", {})
                # Handle object format
                else:
                    tool_name = getattr(tc, "name", None)
                    tool_params = getattr(tc, "args", {})
                break
        
        # Also check for ToolMessage (indicates tool was executed)
        if isinstance(msg, ToolMessage):
            tool_called = True
    
    return tool_called, tool_name, tool_params


async def run_single_test(
    graph,
    test_case: TestCase,
    config: Dict[str, Any]
) -> TestResult:
    """
    Run a single test case through the graph.
    
    Args:
        graph: The chatbot graph
        test_case: Test case to run
        config: Graph configuration
        
    Returns:
        TestResult with all metrics
    """
    start_time = time.time()
    error = None
    
    try:
        # Create input
        input_data = {
            "messages": [HumanMessage(content=test_case.query)],
            "language": test_case.language,
        }
        
        # Invoke graph
        result = graph.invoke(input_data, config)
        
        # Extract response
        messages = result.get("messages", [])
        actual_response = ""
        
        if messages:
            last_msg = messages[-1]
            if isinstance(last_msg, AIMessage):
                actual_response = last_msg.content
            elif hasattr(last_msg, 'content'):
                actual_response = last_msg.content
        
        # Extract tool call info
        tool_called, tool_name, tool_params = extract_tool_call_info(messages)
        
        response_time = time.time() - start_time
        
        return {
            "actual_response": actual_response,
            "tool_called": tool_called,
            "tool_name": tool_name,
            "tool_params": tool_params or {},
            "response_time": response_time,
            "error": None,
            "execution_success": True,
        }
        
    except Exception as e:
        import traceback
        error = str(e)
        traceback.print_exc()
        
        return {
            "actual_response": "",
            "tool_called": False,
            "tool_name": None,
            "tool_params": {},
            "response_time": time.time() - start_time,
            "error": error,
            "execution_success": False,
        }


async def run_evaluation(
    test_cases: List[TestCase],
    graph,
    verbose: bool = True
) -> EvaluationMetrics:
    """
    Run evaluation on all test cases.
    
    Args:
        test_cases: List of test cases to run
        graph: The chatbot graph
        verbose: Print progress
        
    Returns:
        EvaluationMetrics with aggregate results
    """
    evaluator = AgentEvaluator(test_cases)
    
    if verbose:
        print(f"\nRunning {len(test_cases)} test cases...")
        print("-" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        # Create unique config per test
        config = {
            "configurable": {
                "thread_id": f"eval_{test_case.query_id}_{datetime.now().timestamp()}"
            }
        }
        
        if verbose:
            print(f"\n[{i}/{len(test_cases)}] {test_case.query_id}")
            print(f"    Query: {test_case.query[:50]}...")
        
        # Run test
        result = await run_single_test(graph, test_case, config)
        
        # Evaluate result
        test_result = evaluator.evaluate_single(
            test_case=test_case,
            actual_response=result["actual_response"],
            tool_called=result["tool_called"],
            tool_name=result["tool_name"],
            tool_params=result["tool_params"],
            turns=1,  # Single turn for now
            response_time=result["response_time"],
            execution_success=result["execution_success"],
            error=result["error"],
        )
        
        if verbose:
            status = "✓ PASS" if test_result.passed else "✗ FAIL"
            print(f"    Result: {status}")
            if not test_result.passed:
                print(f"    Response: {result['actual_response'][:100]}...")
                if test_case.should_use_tool:
                    print(f"    Tool called: {result['tool_called']} (expected: {test_case.expected_tool})")
                    if result['tool_called']:
                        print(f"    Actual tool: {result['tool_name']}")
        
        # Small delay between tests
        await asyncio.sleep(0.5)
    
    # Calculate aggregate metrics
    metrics = evaluator.calculate_aggregate_metrics()
    
    if verbose:
        print("\n" + evaluator.get_results_summary())
    
    return metrics, evaluator


def save_results(
    metrics: EvaluationMetrics,
    evaluator: AgentEvaluator,
    label: str = "run"
) -> None:
    """
    Save results to JSON file for tracking.
    
    Args:
        metrics: Aggregate metrics
        evaluator: The evaluator with detailed results
        label: Label for this run (e.g., "baseline", "after_fix")
    """
    # Load existing results
    existing = {"runs": []}
    if RESULTS_FILE.exists():
        try:
            with open(RESULTS_FILE, "r") as f:
                existing = json.load(f)
        except json.JSONDecodeError:
            existing = {"runs": []}
    
    # Create new run entry
    run_entry = {
        "timestamp": datetime.now().isoformat(),
        "label": label,
        "metrics": metrics.to_dict(),
        "test_results": [
            {
                "query_id": r.test_case.query_id,
                "query": r.test_case.query,
                "passed": r.passed,
                "tool_called": r.tool_called,
                "response_quality": r.response_quality_score,
                "response_preview": r.actual_response[:200] if r.actual_response else "",
                "error": r.error,
            }
            for r in evaluator.results
        ],
        "tool_call_metrics": [
            {
                "query_id": m.query_id,
                "selected_tool": m.selected_tool,
                "correct_tool": m.correct_tool,
                "tool_selection_correct": m.tool_selection_correct,
                "parameter_accuracy": m.parameter_accuracy,
                "phr": m.parameter_hallucination_rate,
                "pmr": m.parameter_missing_rate,
                "result_quality": m.result_quality.value,
            }
            for m in evaluator.tool_call_metrics
        ],
    }
    
    existing["runs"].append(run_entry)
    
    # Save
    with open(RESULTS_FILE, "w") as f:
        json.dump(existing, f, indent=2)
    
    print(f"\nResults saved to {RESULTS_FILE}")


def compare_to_baseline() -> None:
    """Compare latest run to baseline."""
    if not RESULTS_FILE.exists():
        print("No results file found. Run evaluation first.")
        return
    
    with open(RESULTS_FILE, "r") as f:
        data = json.load(f)
    
    runs = data.get("runs", [])
    if len(runs) < 2:
        print("Need at least 2 runs to compare. Run baseline first, then another evaluation.")
        return
    
    # Find baseline
    baseline = None
    for run in runs:
        if run.get("label") == "baseline":
            baseline = run
            break
    
    if not baseline:
        baseline = runs[0]
        print("No baseline labeled. Using first run as baseline.")
    
    latest = runs[-1]
    
    print("\n" + "=" * 60)
    print("COMPARISON: Baseline vs Latest")
    print("=" * 60)
    
    baseline_metrics = baseline["metrics"]
    latest_metrics = latest["metrics"]
    
    metrics_to_compare = [
        ("Success Probability", "success_probability", True),
        ("Tool Selection Accuracy", "tool_selection_accuracy", True),
        ("Parameter Accuracy", "parameter_accuracy", True),
        ("Parameter Hallucination Rate", "parameter_hallucination_rate", False),
        ("Parameter Missing Rate", "parameter_missing_rate", False),
        ("Success Rate", "success_rate", True),
        ("First-Try Resolution", "first_try_resolution", True),
        ("Hallucinated Answer Rate", "hallucinated_answer_rate", False),
    ]
    
    print(f"\n{'Metric':<30} {'Baseline':>10} {'Latest':>10} {'Change':>10}")
    print("-" * 60)
    
    for name, key, higher_is_better in metrics_to_compare:
        b_val = baseline_metrics.get(key, 0)
        l_val = latest_metrics.get(key, 0)
        diff = l_val - b_val
        
        # Determine if improvement
        if higher_is_better:
            improved = diff > 0
        else:
            improved = diff < 0
        
        sign = "+" if diff > 0 else ""
        indicator = "↑" if improved else "↓" if diff != 0 else "-"
        
        print(f"{name:<30} {b_val:>9.1%} {l_val:>9.1%} {sign}{diff:>7.1%} {indicator}")
    
    print("-" * 60)


def print_failed_tests(evaluator: AgentEvaluator) -> None:
    """Print details of failed tests for debugging."""
    failed = evaluator.get_failed_tests()
    
    if not failed:
        print("\n✓ All tests passed!")
        return
    
    print(f"\n{len(failed)} FAILED TESTS:")
    print("=" * 60)
    
    for result in failed:
        tc = result.test_case
        print(f"\n[{tc.query_id}] {tc.query}")
        print(f"  Language: {tc.language}")
        print(f"  Expected tool: {tc.expected_tool}")
        print(f"  Tool called: {result.tool_called}")
        if result.tool_call_metrics:
            print(f"  Actual tool: {result.tool_call_metrics.selected_tool}")
            print(f"  Tool correct: {result.tool_call_metrics.tool_selection_correct}")
        print(f"  Response quality: {result.response_quality_score:.2f}")
        print(f"  Response preview: {result.actual_response[:150]}...")
        if result.error:
            print(f"  Error: {result.error}")
        print("-" * 60)


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Agent Measurability Framework - Run Evaluations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python run_evaluation.py                    # Run all tests
    python run_evaluation.py --baseline         # Save as baseline
    python run_evaluation.py --compare          # Compare to baseline
    python run_evaluation.py --suite critical   # Run critical tests only
    python run_evaluation.py --suite tool_calling  # Run tool-calling tests
    python run_evaluation.py --test prod_search_001  # Run single test
    python run_evaluation.py --verbose          # Show detailed output
        """
    )
    
    parser.add_argument(
        "--baseline",
        action="store_true",
        help="Save this run as baseline for comparison"
    )
    
    parser.add_argument(
        "--compare",
        action="store_true",
        help="Compare latest run to baseline"
    )
    
    parser.add_argument(
        "--suite",
        type=str,
        default="all",
        choices=["all", "critical", "tool_calling", "rule_based", 
                 "product_search", "category", "details", "business",
                 "contact", "edge", "general"],
        help="Test suite to run (default: all)"
    )
    
    parser.add_argument(
        "--test",
        type=str,
        help="Run a specific test by query_id"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        default=True,
        help="Show detailed output"
    )
    
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Minimal output"
    )
    
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Don't save results to file"
    )
    
    parser.add_argument(
        "--show-failed",
        action="store_true",
        help="Show details of failed tests"
    )
    
    args = parser.parse_args()
    
    # Handle compare mode
    if args.compare:
        compare_to_baseline()
        return
    
    # Determine verbosity
    verbose = not args.quiet
    
    # Get test cases
    if args.test:
        test_case = get_test_by_id(args.test)
        if not test_case:
            print(f"Test case '{args.test}' not found.")
            sys.exit(1)
        test_cases = [test_case]
    else:
        test_cases = get_test_suite(args.suite)
    
    print(f"\n{'=' * 60}")
    print("AGENT MEASURABILITY FRAMEWORK")
    print(f"{'=' * 60}")
    print(f"Test suite: {args.suite}")
    print(f"Test cases: {len(test_cases)}")
    
    # Load graph
    graph = load_chatbot_graph()
    
    # Run evaluation
    metrics, evaluator = await run_evaluation(test_cases, graph, verbose)
    
    # Show failed tests if requested
    if args.show_failed:
        print_failed_tests(evaluator)
    
    # Save results
    if not args.no_save:
        label = "baseline" if args.baseline else "run"
        save_results(metrics, evaluator, label)
    
    # Exit with appropriate code
    if metrics.success_probability() < 0.5:
        sys.exit(1)  # Fail if less than 50% success
    
    sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())

