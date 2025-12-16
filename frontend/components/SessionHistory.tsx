"use client";

import { useState, useEffect } from "react";
import { useSessionTitle } from "@/lib/hooks/use-session-title";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";
import { History, Plus, Trash2, MessageSquare } from "lucide-react";
import { cn } from "@/lib/utils";
// Simple date formatting without external dependency
function formatTimeAgo(timestamp: number): string {
  const now = Date.now();
  const diff = now - timestamp;
  const seconds = Math.floor(diff / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);

  if (days > 0) return `${days} day${days > 1 ? "s" : ""} ago`;
  if (hours > 0) return `${hours} hour${hours > 1 ? "s" : ""} ago`;
  if (minutes > 0) return `${minutes} minute${minutes > 1 ? "s" : ""} ago`;
  return "just now";
}

export function SessionHistory() {
  const [open, setOpen] = useState(false);
  const [isSwitching, setIsSwitching] = useState(() => {
    // Check if we're in the middle of switching (persists across reload)
    if (typeof window !== 'undefined') {
      return sessionStorage.getItem('remittance_switching_session') === 'true';
    }
    return false;
  });
  // Get current thread ID - CopilotKit manages this, but we track it for UI
  const [currentThreadId, setCurrentThreadId] = useState<string | null>(null);
  const { sessions, deleteSession, loading } = useSessionTitle(currentThreadId);
  
  // Debug logging
  useEffect(() => {
    console.log("[SessionHistory] Sessions updated:", sessions);
    console.log("[SessionHistory] Loading:", loading);
    console.log("[SessionHistory] Current thread ID:", currentThreadId);
  }, [sessions, loading, currentThreadId]);
  
  // Log when sheet opens/closes
  useEffect(() => {
    if (open) {
      console.log("[SessionHistory] 🚀 Sheet opened - Chat Sessions clicked!");
      console.log("[SessionHistory] Sessions count:", sessions.length);
      console.log("[SessionHistory] Loading state:", loading);
    } else {
      console.log("[SessionHistory] 🔒 Sheet closed");
    }
  }, [open, sessions.length, loading]);

  // Load current thread ID from localStorage (CopilotKit uses this)
  useEffect(() => {
    const stored = localStorage.getItem("remittance_current_thread");
    const continueSession = sessionStorage.getItem("remittance_continue_session");
    
    if (stored && continueSession === "true") {
      // User explicitly clicked a chat session - continue it
      console.log("[SessionHistory] 📂 Continuing session:", stored);
      setCurrentThreadId(stored);
    } else {
      // Fresh page load - start new session
      console.log("[SessionHistory] 🆕 Fresh load - starting new session");
      localStorage.removeItem("remittance_current_thread");
      
      // Generate a new thread ID for the new session
      const newThreadId = `thread_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      localStorage.setItem("remittance_current_thread", newThreadId);
      setCurrentThreadId(newThreadId);
    }
    
    // Clear the continue session flag after checking
    sessionStorage.removeItem("remittance_continue_session");
  }, []);

  // Clear switching state once the chat has loaded
  useEffect(() => {
    if (isSwitching) {
      console.log("[SessionHistory] 🔄 Checking if chat has loaded...");
      console.log("[SessionHistory] - currentThreadId:", currentThreadId);
      console.log("[SessionHistory] - sessions.length:", sessions.length);
      
      // Simple approach: Just wait a shorter time after page loads
      const timer = setTimeout(() => {
        console.log("[SessionHistory] ✅ Hiding loader after delay");
        sessionStorage.removeItem('remittance_switching_session');
        setIsSwitching(false);
      }, 800); // Reduced to 800ms - just enough for initial render
      
      return () => clearTimeout(timer);
    }
  }, [isSwitching]); // Only depend on isSwitching to run once on mount

  // Sort sessions by updatedAt (most recent first)
  const sortedSessions = [...sessions].sort((a, b) => b.updatedAt - a.updatedAt);

  const handleNewSession = () => {
    // Generate new thread ID - CopilotKit will use this for the new session
    const newThreadId = `thread_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    localStorage.setItem("remittance_current_thread", newThreadId);
    setCurrentThreadId(newThreadId);
    setOpen(false);
    // Reload page to start fresh session (CopilotKit will pick up new thread)
    window.location.reload();
  };

  const handleSwitchSession = (sessionThreadId: string) => {
    console.log("[SessionHistory] 📍 Session clicked:", sessionThreadId);
    console.log("[SessionHistory] 🔄 Setting isSwitching to TRUE");
    
    // Show loader immediately and persist across reload
    setIsSwitching(true);
    sessionStorage.setItem('remittance_switching_session', 'true');
    sessionStorage.setItem('remittance_continue_session', 'true'); // Signal to continue this session
    
    // Set as current thread - CopilotKit will load this session from checkpointer
    localStorage.setItem("remittance_current_thread", sessionThreadId);
    setCurrentThreadId(sessionThreadId);
    setOpen(false);
    
    // Small delay to ensure loader is visible, then reload
    setTimeout(() => {
      console.log("[SessionHistory] 🔄 Reloading page to load session");
      // Reload page to load the session (CopilotKit will load from MongoDB checkpointer)
      window.location.reload();
    }, 100);
  };

  const handleDeleteSession = (e: React.MouseEvent, sessionThreadId: string) => {
    e.stopPropagation();
    if (confirm("Are you sure you want to delete this session?")) {
      deleteSession(sessionThreadId);
    }
  };

  return (
    <>
      {/* Loading overlay when switching sessions */}
      {isSwitching && (
        <div 
          className="fixed inset-0 bg-black/60 flex items-center justify-center"
          style={{ 
            position: 'fixed', 
            top: 0, 
            left: 0, 
            right: 0, 
            bottom: 0,
            zIndex: 99999 
          }}
        >
          <div className="bg-white dark:bg-gray-800 rounded-lg p-8 flex flex-col items-center gap-4 shadow-2xl">
            <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-500"></div>
            <p className="text-base font-medium text-gray-700 dark:text-gray-300">Loading chat...</p>
          </div>
        </div>
      )}

      <Sheet open={open} onOpenChange={setOpen}>
      <SheetTrigger asChild>
        <Button
          variant="ghost"
          size="icon"
          className="h-9 w-9 md:h-10 md:w-10"
          aria-label="Session History"
        >
          <History className="h-5 w-5 md:h-6 md:w-6" />
        </Button>
      </SheetTrigger>
      <SheetContent side="right" className="w-full sm:w-[400px] sm:max-w-[90vw] p-0 flex flex-col">
        <SheetHeader className="border-b px-4 py-3 sm:px-6">
          <SheetTitle className="flex items-center gap-2 text-lg font-semibold">
            <History className="h-5 w-5" />
            Chat Sessions
          </SheetTitle>
        </SheetHeader>
        <div className="flex flex-col h-[calc(100vh-80px)] sm:h-[calc(100vh-88px)]">
          <div className="p-4 sm:p-6 border-b">
            <Button
              onClick={handleNewSession}
              className="w-full"
              variant="default"
              size="lg"
            >
              <Plus className="h-4 w-4 mr-2" />
              New Session
            </Button>
          </div>
          
          <ScrollArea className="flex-1 px-4 sm:px-6 py-4">
            {loading ? (
              <div className="flex flex-col items-center justify-center h-full text-center py-12 text-gray-500 dark:text-gray-400">
                <MessageSquare className="h-12 w-12 mb-4 opacity-50 animate-pulse" />
                <p className="text-sm">Loading sessions...</p>
              </div>
            ) : sortedSessions.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-center py-12 text-gray-500 dark:text-gray-400">
                <MessageSquare className="h-12 w-12 mb-4 opacity-50" />
                <p className="text-sm font-medium">No chat sessions yet</p>
                <p className="text-xs mt-2 text-gray-400 dark:text-gray-500">
                  Start a conversation to create your first session
                </p>
                {/* Debug info */}
                {process.env.NODE_ENV === 'development' && (
                  <div className="mt-4 text-xs text-gray-400">
                    <p>Debug: Sessions count: {sessions.length}</p>
                    <p>Loading: {loading ? 'true' : 'false'}</p>
                  </div>
                )}
              </div>
            ) : (
              <div className="space-y-2 pb-4">
                {sortedSessions.map((session) => (
                  <div
                    key={session.threadId}
                    onClick={() => handleSwitchSession(session.threadId)}
                    className={cn(
                      "flex items-start justify-between p-3 sm:p-4 rounded-lg border cursor-pointer",
                      "transition-all active:scale-[0.98]",
                      "hover:bg-gray-50 dark:hover:bg-zinc-800",
                      "touch-manipulation", // Better mobile touch handling
                      currentThreadId === session.threadId
                        ? "bg-indigo-50 dark:bg-indigo-900/20 border-indigo-200 dark:border-indigo-800 shadow-sm"
                        : "border-gray-200 dark:border-zinc-700"
                    )}
                  >
                    <div className="flex-1 min-w-0 pr-2">
                      <h4 className="font-medium text-sm sm:text-base truncate">
                        {session.title}
                      </h4>
                      {session.lastMessage && (
                        <p className="text-xs sm:text-sm text-gray-500 dark:text-gray-400 mt-1 line-clamp-2">
                          {session.lastMessage}
                        </p>
                      )}
                      <p className="text-xs text-gray-400 dark:text-gray-500 mt-1.5">
                        {formatTimeAgo(session.updatedAt)}
                      </p>
                    </div>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8 sm:h-9 sm:w-9 flex-shrink-0 touch-manipulation"
                      onClick={(e) => handleDeleteSession(e, session.threadId)}
                      aria-label="Delete session"
                    >
                      <Trash2 className="h-4 w-4 sm:h-5 sm:w-5" />
                    </Button>
                  </div>
                ))}
              </div>
            )}
          </ScrollArea>
        </div>
      </SheetContent>
    </Sheet>
    </>
  );
}

