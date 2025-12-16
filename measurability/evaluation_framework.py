"""
Agent Measurability Framework - Core Evaluation Engine

Production-grade evaluation framework following industry standards from 
HammerBench and MCPToolBench++ benchmarks. Implements fine-grained tool-use 
metrics as outlined in 2025 production e-commerce agent reliability research.

Reference: docs/knowledge/agents measurability, reliability .md
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Optional
import json


class QueryType(str, Enum):
    """Types of queries the agent can handle."""
    PRODUCT_SEARCH = "product_search"
    PRODUCT_DETAILS = "product_details"
    CATEGORY_BROWSE = "category_browse"
    BUSINESS_INFO = "business_info"
    CONTACT_INFO = "contact_info"
    GENERAL = "general"


class ResultQuality(str, Enum):
    """Quality grades for tool call results."""
    EXCELLENT = "excellent"  # Perfect tool + params + response
    GOOD = "good"            # Correct tool, minor param issues
    FAIR = "fair"            # Tool called but suboptimal
    POOR = "poor"            # Wrong tool or major issues


@dataclass
class TestCase:
    """
    Single test case with expected behavior (gold standard).
    
    This serves as the gold standard database entry for evaluation.
    """
    query_id: str
    query: str
    language: Literal["vi", "en"]
    query_type: QueryType
    
    # Expected behavior (gold standard)
    expected_tool: Optional[str] = None  # Which tool should be called
    expected_tool_params: Optional[Dict[str, Any]] = None  # Expected parameters
    expected_response_contains: List[str] = field(default_factory=list)  # Keywords that should appear
    expected_response_not_contains: List[str] = field(default_factory=list)  # Should NOT appear
    
    # Quality criteria
    should_use_tool: bool = True  # Must call tool?
    min_product_count: int = 0  # If search, min products expected
    max_turns: int = 2  # Max turns for resolution
    
    # Multi-turn support
    conversation_history: List[Dict[str, str]] = field(default_factory=list)


@dataclass
class ToolCallMetrics:
    """
    Per-call metrics matching research doc structure (lines 340-350).
    
    Tracks individual tool call performance for fine-grained analysis.
    """
    query_id: str
    user_query: str
    selected_tool: Optional[str]  # Tool that was actually called
    correct_tool: Optional[str]   # Tool that should have been called (gold standard)
    parameters: Dict[str, Any]    # Actual parameters passed
    expected_parameters: Dict[str, Any]  # Expected parameters (gold standard)
    execution_success: bool       # Did tool execute successfully?
    result_quality: ResultQuality # Quality grade
    turns_to_resolution: int      # Number of turns needed
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Detailed metrics
    tool_selection_correct: bool = False
    parameter_accuracy: float = 0.0
    parameter_hallucination_rate: float = 0.0  # PHR
    parameter_missing_rate: float = 0.0        # PMR
    hallucinated_params: List[str] = field(default_factory=list)
    missing_params: List[str] = field(default_factory=list)


@dataclass
class TestResult:
    """
    Captures actual result from running a test case.
    """
    test_case: TestCase
    actual_response: str
    tool_call_metrics: Optional[ToolCallMetrics] = None
    response_time: float = 0.0
    error: Optional[str] = None
    
    # Computed results
    tool_called: bool = False
    passed: bool = False
    response_quality_score: float = 0.0  # 0.0 to 1.0


@dataclass
class EvaluationMetrics:
    """
    Aggregate metrics following HammerBench/MCPToolBench++ standards.
    
    Targets from research doc (Section 3):
    - Tool Selection Accuracy: 95%+
    - Parameter Accuracy: 93%+
    - PHR: <2%
    - PMR: <3%
    - Progress Rate: 90%+
    - Success Rate: 85%+
    - First-Try Resolution: 80%+
    - Hallucinated Answer Rate: <5%
    """
    # Core metrics
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    
    # Tool calling metrics (Industry targets)
    tool_calling_rate: float = 0.0          # % that called tools when expected
    tool_selection_accuracy: float = 0.0    # Target: 95%+
    parameter_accuracy: float = 0.0         # Target: 93%+
    parameter_hallucination_rate: float = 0.0  # PHR, Target: <2%
    parameter_missing_rate: float = 0.0     # PMR, Target: <3%
    
    # Performance metrics
    progress_rate: float = 0.0              # Target: 90%+
    success_rate: float = 0.0               # Target: 85%+
    first_try_resolution: float = 0.0       # Target: 80%+
    hallucinated_answer_rate: float = 0.0   # HAR, Target: <5%
    
    # Additional metrics
    avg_response_quality: float = 0.0
    avg_turns_to_resolution: float = 0.0
    execution_success_rate: float = 0.0
    avg_response_time: float = 0.0
    
    # Breakdown by query type
    metrics_by_type: Dict[str, Dict[str, float]] = field(default_factory=dict)
    
    # Timestamp
    timestamp: datetime = field(default_factory=datetime.now)
    
    def success_probability(self) -> float:
        """Overall probability of desired outcome."""
        return self.passed_tests / self.total_tests if self.total_tests > 0 else 0.0
    
    def meets_industry_targets(self) -> Dict[str, bool]:
        """Check if metrics meet industry targets."""
        return {
            "tool_selection_accuracy": self.tool_selection_accuracy >= 0.95,
            "parameter_accuracy": self.parameter_accuracy >= 0.93,
            "parameter_hallucination_rate": self.parameter_hallucination_rate <= 0.02,
            "parameter_missing_rate": self.parameter_missing_rate <= 0.03,
            "progress_rate": self.progress_rate >= 0.90,
            "success_rate": self.success_rate >= 0.85,
            "first_try_resolution": self.first_try_resolution >= 0.80,
            "hallucinated_answer_rate": self.hallucinated_answer_rate <= 0.05,
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "total_tests": self.total_tests,
            "passed_tests": self.passed_tests,
            "failed_tests": self.failed_tests,
            "tool_calling_rate": self.tool_calling_rate,
            "tool_selection_accuracy": self.tool_selection_accuracy,
            "parameter_accuracy": self.parameter_accuracy,
            "parameter_hallucination_rate": self.parameter_hallucination_rate,
            "parameter_missing_rate": self.parameter_missing_rate,
            "progress_rate": self.progress_rate,
            "success_rate": self.success_rate,
            "first_try_resolution": self.first_try_resolution,
            "hallucinated_answer_rate": self.hallucinated_answer_rate,
            "avg_response_quality": self.avg_response_quality,
            "avg_turns_to_resolution": self.avg_turns_to_resolution,
            "execution_success_rate": self.execution_success_rate,
            "avg_response_time": self.avg_response_time,
            "metrics_by_type": self.metrics_by_type,
            "timestamp": self.timestamp.isoformat(),
            "success_probability": self.success_probability(),
            "meets_targets": self.meets_industry_targets(),
        }


class AgentEvaluator:
    """
    Main evaluator implementing ToolCallEvaluator pattern from research doc (lines 352-407).
    
    Evaluates agent against test cases and computes industry-standard metrics.
    """
    
    def __init__(self, test_cases: List[TestCase]):
        """
        Initialize evaluator with test cases (gold standard database).
        
        Args:
            test_cases: List of TestCase objects serving as gold standard
        """
        self.test_cases = test_cases
        self.results: List[TestResult] = []
        self.tool_call_metrics: List[ToolCallMetrics] = []
    
    def evaluate_tool_call(
        self,
        test_case: TestCase,
        tool_name: Optional[str],
        params: Dict[str, Any],
        turns: int = 1,
        execution_success: bool = True
    ) -> ToolCallMetrics:
        """
        Evaluate a single tool call during execution.
        
        Implements the pattern from research doc (lines 357-390):
        1. Tool Selection Accuracy
        2. Parameter Accuracy
        3. Parameter Hallucination Rate
        4. Parameter Missing Rate
        
        Args:
            test_case: The test case (gold standard)
            tool_name: Tool that was actually called
            params: Actual parameters passed
            turns: Number of turns taken
            execution_success: Whether tool executed successfully
            
        Returns:
            ToolCallMetrics with all calculated metrics
        """
        expected_tool = test_case.expected_tool
        expected_params = test_case.expected_tool_params or {}
        
        # 1. Tool Selection Accuracy
        tool_selection_correct = (tool_name == expected_tool)
        
        # 2. Parameter Accuracy
        param_accuracy = self._calculate_param_accuracy(params, expected_params)
        
        # 3. Parameter Hallucination Rate (PHR)
        hallucinated_params, phr = self._detect_parameter_hallucination(params, expected_params)
        
        # 4. Parameter Missing Rate (PMR)
        missing_params, pmr = self._detect_missing_parameters(params, expected_params)
        
        # 5. Grade result quality
        result_quality = self._grade_result_quality(
            tool_selection_correct,
            param_accuracy,
            phr,
            pmr,
            execution_success
        )
        
        # Create metrics
        metric = ToolCallMetrics(
            query_id=test_case.query_id,
            user_query=test_case.query,
            selected_tool=tool_name,
            correct_tool=expected_tool,
            parameters=params,
            expected_parameters=expected_params,
            execution_success=execution_success and tool_selection_correct and phr < 0.05,
            result_quality=result_quality,
            turns_to_resolution=turns,
            tool_selection_correct=tool_selection_correct,
            parameter_accuracy=param_accuracy,
            parameter_hallucination_rate=phr,
            parameter_missing_rate=pmr,
            hallucinated_params=hallucinated_params,
            missing_params=missing_params,
        )
        
        self.tool_call_metrics.append(metric)
        return metric
    
    def evaluate_single(
        self,
        test_case: TestCase,
        actual_response: str,
        tool_called: bool,
        tool_name: Optional[str] = None,
        tool_params: Optional[Dict[str, Any]] = None,
        turns: int = 1,
        response_time: float = 0.0,
        execution_success: bool = True,
        error: Optional[str] = None
    ) -> TestResult:
        """
        Evaluate one test case against actual results.
        
        Args:
            test_case: The test case (gold standard)
            actual_response: Response from agent
            tool_called: Whether any tool was called
            tool_name: Name of tool called (if any)
            tool_params: Parameters passed to tool (if any)
            turns: Number of turns taken
            response_time: Time to get response
            execution_success: Whether tool executed successfully
            error: Error message if any
            
        Returns:
            TestResult with all metrics
        """
        # Evaluate tool call if applicable
        tool_call_metrics = None
        if test_case.should_use_tool or tool_called:
            tool_call_metrics = self.evaluate_tool_call(
                test_case,
                tool_name,
                tool_params or {},
                turns,
                execution_success
            )
        
        # Score response quality
        response_quality_score = self._score_response(
            actual_response,
            test_case.expected_response_contains,
            test_case.expected_response_not_contains
        )
        
        # Determine pass/fail
        passed = self._determine_pass(
            test_case,
            tool_called,
            tool_call_metrics,
            response_quality_score,
            turns
        )
        
        result = TestResult(
            test_case=test_case,
            actual_response=actual_response,
            tool_call_metrics=tool_call_metrics,
            response_time=response_time,
            error=error,
            tool_called=tool_called,
            passed=passed,
            response_quality_score=response_quality_score,
        )
        
        self.results.append(result)
        return result
    
    def calculate_aggregate_metrics(self) -> EvaluationMetrics:
        """
        Production-grade reporting (lines 392-407).
        
        Computes all industry-standard metrics across all results.
        
        Returns:
            EvaluationMetrics with aggregate statistics
        """
        if not self.results:
            return EvaluationMetrics()
        
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        
        # Tool calling metrics
        expected_tool_calls = sum(1 for r in self.results if r.test_case.should_use_tool)
        actual_tool_calls = sum(1 for r in self.results if r.tool_called and r.test_case.should_use_tool)
        tool_calling_rate = actual_tool_calls / expected_tool_calls if expected_tool_calls > 0 else 0
        
        # Tool selection accuracy
        correct_tools = sum(
            1 for m in self.tool_call_metrics 
            if m.tool_selection_correct
        )
        tool_selection_accuracy = correct_tools / len(self.tool_call_metrics) if self.tool_call_metrics else 0
        
        # Parameter metrics
        param_accuracy = sum(m.parameter_accuracy for m in self.tool_call_metrics) / len(self.tool_call_metrics) if self.tool_call_metrics else 0
        phr = sum(m.parameter_hallucination_rate for m in self.tool_call_metrics) / len(self.tool_call_metrics) if self.tool_call_metrics else 0
        pmr = sum(m.parameter_missing_rate for m in self.tool_call_metrics) / len(self.tool_call_metrics) if self.tool_call_metrics else 0
        
        # Progress Rate: % of correct turns before error
        # For single-turn, this is just success rate
        # For multi-turn, track sequence of successes
        progress_rate = passed / total if total > 0 else 0
        
        # Success Rate
        success_rate = passed / total if total > 0 else 0
        
        # First-Try Resolution: resolved in 1-2 turns
        first_try = sum(
            1 for r in self.results 
            if r.passed and r.tool_call_metrics and r.tool_call_metrics.turns_to_resolution <= 2
        )
        first_try_resolution = first_try / total if total > 0 else 0
        
        # Hallucinated Answer Rate: claiming product exists when tool wasn't called
        hallucinated_answers = sum(
            1 for r in self.results
            if r.test_case.should_use_tool and not r.tool_called and r.response_quality_score < 0.5
        )
        har = hallucinated_answers / total if total > 0 else 0
        
        # Additional metrics
        avg_quality = sum(r.response_quality_score for r in self.results) / total
        avg_turns = sum(
            r.tool_call_metrics.turns_to_resolution 
            for r in self.results if r.tool_call_metrics
        ) / len([r for r in self.results if r.tool_call_metrics]) if any(r.tool_call_metrics for r in self.results) else 1
        
        execution_success = sum(
            1 for m in self.tool_call_metrics if m.execution_success
        ) / len(self.tool_call_metrics) if self.tool_call_metrics else 0
        
        avg_response_time = sum(r.response_time for r in self.results) / total
        
        # Metrics by query type
        metrics_by_type = self._calculate_metrics_by_type()
        
        return EvaluationMetrics(
            total_tests=total,
            passed_tests=passed,
            failed_tests=total - passed,
            tool_calling_rate=tool_calling_rate,
            tool_selection_accuracy=tool_selection_accuracy,
            parameter_accuracy=param_accuracy,
            parameter_hallucination_rate=phr,
            parameter_missing_rate=pmr,
            progress_rate=progress_rate,
            success_rate=success_rate,
            first_try_resolution=first_try_resolution,
            hallucinated_answer_rate=har,
            avg_response_quality=avg_quality,
            avg_turns_to_resolution=avg_turns,
            execution_success_rate=execution_success,
            avg_response_time=avg_response_time,
            metrics_by_type=metrics_by_type,
        )
    
    def _calculate_param_accuracy(
        self, 
        actual: Dict[str, Any], 
        expected: Dict[str, Any]
    ) -> float:
        """
        Calculate parameter accuracy.
        
        AST-parse arguments, validate types.
        
        Args:
            actual: Actual parameters passed
            expected: Expected parameters (gold standard)
            
        Returns:
            Accuracy score 0.0-1.0
        """
        if not expected:
            return 1.0 if not actual else 0.5  # No params expected
        
        if not actual:
            return 0.0  # Expected params but got none
        
        score = 0.0
        total_weight = len(expected)
        
        for key, expected_value in expected.items():
            if key in actual:
                actual_value = actual[key]
                
                # Fuzzy matching for string params (query, category, etc.)
                if isinstance(expected_value, str) and isinstance(actual_value, str):
                    # Check if expected keywords are in actual
                    expected_lower = expected_value.lower()
                    actual_lower = actual_value.lower()
                    
                    if expected_lower in actual_lower or actual_lower in expected_lower:
                        score += 1.0
                    elif any(word in actual_lower for word in expected_lower.split()):
                        score += 0.5  # Partial match
                else:
                    # Exact match for non-strings
                    if actual_value == expected_value:
                        score += 1.0
        
        return score / total_weight if total_weight > 0 else 1.0
    
    def _detect_parameter_hallucination(
        self,
        actual: Dict[str, Any],
        expected: Dict[str, Any]
    ) -> tuple[List[str], float]:
        """
        Detect parameter hallucination (phantom params).
        
        Count non-existent param names.
        
        Args:
            actual: Actual parameters passed
            expected: Expected parameters (gold standard)
            
        Returns:
            Tuple of (list of hallucinated param names, hallucination rate)
        """
        if not actual:
            return [], 0.0
        
        expected_keys = set(expected.keys()) if expected else set()
        actual_keys = set(actual.keys())
        
        # Hallucinated params = params in actual but not in expected
        hallucinated = list(actual_keys - expected_keys)
        
        # PHR = hallucinated / total actual params
        phr = len(hallucinated) / len(actual_keys) if actual_keys else 0.0
        
        return hallucinated, phr
    
    def _detect_missing_parameters(
        self,
        actual: Dict[str, Any],
        expected: Dict[str, Any]
    ) -> tuple[List[str], float]:
        """
        Detect missing required parameters.
        
        Verify required_params present.
        
        Args:
            actual: Actual parameters passed
            expected: Expected parameters (gold standard)
            
        Returns:
            Tuple of (list of missing param names, missing rate)
        """
        if not expected:
            return [], 0.0
        
        expected_keys = set(expected.keys())
        actual_keys = set(actual.keys()) if actual else set()
        
        # Missing params = params in expected but not in actual
        missing = list(expected_keys - actual_keys)
        
        # PMR = missing / total expected params
        pmr = len(missing) / len(expected_keys) if expected_keys else 0.0
        
        return missing, pmr
    
    def _grade_result_quality(
        self,
        tool_correct: bool,
        param_accuracy: float,
        phr: float,
        pmr: float,
        execution_success: bool
    ) -> ResultQuality:
        """
        Grade overall result quality.
        
        Args:
            tool_correct: Was correct tool selected?
            param_accuracy: Parameter accuracy score
            phr: Parameter hallucination rate
            pmr: Parameter missing rate
            execution_success: Did tool execute successfully?
            
        Returns:
            ResultQuality grade
        """
        if not tool_correct:
            return ResultQuality.POOR
        
        if not execution_success:
            return ResultQuality.POOR
        
        # Excellent: perfect or near-perfect
        if param_accuracy >= 0.9 and phr <= 0.02 and pmr <= 0.03:
            return ResultQuality.EXCELLENT
        
        # Good: minor issues
        if param_accuracy >= 0.7 and phr <= 0.1 and pmr <= 0.1:
            return ResultQuality.GOOD
        
        # Fair: tool called but suboptimal
        if param_accuracy >= 0.5:
            return ResultQuality.FAIR
        
        return ResultQuality.POOR
    
    def _score_response(
        self,
        response: str,
        should_contain: List[str],
        should_not_contain: List[str]
    ) -> float:
        """
        Score response quality based on content.
        
        Args:
            response: Actual response text
            should_contain: Keywords that should appear
            should_not_contain: Keywords that should NOT appear
            
        Returns:
            Quality score 0.0-1.0
        """
        if not response:
            return 0.0
        
        score = 1.0
        response_lower = response.lower()
        
        # Heavy penalty for forbidden phrases
        for forbidden in should_not_contain:
            if forbidden.lower() in response_lower:
                score -= 0.5  # Heavy penalty
        
        # Reward for expected content
        if should_contain:
            matches = sum(
                1 for expected in should_contain 
                if expected.lower() in response_lower
            )
            # Bonus for matching expected content
            score += 0.1 * matches
        
        return max(0.0, min(1.0, score))
    
    def _determine_pass(
        self,
        test_case: TestCase,
        tool_called: bool,
        tool_metrics: Optional[ToolCallMetrics],
        response_quality: float,
        turns: int
    ) -> bool:
        """
        Determine if test passed.
        
        Args:
            test_case: The test case
            tool_called: Whether tool was called
            tool_metrics: Tool call metrics
            response_quality: Response quality score
            turns: Number of turns taken
            
        Returns:
            True if passed
        """
        # Must call tool if expected
        if test_case.should_use_tool and not tool_called:
            return False
        
        # Tool selection must be correct
        if tool_metrics and not tool_metrics.tool_selection_correct:
            return False
        
        # Response quality threshold
        if response_quality < 0.5:
            return False
        
        # Max turns constraint
        if turns > test_case.max_turns:
            return False
        
        return True
    
    def _calculate_metrics_by_type(self) -> Dict[str, Dict[str, float]]:
        """Calculate metrics broken down by query type."""
        by_type: Dict[str, List[TestResult]] = {}
        
        for result in self.results:
            query_type = result.test_case.query_type.value
            if query_type not in by_type:
                by_type[query_type] = []
            by_type[query_type].append(result)
        
        metrics_by_type = {}
        for query_type, results in by_type.items():
            total = len(results)
            passed = sum(1 for r in results if r.passed)
            tool_called = sum(1 for r in results if r.tool_called)
            
            metrics_by_type[query_type] = {
                "total": total,
                "passed": passed,
                "success_rate": passed / total if total > 0 else 0,
                "tool_calling_rate": tool_called / total if total > 0 else 0,
            }
        
        return metrics_by_type
    
    def reset(self):
        """Reset evaluator state for new evaluation run."""
        self.results = []
        self.tool_call_metrics = []
    
    def get_failed_tests(self) -> List[TestResult]:
        """Get list of failed test results for analysis."""
        return [r for r in self.results if not r.passed]
    
    def get_results_summary(self) -> str:
        """Get human-readable summary of results."""
        metrics = self.calculate_aggregate_metrics()
        targets = metrics.meets_industry_targets()
        
        lines = [
            "=" * 60,
            "AGENT MEASURABILITY RESULTS",
            "=" * 60,
            "",
            f"Total Tests: {metrics.total_tests}",
            f"Passed: {metrics.passed_tests} ({metrics.success_probability():.1%})",
            f"Failed: {metrics.failed_tests}",
            "",
            "CORE METRICS (Industry Targets):",
            "-" * 40,
            f"  Tool Selection Accuracy:     {metrics.tool_selection_accuracy:6.1%}  {'✓' if targets['tool_selection_accuracy'] else '✗'} (target: 95%+)",
            f"  Parameter Accuracy:          {metrics.parameter_accuracy:6.1%}  {'✓' if targets['parameter_accuracy'] else '✗'} (target: 93%+)",
            f"  Parameter Hallucination:     {metrics.parameter_hallucination_rate:6.1%}  {'✓' if targets['parameter_hallucination_rate'] else '✗'} (target: <2%)",
            f"  Parameter Missing Rate:      {metrics.parameter_missing_rate:6.1%}  {'✓' if targets['parameter_missing_rate'] else '✗'} (target: <3%)",
            f"  Progress Rate:               {metrics.progress_rate:6.1%}  {'✓' if targets['progress_rate'] else '✗'} (target: 90%+)",
            f"  Success Rate:                {metrics.success_rate:6.1%}  {'✓' if targets['success_rate'] else '✗'} (target: 85%+)",
            f"  First-Try Resolution:        {metrics.first_try_resolution:6.1%}  {'✓' if targets['first_try_resolution'] else '✗'} (target: 80%+)",
            f"  Hallucinated Answer Rate:    {metrics.hallucinated_answer_rate:6.1%}  {'✓' if targets['hallucinated_answer_rate'] else '✗'} (target: <5%)",
            "",
            "ADDITIONAL METRICS:",
            "-" * 40,
            f"  Tool Calling Rate:           {metrics.tool_calling_rate:6.1%}",
            f"  Avg Response Quality:        {metrics.avg_response_quality:6.2f}",
            f"  Avg Turns to Resolution:     {metrics.avg_turns_to_resolution:6.2f}",
            f"  Execution Success Rate:      {metrics.execution_success_rate:6.1%}",
            f"  Avg Response Time:           {metrics.avg_response_time:6.2f}s",
            "",
            "=" * 60,
        ]
        
        return "\n".join(lines)









