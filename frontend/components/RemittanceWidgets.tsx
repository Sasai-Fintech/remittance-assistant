"use client";

import { useCopilotAction } from "@copilotkit/react-core";
import { useRef } from "react";
import { CountrySelector } from "@/components/widgets/CountrySelector";
import { ExchangeRateCard } from "@/components/widgets/ExchangeRateCard";
import { TicketConfirmation } from "@/components/widgets/TicketConfirmation";
import { TicketCard } from "@/components/widgets/TicketCard";
import { RecipientListCard } from "@/components/widgets/RecipientListCard";
import { QuoteCard } from "@/components/widgets/QuoteCard";
import { TransactionReceipt } from "@/components/widgets/TransactionReceipt";
import { BalanceCard } from "@/components/widgets/BalanceCard";
import { TransactionGrid } from "@/components/widgets/TransactionGrid";
import type { Transaction } from "@/components/widgets/TransactionCard";

/**
 * Registers CopilotKit actions for rendering re    name: "execute_remittance_transaction",
    description: "Execute the remittance transaction and send money to the recipient",
    parameters: [],
    render: ({ result, status, callInfo }: any) => {
      if (status !== "complete" || !result) {
        return <></>;
      }

      // Generate unique key for this widget
      const widgetKey = callInfo?.callId || `transaction-${Date.now()}`;idgets inline in chat.
 * Uses useCopilotAction with render to display widgets when tools are called.
 * The render function receives the tool result directly.
 * 
 * Reference: https://docs.copilotkit.ai/langgraph/generative-ui/backend-tools
 */
export function RemittanceWidgets() {
  const callCounterRef = useRef<number>(0);
  const transactionsCallRef = useRef<{ callId: string; timestamp: number } | null>(null);

  // Helper function to generate unique call ID from args and timestamp
  const getCallId = (toolName: string, args: any): { callId: string; timestamp: number } => {
    const argsKey = JSON.stringify(args || {});
    const timestamp = Date.now();
    const counter = callCounterRef.current++;
    return {
      callId: `${toolName}-${argsKey}-${counter}`,
      timestamp
    };
  };

  // Register action for receiving countries widget
  useCopilotAction({
    name: "get_receiving_countries",
    description: "Get list of countries where money can be sent from South Africa",
    parameters: [],
    render: ({ result, status }) => {
      const callInfo = getCallId("get_receiving_countries", {});

      // Show loading state while tool is executing
      if (status !== "complete") {
        return (
          <div key={callInfo.callId} className="bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 p-4 rounded-lg max-w-md">
            <span className="animate-pulse">⚙️ Loading countries...</span>
          </div>
        );
      }

      try {
        // Parse result if it's a string
        let parsedResult = result;
        if (typeof result === "string") {
          parsedResult = JSON.parse(result);
        }

        // Extract countries from nested structure
        const countries = parsedResult?.data?.receivingCountries || parsedResult?.receivingCountries || [];

        if (!countries || countries.length === 0) {
          return (
            <div key={callInfo.callId} className="bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-300 p-4 rounded-lg max-w-md">
              ⚠️ No destination countries available at the moment.
            </div>
          );
        }

        // Handler for when user selects a country
        const handleCountrySelect = (countryCode: string, currencyCode: string, countryName: string) => {
          // TODO: Trigger exchange rate lookup automatically
          // For now, user will need to type the request manually
          console.log(`Selected country: ${countryName} (${countryCode}) in ${currencyCode}`);
        };

        return (
          <div key={callInfo.callId} className="my-4">
            <CountrySelector 
              countries={countries} 
              onSelect={handleCountrySelect}
            />
          </div>
        );
      } catch (error) {
        console.error("[RemittanceWidgets] Error rendering country selector:", error);
        return (
          <div key={callInfo.callId} className="bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-300 p-4 rounded-lg max-w-md">
            ⚠️ Error loading countries. Please try again.
          </div>
        );
      }
    },
  });

  // Register action for exchange rate widget
  useCopilotAction({
    name: "get_exchange_rate",
    description: "Get exchange rate for sending money from South Africa",
    parameters: [
      {
        name: "receiving_country",
        type: "string",
        description: "Destination country code (e.g., ZW, KE, NG)",
        required: true,
      },
      {
        name: "receiving_currency",
        type: "string",
        description: "Destination currency code (e.g., USD, KES, NGN)",
        required: true,
      },
      {
        name: "amount",
        type: "number",
        description: "Amount to send in ZAR",
        required: false,
      },
      {
        name: "receive",
        type: "boolean",
        description: "If true, amount is receiving amount; if false, amount is sending amount",
        required: false,
      },
    ],
    render: ({ args, result, status }) => {
      const callInfo = getCallId("get_exchange_rate", args);

      // Show loading state while tool is executing
      if (status !== "complete") {
        return (
          <div key={callInfo.callId} className="bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 p-4 rounded-lg max-w-md">
            <span className="animate-pulse">⚙️ Calculating exchange rate...</span>
          </div>
        );
      }

      try {
        // Parse result if it's a string
        let parsedResult = result;
        if (typeof result === "string") {
          parsedResult = JSON.parse(result);
        }

        // Extract products from nested structure
        const products = parsedResult?.data?.items || parsedResult?.items || [];
        const requestInfo = parsedResult?.request_info;

        if (!products || products.length === 0) {
          return (
            <div key={callInfo.callId} className="bg-yellow-100 dark:bg-yellow-900 text-yellow-700 dark:text-yellow-300 p-4 rounded-lg max-w-md">
              ℹ️ No exchange rates available for this route at the moment.
            </div>
          );
        }

        return (
          <div key={callInfo.callId} className="my-4">
            <ExchangeRateCard
              sendingCountry="South Africa"
              receivingCountry={args.receiving_country || requestInfo?.receiving_country || "N/A"}
              sendingCurrency="ZAR"
              receivingCurrency={args.receiving_currency || requestInfo?.receiving_currency || "USD"}
              products={products}
              requestInfo={requestInfo}
            />
          </div>
        );
      } catch (error) {
        console.error("[RemittanceWidgets] Error rendering exchange rate card:", error);
        return (
          <div key={callInfo.callId} className="bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-300 p-4 rounded-lg max-w-md">
            ⚠️ Error loading exchange rates. Please try again.
          </div>
        );
      }
    },
  });

  // Register action for balance widget
  useCopilotAction({
    name: "get_balance",
    description: "Get the user's account balance",
    parameters: [],
    render: ({ result, status }) => {
      const callInfo = getCallId("get_balance", {});

      // Show loading state while tool is executing
      if (status !== "complete") {
        return (
          <div key={callInfo.callId} className="bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 p-4 rounded-lg max-w-md">
            <span className="animate-pulse">⚙️ Loading balance...</span>
          </div>
        );
      }

      let balance = 0;
      let currency = "USD";

      try {
        // Parse result if it's a string
        let parsedResult = result;
        if (typeof result === "string") {
          parsedResult = JSON.parse(result);
        }

        // Extract balance from nested structure
        if (typeof parsedResult === "object" && parsedResult !== null) {
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
      const body = args?.body || "User requested assistance with a remittance transaction.";

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

      // Show loading state while tool is executing
      if (status !== "complete") {
        return (
          <div key={callInfo.callId} className="bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300 p-4 rounded-lg max-w-md">
            <span className="animate-pulse">⚙️ Creating support ticket...</span>
          </div>
        );
      }

      try {
        // Parse result if it's a string
        let parsedResult = result;
        if (typeof result === "string") {
          parsedResult = JSON.parse(result);
        }

        // Extract ticket data from the result
        const ticketData = parsedResult?.data?.ticket || parsedResult?.ticket || parsedResult;
        
        return (
          <div key={callInfo.callId} className="my-4">
            <TicketCard ticket={ticketData} />
          </div>
        );
      } catch (error) {
        console.error("[RemittanceWidgets] Error rendering ticket card:", error);
        return (
          <div key={callInfo.callId} className="bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-300 p-4 rounded-lg max-w-md">
            ⚠️ Error creating ticket. Please try again.
          </div>
        );
      }
    },
  });

  // Register action for recipient list widget
  useCopilotAction({
    name: "get_recipient_list",
    description: "Get the user's recipient list for money transfers",
    parameters: [],
    render: ({ result, status }) => {
      const callInfo = getCallId("get_recipient_list", {});

      // Show loading state while tool is executing
      if (status !== "complete") {
        return (
          <div key={callInfo.callId} className="bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 p-4 rounded-lg max-w-md">
            <span className="animate-pulse">⚙️ Loading recipient list...</span>
          </div>
        );
      }

      try {
        // Parse result if it's a string
        let parsedResult = result;
        if (typeof result === "string") {
          parsedResult = JSON.parse(result);
        }

        // API returns: { items: [...], total: 155, page: 1, count: 20 }
        // Extract the full data structure
        const items = parsedResult?.items || parsedResult?.data?.items || parsedResult?.recipients || parsedResult?.data?.recipients || [];
        const total = parsedResult?.total || parsedResult?.data?.total || items.length;
        const page = parsedResult?.page || parsedResult?.data?.page || 1;
        const count = parsedResult?.count || parsedResult?.data?.count || items.length;

        console.log("[RemittanceWidgets] Parsed recipient result:", parsedResult);
        console.log("[RemittanceWidgets] Recipients count:", items.length);

        if (!items || items.length === 0) {
          return (
            <div key={callInfo.callId} className="bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-300 p-4 rounded-lg max-w-md">
              ⚠️ No recipients found. Add some recipients to your list.
            </div>
          );
        }

        return (
          <div key={callInfo.callId} className="my-4">
            <RecipientListCard 
              items={items}
              total={total}
              page={page}
              count={count}
            />
          </div>
        );
      } catch (error) {
        console.error("[RemittanceWidgets] Error rendering recipient list:", error);
        return (
          <div key={callInfo.callId} className="bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-300 p-4 rounded-lg max-w-md">
            ⚠️ Error loading recipients. Please try again.
          </div>
        );
      }
    },
  });

  // Widget 2: Generate Remittance Quote
  useCopilotAction({
    name: "generate_remittance_quote",
    description: "Generate a detailed quote for sending money to a recipient with exchange rates, fees, and total costs",
    parameters: [],
    render: ({ result, status, callInfo }: any) => {
      if (status !== "complete" || !result) {
        return <></>;
      }

      // Generate unique key for this widget
      const widgetKey = callInfo?.callId || `quote-${Date.now()}`;

      try {
        // Parse result if it's a string
        let parsedResult = result;
        if (typeof result === "string") {
          parsedResult = JSON.parse(result);
        }

        console.log("[RemittanceWidgets] Parsed quote result:", parsedResult);

        // Check for errors
        if (parsedResult.error || !parsedResult.calculationId) {
          return (
            <div key={widgetKey} className="bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-300 p-4 rounded-lg max-w-md">
              ⚠️ Failed to generate quote. {parsedResult.error || "Please try again."}
            </div>
          );
        }

        return (
          <div key={widgetKey} className="my-4">
            <QuoteCard 
              quote={parsedResult}
            />
          </div>
        );
      } catch (error) {
        console.error("[RemittanceWidgets] Error rendering quote:", error);
        return (
          <div key={widgetKey} className="bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-300 p-4 rounded-lg max-w-md">
            ⚠️ Error loading quote. Please try again.
          </div>
        );
      }
    },
  });

  // Widget 3: Transaction Receipt
  useCopilotAction({
    name: "execute_remittance_transaction",
    description: "Execute a remittance transaction and display the receipt after user confirms payment",
    parameters: [],
    render: ({ result, status, callInfo }: any) => {
      if (status !== "complete" || !result) {
        return <></>;
      }

      // Generate unique key for this widget
      const widgetKey = callInfo?.callId || `transaction-${Date.now()}`;

      try {
        // Parse result if it's a string
        let parsedResult = result;
        if (typeof result === "string") {
          parsedResult = JSON.parse(result);
        }

        console.log("[RemittanceWidgets] Parsed transaction result:", parsedResult);

        // Check for errors
        if (parsedResult.error || !parsedResult.transactionId) {
          return (
            <div key={widgetKey} className="bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-300 p-4 rounded-lg max-w-md">
              ⚠️ Transaction failed. {parsedResult.error || "Please try again."}
            </div>
          );
        }

        return (
          <div key={widgetKey} className="my-4">
            <TransactionReceipt 
              transaction={parsedResult}
            />
          </div>
        );
      } catch (error) {
        console.error("[RemittanceWidgets] Error rendering transaction receipt:", error);
        return (
          <div key={widgetKey} className="bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-300 p-4 rounded-lg max-w-md">
            ⚠️ Error loading transaction receipt. Please try again.
          </div>
        );
      }
    },
  });

  return null;
}
