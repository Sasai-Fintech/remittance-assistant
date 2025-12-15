#!/usr/bin/env python3
"""
Test script for LangGraph subgraphs.

This script tests each subgraph independently to catch missing keys, import errors,
and basic functionality issues before integration.

Usage:
    poetry run python backend/test_subgraphs.py
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from langchain_core.messages import HumanMessage
from engine.state import AgentState

# Import subgraph builders
from agent.workflows.subgraphs.transaction_help_graph import build_transaction_help_subgraph
from agent.workflows.subgraphs.refund_graph import build_refund_subgraph
from agent.workflows.subgraphs.loan_enquiry_graph import build_loan_enquiry_graph
from agent.workflows.subgraphs.card_issue_graph import build_card_issue_subgraph
from agent.workflows.subgraphs.general_enquiry_graph import build_general_enquiry_subgraph


async def test_subgraph(subgraph_name, build_func, test_message):
    """Test a subgraph with mock state."""
    print(f"\n{'='*60}")
    print(f"Testing {subgraph_name} subgraph")
    print(f"{'='*60}")
    
    try:
        # Build subgraph
        graph = build_func()
        print(f"✓ Subgraph compiled successfully")
        
        # Create mock state
        initial_state: AgentState = {
            "messages": [HumanMessage(content=test_message)],
            "user_id": "demo_user",
            "current_workflow": None,
            "workflow_step": None,
        }
        
        print(f"✓ Initial state created")
        print(f"  - Messages: {len(initial_state['messages'])}")
        print(f"  - User ID: {initial_state['user_id']}")
        
        # Invoke subgraph
        result = await graph.ainvoke(initial_state)
        
        print(f"✓ Subgraph executed successfully")
        print(f"  - Result messages: {len(result.get('messages', []))}")
        print(f"  - Current workflow: {result.get('current_workflow')}")
        print(f"  - Workflow step: {result.get('workflow_step')}")
        
        # Check state updates
        if result.get('workflow_step') == 'completed':
            print(f"✓ Workflow step marked as completed")
        else:
            print(f"⚠ Warning: workflow_step is '{result.get('workflow_step')}', expected 'completed'")
        
        if result.get('current_workflow') is None:
            print(f"✓ Current workflow cleared (allows new intent detection)")
        else:
            print(f"⚠ Warning: current_workflow is '{result.get('current_workflow')}', expected None")
        
        # Check for context
        context_keys = [k for k in result.keys() if k.endswith('_context')]
        if context_keys:
            print(f"✓ Context fields set: {', '.join(context_keys)}")
        else:
            print(f"⚠ Warning: No context fields found")
        
        # Check messages
        ai_messages = [msg for msg in result.get('messages', []) if msg.__class__.__name__ == 'AIMessage']
        if ai_messages:
            last_msg = ai_messages[-1]
            print(f"✓ Summary message created: {str(last_msg.content)[:100]}...")
        else:
            print(f"⚠ Warning: No AI messages found")
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing {subgraph_name}: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all subgraph tests."""
    print("LangGraph Subgraph Test Suite")
    print("=" * 60)
    
    tests = [
        ("transaction_help", build_transaction_help_subgraph, "I need help with my transaction to Coffee Shop"),
        ("refund", build_refund_subgraph, "I need a refund"),
        ("loan_enquiry", build_loan_enquiry_graph, "I want to apply for a loan"),
        ("card_issue", build_card_issue_subgraph, "My card is not working"),
        ("general_enquiry", build_general_enquiry_subgraph, "I have a question"),
    ]
    
    results = []
    for name, build_func, message in tests:
        success = await test_subgraph(name, build_func, message)
        results.append((name, success))
    
    # Summary
    print(f"\n{'='*60}")
    print("Test Summary")
    print(f"{'='*60}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

