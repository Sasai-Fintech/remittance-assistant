"use client";

import { useState, useEffect, useRef, lazy, Suspense } from "react";
import { CopilotKit, useCopilotChat } from "@copilotkit/react-core";
import { CopilotChat, useCopilotChatSuggestions, type InputProps } from "@copilotkit/react-ui";
import "@copilotkit/react-ui/styles.css";
import { Button } from "@/components/ui/button";
import { Plus, History, Send, X } from "lucide-react";
import { useMobileAuth } from "@/lib/hooks/use-mobile-auth";
import { useMobileContext } from "@/lib/hooks/use-mobile-context";
import { useTranslations } from "@/lib/hooks/use-translations";
import { LanguageSwitcher } from "@/components/LanguageSwitcher";

// Lazy load heavy components to reduce initial bundle size
const EcocashWidgets = lazy(() => import("@/components/EcocashWidgets").then(m => ({ default: m.EcocashWidgets })));
const Chat = lazy(() => import("@/components/Chat").then(m => ({ default: m.Chat })));
const SessionHistory = lazy(() => import("@/components/SessionHistory").then(m => ({ default: m.SessionHistory })));
const SessionTitleGenerator = lazy(() => import("@/components/SessionTitleGenerator").then(m => ({ default: m.SessionTitleGenerator })));

function NewSessionButton() {
  const handleNewSession = () => {
    // Generate new thread ID - CopilotKit will use this for the new session
    const newThreadId = `thread_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    localStorage.setItem("ecocash_current_thread", newThreadId);
    // Reload page to start fresh session (CopilotKit will pick up new thread)
    window.location.reload();
  };

  return (
    <Button
      variant="ghost"
      size="icon"
      className="h-9 w-9 md:h-10 md:w-10"
      onClick={handleNewSession}
      aria-label="New Session"
    >
      <Plus className="h-5 w-5 md:h-6 md:w-6" />
    </Button>
  );
}

function SuggestionsComponent() {
  const { language } = useTranslations();
  
  // Build language-specific instructions
  const languageInstruction = language === "sn" 
    ? `CRITICAL LANGUAGE REQUIREMENT - SHONA (ChiShona):
The user has selected Shona as their preferred language. You MUST generate ALL suggestions in Shona (ChiShona), not English.

IMPORTANT: All suggestion text must be in Shona. Use these Shona phrases:
- "Tarisa mari yangu" (Check my balance)
- "Ona zvishandiswa" (View transactions)  
- "Ratidza ruzivo rwemari" (Show financial insights)
- "Wana rubatsiro" (Get help)
- "Ona zvishandiswa zvichangobva" (View recent transactions)
- "Ona mari yemuhomwe" (View wallet balance)
- "Ratidza mari inopinda" (Show incoming money)
- "Ratidza mari inobuda" (Show spending)
- "Ratidza mari yekudyara" (Show investments)

DO NOT use English for suggestions when the user has selected Shona. All suggestion buttons must display Shona text.

`
    : ``;
  
  const baseInstructions = `Offer context-aware suggestions based on the conversation state. CRITICAL: Never suggest actions that have already been completed. Always prioritize financial insights and account management actions.`;
  
  const instructions = languageInstruction + baseInstructions + `

    Rules:
    1. If the AI has confirmed a ticket was "successfully submitted" or "submitted", DO NOT suggest ${language === "sn" ? '"Simbisa kutumira"' : '"Confirm submission"'} - the ticket is already confirmed. Instead suggest: ${language === "sn" ? '"Tarisa mari yangu", "Ona zvishandiswa", "Ratidza ruzivo rwemari", kana "Wana rubatsiro rwakawanda"' : '"Check my balance", "View transactions", "Show financial insights", or "Get more help"'}
    
    2. If there's a pending ticket confirmation dialog visible (user hasn't confirmed yet), suggest ${language === "sn" ? '"Simbisa kutumira" kana "Kanzura tikiti"' : '"Confirm submission" or "Cancel ticket"'}
    
    3. If AI just summarized a transaction and asked "tell us what's wrong" or "what issue are you facing", suggest common transaction issues:
       ${language === "sn"
         ? '- "Mutengi haana kugamuchira mari"\n       - "Mari yakabviswa kaviri"\n       - "Chishandiso chakakundikana"\n       - "Ndinoda kudzoserwa mari"\n       - "Mari isiri iyo yakabhadharwa"\n       - "Chipo hachina kushandiswa"'
         : '- "Receiver has not received the payment"\n       - "Amount debited twice"\n       - "Transaction failed"\n       - "Need refund"\n       - "Wrong amount charged"\n       - "Offer not applied"'}
    
    4. If AI is providing resolution steps (e.g., "contact merchant with UTR"), suggest:
       ${language === "sn"
         ? '- "Zvakanaka" kana "Ndinonzwisisa"\n       - "Ndakabata mutengesi, dambudziko harina kugadziriswa"\n       - "Dambudziko ragadziriswa"'
         : '- "Okay" or "Got it"\n       - "Contacted merchant, issue not resolved"\n       - "Issue resolved"'}
    
    5. If user just viewed transactions, suggest: ${language === "sn" ? '"Wana rubatsiro nechishandiso", "Tarisa mari yangu", kana "Ratidza ruzivo rwemari"' : '"Get help with a transaction", "Check my balance", or "Show financial insights"'}
    
    6. If user is asking about a specific transaction, suggest ${language === "sn" ? '"Ona ruzivo rwechishandiso" kana "Zivisa dambudziko"' : '"View transaction details" or "Report an issue"'}
    
    7. If a ticket was just successfully submitted, suggest next logical steps like ${language === "sn" ? '"Tarisa mari yangu", "Ona zvishandiswa zvichangobva", kana "Ratidza ruzivo rwemari"' : '"Check my balance", "View recent transactions", or "Show financial insights"'}
    
    8. If the conversation shows the ticket is already processed/completed, suggest new actions, not confirmation actions
    
    9. If user asks about financial insights, analysis, or wants to see spending/incoming/investment breakdown, suggest:
       ${language === "sn" 
         ? '- "Ratidza kuyerera kwemari" (for overview bar chart)\n       - "Ongorora mari inopinda" (for detailed incoming breakdown)\n       - "Ongorora mari inobuda" (for detailed spending breakdown)\n       - "Ongorora mari yekudyara" (for detailed investment breakdown)'
         : '- "Show cash flow" (for overview bar chart)\n       - "Analyze incoming" (for detailed incoming breakdown)\n       - "Analyze spends" (for detailed spending breakdown)\n       - "Analyze investment" (for detailed investment breakdown)'}
    
    10. For new conversations or when no specific context, ALWAYS include ${language === "sn" ? '"Ratidza ruzivo rwemari"' : '"Show financial insights"'} as one of the suggestions. Other good defaults are:
       ${language === "sn"
         ? '- "Tarisa mari yemuhomwe"\n       - "Ona zvishandiswa zvichangobva"\n       - "Ratidza ruzivo rwemari"\n       - "Wana rubatsiro nechishandiso"'
         : '- "Check my wallet balance"\n       - "View recent transactions"\n       - "Show financial insights"\n       - "Get help with a transaction"'}
    
    11. NEVER suggest "Ask another question" - it's not relevant. Instead suggest specific actionable items.
    
    Always check the last AI message - if it mentions "successfully submitted", "has been submitted", "ticket created", or similar completion phrases, do NOT suggest confirmation actions.
    If AI asks "what's wrong" or "what issue", provide issue-specific suggestions, not generic ones.
    If AI mentions financial insights or analysis, provide financial insights suggestions.
    Keep suggestions concise (2-5 words), actionable, and relevant to the current conversation context.
    Prioritize financial insights suggestions when appropriate.`;
  
  useCopilotChatSuggestions({
    instructions: instructions,
    minSuggestions: 2,
    maxSuggestions: 4,
  }, [language]); // Re-run when language changes

  return null; // Suggestions are automatically rendered by CopilotKit
}

function CustomInput({ inProgress, onSend, isVisible, onStop }: InputProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const { t } = useTranslations();

  const handleSubmit = (value: string) => {
    if (value.trim()) {
      onSend(value);
      if (inputRef.current) {
        inputRef.current.value = '';
      }
    }
  };

  return (
    <div className="flex items-center gap-1.5 sm:gap-2 px-2 sm:px-3 md:px-4 pt-2 sm:pt-3 pb-3 sm:pb-4 md:pb-6 border-t border-gray-200 dark:border-zinc-700 bg-white dark:bg-zinc-900 sticky bottom-0 z-20">
      <input
        ref={inputRef}
        disabled={inProgress}
        type="text"
        placeholder={t("chat.placeholder")}
        className="flex-1 px-3 sm:px-4 py-2.5 sm:py-3 rounded-full border border-gray-300 dark:border-zinc-600 bg-white dark:bg-zinc-800 text-gray-900 dark:text-gray-100 placeholder:text-gray-500 dark:placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:focus:ring-indigo-400 disabled:bg-gray-100 dark:disabled:bg-zinc-700 transition-all text-sm sm:text-base"
        onKeyDown={(e) => {
          if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit(e.currentTarget.value);
          }
        }}
      />
      {inProgress ? (
        <button
          type="button"
          className="h-9 w-9 sm:h-10 sm:w-10 md:h-12 md:w-12 rounded-full bg-red-600 hover:bg-red-700 text-white flex items-center justify-center transition-all shadow-sm hover:shadow-md disabled:opacity-50 disabled:cursor-not-allowed flex-shrink-0 touch-manipulation"
          onClick={() => {
            if (onStop) {
              onStop();
            }
            if (inputRef.current) {
              inputRef.current.value = '';
            }
          }}
          title="Cancel"
          aria-label="Cancel"
        >
          <X className="h-4 w-4 sm:h-5 sm:w-5" />
        </button>
      ) : (
        <button
          type="button"
          disabled={inProgress}
          className="h-9 w-9 sm:h-10 sm:w-10 md:h-12 md:w-12 rounded-full bg-indigo-600 hover:bg-indigo-700 text-white flex items-center justify-center transition-all shadow-sm hover:shadow-md disabled:opacity-50 disabled:cursor-not-allowed flex-shrink-0 touch-manipulation"
          onClick={() => {
            if (inputRef.current) {
              handleSubmit(inputRef.current.value);
            }
          }}
          title="Send"
          aria-label="Send"
        >
          <Send className="h-4 w-4 sm:h-5 sm:w-5" />
        </button>
      )}
    </div>
  );
}

function ChatWithContext({ threadId }: { threadId: string | null }) {
  const { context } = useMobileContext();
  
  // Note: CopilotKit should automatically load messages when threadId is provided
  // The key prop on CopilotKit component forces re-mount when threadId changes
  // This should trigger CopilotKit to fetch existing messages from the backend
  
  return (
    <CopilotChat
      className="h-full border-0 rounded-2xl shadow-xl bg-white/95 dark:bg-zinc-800/95 backdrop-blur-sm"
      instructions="You are the Ecocash Assistant, a helpful and friendly AI financial companion. Help users with their wallet balance, transaction history, and support tickets. Be proactive and suggest helpful actions when appropriate. When starting a new conversation, greet the user with 'How can I help you today?'"
      labels={{
        title: "What's on your mind today?",
        initial: "How can I help you today?",
        placeholder: "Ask anything",
      }}
      Input={CustomInput}
    />
  );
}

export default function Home() {
  // Get JWT token and Sasai token from Flutter WebView (via postMessage)
  // This hook doesn't require CopilotKit, so it can be called outside
  const { token, userId, sasaiToken, isAuthenticated } = useMobileAuth();
  const { language } = useTranslations();
  
  // Get or create thread ID from localStorage (for session persistence)
  // Read synchronously on initial render to ensure CopilotKit gets it immediately
  const [threadId, setThreadId] = useState<string | null>(() => {
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem("ecocash_current_thread");
      if (stored) {
        return stored;
      } else {
        // Generate a new thread ID if none exists
        const newThreadId = `thread_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        localStorage.setItem("ecocash_current_thread", newThreadId);
        return newThreadId;
      }
    }
    return null;
  });
  
  // Update threadId if localStorage changes (e.g., after session switch)
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem("ecocash_current_thread");
      if (stored && stored !== threadId) {
        setThreadId(stored);
        console.log('[COPILOTKIT] ThreadId updated from localStorage:', stored);
      }
    }
  }, [threadId]);

  // Build properties for CopilotKit with auth headers
  // Following CopilotKit's self-hosted auth pattern: https://docs.copilotkit.ai/langgraph/auth
  // Only pass tokens if they exist (from mobile-wrapper), otherwise let token manager handle it
  // Debug logging
  if (process.env.NODE_ENV === 'development') {
    console.log('[COPILOTKIT_PROPS] Token:', token ? 'present' : 'missing');
    console.log('[COPILOTKIT_PROPS] UserId:', userId || 'missing');
    console.log('[COPILOTKIT_PROPS] SasaiToken:', sasaiToken ? `${sasaiToken.substring(0, 20)}...` : 'MISSING');
    console.log('[COPILOTKIT_PROPS] ThreadId:', threadId || 'missing');
    console.log('[COPILOTKIT_PROPS] Mode:', (token || sasaiToken) ? 'mobile-wrapper (external token)' : 'direct access (token manager)');
  }
  
  // Set properties if we have a token OR sasaiToken (from mobile-wrapper)
  // If no tokens, CopilotKit won't send auth headers, and backend will use token manager
  // Pass thread_id in metadata so CopilotKit/LangGraph can use it for session persistence
  const copilotKitProperties = (token || sasaiToken)
    ? {
        headers: {
          ...(token && { Authorization: `Bearer ${token}` }),
          ...(userId && { 'X-User-Id': userId }),
          ...(sasaiToken && { 'X-Sasai-Token': sasaiToken }), // Pass Sasai token as custom header
          'X-Language': language, // Pass current language preference
        },
        // Also pass in metadata for LangGraph config
        metadata: {
          ...(sasaiToken && { external_token: sasaiToken }),
          language: language, // Pass language in metadata too
          ...(threadId && { thread_id: threadId }), // Pass thread_id for session persistence
        },
      }
    : {
        // Even without token, pass language preference and thread_id
        headers: {
          'X-Language': language,
        },
        metadata: {
          language: language,
          ...(threadId && { thread_id: threadId }), // Pass thread_id for session persistence
        },
      };
  
  // Debug: Log what we're sending
  if (process.env.NODE_ENV === 'development' && copilotKitProperties) {
    console.log('[COPILOTKIT_PROPS] Headers being sent:', Object.keys(copilotKitProperties.headers));
    console.log('[COPILOTKIT_PROPS] Metadata being sent:', copilotKitProperties.metadata);
  }

  // Get basePath for CopilotKit runtimeUrl (must match Next.js basePath)
  // Try multiple methods to get basePath since NEXT_PUBLIC_* vars are build-time only
  const getBasePath = () => {
    // Method 1: Use environment variable (if available at build time)
    if (process.env.NEXT_PUBLIC_BASE_PATH) {
      return process.env.NEXT_PUBLIC_BASE_PATH;
    }
    // Method 2: Detect from current URL (runtime detection)
    if (typeof window !== 'undefined') {
      const pathname = window.location.pathname;
      // If pathname starts with /ecocash-assistant, extract it
      if (pathname.startsWith('/ecocash-assistant')) {
        return '/ecocash-assistant';
      }
    }
    // Method 3: Default to empty (for local dev)
    return '';
  };
  
  const basePath = getBasePath();
  const runtimeUrl = `${basePath}/api/copilotkit`;
  
  if (process.env.NODE_ENV === 'development') {
    console.log('[COPILOTKIT] runtimeUrl:', runtimeUrl);
    console.log('[COPILOTKIT] basePath:', basePath);
    console.log('[COPILOTKIT] window.location.pathname:', typeof window !== 'undefined' ? window.location.pathname : 'N/A');
  }

  return (
    <CopilotKit
      agent="ecocash_agent"
      runtimeUrl={runtimeUrl}
      properties={copilotKitProperties}
      threadId={threadId || undefined}
      key={threadId || 'new-session'} // Force re-render when threadId changes to load session
    >
      <Suspense fallback={<div className="hidden" />}>
        <EcocashWidgets />
        <Chat />
        <SessionTitleGenerator />
      </Suspense>
      <SuggestionsComponent />
      <main className="flex flex-col h-screen bg-gradient-to-br from-gray-50 via-indigo-50/30 to-purple-50/20 dark:from-zinc-900 dark:via-zinc-900 dark:to-zinc-900 overflow-hidden">
        {/* Header - optimized for mobile */}
        <div className="p-1.5 sm:p-2 md:p-4 lg:p-6 bg-white/80 dark:bg-zinc-800/80 backdrop-blur-sm shadow-sm z-10 border-b border-gray-200/50 dark:border-zinc-700/50 relative min-h-[50px] sm:min-h-[60px] md:min-h-[70px] flex-shrink-0">
          <div className="w-full flex items-center justify-end">
            <div className="flex items-center gap-0.5 sm:gap-1 md:gap-2">
              <LanguageSwitcher />
              <NewSessionButton />
              <Suspense fallback={
                <Button variant="ghost" size="icon" className="h-9 w-9 md:h-10 md:w-10" disabled>
                  <History className="h-5 w-5 md:h-6 md:w-6 opacity-50" />
                </Button>
              }>
                <SessionHistory />
              </Suspense>
            </div>
          </div>
        </div>

        {/* Chat Area - full width on mobile, centered on desktop */}
        <div className="flex-1 overflow-hidden relative min-h-0">
          <div className="h-full max-w-5xl mx-auto w-full p-0 sm:p-2 md:p-4 lg:p-6">
            <div className="h-full flex flex-col gap-1 sm:gap-2 md:gap-4">
              {/* Chat - full height on mobile */}
              <div className="flex-1 min-h-0 overflow-hidden">
                <ChatWithContext threadId={threadId} />
              </div>
            </div>
          </div>
        </div>
      </main>
    </CopilotKit>
  );
}
