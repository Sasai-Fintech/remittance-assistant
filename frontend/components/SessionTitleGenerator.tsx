"use client";

import { useEffect, useRef, useState } from "react";
import { useSessionTitle } from "@/lib/hooks/use-session-title";

/**
 * Component that automatically generates session titles from the first user message
 * This should be placed inside CopilotKit context to access chat messages
 */
export function SessionTitleGenerator() {
  const [currentThreadId, setCurrentThreadId] = useState<string | null>(null);
  const { autoGenerateTitle } = useSessionTitle(currentThreadId);
  const hasGeneratedTitle = useRef(false);

  // Get current thread ID
  useEffect(() => {
    const stored = localStorage.getItem("remittance_current_thread");
    if (stored) {
      setCurrentThreadId(stored);
    } else {
      // Create new thread ID if none exists
      const newThreadId = `thread_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      localStorage.setItem("remittance_current_thread", newThreadId);
      setCurrentThreadId(newThreadId);
    }
  }, []);

  // Listen for first user message in chat
  useEffect(() => {
    if (!currentThreadId || hasGeneratedTitle.current) return;

    // Listen for messages in the chat
    const checkForFirstMessage = () => {
      // Get chat messages from DOM (CopilotKit renders them)
      const chatMessages = document.querySelectorAll('[data-copilot-chat-message]');
      const userMessages = Array.from(chatMessages).filter((msg) => {
        // Check if it's a user message (not AI message)
        return msg.getAttribute('data-role') === 'user' || 
               msg.querySelector('[data-role="user"]');
      });

      if (userMessages.length === 1 && !hasGeneratedTitle.current) {
        const firstMessage = userMessages[0];
        // textContent works on Element, innerText only on HTMLElement
        const messageText = firstMessage.textContent || 
          (firstMessage instanceof HTMLElement ? firstMessage.innerText : null);
        
        if (messageText && messageText.trim()) {
          autoGenerateTitle(messageText.trim());
          hasGeneratedTitle.current = true;
        }
      }
    };

    // Check periodically for first message (since CopilotKit renders asynchronously)
    const interval = setInterval(checkForFirstMessage, 1000);
    
    // Also check on DOM mutations
    const observer = new MutationObserver(checkForFirstMessage);
    observer.observe(document.body, { childList: true, subtree: true });

    return () => {
      clearInterval(interval);
      observer.disconnect();
    };
  }, [currentThreadId, autoGenerateTitle]);

  return null; // This component doesn't render anything
}

