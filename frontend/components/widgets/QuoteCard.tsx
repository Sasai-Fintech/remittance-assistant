import React from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { 
  ArrowRight, 
  DollarSign, 
  TrendingUp, 
  Receipt, 
  Wallet,
  AlertCircle,
  CheckCircle,
  Banknote,
  Smartphone
} from "lucide-react";

interface QuoteData {
  // Step 2 fields (from rate calculation)
  calculationId?: string;  // Optional - from Step 2
  calculateId?: string;
  sendingAmount?: string;
  sendingAmountInitial?: string;
  recipientAmount?: string;
  recipientAmountInitial?: string;
  rate?: string;
  rateInitial?: string;
  reverseRate?: string;
  reverseRateInitial?: string;
  fees?: string;
  feesInitial?: string;
  vat?: string;
  surcharges?: string;
  amountToPay?: string;
  amountToPayInitial?: string;
  // Step 3 fields (from quote generation)
  transactionId?: string;  // New - from Step 3 (this is the quote ID)
  transactionDate?: string;
  expiryDate?: string;
  promocode?: string | null;
  // Additional fields from our tool
  recipientName?: string;
  payoutMethod?: string;
  productId?: number;
}

interface QuoteCardProps {
  quote: QuoteData;
  onConfirm?: (quoteId: string) => void;  // Changed from calculationId to quoteId
  onCancel?: () => void;
}

const getPayoutIcon = (method?: string) => {
  if (!method) return <DollarSign className="h-5 w-5" />;
  if (method.toLowerCase().includes('cash')) {
    return <Banknote className="h-5 w-5" />;
  } else if (method.toLowerCase().includes('mobile') || method.toLowerCase().includes('ecocash')) {
    return <Smartphone className="h-5 w-5" />;
  }
  return <DollarSign className="h-5 w-5" />;
};

export const QuoteCard: React.FC<QuoteCardProps> = ({ 
  quote, 
  onConfirm, 
  onCancel 
}) => {
  // Parse amounts with fallbacks
  const sendingAmount = parseFloat(quote.sendingAmount || '0');
  const recipientAmount = parseFloat(quote.recipientAmount || '0');
  const rate = parseFloat(quote.rate || '0');
  const fees = parseFloat(quote.fees || '0');
  const vat = parseFloat(quote.vat || '0');
  const surcharges = parseFloat(quote.surcharges || '0');
  const totalToPay = parseFloat(quote.amountToPay || '0');
  
  // The quote ID is transactionId (from Step 3)
  const quoteId = quote.transactionId || quote.calculationId || 'N/A';

  return (
    <Card className="w-full max-w-2xl mx-auto shadow-xl border-2 border-blue-200">
      <CardHeader className="bg-gradient-to-r from-blue-500 to-purple-600 text-white">
        <CardTitle className="flex items-center gap-2">
          <TrendingUp className="h-6 w-6" />
          Remittance Quote
        </CardTitle>
        {quote.recipientName && (
          <p className="text-sm text-blue-100 mt-1">
            Sending to: <strong>{quote.recipientName}</strong>
            {quote.payoutMethod && ` via ${quote.payoutMethod}`}
          </p>
        )}
      </CardHeader>

      <CardContent className="p-6 space-y-6">
        {/* Amount Summary - Big Numbers */}
        <div className="flex items-center justify-between p-4 bg-blue-50 dark:bg-blue-950 rounded-lg">
          <div className="text-center flex-1">
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">You Send</p>
            <p className="text-3xl font-bold text-blue-600">
              R {sendingAmount.toFixed(2)}
            </p>
            <p className="text-xs text-gray-500 mt-1">ZAR</p>
          </div>
          
          <div className="flex-shrink-0 mx-4">
            <ArrowRight className="h-8 w-8 text-gray-400" />
          </div>
          
          <div className="text-center flex-1">
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">They Receive</p>
            <p className="text-3xl font-bold text-green-600">
              $ {recipientAmount.toFixed(2)}
            </p>
            <p className="text-xs text-gray-500 mt-1">USD</p>
          </div>
        </div>

        {/* Exchange Rate */}
        <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-900 rounded-lg">
          <div className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-gray-600" />
            <span className="font-medium">Exchange Rate</span>
          </div>
          <div className="text-right">
            <p className="font-bold">1 ZAR = ${rate.toFixed(4)} USD</p>
            <p className="text-sm text-gray-500">1 USD = R{parseFloat(quote.reverseRate || '0').toFixed(4)} ZAR</p>
          </div>
        </div>

        {/* Payout Method */}
        {quote.payoutMethod && (
          <div className="flex items-center justify-between p-3 bg-purple-50 dark:bg-purple-950 rounded-lg">
            <div className="flex items-center gap-2">
              {getPayoutIcon(quote.payoutMethod)}
              <span className="font-medium">Payout Method</span>
            </div>
            <Badge variant="secondary" className="text-sm">
              {quote.payoutMethod}
            </Badge>
          </div>
        )}

        {/* Cost Breakdown */}
        <div className="space-y-3 border-t pt-4">
          <h3 className="font-semibold flex items-center gap-2 text-gray-700 dark:text-gray-300">
            <Receipt className="h-4 w-4" />
            Cost Breakdown
          </h3>
          
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Sending Amount:</span>
              <span className="font-medium">R {sendingAmount.toFixed(2)}</span>
            </div>
            
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Transaction Fee:</span>
              <span className="font-medium text-orange-600">+ R {fees.toFixed(2)}</span>
            </div>
            
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">VAT:</span>
              <span className="font-medium text-orange-600">+ R {vat.toFixed(2)}</span>
            </div>
            
            {surcharges > 0 && (
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">Surcharges:</span>
                <span className="font-medium text-orange-600">+ R {surcharges.toFixed(2)}</span>
              </div>
            )}
            
            <div className="border-t pt-2 flex justify-between font-bold text-lg">
              <span className="flex items-center gap-2">
                <Wallet className="h-5 w-5" />
                Total to Pay:
              </span>
              <span className="text-blue-600">R {totalToPay.toFixed(2)}</span>
            </div>
          </div>
        </div>

        {/* Info Banner */}
        <div className="flex items-start gap-2 p-3 bg-blue-50 dark:bg-blue-950 border border-blue-200 dark:border-blue-800 rounded-lg">
          <AlertCircle className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
          <div className="text-sm text-gray-700 dark:text-gray-300">
            <p className="font-medium mb-1">Quick Facts:</p>
            <ul className="space-y-1 text-xs">
              <li>• Quote valid for 15 minutes</li>
              <li>• Exchange rate locked at time of confirmation</li>
              <li>• Recipient receives funds within minutes</li>
            </ul>
          </div>
        </div>

        {/* Quote ID for reference */}
        <div className="text-xs text-gray-500 text-center">
          Quote ID: {quoteId.length > 16 ? quoteId.substring(0, 16) + '...' : quoteId}
        </div>
      </CardContent>

      {(onConfirm || onCancel) && (
        <CardFooter className="flex gap-3 p-6 bg-gray-50 dark:bg-gray-900">
          {onCancel && (
            <Button 
              variant="outline" 
              className="flex-1"
              onClick={onCancel}
            >
              Cancel
            </Button>
          )}
          {onConfirm && (
            <Button 
              className="flex-1 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700"
              onClick={() => onConfirm(quoteId)}
            >
              <CheckCircle className="h-4 w-4 mr-2" />
              Confirm & Send Money
            </Button>
          )}
        </CardFooter>
      )}
    </Card>
  );
};
