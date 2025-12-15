# How Ecocash Assistant Works: A Simple Guide

This document explains how the Ecocash Assistant "thinks" and processes your requests. We use a technology called **LangGraph** to organize the AI's logic, similar to a flowchart or a company's organizational chart.

## The Analogy: A Bank Branch

Imagine the Ecocash Assistant as a physical bank branch.

1.  **Nodes (The Staff)**: Each "Node" is like a specific person or department in the bank. They have a specific job (e.g., the Greeter, the Teller, the Loan Officer).
2.  **Edges (The Hallways)**: "Edges" are the paths between these people. They define where you go next based on what just happened (e.g., "If you need a loan, go to the Loan Officer").
3.  **State (The Clipboard)**: As you move through the bank, you carry a clipboard with your conversation history and current details. Every staff member reads from and adds to this clipboard.

---

## The Main Workflow (The Lobby)

When you send a message, it enters the "Main Graph". Here is the flow:

```mermaid
graph TD
    Start([User Message]) --> DetectIntent[Detect Intent Node\n(The Receptionist)]
    
    DetectIntent -- "Need Help with Transaction" --> TransactionHelp[Transaction Help Subgraph\n(Specialist Dept)]
    DetectIntent -- "Want Financial Insights" --> FinancialInsights[Financial Insights Subgraph\n(Specialist Dept)]
    DetectIntent -- "Request Refund" --> Refund[Refund Subgraph\n(Specialist Dept)]
    DetectIntent -- "General Chat" --> ChatNode[Chat Node\n(General Banker)]
    
    TransactionHelp --> ChatNode
    FinancialInsights --> ChatNode
    Refund --> ChatNode
    
    ChatNode -- "Needs Tool (e.g. Balance)" --> Tools[Ecocash Tools\n(The Computer System)]
    ChatNode -- "Create Ticket" --> TicketConfirm[Ticket Confirmation\n(Manager Approval)]
    
    Tools --> ChatNode
    TicketConfirm -- "Confirmed" --> PerformTicket[Create Ticket]
    TicketConfirm -- "Cancelled" --> ChatNode
    PerformTicket --> ChatNode
    
    ChatNode --> End([Reply to User])
```

### 1. The Receptionist (`detect_intent`)
**Job**: When you first speak, the "Receptionist" listens to decide where you should go.
- If you say "Hi", they send you to the **General Banker** (`chat_node`).
- If you say "I have an issue with a transaction", they send you to the **Transaction Specialist** (`transaction_help` subgraph).

### 2. The Specialist Departments (Subgraphs)
**Job**: These are specialized workflows for complex tasks. They collect specific information before sending you back to the General Banker.
- **Transaction Help**: Asks for Transaction ID, Date, etc.
- **Financial Insights**: Asks what kind of analysis you want.
- **Refunds**: Collects details needed for a refund request.

*Think of a Subgraph as a mini-flowchart inside the main flowchart.*

### 3. The General Banker (`chat_node`)
**Job**: This is the main AI brain. It talks to you, answers questions, and decides if it needs to use "Tools".
- It reads the notes from the Specialists.
- It can check your balance or look up history using the **Tools**.

### 4. The Computer System (`ecocash_tools`)
**Job**: These are the actual functions that fetch data.
- `get_wallet_balance`: Checks your account balance.
- `get_wallet_transaction_history`: Pulls your statement.
- These tools run on a separate "Server" (MCP Server) to keep things secure and modular.

### 5. Manager Approval (`ticket_confirmation`)
**Job**: Before doing something serious like creating a support ticket, the system pauses and asks for your confirmation.
- **Human-in-the-loop**: The AI stops and waits for you to click "Confirm" or "Cancel". It won't proceed until you do.

---

## Example: "I need help with a transaction"

Let's trace a user request through the graph:

1.  **User**: "I need help with a transaction."
2.  **Receptionist (`detect_intent`)**: "Ah, a transaction issue! Go to the Transaction Help department."
3.  **Transaction Specialist (`transaction_help`)**: 
    - *Checks clipboard*: "Do I know which transaction?" -> No.
    - *Action*: Asks user "Which transaction are you referring to?"
4.  **User**: "The one to Coffee Shop yesterday."
5.  **Transaction Specialist**:
    - *Update clipboard*: Transaction = Coffee Shop.
    - *Action*: "Okay, I have the details. Sending you to the General Banker."
6.  **General Banker (`chat_node`)**:
    - *Reads clipboard*: User has issue with Coffee Shop transaction.
    - *Action*: Calls Tool `get_transaction_details` to see what happened.
7.  **Tools**: Returns "Transaction successful, $5.00".
8.  **General Banker**: "I see the transaction was successful. What seems to be the problem?"

---

## Key Concepts Summary

| Concept | Analogy | In Code (`graph.py`) |
| :--- | :--- | :--- |
| **Graph** | The entire Bank building | `StateGraph(AgentState)` |
| **Node** | A staff member or department | `graph_builder.add_node("chat_node", ...)` |
| **Edge** | Hallway/Direction | `graph_builder.add_edge(...)` |
| **Conditional Edge** | A decision point (e.g., "If X, go Left; if Y, go Right") | `graph_builder.add_conditional_edges(...)` |
| **Subgraph** | A specialized department with its own internal process | `build_transaction_help_subgraph()` |
| **MCP Tools** | The bank's computer/database | `get_wallet_balance`, `create_ticket` |
