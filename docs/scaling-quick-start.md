# Quick Start: Scaling Your Support Workflows

## 🎯 What You Can Do Now

You now have a **scalable architecture** to handle multiple support workflows:

✅ **Transaction Help** - Already implemented  
✅ **Refunds** - Ready to use  
✅ **Loans** - Ready to use  
✅ **Cards** - Ready to use  
✅ **General Enquiries** - Ready to use  
✅ **Add New Workflows** - Takes 10 minutes!

## 📋 Current Workflows

| Workflow | Intent Keywords | Status |
|----------|----------------|--------|
| Transaction Help | "help with transaction", "payment problem" | ✅ Active |
| Refunds | "refund", "money back", "return payment" | ✅ Ready |
| Loans | "loan", "borrow", "credit", "apply for loan" | ✅ Ready |
| Cards | "card", "card blocked", "card not working" | ✅ Ready |
| General | "help", "question", "enquiry" | ✅ Ready |

## 🚀 How to Add a New Workflow (3 Steps)

### Example: Adding "Insurance" Workflow

**Step 1:** Create `backend/agent/workflows/insurance.py`

```python
from .base import BaseWorkflow

class InsuranceWorkflow(BaseWorkflow):
    name = "insurance"
    intent_keywords = ["insurance", "claim", "coverage"]
    
    async def summarize(self, state, config):
        return {"policies": [...]}
    
    def get_summary_message(self, context):
        return "I can help with insurance. What do you need?"
    
    def get_question(self, context):
        return "What would you like to know?"
    
    def get_suggestions(self, context):
        return ["File claim", "Check coverage", "Premium payment"]
    
    def get_resolution_guide(self, issue_type, context):
        # Return guidance based on issue
        return {...}
```

**Step 2:** Register in `backend/agent/workflows/__init__.py`

```python
from .insurance import InsuranceWorkflow

# Add to priority_order and workflows list
```

**Step 3:** Done! 🎉

The workflow is now active and will automatically detect when users mention insurance.

## 📁 File Structure

```
backend/agent/workflows/
├── __init__.py          # Registry (auto-detects workflows)
├── base.py              # Base class (all workflows inherit)
├── transaction_help.py  # ✅ Transaction issues
├── refund.py            # ✅ Refund requests
├── loan_enquiry.py      # ✅ Loan questions
├── card_issue.py        # ✅ Card problems
└── general_enquiry.py   # ✅ General questions
```

## 🔄 Workflow Pattern

Every workflow follows this pattern:

```
1. IDENTIFY → User says "I need help with X"
2. SUMMARIZE → "Good news: your X is..."
3. ASK → "Tell us what's wrong"
4. SUGGEST → ["Issue 1", "Issue 2", "Issue 3"]
5. RESOLVE → "Here's what you can do: ..."
6. ESCALATE → Create ticket only if needed
```

## 💡 Key Benefits

1. **Scalable**: Add unlimited workflows
2. **Consistent**: All follow same pattern
3. **Maintainable**: Each workflow is isolated
4. **Fast**: Takes 10 minutes to add new workflow
5. **Flexible**: Customize each workflow as needed

## 📚 Documentation

- **SCALING_ARCHITECTURE.md** - Full architecture details
- **ADDING_NEW_WORKFLOW.md** - Detailed step-by-step guide
- **SCALING_IMPLEMENTATION.md** - Implementation summary

## 🎓 Example: Complete Workflow

See `backend/agent/workflows/refund.py` for a complete, well-structured example.

## ⚡ Quick Test

Test workflow detection:

```python
from backend.agent.workflows import detect_workflow

detect_workflow("I need help with my transaction")  # → "transaction_help"
detect_workflow("I want a refund")                  # → "refund"
detect_workflow("Apply for a loan")                  # → "loan_enquiry"
detect_workflow("My card is blocked")               # → "card_issue"
```

## 🔧 Next Steps

1. **Integrate workflows** with chat node (update `chat.py`)
2. **Test each workflow** with sample messages
3. **Add domain-specific tools** for each workflow
4. **Monitor workflow performance**

## 💬 Need Help?

- Check `ADDING_NEW_WORKFLOW.md` for detailed instructions
- Look at existing workflows for examples
- All workflows follow the same pattern - copy and modify!

---

**You're all set!** Start adding workflows and scale your support system. 🚀

