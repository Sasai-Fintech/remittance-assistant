"use client";

import React, { useState } from "react";
import { CreditCard, ExternalLink, AlertCircle, CheckCircle } from "lucide-react";

interface PaymentGatewayWidgetProps {
  transactionUrl: string;
  transactionId: string;
  recipientName?: string;
  sendingAmount?: string;
  recipientAmount?: string;
  payoutMethod?: string;
}

export function PaymentGatewayWidget({
  transactionUrl,
  transactionId,
  recipientName,
  sendingAmount,
  recipientAmount,
  payoutMethod,
}: PaymentGatewayWidgetProps) {
  const [isLoading, setIsLoading] = useState(true);
  const [isFullScreen, setIsFullScreen] = useState(false);
  const [iframeBlocked, setIframeBlocked] = useState(false);

  const handleIframeLoad = () => {
    setIsLoading(false);
  };

  const handleIframeError = () => {
    setIsLoading(false);
    setIframeBlocked(true);
  };

  const openInNewTab = () => {
    window.open(transactionUrl, "_blank", "noopener,noreferrer");
  };

  const toggleFullScreen = () => {
    setIsFullScreen(!isFullScreen);
  };

  // Auto-detect if iframe is blocked after 3 seconds
  React.useEffect(() => {
    const timer = setTimeout(() => {
      if (isLoading) {
        setIframeBlocked(true);
        setIsLoading(false);
      }
    }, 3000);

    return () => clearTimeout(timer);
  }, [isLoading]);

  return (
    <div
      className={`border border-blue-200 rounded-lg bg-white dark:bg-gray-800 dark:border-gray-700 shadow-sm transition-all ${
        isFullScreen ? "fixed inset-4 z-50" : "w-full max-w-4xl mx-auto"
      }`}
    >
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-500 to-blue-600 dark:from-blue-600 dark:to-blue-700 text-white p-4 rounded-t-lg">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="bg-white/20 p-2 rounded-lg">
              <CreditCard className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-semibold text-lg">Complete Your Payment</h3>
              <p className="text-sm text-blue-100">Transaction ID: {transactionId}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={toggleFullScreen}
              className="bg-white/20 hover:bg-white/30 px-3 py-1.5 rounded-lg text-sm transition-colors"
              title={isFullScreen ? "Exit Full Screen" : "Full Screen"}
            >
              {isFullScreen ? "Exit Full Screen" : "⛶ Full Screen"}
            </button>
            <button
              onClick={openInNewTab}
              className="bg-white/20 hover:bg-white/30 p-2 rounded-lg transition-colors"
              title="Open in New Tab"
            >
              <ExternalLink className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Transaction Summary */}
        {recipientName && (
          <div className="mt-3 pt-3 border-t border-white/20 text-sm">
            <div className="flex justify-between items-center">
              <span className="text-blue-100">To: {recipientName}</span>
              {sendingAmount && recipientAmount && (
                <span className="font-medium">
                  {sendingAmount} → {recipientAmount}
                </span>
              )}
            </div>
            {payoutMethod && (
              <div className="text-blue-100 mt-1">via {payoutMethod}</div>
            )}
          </div>
        )}
      </div>

      {/* Instructions */}
      <div className="bg-blue-50 dark:bg-gray-700 border-b border-blue-100 dark:border-gray-600 p-3">
        <div className="flex items-start gap-2">
          <AlertCircle className="w-5 h-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
          <div className="text-sm text-gray-700 dark:text-gray-300">
            <p className="font-medium text-blue-900 dark:text-blue-300 mb-1">
              Please complete the payment steps below:
            </p>
            <ul className="list-disc list-inside space-y-1 text-gray-600 dark:text-gray-400">
              <li>Follow the instructions on the payment page</li>
              <li>Enter your payment details securely</li>
              <li>Wait for the confirmation message</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Loading Indicator */}
      {isLoading && !iframeBlocked && (
        <div className="absolute inset-0 flex items-center justify-center bg-white dark:bg-gray-800 z-10 rounded-b-lg">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600 dark:text-gray-400">Loading payment gateway...</p>
          </div>
        </div>
      )}

      {/* Iframe Blocked Message */}
      {iframeBlocked ? (
        <div className={`relative bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-gray-900 dark:to-gray-800 ${isFullScreen ? "h-[calc(100vh-240px)]" : "h-[600px]"} flex items-center justify-center p-8`}>
          <div className="text-center max-w-md">
            <div className="bg-white dark:bg-gray-700 rounded-full w-20 h-20 flex items-center justify-center mx-auto mb-6 shadow-lg">
              <ExternalLink className="w-10 h-10 text-blue-600 dark:text-blue-400" />
            </div>
            
            <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-3">
              Payment Gateway Ready
            </h3>
            
            <p className="text-gray-600 dark:text-gray-300 mb-6 leading-relaxed">
              For security reasons, the payment gateway cannot be embedded. 
              Click the button below to complete your payment in a new secure window.
            </p>

            <button
              onClick={openInNewTab}
              className="bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white font-semibold px-8 py-4 rounded-lg shadow-lg hover:shadow-xl transition-all duration-200 flex items-center gap-3 mx-auto group"
            >
              <span>Open Payment Gateway</span>
              <ExternalLink className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </button>

            <div className="mt-6 bg-blue-100 dark:bg-gray-600 rounded-lg p-4">
              <p className="text-sm text-gray-700 dark:text-gray-300">
                <strong>Transaction ID:</strong> {transactionId}
              </p>
              {recipientName && (
                <p className="text-sm text-gray-700 dark:text-gray-300 mt-2">
                  <strong>To:</strong> {recipientName}
                </p>
              )}
              {sendingAmount && recipientAmount && (
                <p className="text-sm text-gray-700 dark:text-gray-300 mt-2">
                  <strong>Amount:</strong> {sendingAmount} → {recipientAmount}
                </p>
              )}
            </div>

            <div className="mt-6 flex items-center justify-center gap-2 text-sm text-gray-500 dark:text-gray-400">
              <CheckCircle className="w-4 h-4 text-green-500" />
              <span>Secure SSL encrypted connection</span>
            </div>
          </div>
        </div>
      ) : (
        /* Embedded Payment Gateway */
        <div className={`relative bg-gray-100 dark:bg-gray-900 ${isFullScreen ? "h-[calc(100vh-240px)]" : "h-[600px]"}`}>
          <iframe
            src={transactionUrl}
            className="w-full h-full border-0 rounded-b-lg"
            onLoad={handleIframeLoad}
            onError={handleIframeError}
            title="Payment Gateway"
            sandbox="allow-same-origin allow-scripts allow-forms allow-popups allow-popups-to-escape-sandbox"
            allow="payment"
          />
        </div>
      )}

      {/* Footer Help */}
      <div className="bg-gray-50 dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 p-3 rounded-b-lg">
        <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
          <div className="flex items-center gap-2">
            <CheckCircle className="w-4 h-4 text-green-500" />
            <span>Secure payment gateway</span>
          </div>
          <div className="flex items-center gap-4">
            <span>Having issues?</span>
            <button
              onClick={openInNewTab}
              className="text-blue-600 dark:text-blue-400 hover:underline font-medium"
            >
              Open in new window
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
