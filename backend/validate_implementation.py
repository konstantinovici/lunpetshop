#!/usr/bin/env python3
"""Validation script to verify WooCommerce integration implementation.

This script checks:
1. All required files exist
2. Classes and functions are properly defined
3. Import structure is correct
4. Test files are structured correctly
"""

import ast
import os
import sys
from pathlib import Path


def check_file_exists(filepath):
    """Check if file exists."""
    return os.path.exists(filepath)


def get_class_names(filepath):
    """Extract class names from Python file."""
    try:
        with open(filepath, 'r') as f:
            tree = ast.parse(f.read())
        classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        return classes
    except Exception as e:
        return []


def get_function_names(filepath):
    """Extract function names from Python file."""
    try:
        with open(filepath, 'r') as f:
            tree = ast.parse(f.read())
        functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        return functions
    except Exception as e:
        return []


def check_imports(filepath, required_imports):
    """Check if required imports are present."""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        found = []
        missing = []
        for imp in required_imports:
            if imp in content:
                found.append(imp)
            else:
                missing.append(imp)
        return found, missing
    except Exception as e:
        return [], required_imports


def main():
    """Run validation checks."""
    print("🔍 Validating WooCommerce Integration Implementation\n")
    print("=" * 60)
    
    all_passed = True
    
    # Check implementation files
    print("\n📁 Implementation Files:")
    impl_files = {
        'src/woocommerce.py': {
            'classes': ['WooCommerceClient'],
            'functions': ['search_products', 'get_products_by_category', 'get_products_by_category_name', 
                         'get_all_products', 'get_product_by_id', 'get_product_by_name', 'get_categories'],
            'imports': ['httpx', 'typing']
        },
        'src/woocommerce_tools.py': {
            'classes': [],
            'functions': ['search_products_tool', 'get_products_by_category_tool', 'get_product_details_tool'],
            'imports': ['langchain_core.tools', 'tool']
        },
        'src/chatbot.py': {
            'classes': ['ChatbotState'],
            'functions': ['chatbot_node', 'get_llm', 'create_graph'],
            'imports': ['ToolMessage', 'bind_tools']
        }
    }
    
    for filepath, checks in impl_files.items():
        print(f"\n  Checking {filepath}...")
        if not check_file_exists(filepath):
            print(f"    ✗ File does not exist!")
            all_passed = False
            continue
        
        # Check classes
        classes = get_class_names(filepath)
        for expected_class in checks['classes']:
            if expected_class in classes:
                print(f"    ✓ Class '{expected_class}' found")
            else:
                print(f"    ✗ Class '{expected_class}' NOT found")
                all_passed = False
        
        # Check functions
        functions = get_function_names(filepath)
        for expected_func in checks['functions']:
            if expected_func in functions:
                print(f"    ✓ Function '{expected_func}' found")
            else:
                print(f"    ✗ Function '{expected_func}' NOT found")
                all_passed = False
        
        # Check imports
        found_imports, missing_imports = check_imports(filepath, checks['imports'])
        for imp in found_imports:
            print(f"    ✓ Import '{imp}' found")
        for imp in missing_imports:
            print(f"    ⚠ Import '{imp}' not explicitly checked (may be imported differently)")
    
    # Check test files
    print("\n📋 Test Files:")
    test_files = [
        'test_woocommerce.py',
        'test_woocommerce_tools.py',
        'test_chatbot_with_tools.py'
    ]
    
    for test_file in test_files:
        print(f"\n  Checking {test_file}...")
        if not check_file_exists(test_file):
            print(f"    ✗ File does not exist!")
            all_passed = False
            continue
        
        # Check for test classes
        classes = get_class_names(test_file)
        test_classes = [c for c in classes if c.startswith('Test')]
        if test_classes:
            print(f"    ✓ Found test classes: {', '.join(test_classes)}")
        else:
            print(f"    ⚠ No test classes found (may use functions)")
        
        # Check for test methods
        functions = get_function_names(test_file)
        test_methods = [f for f in functions if f.startswith('test_')]
        if test_methods:
            print(f"    ✓ Found {len(test_methods)} test methods")
        else:
            print(f"    ✗ No test methods found!")
            all_passed = False
    
    # Check supporting files were updated
    print("\n📝 Supporting Files:")
    supporting_checks = {
        'src/utils.py': {
            'functions': ['classify_intent'],
            'keywords': ['product_search']
        },
        'src/prompts.py': {
            'functions': ['get_system_prompt'],
            'keywords': ['search_products_tool', 'get_products_by_category_tool']
        }
    }
    
    for filepath, checks in supporting_checks.items():
        print(f"\n  Checking {filepath}...")
        if not check_file_exists(filepath):
            print(f"    ✗ File does not exist!")
            all_passed = False
            continue
        
        # Check functions
        functions = get_function_names(filepath)
        for expected_func in checks['functions']:
            if expected_func in functions:
                print(f"    ✓ Function '{expected_func}' found")
            else:
                print(f"    ✗ Function '{expected_func}' NOT found")
                all_passed = False
        
        # Check keywords (for tool instructions, etc.)
        found_keywords, missing_keywords = check_imports(filepath, checks['keywords'])
        for keyword in found_keywords:
            print(f"    ✓ Keyword '{keyword}' found")
        for keyword in missing_keywords:
            print(f"    ⚠ Keyword '{keyword}' not found (may need update)")
    
    # Summary
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ All critical checks passed!")
        print("\n📌 Next steps:")
        print("  1. Install dependencies: pip install httpx langchain-core")
        print("  2. Run tests: python3 -m unittest test_woocommerce.py")
        print("  3. Test integration with real API (optional)")
    else:
        print("⚠️  Some checks failed. Please review the output above.")
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())









