"use client";

import { useCopilotAction } from "@copilotkit/react-core";
import { useRef, useMemo } from "react";
import { BalanceCard } from "@/components/widgets/BalanceCard";
import { TransactionGrid } from "@/components/widgets/TransactionGrid";
import { TicketConfirmation } from "@/components/widgets/TicketConfirmation";
import { TicketCard } from "@/components/widgets/TicketCard";
import { Transaction } from "@/components/widgets/TransactionCard";
import { FinancialInsightsChart } from "@/components/widgets/FinancialInsightsChart";
import { CashFlowBarChart } from "@/components/widgets/CashFlowBarChart";
import { FinancialInsights, CashFlowOverview } from "@/types/schemas";

/**
 * Registers CopilotKit actions for rendering widgets inline in chat.
 * Uses useCopilotAction with render to display widgets when tools are called.
 * The render function receives the tool result directly.
 * 
 * Reference: https://docs.copilotkit.ai/langgraph/generative-ui/backend-tools
 */
export function RemittanceWidgets() {
  // Track active tool calls to prevent duplicate widgets
  // Use refs to track the latest call timestamp for each tool
  // This ensures retries with same args are treated as new calls
  const balanceCallRef = useRef<{ callId: string; timestamp: number } | null>(null);
  const transactionsCallRef = useRef<{ callId: string; timestamp: number } | null>(null);
  const ticketCallRef = useRef<{ callId: string; timestamp: number } | null>(null);
  const cashFlowCallRef = useRef<{ callId: string; timestamp: number } | null>(null);
  const insightsCallRefs = useRef<Map<string, { callId: string; timestamp: number }>>(new Map());
  const callCounterRef = useRef<number>(0);

  // Helper function to generate unique call ID from args and timestamp
  const getCallId = (toolName: string, args: any): { callId: string; timestamp: number } => {
    const argsKey = JSON.stringify(args || {});
    const timestamp = Date.now();
    const counter = callCounterRef.current++;
    // Include counter to ensure uniqueness even if called at same millisecond
    return {
      callId: `${toolName}-${argsKey}-${counter}`,
      timestamp
    };
  };

  // Register action for balance widget - name must match tool name
  useCopilotAction({
    name: "get_wallet_balance",
    description: "Get the current wallet balance for the user",
    parameters: [
      {
        name: "currency",
        type: "string",
        description: "The currency code (USD, EUR, GBP, ZWL)",
        required: false,
      },
      {
        name: "provider_code",
        type: "string",
        description: "The payment provider code",
        required: false,
      },
    ],
    render: ({ args, result, status }) => {
      const callInfo = getCallId("get_wallet_balance", args);
      const isLatestCall = !balanceCallRef.current || 
                          balanceCallRef.current.timestamp <= callInfo.timestamp;
      
      // Update ref to track this as the latest call (always update for new calls)
      if (isLatestCall) {
        balanceCallRef.current = callInfo;
      } else {
        // This is an old call, don't render to prevent duplicates
        return <></>;
      }

      // Show loading state while tool is executing
      if (status !== "complete") {
        return (
          <div key={callInfo.callId} className="bg-indigo-100 text-indigo-700 p-4 rounded-lg max-w-md">
            <span className="animate-pulse">⚙️ Retrieving balance...</span>
          </div>
        );
      }

      // Extract balance from the MCP tool result
      // The result can be:
      // 1. A number directly
      // 2. A JSON string that needs parsing
      // 3. An object with nested structure: {success: true, data: {balance: number, currency: string, ...}}
      let balance = 0;
      let currency = "USD";

      try {
        // If result is a string, try to parse it as JSON
        let parsedResult = result;
        if (typeof result === "string") {
          parsedResult = JSON.parse(result);
        }

        // If it's a number, use it directly
        if (typeof parsedResult === "number") {
          balance = parsedResult;
        }
        // If it's an object, extract from nested structure
        else if (typeof parsedResult === "object" && parsedResult !== null) {
          // Try different possible paths to the balance
          if (parsedResult.balance !== undefined) {
            balance = typeof parsedResult.balance === "number" ? parsedResult.balance : parseFloat(parsedResult.balance) || 0;
            currency = parsedResult.currency || parsedResult.data?.currency || "USD";
          } else if (parsedResult.data?.balance !== undefined) {
            balance = typeof parsedResult.data.balance === "number" ? parsedResult.data.balance : parseFloat(parsedResult.data.balance) || 0;
            currency = parsedResult.data.currency || parsedResult.currency || "USD";
          } else if (parsedResult.data?.data?.balance !== undefined) {
            // Handle double-nested data structure
            balance = typeof parsedResult.data.data.balance === "number" ? parsedResult.data.data.balance : parseFloat(parsedResult.data.data.balance) || 0;
            currency = parsedResult.data.data.currency || parsedResult.data.currency || parsedResult.currency || "USD";
          } else {
            // Fallback: try to parse as float if it's a string representation
            balance = parseFloat(parsedResult) || 0;
          }
        } else {
          // Fallback: try to parse as float
          balance = parseFloat(result) || 0;
        }
      } catch (e) {
        // If parsing fails, try to extract as number
        balance = typeof result === "number" ? result : parseFloat(result) || 0;
      }

      return (
        <BalanceCard
          key={callInfo.callId}
          accounts={[{
            id: "main",
            label: "Main Account",
            balance: {
              currency: currency,
              amount: balance,
            },
          }]}
        />
      );
    },
  });

  // Register action for transactions widget - name must match tool name
  useCopilotAction({
    name: "get_wallet_transaction_history",
    description: "List recent transactions for the user",
    parameters: [
      {
        name: "page",
        type: "number",
        description: "Page number",
        required: false,
      },
      {
        name: "pageSize",
        type: "number",
        description: "Number of transactions per page",
        required: false,
      },
      {
        name: "currency",
        type: "string",
        description: "Currency code",
        required: false,
      },
    ],
    render: ({ args, result, status }) => {
      const callInfo = getCallId("get_wallet_transaction_history", args);
      const isLatestCall = !transactionsCallRef.current || 
                          transactionsCallRef.current.timestamp <= callInfo.timestamp;
      
      // Update ref to track this as the latest call (always update for new calls)
      if (isLatestCall) {
        transactionsCallRef.current = callInfo;
      } else {
        // This is an old call, don't render to prevent duplicates
        return <></>;
      }

      // Show loading state while tool is executing
      if (status !== "complete") {
        return (
          <div key={callInfo.callId} className="bg-indigo-100 text-indigo-700 p-4 rounded-lg max-w-md">
            <span className="animate-pulse">⚙️ Loading transactions...</span>
          </div>
        );
      }

      // Extract transactions from the MCP tool result
      // The result can be:
      // 1. An array directly
      // 2. A JSON string that needs parsing
      // 3. An object with nested structure: {success: true, data: {transactions: [...], ...}}
      let transactions: Transaction[] = [];

      try {
        // Log the raw result first
        console.log('🔍 Raw result received:', result);
        console.log('🔍 Result type:', typeof result);
        
        // If result is a string, try to parse it as JSON
        let parsedResult = result;
        if (typeof result === "string") {
          try {
            parsedResult = JSON.parse(result);
            console.log('✅ Parsed JSON string:', parsedResult);
          } catch (parseError) {
            console.error('❌ Failed to parse JSON string:', parseError);
            // If it's not valid JSON, it might be a plain string representation
            // Try to extract JSON from the string
            const jsonMatch = result.match(/\{[\s\S]*\}/);
            if (jsonMatch) {
              try {
                parsedResult = JSON.parse(jsonMatch[0]);
                console.log('✅ Extracted and parsed JSON from string');
              } catch (e) {
                console.error('❌ Failed to extract JSON:', e);
              }
            }
          }
        }

        // Debug logging in development
        console.log('🔍 Transaction result structure:', {
          type: typeof parsedResult,
          isArray: Array.isArray(parsedResult),
          keys: typeof parsedResult === 'object' && parsedResult !== null ? Object.keys(parsedResult) : [],
          hasData: typeof parsedResult === 'object' && parsedResult !== null ? 'data' in parsedResult : false,
          hasTransactions: typeof parsedResult === 'object' && parsedResult !== null ? 'transactions' in parsedResult : false,
          dataKeys: typeof parsedResult === 'object' && parsedResult !== null && parsedResult.data ? Object.keys(parsedResult.data) : [],
          fullStructure: parsedResult,
        });

        // If it's already an array, use it directly
        if (Array.isArray(parsedResult)) {
          transactions = parsedResult;
        }
        // If it's an object, extract from nested structure
        else if (typeof parsedResult === "object" && parsedResult !== null) {
          // Try different possible paths to the transactions array
          if (Array.isArray(parsedResult.transactions)) {
            transactions = parsedResult.transactions;
          } else if (Array.isArray(parsedResult.data?.transactions)) {
            transactions = parsedResult.data.transactions;
          } else if (Array.isArray(parsedResult.data?.data?.transactions)) {
            // Handle double-nested data structure
            transactions = parsedResult.data.data.transactions;
          } else if (Array.isArray(parsedResult.data)) {
            // If data itself is an array
            transactions = parsedResult.data;
          } else if (parsedResult.data && typeof parsedResult.data === 'object') {
            // Check if data contains a list/array property
            // Prioritize 'transactions' key if it exists
            if (Array.isArray(parsedResult.data.transactions)) {
              transactions = parsedResult.data.transactions;
            } else {
              // Otherwise, find the first array property
              const dataKeys = Object.keys(parsedResult.data);
              for (const key of dataKeys) {
                if (Array.isArray(parsedResult.data[key])) {
                  transactions = parsedResult.data[key];
                  break;
                }
              }
            }
          }
        }
      } catch (e) {
        console.error('Error parsing transaction result:', e);
        // If parsing fails, try to use result as-is if it's an array
        transactions = Array.isArray(result) ? result : [];
      }

      // Debug logging for extracted transactions
      console.log('📊 Extracted transactions count:', transactions.length);
      if (transactions.length > 0) {
        console.log('📊 First transaction sample:', transactions[0]);
        console.log('📊 All transactions:', transactions);
      } else {
        console.warn('⚠️ No transactions extracted! Full result structure:', result);
        // Try one more time with a different approach - maybe the result itself is the transactions array wrapped
        if (typeof result === 'object' && result !== null) {
          console.log('🔍 Attempting alternative extraction...');
          // Check all top-level properties for arrays
          for (const key in result) {
            if (Array.isArray(result[key])) {
              console.log(`✅ Found array at key: ${key}`, result[key]);
              transactions = result[key];
              break;
            }
          }
        }
      }

      // Map API response format to Transaction interface format
      // The API might return transactions with different field names
      // Based on the API response, it includes: transactionId, date, payer, payee, amount, status
      transactions = transactions.map((tx: any) => {
        // Log the transaction structure for debugging (remove in production)
        if (process.env.NODE_ENV === 'development') {
          console.log('Raw transaction data:', tx);
        }

        // Extract transaction ID - handle various formats
        // API uses: transferId
        const transactionId = tx.transferId || tx.id || tx.transactionId || tx.transaction_id || tx.utr || tx.reference || String(Math.random());
        
        // Extract date - handle Unix timestamp (transferDate) or date strings
        // API uses: transferDate (Unix timestamp in seconds)
        let dateValue = null;
        if (tx.transferDate) {
          // Convert Unix timestamp (seconds) to ISO date string
          const date = new Date(tx.transferDate * 1000);
          if (!isNaN(date.getTime())) {
            dateValue = date.toISOString().split('T')[0]; // Format: YYYY-MM-DD
          }
        } else {
          // Fallback to other date fields
          dateValue = tx.date || tx.transactionDate || tx.createdAt || tx.timestamp || tx.time || tx.created_date;
          if (dateValue && typeof dateValue === 'string') {
            // Handle date strings like "2025-11-29" or "2025-11-29 15:02:00"
            if (dateValue.match(/^\d{4}-\d{2}-\d{2}/)) {
              // Valid date format, keep as is
            } else {
              // Try to parse other formats
              const parsed = new Date(dateValue);
              if (!isNaN(parsed.getTime())) {
                dateValue = parsed.toISOString().split('T')[0];
              }
            }
          }
        }
        
        // Extract merchant/payee - API uses: payeeName (for incoming) or payerName (for outgoing)
        // For debit (outgoing), show payeeName; for credit (incoming), show payerName
        const merchant = tx.payeeName || tx.payerName || 
                        tx.merchant || tx.merchantName || tx.merchant_name || 
                        tx.payee || tx.recipient || tx.payer || 
                        tx.serviceName || tx.description || "Transaction";
        
        // Extract description - use serviceName if available
        const description = tx.serviceName || tx.description || tx.remarks || tx.note || 
                          tx.purpose || tx.merchant || merchant;
        
        // Extract amount - API uses: actualAmount
        // For debit (outgoing), amount should be negative
        let amount = 0;
        if (tx.actualAmount !== undefined && tx.actualAmount !== null) {
          amount = typeof tx.actualAmount === "number" ? tx.actualAmount : parseFloat(tx.actualAmount) || 0;
          // If it's a debit (outgoing transaction), make it negative
          if (tx.actionType === 'debit' && amount > 0) {
            amount = -amount;
          }
        } else {
          // Fallback to other amount fields
          if (typeof tx.amount === "number") {
            amount = tx.amount;
          } else if (typeof tx.amount === "string") {
            // Remove currency symbols and parse (handle "$22.00", "22.00", "-$22.00", etc.)
            const cleaned = tx.amount.replace(/[^0-9.-]/g, '');
            amount = parseFloat(cleaned) || 0;
          } else {
            // Try other amount fields
            const amountValue = tx.amountValue || tx.amount_value || tx.value || tx.total;
            if (typeof amountValue === "number") {
              amount = amountValue;
            } else if (typeof amountValue === "string") {
              const cleaned = amountValue.replace(/[^0-9.-]/g, '');
              amount = parseFloat(cleaned) || 0;
            }
          }
        }
        
        // Extract currency - API uses: currency
        const currency = tx.currency || tx.currencyCode || tx.currency_code || "USD";

        return {
          id: transactionId,
          date: dateValue,
          merchant: merchant,
          description: description,
          amount: amount,
          currency: currency,
        };
      });

      const handleSupportClick = (transaction: Transaction) => {
        const displayName = transaction.merchant || transaction.description || "Transaction";
        const dateStr = transaction.date ? new Date(transaction.date).toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" }) : "";
        const amount = transaction.amount ? Math.abs(transaction.amount).toLocaleString("en-US", { style: "currency", currency: transaction.currency || "USD" }) : "";
        // Send a message that asks for help, not immediately create ticket
        // This triggers the guided support flow
        const message = `I need help with my transaction to ${displayName}${dateStr ? ` on ${dateStr}` : ""}${amount ? ` for ${amount}` : ""}.`;

        // Properly trigger React's onChange to enable send button
        const sendMessage = () => {
          // Try multiple selectors for chat input
          const selectors = [
            'textarea[placeholder*="message" i]',
            'textarea[placeholder*="type" i]',
            'textarea[data-testid*="input"]',
            'textarea',
            'input[type="text"]'
          ];

          let chatInput: HTMLTextAreaElement | HTMLInputElement | null = null;
          for (const selector of selectors) {
            chatInput = document.querySelector(selector) as HTMLTextAreaElement | HTMLInputElement;
            if (chatInput) break;
          }

          if (!chatInput) {
            console.warn('Could not find chat input');
            return;
          }

          // Focus first
          chatInput.focus();

          // Set value directly
          chatInput.value = message;

          // Create React-compatible input event
          // Use InputEvent if available, otherwise fallback to Event
          let inputEvent: Event;
          try {
            inputEvent = new InputEvent('input', {
              bubbles: true,
              cancelable: true,
              data: message,
              inputType: 'insertText'
            });
          } catch (e) {
            // Fallback for browsers that don't support InputEvent constructor
            inputEvent = new Event('input', { bubbles: true, cancelable: true });
          }
          chatInput.dispatchEvent(inputEvent);

          // Also trigger change event
          const changeEvent = new Event('change', { bubbles: true, cancelable: true });
          chatInput.dispatchEvent(changeEvent);

          // Try to access React's internal handlers
          const reactFiber = (chatInput as any).__reactInternalInstance ||
            (chatInput as any).__reactFiber$ ||
            (chatInput as any)._reactInternalFiber;

          if (reactFiber) {
            const props = reactFiber.memoizedProps || reactFiber.currentProps;
            if (props?.onChange) {
              props.onChange({
                target: chatInput,
                currentTarget: chatInput,
                bubbles: true,
                cancelable: true,
              });
            }
          }

          // Wait a bit for React to process, then find and enable/click send button
          setTimeout(() => {
            const form = chatInput.closest('form');
            let sendButton: HTMLButtonElement | null = null;

            // Find send button with multiple strategies
            if (form) {
              // Strategy 1: Standard submit button
              sendButton = form.querySelector('button[type="submit"]') as HTMLButtonElement;

              // Strategy 2: Button near the input
              if (!sendButton) {
                const buttons = form.querySelectorAll('button');
                for (const btn of Array.from(buttons)) {
                  const btnEl = btn as HTMLButtonElement;
                  if (btnEl.offsetParent !== null) {
                    sendButton = btnEl;
                    break;
                  }
                }
              }
            }

            // Strategy 3: Find by aria-label or data attributes
            if (!sendButton) {
              sendButton = document.querySelector(
                'button[aria-label*="send" i], button[aria-label*="submit" i], button[data-testid*="send"], button[data-testid*="submit"]'
              ) as HTMLButtonElement;
            }

            if (sendButton) {
              // If button is disabled, try to enable it by removing disabled attribute
              // This might work if CopilotKit just uses disabled attribute
              if (sendButton.disabled) {
                sendButton.removeAttribute('disabled');
                sendButton.disabled = false;
              }

              // Click the button if it's now enabled
              if (!sendButton.disabled) {
                sendButton.click();
                return;
              }
            }

            // Fallback: Try Enter key
            const enterEvent = new KeyboardEvent('keydown', {
              key: 'Enter',
              code: 'Enter',
              keyCode: 13,
              which: 13,
              bubbles: true,
              cancelable: true,
            });
            chatInput.dispatchEvent(enterEvent);

            // Also try form submit as last resort
            if (form) {
              const submitEvent = new Event('submit', { bubbles: true, cancelable: true });
              form.dispatchEvent(submitEvent);
            }
          }, 150);
        };

        // Small delay to ensure DOM is ready
        setTimeout(sendMessage, 50);
      };

      return <TransactionGrid key={callInfo.callId} transactions={transactions} onSupportClick={handleSupportClick} />;
    },
  });

  // Register action for ticket confirmation (human-in-the-loop)
  useCopilotAction({
    name: "create_ticket",
    description: "Create a support ticket for the user",
    parameters: [
      {
        name: "user_id",
        type: "string",
        description: "The user ID",
        required: true,
      },
      {
        name: "subject",
        type: "string",
        description: "The ticket subject - a clear summary of the issue extracted from the user's message",
        required: true,
      },
      {
        name: "body",
        type: "string",
        description: "The ticket description - detailed information about the problem extracted from the user's message",
        required: true,
      },
    ],
    renderAndWait: ({ args, status, handler }) => {
      // Extract subject and body from args (tool call arguments)
      const subject = args?.subject || "Support Request";
      const body = args?.body || "User requested assistance with a transaction.";

      return (
        <TicketConfirmation
          issue={subject}
          description={body}
          status={status}
          handler={handler}
        />
      );
    },
  });

  // Register action for create_support_ticket (MCP tool) - displays ticket after creation
  useCopilotAction({
    name: "create_support_ticket",
    description: "Create a support ticket and display the created ticket details",
    parameters: [
      {
        name: "name",
        type: "string",
        description: "Name of the user creating the ticket",
        required: true,
      },
      {
        name: "phone",
        type: "string",
        description: "Phone number of the user",
        required: true,
      },
      {
        name: "subject",
        type: "string",
        description: "Subject/title of the ticket",
        required: true,
      },
      {
        name: "type",
        type: "string",
        description: "Type of ticket",
        required: false,
      },
      {
        name: "description",
        type: "string",
        description: "Detailed description of the issue",
        required: false,
      },
    ],
    render: ({ args, result, status }) => {
      const callInfo = getCallId("create_support_ticket", args);
      const isLatestCall = !ticketCallRef.current || 
                          ticketCallRef.current.timestamp <= callInfo.timestamp;
      
      // Update ref to track this as the latest call (always update for new calls)
      if (isLatestCall) {
        ticketCallRef.current = callInfo;
      } else {
        // This is an old call, don't render to prevent duplicates
        return <></>;
      }

      // Show loading state while tool is executing
      if (status !== "complete") {
        return (
          <div key={callInfo.callId} className="bg-indigo-100 text-indigo-700 p-4 rounded-lg max-w-md">
            <span className="animate-pulse">⚙️ Creating support ticket...</span>
          </div>
        );
      }

      // Extract ticket data from the MCP tool result
      // The result structure: {success: true, data: {...ticket data...}}
      let ticketData = null;

      // Debug logging
      console.log('🎫 Ticket creation result:', result);
      console.log('🎫 Result type:', typeof result);

      try {
        // If result is a string, try to parse it as JSON
        let parsedResult = result;
        if (typeof result === "string") {
          try {
            parsedResult = JSON.parse(result);
            console.log('🎫 Parsed JSON result:', parsedResult);
          } catch (parseError) {
            console.error('🎫 Failed to parse JSON:', parseError);
          }
        }

        console.log('🎫 Parsed result structure:', {
          type: typeof parsedResult,
          keys: typeof parsedResult === 'object' && parsedResult !== null ? Object.keys(parsedResult) : [],
          hasData: typeof parsedResult === 'object' && parsedResult !== null ? 'data' in parsedResult : false,
          dataKeys: typeof parsedResult === 'object' && parsedResult !== null && parsedResult.data ? Object.keys(parsedResult.data) : [],
        });

        // Extract ticket from nested structure
        if (typeof parsedResult === "object" && parsedResult !== null) {
          // Try different possible paths to the ticket data
          if (parsedResult.ticket) {
            ticketData = parsedResult.ticket;
            console.log('🎫 Found ticket at result.ticket');
          } else if (parsedResult.data?.ticket) {
            ticketData = parsedResult.data.ticket;
            console.log('🎫 Found ticket at result.data.ticket');
          } else if (parsedResult.data && typeof parsedResult.data === 'object') {
            // If data itself contains ticket fields, use it directly
            if (parsedResult.data.id || parsedResult.data.ticketId || parsedResult.data.subject || parsedResult.data.ticketId) {
              ticketData = parsedResult.data;
              console.log('🎫 Found ticket at result.data');
            }
          } else if (parsedResult.id || parsedResult.ticketId || parsedResult.subject) {
            // Result itself is the ticket
            ticketData = parsedResult;
            console.log('🎫 Result itself is the ticket');
          }
        }

        // If no ticket data found, create a ticket object from the args and result
        if (!ticketData) {
          ticketData = {
            subject: args?.subject || "Support Ticket",
            description: args?.description || "",
            type: args?.type || "General Enquiry",
            name: args?.name || "",
            phone: args?.phone || "",
            status: parsedResult?.success ? "created" : "pending",
            // Try to extract ticket ID from result
            id: parsedResult?.data?.id || 
                parsedResult?.data?.ticketId || 
                parsedResult?.data?.ticket_id ||
                parsedResult?.ticketId ||
                parsedResult?.id ||
                "Pending"
          };
        }
      } catch (e) {
        console.error('Error parsing ticket result:', e);
        // Fallback: create ticket from args
        ticketData = {
          subject: args?.subject || "Support Ticket",
          description: args?.description || "",
          type: args?.type || "General Enquiry",
          status: "created"
        };
      }

      return <TicketCard key={callInfo.callId} ticket={ticketData} />;
    },
  });

  // Register action for cash flow overview widget (bar chart)
  useCopilotAction({
    name: "get_cash_flow_overview",
    description: "Get overall cash flow overview with incoming, investment, and spends totals",
    parameters: [
      {
        name: "user_id",
        type: "string",
        description: "The user ID",
        required: true,
      },
      {
        name: "account",
        type: "string",
        description: "Account filter (e.g., 'all accounts')",
        required: false,
      },
      {
        name: "start_date",
        type: "string",
        description: "Start date for the period (YYYY-MM-DD)",
        required: false,
      },
      {
        name: "end_date",
        type: "string",
        description: "End date for the period (YYYY-MM-DD)",
        required: false,
      },
    ],
    render: ({ args, result, status }) => {
      const callInfo = getCallId("get_cash_flow_overview", args);
      const isLatestCall = !cashFlowCallRef.current || 
                          cashFlowCallRef.current.timestamp <= callInfo.timestamp;
      
      // Update ref to track this as the latest call (always update for new calls)
      if (isLatestCall) {
        cashFlowCallRef.current = callInfo;
      } else {
        // This is an old call, don't render to prevent duplicates
        return <></>;
      }

      if (status !== "complete") {
        return (
          <div key={callInfo.callId} className="bg-indigo-100 text-indigo-700 p-4 rounded-lg max-w-md">
            <span className="animate-pulse">⚙️ Loading cash flow overview...</span>
          </div>
        );
      }

      const overview = result as CashFlowOverview;
      return <CashFlowBarChart key={callInfo.callId} overview={overview} />;
    },
  });

  // Register action for incoming insights widget
  useCopilotAction({
    name: "get_incoming_insights",
    description: "Get financial insights for incoming transactions",
    parameters: [
      {
        name: "user_id",
        type: "string",
        description: "The user ID",
        required: true,
      },
      {
        name: "account",
        type: "string",
        description: "Account filter (e.g., 'all accounts')",
        required: false,
      },
      {
        name: "start_date",
        type: "string",
        description: "Start date for the period (YYYY-MM-DD)",
        required: false,
      },
      {
        name: "end_date",
        type: "string",
        description: "End date for the period (YYYY-MM-DD)",
        required: false,
      },
    ],
    render: ({ args, result, status }) => {
      const callInfo = getCallId("get_incoming_insights", args);
      const currentCall = insightsCallRefs.current.get("get_incoming_insights");
      const isLatestCall = !currentCall || currentCall.timestamp <= callInfo.timestamp;
      
      // Update ref to track this as the latest call (always update for new calls)
      if (isLatestCall) {
        insightsCallRefs.current.set("get_incoming_insights", callInfo);
      } else {
        // This is an old call, don't render to prevent duplicates
        return <></>;
      }

      if (status !== "complete") {
        return (
          <div key={callInfo.callId} className="bg-indigo-100 text-indigo-700 p-4 rounded-lg max-w-md">
            <span className="animate-pulse">⚙️ Analyzing incoming transactions...</span>
          </div>
        );
      }

      const insights = result as FinancialInsights;
      return <FinancialInsightsChart key={callInfo.callId} insights={insights} />;
    },
  });

  // Register action for investment insights widget
  useCopilotAction({
    name: "get_investment_insights",
    description: "Get financial insights for investment transactions",
    parameters: [
      {
        name: "user_id",
        type: "string",
        description: "The user ID",
        required: true,
      },
      {
        name: "account",
        type: "string",
        description: "Account filter (e.g., 'all accounts')",
        required: false,
      },
      {
        name: "start_date",
        type: "string",
        description: "Start date for the period (YYYY-MM-DD)",
        required: false,
      },
      {
        name: "end_date",
        type: "string",
        description: "End date for the period (YYYY-MM-DD)",
        required: false,
      },
    ],
    render: ({ args, result, status }) => {
      const callInfo = getCallId("get_investment_insights", args);
      const currentCall = insightsCallRefs.current.get("get_investment_insights");
      const isLatestCall = !currentCall || currentCall.timestamp <= callInfo.timestamp;
      
      // Update ref to track this as the latest call (always update for new calls)
      if (isLatestCall) {
        insightsCallRefs.current.set("get_investment_insights", callInfo);
      } else {
        // This is an old call, don't render to prevent duplicates
        return <></>;
      }

      if (status !== "complete") {
        return (
          <div key={callInfo.callId} className="bg-indigo-100 text-indigo-700 p-4 rounded-lg max-w-md">
            <span className="animate-pulse">⚙️ Analyzing investments...</span>
          </div>
        );
      }

      const insights = result as FinancialInsights;
      return <FinancialInsightsChart key={callInfo.callId} insights={insights} />;
    },
  });

  // Register action for spends insights widget
  useCopilotAction({
    name: "get_spends_insights",
    description: "Get financial insights for spending transactions",
    parameters: [
      {
        name: "user_id",
        type: "string",
        description: "The user ID",
        required: true,
      },
      {
        name: "account",
        type: "string",
        description: "Account filter (e.g., 'all accounts')",
        required: false,
      },
      {
        name: "start_date",
        type: "string",
        description: "Start date for the period (YYYY-MM-DD)",
        required: false,
      },
      {
        name: "end_date",
        type: "string",
        description: "End date for the period (YYYY-MM-DD)",
        required: false,
      },
    ],
    render: ({ args, result, status }) => {
      const callInfo = getCallId("get_spends_insights", args);
      const currentCall = insightsCallRefs.current.get("get_spends_insights");
      const isLatestCall = !currentCall || currentCall.timestamp <= callInfo.timestamp;
      
      // Update ref to track this as the latest call (always update for new calls)
      if (isLatestCall) {
        insightsCallRefs.current.set("get_spends_insights", callInfo);
      } else {
        // This is an old call, don't render to prevent duplicates
        return <></>;
      }

      if (status !== "complete") {
        return (
          <div key={callInfo.callId} className="bg-indigo-100 text-indigo-700 p-4 rounded-lg max-w-md">
            <span className="animate-pulse">⚙️ Analyzing spending patterns...</span>
          </div>
        );
      }

      const insights = result as FinancialInsights;
      return <FinancialInsightsChart key={callInfo.callId} insights={insights} />;
    },
  });

  return null;
}
