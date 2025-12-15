"use client";

import { useState, useEffect, useCallback, useRef } from 'react';
import { useCopilotChat } from '@copilotkit/react-core';
import { TextMessage, Role } from '@copilotkit/runtime-client-gql';
import { isValidMobileMessage, isAllowedOrigin } from '@/lib/mobile-bridge';

export interface MobileContext {
  transactionId?: string;
  deviceInfo?: Record<string, any>;
  channel?: string;
  [key: string]: any;
}

/**
 * Hook to manage context metadata from Flutter WebView
 * 
 * Handles context passing for transaction help flows and other
 * context-aware features.
 * 
 * Note: This hook must be called inside a CopilotKit provider.
 */
export function useMobileContext(): {
  context: MobileContext | null;
  triggerTransactionHelp: (transactionId: string) => void;
} {
  const [context, setContext] = useState<MobileContext | null>(null);
  
  // Get CopilotChat hook - must be called unconditionally (React rules)
  // This hook must be called inside CopilotKit provider
  const chatHook = useCopilotChat();
  const appendMessageRef = useRef(chatHook.appendMessage);
  
  // Update ref when appendMessage changes
  useEffect(() => {
    appendMessageRef.current = chatHook.appendMessage;
  }, [chatHook.appendMessage]);

  // Handle incoming messages from Flutter
  useEffect(() => {
    const handleMessage = (event: MessageEvent) => {
      // Security: Validate origin
      if (!isAllowedOrigin(event.origin)) {
        console.warn('[MobileContext] Message from unauthorized origin:', event.origin);
        return;
      }

      // Validate message format
      if (!isValidMobileMessage(event.data)) {
        return;
      }

      // Handle SET_CONTEXT message
      if (event.data.type === 'SET_CONTEXT') {
        const newContext: MobileContext = {
          ...event.data.context,
          channel: 'mobile',
        };
        setContext(newContext);
        
        console.log('[MobileContext] Context received', {
          hasTransactionId: !!newContext.transactionId,
          contextKeys: Object.keys(newContext),
        });
      }

      // Handle TRANSACTION_HELP message
      if (event.data.type === 'TRANSACTION_HELP') {
        const { transactionId } = event.data;
        
        console.log('[MobileContext] TRANSACTION_HELP received', { transactionId });
        
        // Update context
        setContext((prev) => ({
          ...prev,
          transactionId,
          channel: 'mobile',
        }));

        // Automatically send initial message to agent that will trigger transaction details fetch
        // The message is crafted to explicitly request transaction details, which will cause
        // the agent to automatically call get_transaction_details tool
        const initialMessage = `Please show me details for transaction ${transactionId} and help me with it`;
        
        // Function to send message with retry logic
        const sendMessageWithRetry = (retries = 5, delay = 500) => {
          const appendMessage = appendMessageRef.current || chatHook.appendMessage;
          
          if (appendMessage && typeof appendMessage === 'function') {
            try {
              console.log('[MobileContext] Sending transaction help message', {
                transactionId,
                message: initialMessage,
                retriesLeft: retries,
              });
              
              appendMessage(
                new TextMessage({
                  role: Role.User,
                  content: initialMessage,
                })
              )
                .then(() => {
                  console.log('[MobileContext] Transaction help message sent successfully');
                })
                .catch((error) => {
                  console.error('[MobileContext] Failed to send message:', error);
                  // Retry if appendMessage becomes available
                  if (retries > 0) {
                    setTimeout(() => sendMessageWithRetry(retries - 1, delay), delay);
                  }
                });
            } catch (error) {
              console.error('[MobileContext] Error sending transaction help message:', error);
              // Retry if appendMessage becomes available
              if (retries > 0) {
                setTimeout(() => sendMessageWithRetry(retries - 1, delay), delay);
              }
            }
          } else {
            // appendMessage not available yet, retry
            if (retries > 0) {
              console.log('[MobileContext] appendMessage not ready, retrying...', { retriesLeft: retries });
              setTimeout(() => sendMessageWithRetry(retries - 1, delay), delay);
            } else {
              console.error('[MobileContext] appendMessage not available after retries');
            }
          }
        };
        
        // Start sending with retry
        sendMessageWithRetry();
      }
    };

    // Listen for messages
    window.addEventListener('message', handleMessage);

    // Cleanup
    return () => {
      window.removeEventListener('message', handleMessage);
    };
  }, []); // Remove appendMessage from dependencies to avoid re-running when it changes

  // Manual trigger for transaction help (for testing)
  const triggerTransactionHelp = useCallback((transactionId: string) => {
    setContext((prev) => ({
      ...prev,
      transactionId,
      channel: 'mobile',
    }));

    // Send message that explicitly requests transaction details
    // This will trigger the agent to automatically call get_transaction_details tool
    const initialMessage = `Please show me details for transaction ${transactionId} and help me with it`;
    const appendMessage = appendMessageRef.current;
    if (appendMessage) {
      try {
        appendMessage(
          new TextMessage({
            role: Role.User,
            content: initialMessage,
          })
        ).catch((error) => {
          console.error('[MobileContext] Failed to send message:', error);
        });
      } catch (error) {
        console.error('[MobileContext] Error sending transaction help message:', error);
      }
    }
  }, []);

  return {
    context,
    triggerTransactionHelp,
  };
}

