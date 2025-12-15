"use client";

import { useState, useEffect, useCallback } from 'react';
import { isValidMobileMessage, isAllowedOrigin, sendToFlutter } from '@/lib/mobile-bridge';

export interface MobileAuthState {
  token: string | null;
  userId: string | null;
  sasaiToken: string | null; // Sasai Payment Gateway authentication token
  isAuthenticated: boolean;
}

/**
 * Hook to manage JWT authentication from Flutter WebView
 * 
 * Listens for postMessage events from Flutter app containing JWT tokens.
 * Follows CopilotKit's authentication pattern for self-hosted deployments.
 * 
 * @see https://docs.copilotkit.ai/langgraph/auth
 */
export function useMobileAuth(): MobileAuthState & {
  setToken: (token: string, userId?: string, sasaiToken?: string) => void;
} {
  const [token, setTokenState] = useState<string | null>(null);
  const [userId, setUserId] = useState<string | null>(null);
  const [sasaiToken, setSasaiToken] = useState<string | null>(null);

  // Extract tokens from URL query parameters on initial load (for direct access)
  useEffect(() => {
    if (typeof window === 'undefined') return;
    
    const urlParams = new URLSearchParams(window.location.search);
    const urlToken = urlParams.get('token');
    const urlSasaiToken = urlParams.get('sasaiToken') || urlParams.get('sasai_token');
    const urlUserId = urlParams.get('userId') || urlParams.get('user_id');
    
    // Extract tokens from URL (postMessage will override these if received)
    if (urlToken) {
      const decodedToken = decodeURIComponent(urlToken);
      setTokenState(decodedToken);
      console.log('[MobileAuth] Token extracted from URL query parameter');
    }
    
    if (urlSasaiToken) {
      const decodedSasaiToken = decodeURIComponent(urlSasaiToken);
      setSasaiToken(decodedSasaiToken);
      console.log('[MobileAuth] Sasai token extracted from URL query parameter');
    }
    
    if (urlUserId) {
      const decodedUserId = decodeURIComponent(urlUserId);
      setUserId(decodedUserId);
      console.log('[MobileAuth] User ID extracted from URL query parameter');
    }
  }, []); // Only run once on mount

  // Handle incoming messages from Flutter (mobile-wrapper.html)
  useEffect(() => {
    const handleMessage = (event: MessageEvent) => {
      // Security: Validate origin (in production, be more strict)
      if (!isAllowedOrigin(event.origin)) {
        console.warn('[MobileAuth] Message from unauthorized origin:', event.origin);
        return;
      }

      // Validate message format
      if (!isValidMobileMessage(event.data)) {
        return;
      }

      // Handle SET_TOKEN message
      if (event.data.type === 'SET_TOKEN') {
        try {
          const { token: newToken, userId: newUserId, sasaiToken: newSasaiToken } = event.data;
          
          // Allow setting token, sasaiToken, or both independently
          if (newToken && typeof newToken === 'string' && newToken.length > 0) {
            setTokenState(newToken);
          }
          
          if (newUserId) {
            setUserId(newUserId);
          }
          
          if (newSasaiToken && typeof newSasaiToken === 'string' && newSasaiToken.length > 0) {
            setSasaiToken(newSasaiToken);
          }
          
          // Log what was received
          if (newToken || newSasaiToken) {
            console.log('[MobileAuth] Token(s) received via postMessage', {
              hasToken: !!newToken,
              userId: newUserId,
              tokenLength: newToken?.length || 0,
              hasSasaiToken: !!newSasaiToken,
            });
            
            // Notify Flutter that token was received
            try {
              sendToFlutter({
                type: 'TOKEN_RECEIVED',
                success: true,
              });
            } catch (error) {
              console.warn('[MobileAuth] Failed to notify Flutter:', error);
            }
          } else {
            console.warn('[MobileAuth] No valid tokens in SET_TOKEN message');
          }
        } catch (error) {
          console.error('[MobileAuth] Error processing SET_TOKEN message:', error);
        }
      }
    };

    // Listen for messages
    window.addEventListener('message', handleMessage);

    // Cleanup
    return () => {
      window.removeEventListener('message', handleMessage);
    };
  }, []);

  // Manual token setter (for testing or programmatic updates)
  const setToken = useCallback((newToken: string, newUserId?: string, newSasaiToken?: string) => {
    setTokenState(newToken);
    setUserId(newUserId || null);
    if (newSasaiToken) {
      setSasaiToken(newSasaiToken);
    }
  }, []);

  return {
    token,
    userId,
    sasaiToken,
    isAuthenticated: !!token,
    setToken,
  };
}

