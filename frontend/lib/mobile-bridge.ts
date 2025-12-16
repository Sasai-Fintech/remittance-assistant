/**
 * Mobile Bridge - TypeScript types and utilities for Flutter WebView communication
 * 
 * This module defines the message protocol between Flutter app and Next.js UI
 * via postMessage API.
 */

/**
 * Message types sent from Flutter to WebView
 */
export type MobileMessage =
  | { type: 'SET_TOKEN'; token: string; userId?: string; sasaiToken?: string; timestamp?: number }
  | { type: 'SET_CONTEXT'; context: Record<string, any>; timestamp?: number }
  | { type: 'TRANSACTION_HELP'; transactionId: string; timestamp?: number };

/**
 * Message types sent from WebView to Flutter
 */
export type WebViewMessage =
  | { type: 'NAVIGATE'; route: string; params?: Record<string, any> }
  | { type: 'TOKEN_RECEIVED'; success: boolean }
  | { type: 'CONTEXT_RECEIVED'; success: boolean }
  | { type: 'ERROR'; message: string; code?: string };

/**
 * Validates if a message is a valid MobileMessage
 */
export function isValidMobileMessage(message: any): message is MobileMessage {
  if (!message || typeof message !== 'object') return false;
  
  const validTypes = ['SET_TOKEN', 'SET_CONTEXT', 'TRANSACTION_HELP'];
  if (!validTypes.includes(message.type)) return false;
  
  switch (message.type) {
    case 'SET_TOKEN':
      return typeof message.token === 'string' && message.token.length > 0;
    case 'SET_CONTEXT':
      return typeof message.context === 'object' && message.context !== null;
    case 'TRANSACTION_HELP':
      return typeof message.transactionId === 'string' && message.transactionId.length > 0;
    default:
      return false;
  }
}

/**
 * Sends a message from WebView to Flutter (parent window)
 */
export function sendToFlutter(message: WebViewMessage): void {
  if (typeof window !== 'undefined' && window.parent) {
    window.parent.postMessage(message, '*');
  }
}

/**
 * Validates message origin for security
 * In production, you should validate against specific allowed origins
 */
export function isAllowedOrigin(origin: string): boolean {
  // For development, allow all origins
  // In production, validate against your Flutter app's origin
  if (process.env.NODE_ENV === 'development') {
    return true;
  }
  
  // Production: Add your Flutter app's origin here
  // Also allow dev/staging/sandbox domains for testing
  const allowedOrigins = [
    'remittance://', // Flutter deep link scheme
    'https://remittance.app', // Production web origin
    'https://dev.sasaipaymentgateway.com', // Dev environment
    'https://staging.sasaipaymentgateway.com', // Staging environment
    'https://sandbox.sasaipaymentgateway.com', // Sandbox environment
  ];
  
  return allowedOrigins.some(allowed => origin.startsWith(allowed));
}

