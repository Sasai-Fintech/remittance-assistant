"use client";

import { useEffect, useState } from "react";

export interface SessionInfo {
  threadId: string;
  title: string;
  createdAt: number;
  updatedAt: number;
  lastMessage?: string;
}

const STORAGE_KEY = "ecocash_sessions";
// Use Next.js API routes which proxy to the backend
// This allows server-side code to read environment variables at runtime
// Client-side code uses relative URLs to the Next.js API routes
// In production with basePath, we need to ensure the basePath is included
const getApiBase = () => {
  // In production, Next.js basePath should handle this automatically
  // But we can also use the basePath from next.config if needed
  if (typeof window !== 'undefined') {
    // Get basePath from Next.js router or use environment variable
    // Next.js automatically handles basePath for relative URLs, but we can be explicit
    const basePath = process.env.NEXT_PUBLIC_BASE_PATH || '';
    return basePath;
  }
  return '';
};
const API_BASE = getApiBase();

/**
 * Hook to manage session titles and metadata
 * Sessions are now queried from the backend (MongoDB) instead of localStorage
 */
export function useSessionTitle(threadId: string | null) {
  const [title, setTitle] = useState<string>("New Chat");
  const [sessions, setSessions] = useState<SessionInfo[]>([]);
  const [loading, setLoading] = useState(true);

  // Load sessions from backend API (load once on mount, not dependent on threadId)
  useEffect(() => {
    const loadSessions = async () => {
      try {
        setLoading(true);
        // NEXT_PUBLIC_BASE_PATH is embedded at build time
        // In production with basePath set, this will be '/remittance-assistant'
        // In development without basePath, this will be ''
        const basePath = process.env.NEXT_PUBLIC_BASE_PATH || '';
        const apiUrl = `${basePath}/api/sessions/`;
        console.log("[useSessionTitle] Fetching sessions from:", apiUrl);
        
        const response = await fetch(apiUrl, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        });
        
        console.log("[useSessionTitle] Response status:", response.status, response.statusText);
        
        if (response.ok) {
          const data = await response.json();
          console.log("[useSessionTitle] Raw API response:", data);
          console.log("[useSessionTitle] Data type:", Array.isArray(data) ? 'array' : typeof data);
          console.log("[useSessionTitle] Data length:", Array.isArray(data) ? data.length : 'N/A');
          
          // Ensure data is an array
          if (!Array.isArray(data)) {
            console.error("[useSessionTitle] Expected array but got:", typeof data, data);
            setSessions([]);
            return;
          }
          
          // Convert backend format to frontend format
          const converted: SessionInfo[] = data
            .map((s: any): SessionInfo | null => {
              if (!s.thread_id) {
                console.warn("[useSessionTitle] Session missing thread_id:", s);
                return null;
              }
              return {
                threadId: s.thread_id,
                title: s.title || `Session ${s.thread_id.substring(0, 8)}`,
                createdAt: s.created_at ? new Date(s.created_at).getTime() : Date.now() - 86400000, // Default to 1 day ago if null
                updatedAt: s.updated_at ? new Date(s.updated_at).getTime() : Date.now(), // Use current time if null
                lastMessage: s.last_message,
              };
            })
            .filter((s): s is SessionInfo => s !== null);
          
          console.log("[useSessionTitle] Converted sessions:", converted);
          console.log("[useSessionTitle] Setting sessions state with", converted.length, "sessions");
          setSessions(converted);
          
          // Set current session title if threadId exists
          if (threadId) {
            const current = converted.find((s: SessionInfo) => s.threadId === threadId);
            if (current) {
              console.log("[useSessionTitle] Setting title for current thread:", current.title);
              setTitle(current.title);
            }
          }
        } else {
          const errorText = await response.text();
          console.error(`[useSessionTitle] Failed to load sessions from backend: ${response.status} ${errorText}`);
          // Fallback to localStorage if backend fails
          const stored = localStorage.getItem(STORAGE_KEY);
          if (stored) {
            try {
              const parsed = JSON.parse(stored);
              console.log("[useSessionTitle] Using localStorage fallback:", parsed.length, "sessions");
              setSessions(parsed);
            } catch (e) {
              console.error("[useSessionTitle] Failed to parse localStorage sessions:", e);
            }
          }
        }
      } catch (error) {
        console.error("[useSessionTitle] Failed to load sessions:", error);
        // Fallback to localStorage
        const stored = localStorage.getItem(STORAGE_KEY);
        if (stored) {
          try {
            const parsed = JSON.parse(stored);
            console.log("[useSessionTitle] Using localStorage fallback after error:", parsed.length, "sessions");
            setSessions(parsed);
          } catch (e) {
            console.error("[useSessionTitle] Failed to parse localStorage sessions:", e);
          }
        }
      } finally {
        setLoading(false);
      }
    };
    
    loadSessions();
  }, []); // Load once on mount, not dependent on threadId
  
  // Update title when threadId changes (separate effect)
  useEffect(() => {
    if (threadId && sessions.length > 0) {
      const current = sessions.find((s: SessionInfo) => s.threadId === threadId);
      if (current) {
        console.log("[useSessionTitle] Updating title for threadId:", threadId, "->", current.title);
        setTitle(current.title);
      }
    }
  }, [threadId, sessions]);

  // Update session title
  const updateTitle = async (newTitle: string, message?: string) => {
    if (!threadId) return;

    // Update local state immediately
    setTitle(newTitle);
    
    // Also update in localStorage as cache (backend is source of truth)
    const updated: SessionInfo = {
      threadId,
      title: newTitle,
      createdAt: Date.now(),
      updatedAt: Date.now(),
      lastMessage: message,
    };

    setSessions((prev) => {
      const existing = prev.findIndex((s) => s.threadId === threadId);
      let updatedSessions: SessionInfo[];

      if (existing >= 0) {
        // Update existing session
        updatedSessions = [...prev];
        updatedSessions[existing] = {
          ...updatedSessions[existing],
          title: newTitle,
          updatedAt: Date.now(),
          lastMessage: message,
        };
      } else {
        // Add new session
        updatedSessions = [...prev, updated];
      }

      // Cache in localStorage
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(updatedSessions));
      } catch (error) {
        console.error("Failed to cache sessions:", error);
      }

      return updatedSessions;
    });
  };

  // Generate title from first message
  const generateTitleFromMessage = (message: string): string => {
    // Truncate to 50 characters, remove newlines
    const cleaned = message.replace(/\n/g, " ").trim();
    if (cleaned.length <= 50) {
      return cleaned || "New Chat";
    }
    return cleaned.substring(0, 47) + "...";
  };

  // Auto-generate title from first user message
  const autoGenerateTitle = (firstMessage: string) => {
    const generated = generateTitleFromMessage(firstMessage);
    updateTitle(generated, firstMessage);
  };

  // Delete session
  const deleteSession = async (sessionThreadId: string) => {
    try {
      // Use Next.js API route which proxies to backend
      const basePath = process.env.NEXT_PUBLIC_BASE_PATH || '';
      const apiUrl = `${basePath}/api/sessions/${sessionThreadId}`;
      const response = await fetch(apiUrl, {
        method: "DELETE",
      });
      
      if (response.ok) {
        // Update local state
        setSessions((prev) => {
          const filtered = prev.filter((s) => s.threadId !== sessionThreadId);
          // Update localStorage cache
          try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(filtered));
          } catch (error) {
            console.error("Failed to update cache:", error);
          }
          return filtered;
        });
      } else {
        console.error("Failed to delete session from backend");
        // Still update local state as fallback
        setSessions((prev) => {
          const filtered = prev.filter((s) => s.threadId !== sessionThreadId);
          try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(filtered));
          } catch (error) {
            console.error("Failed to delete session:", error);
          }
          return filtered;
        });
      }
    } catch (error) {
      console.error("Failed to delete session:", error);
      // Fallback: update local state
      setSessions((prev) => {
        const filtered = prev.filter((s) => s.threadId !== sessionThreadId);
        try {
          localStorage.setItem(STORAGE_KEY, JSON.stringify(filtered));
        } catch (error) {
          console.error("Failed to delete session:", error);
        }
        return filtered;
      });
    }
  };

  
  return {
    title,
    sessions,
    loading,
    updateTitle,
    autoGenerateTitle,
    deleteSession,
    generateTitleFromMessage,
  };
}

