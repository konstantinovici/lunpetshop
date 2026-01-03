# Agent Measurability Framework

Production-grade evaluation framework for measuring agent reliability following industry standards from HammerBench and MCPToolBench++ benchmarks (2025).

## Overview

This framework measures **tool-calling reliability** and **response quality** for the LùnPetShop chatbot agent. It implements fine-grained metrics as outlined in production e-commerce agent reliability research.

**Reference:** `docs/knowledge/agents measurability, reliability .md`

## Quick Start

```bash
# From project root
cd measurability

# Run all tests
python run_evaluation.py

# Run and save as baseline
python run_evaluation.py --baseline

# Run critical tests only (faster)
python run_evaluation.py --suite critical

# Compare latest run to baseline
python run_evaluation.py --compare

# Run a specific test
python run_evaluation.py --test prod_search_001
```

## Industry-Standard Metrics

The framework tracks 8 core metrics with industry targets:

| Metric | Target | Description |
|--------|--------|-------------|
| **Tool Selection Accuracy** | 95%+ | % of queries routed to correct tool |
| **Parameter Accuracy** | 93%+ | % of tool calls with correct parameters |
| **Parameter Hallucination Rate (PHR)** | <2% | % of incorrect parameters added |
| **Parameter Missing Rate (PMR)** | <3% | % of missing required parameters |
| **Progress Rate (PR)** | 90%+ | % of correct turns before error |
| **Success Rate (SR)** | 85%+ | Overall task completion across turns |
| **First-Try Resolution (FTR)** | 80%+ | % of queries resolved in 1-2 turns |
| **Hallucinated Answer Rate (HAR)** | <5% | % claiming product exists when not |

## Files

```
measurability/
├── evaluation_framework.py  # Core evaluation engine
├── test_suite.py           # Test case definitions (gold standard)
├── run_evaluation.py       # Main runner script
├── evaluation_results.json # Results history (auto-generated)
└── README.md              # This file
```

## Test Suites

Available test suites:

| Suite | Description | Count |
|-------|-------------|-------|
| `all` | All test cases | ~25 |
| `critical` | Must-pass tests (the failure case, etc.) | 4 |
| `tool_calling` | Tests requiring tool calls | ~15 |
| `rule_based` | Tests not requiring tools | ~10 |
| `product_search` | Product search queries | 8 |
| `category` | Category browse queries | 3 |
| `details` | Product details queries | 2 |
| `business` | Business info queries | 2 |
| `contact` | Contact info queries | 4 |
| `edge` | Edge cases / ambiguous queries | 4 |
| `general` | General conversation | 4 |

## Usage Examples

### Running Evaluations

```bash
# Full evaluation
python run_evaluation.py

# Quick critical-only check
python run_evaluation.py --suite critical

# Tool-calling reliability focus
python run_evaluation.py --suite tool_calling

# Save baseline before making changes
python run_evaluation.py --baseline

# After implementing a fix, compare to baseline
python run_evaluation.py --compare
```

### Interpreting Results

Sample output:

```
============================================================
AGENT MEASURABILITY RESULTS
============================================================

Total Tests: 25
Passed: 18 (72.0%)
Failed: 7

CORE METRICS (Industry Targets):
----------------------------------------
  Tool Selection Accuracy:      65.0%  ✗ (target: 95%+)
  Parameter Accuracy:           80.0%  ✗ (target: 93%+)
  Parameter Hallucination:       5.0%  ✗ (target: <2%)
  Parameter Missing Rate:        3.0%  ✗ (target: <3%)
  Progress Rate:                72.0%  ✗ (target: 90%+)
  Success Rate:                 72.0%  ✗ (target: 85%+)
  First-Try Resolution:         60.0%  ✗ (target: 80%+)
  Hallucinated Answer Rate:     12.0%  ✗ (target: <5%)

============================================================
```

The ✓ and ✗ indicate whether each metric meets industry targets.

### Comparing Runs

After implementing fixes:

```bash
python run_evaluation.py --compare
```

Output:

```
============================================================
COMPARISON: Baseline vs Latest
============================================================

Metric                         Baseline    Latest     Change
------------------------------------------------------------
Success Probability              60.0%     75.0%     +15.0% ↑
Tool Selection Accuracy          65.0%     85.0%     +20.0% ↑
Parameter Accuracy               80.0%     90.0%     +10.0% ↑
...
------------------------------------------------------------
```

## Adding New Test Cases

Edit `test_suite.py`:

```python
from evaluation_framework import TestCase, QueryType

NEW_TEST = TestCase(
    query_id="prod_search_new",
    query="Your test query here",
    language="en",
    query_type=QueryType.PRODUCT_SEARCH,
    expected_tool="search_products_tool",
    expected_tool_params={"query": "expected params"},
    expected_response_contains=["keywords", "to", "find"],
    expected_response_not_contains=["forbidden", "words"],
    should_use_tool=True,
)

# Add to TEST_SUITE list
```

### Test Case Fields

| Field | Description |
|-------|-------------|
| `query_id` | Unique identifier |
| `query` | The user query to test |
| `language` | "en" or "vi" |
| `query_type` | QueryType enum value |
| `expected_tool` | Tool that should be called (or None) |
| `expected_tool_params` | Expected parameters (gold standard) |
| `expected_response_contains` | Keywords response should include |
| `expected_response_not_contains` | Forbidden phrases |
| `should_use_tool` | Whether tool call is expected |
| `min_product_count` | Minimum products expected (for search) |
| `max_turns` | Maximum turns for resolution (default: 2) |

## The Game Plan

1. **Baseline**: Run `python run_evaluation.py --baseline` to establish current metrics
2. **Implement Fix**: Make changes to the chatbot (e.g., add retry logic)
3. **Re-evaluate**: Run `python run_evaluation.py`
4. **Compare**: Run `python run_evaluation.py --compare` to see improvement
5. **Iterate**: Repeat until metrics meet industry targets

### Expected Reliability Progression (from research)

| Stage | Tool-Calling Success |
|-------|---------------------|
| Baseline (ReAct only) | 65-75% |
| + IRMA (Input Reformulation) | 81-87% |
| + AgentSpec (Runtime Constraints) | 88-92% |
| + Multi-Agent Orchestration | 93-96% |
| + Continuous Evaluation | 96-98% |

## Integration with Chatbot

The framework connects to `backend/src/chatbot.py`:

```python
from src.chatbot import graph

# The graph is invoked with:
result = graph.invoke({
    "messages": [HumanMessage(content=query)],
    "language": language,
}, config)
```

Tool calls are extracted from the LangGraph message format (handles both dict and object formats).

## Results File Structure

`evaluation_results.json`:

```json
{
  "runs": [
    {
      "timestamp": "2025-11-30T12:00:00",
      "label": "baseline",
      "metrics": {
        "tool_selection_accuracy": 0.65,
        "parameter_accuracy": 0.80,
        "success_rate": 0.72,
        ...
      },
      "test_results": [
        {
          "query_id": "prod_search_001",
          "passed": false,
          "tool_called": false,
          "response_quality": 0.3,
          ...
        }
      ],
      "tool_call_metrics": [...]
    }
  ]
}
```

## Troubleshooting

### "Error importing chatbot graph"

Make sure you're running from the project root and the backend is set up:

```bash
cd /path/to/lunpetshop
source backend/venv/bin/activate
python measurability/run_evaluation.py
```

### "No results file found"

Run an evaluation first:

```bash
python measurability/run_evaluation.py --baseline
```

### Tests timing out

The framework includes delays between tests. For faster runs:

```bash
python measurability/run_evaluation.py --suite critical
```

## References

- HammerBench (June 2025): Multi-turn dialogue evaluation
- MCPToolBench++ (August 2025): Real-world MCP server benchmarks
- AgentSpec: Runtime constraint enforcement
- IRMA: Input Reformulation Multi-Agent framework

See `docs/knowledge/agents measurability, reliability .md` for full research details.












