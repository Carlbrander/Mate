"""
Test script for the summary history feature.
This script demonstrates how to use the summary functions.

Run this script from the project root directory:
python -m context_retrieval.test_summary

Or set LEARNING_OBJECTIVE environment variable before running:
set LEARNING_OBJECTIVE=Learn Python data structures
python -m context_retrieval.test_summary
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from context_retrieval.insights_generation import (
    update_summary_history,
    get_current_summary,
    load_summary_history,
    save_summary_history
)


def test_summary_feature():
    """Test the summary history feature with sample data"""
    
    print("=" * 60)
    print("TESTING SUMMARY HISTORY FEATURE")
    print("=" * 60)
    
    # Sample learning objective
    learning_objective = "Learn Python data structures and algorithms"
    
    # Sample context from a screenshot (XML format)
    sample_context_1 = """
    <Tab>
        <Name>Python Lists Tutorial</Name>
        <URL>https://www.python.org/doc/lists</URL>
        <Context>Documentation page for Python lists</Context>
        <TextContent>
            Python Lists - A list is a collection which is ordered and changeable.
            Lists are written with square brackets.
            Example: fruits = ["apple", "banana", "cherry"]
        </TextContent>
    </Tab>
    """
    
    # Test 1: Create initial summary
    print("\n1. Creating initial summary...")
    summary = update_summary_history(learning_objective, sample_context_1)
    
    if summary:
        print("✓ Initial summary created successfully!")
        print(f"\nSummary:\n{summary}\n")
    else:
        print("✗ Failed to create initial summary")
        return
    
    # Test 2: Load existing summary
    print("\n2. Loading existing summary...")
    loaded_summary = load_summary_history()
    print(f"✓ Loaded summary ({len(loaded_summary)} characters)")
    
    # Sample context 2 - Different content
    sample_context_2 = """
    <Tab>
        <Name>Python Dictionaries</Name>
        <URL>https://www.python.org/doc/dictionaries</URL>
        <Context>Documentation page for Python dictionaries</Context>
        <TextContent>
            Python Dictionaries - A dictionary is a collection which is unordered, changeable and indexed.
            Dictionaries are written with curly brackets and have keys and values.
            Example: car = {"brand": "Ford", "model": "Mustang", "year": 1964}
        </TextContent>
    </Tab>
    """
    
    # Test 3: Update summary with new content
    print("\n3. Updating summary with new content...")
    updated_summary = update_summary_history(learning_objective, sample_context_2)
    
    if updated_summary:
        print("✓ Summary updated successfully!")
        print(f"\nUpdated Summary:\n{updated_summary}\n")
    else:
        print("✗ Failed to update summary")
        return
    
    # Test 4: Get current summary using convenience function
    print("\n4. Getting current summary...")
    current = get_current_summary()
    print(f"✓ Current summary retrieved ({len(current)} characters)")
    
    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETED")
    print("=" * 60)
    print(f"\nSummary file location: context_retrieval/summary_history.txt")


if __name__ == "__main__":
    test_summary_feature()

