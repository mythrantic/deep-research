#!/usr/bin/env python3
"""
Verification script to test the deep-research backend implementation.
This script verifies that all components are properly implemented and can be imported.
"""

import sys
import asyncio
from typing import List, Dict, Any


def verify_imports():
    """Verify all modules can be imported."""
    print("🔍 Verifying imports...")
    
    try:
        # Core module
        from deep_research import Researcher
        print("  ✓ Researcher imported")
        
        # Internal modules
        from deep_research.planner import ResearchPlanner
        print("  ✓ ResearchPlanner imported")
        
        from deep_research.task_splitter import TaskSplitter
        print("  ✓ TaskSplitter imported")
        
        from deep_research.coordinator import SubAgent, CoordinatorAgent, run_deep_research
        print("  ✓ Coordinator components imported")
        
        from deep_research.report_generator import ReportGenerator, generate_custom_report
        print("  ✓ Report generator imported")
        
        from deep_research import prompts
        print("  ✓ Prompts module imported")
        
        print("✅ All imports successful!\n")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}\n")
        return False


def verify_researcher_interface():
    """Verify Researcher has all required methods."""
    print("🔍 Verifying Researcher interface...")
    
    from deep_research import Researcher
    
    required_methods = [
        ('conduct_research', True),  # async
        ('get_research_context', False),
        ('get_research_sources', False),
        ('get_source_urls', False),
        ('quick_search', True),  # async
        ('write_report', True),  # async
        ('get_costs', False),
    ]
    
    all_present = True
    for method_name, is_async in required_methods:
        if hasattr(Researcher, method_name):
            method = getattr(Researcher, method_name)
            if is_async:
                if asyncio.iscoroutinefunction(method):
                    print(f"  ✓ async {method_name}() exists")
                else:
                    print(f"  ⚠️  {method_name}() exists but is not async")
                    all_present = False
            else:
                print(f"  ✓ {method_name}() exists")
        else:
            print(f"  ❌ {method_name}() missing")
            all_present = False
    
    if all_present:
        print("✅ All required methods present!\n")
    else:
        print("❌ Some methods missing or incorrect!\n")
    
    return all_present


def verify_no_todos():
    """Check for any TODO comments in the code."""
    print("🔍 Checking for TODOs...")
    
    import os
    import re
    
    src_dir = os.path.join(os.path.dirname(__file__), '../src/deep_research')
    todo_pattern = re.compile(r'#\s*TODO', re.IGNORECASE)
    
    todos_found = []
    for root, dirs, files in os.walk(src_dir):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r') as f:
                    for line_num, line in enumerate(f, 1):
                        if todo_pattern.search(line):
                            todos_found.append((filepath, line_num, line.strip()))
    
    if todos_found:
        print(f"❌ Found {len(todos_found)} TODO(s):")
        for filepath, line_num, line in todos_found:
            print(f"  {filepath}:{line_num} - {line}")
        print()
        return False
    else:
        print("✅ No TODOs found!\n")
        return True


async def test_basic_instantiation():
    """Test basic instantiation of Researcher."""
    print("🔍 Testing basic instantiation...")
    
    try:
        from deep_research import Researcher
        
        researcher = Researcher("test query")
        
        # Check initial state
        assert researcher.query == "test query"
        assert researcher.get_research_context() == ""
        assert researcher.get_research_sources() == []
        assert researcher.get_source_urls() == []
        assert researcher.get_costs() == {"total_cost": 0.0}
        
        print("✅ Basic instantiation works!\n")
        return True
    except Exception as e:
        print(f"❌ Instantiation failed: {e}\n")
        return False


def verify_structure():
    """Verify directory structure."""
    print("🔍 Verifying directory structure...")
    
    import os
    
    base_dir = os.path.join(os.path.dirname(__file__), '../src/deep_research')
    
    required_files = [
        '__init__.py',
        'researcher.py',
        'coordinator.py',
        'planner.py',
        'task_splitter.py',
        'prompts.py',
        'report_generator.py',
        'utils.py',
    ]
    
    all_present = True
    for filename in required_files:
        filepath = os.path.join(base_dir, filename)
        if os.path.exists(filepath):
            print(f"  ✓ {filename}")
        else:
            print(f"  ❌ {filename} missing")
            all_present = False
    
    if all_present:
        print("✅ All required files present!\n")
    else:
        print("❌ Some files missing!\n")
    
    return all_present


async def main():
    """Run all verification tests."""
    print("=" * 60)
    print("Deep Research Backend Verification")
    print("=" * 60)
    print()
    
    results = []
    
    # Run synchronous tests
    results.append(("Directory Structure", verify_structure()))
    results.append(("Imports", verify_imports()))
    results.append(("Researcher Interface", verify_researcher_interface()))
    results.append(("No TODOs", verify_no_todos()))
    
    # Run async tests
    results.append(("Basic Instantiation", await test_basic_instantiation()))
    
    # Summary
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
        if not passed:
            all_passed = False
    
    print()
    if all_passed:
        print("🎉 All verification tests passed!")
        print("The deep-research backend is ready to use!")
        return 0
    else:
        print("⚠️  Some verification tests failed.")
        print("Please review the errors above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
