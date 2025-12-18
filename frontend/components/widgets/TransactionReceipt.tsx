import React from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { 
  CheckCircle2, 
  Calendar,
  Clock,
  User,
  DollarSign,
  Receipt,
  Download,
  Share2,
  AlertCircle,
  Copy,
  Banknote,
  Smartphone
} from "lucide-react";

interface TransactionData {
  transactionId: string;
  transactionDate: string;
  expiryDate: string;
  promocode?: string | null;
  // Additional enriched fields from our tool
  recipientName?: string;
  payoutMethod?: string;
  sendingAmount?: string;
  recipientAmount?: string;
}

interface TransactionReceiptProps {
  transaction: TransactionData;
  onShare?: () => void;
  onDownload?: () => void;
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

const formatDate = (dateStr: string) => {
  try {
    const date = new Date(dateStr);
    return date.toLocaleString('en-ZA', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  } catch {
    return dateStr;
  }
};

const copyToClipboard = (text: string) => {
  navigator.clipboard.writeText(text);
};

export const TransactionReceipt: React.FC<TransactionReceiptProps> = ({ 
  transaction, 
  onShare, 
  onDownload 
}) => {
  const [copied, setCopied] = React.useState(false);

  const handleCopy = () => {
    copyToClipboard(transaction.transactionId);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <Card className="w-full max-w-2xl mx-auto shadow-2xl border-2 border-green-300">
      {/* Success Header */}
      <CardHeader className="bg-gradient-to-r from-green-500 to-emerald-600 text-white">
        <div className="flex items-center justify-center mb-4">
          <div className="bg-white rounded-full p-3">
            <CheckCircle2 className="h-12 w-12 text-green-500" />
          </div>
        </div>
        <CardTitle className="text-center text-2xl">
          Transfer Successful!
        </CardTitle>
        <p className="text-center text-green-100 mt-2">
          Your money is on its way
        </p>
      </CardHeader>

      <CardContent className="p-6 space-y-6">
        {/* Transaction ID - Prominent */}
        <div className="bg-blue-50 dark:bg-blue-950 p-4 rounded-lg border-2 border-blue-200 dark:border-blue-800">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Transaction ID</p>
              <p className="text-xl font-mono font-bold text-blue-600">{transaction.transactionId}</p>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={handleCopy}
              className="flex items-center gap-2"
            >
              {copied ? (
                <>
                  <CheckCircle2 className="h-4 w-4" />
                  Copied!
                </>
              ) : (
                <>
                  <Copy className="h-4 w-4" />
                  Copy
                </>
              )}
            </Button>
          </div>
        </div>

        {/* Recipient Info */}
        {transaction.recipientName && (
          <div className="flex items-center gap-3 p-4 bg-gray-50 dark:bg-gray-900 rounded-lg">
            <User className="h-10 w-10 text-purple-600" />
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Recipient</p>
              <p className="text-lg font-semibold">{transaction.recipientName}</p>
              {transaction.payoutMethod && (
                <div className="flex items-center gap-2 mt-1">
                  {getPayoutIcon(transaction.payoutMethod)}
                  <Badge variant="secondary" className="text-xs">
                    {transaction.payoutMethod}
                  </Badge>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Amount Summary */}
        {transaction.sendingAmount && transaction.recipientAmount && (
          <div className="grid grid-cols-2 gap-4">
            <div className="text-center p-4 bg-orange-50 dark:bg-orange-950 rounded-lg border border-orange-200 dark:border-orange-800">
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">You Sent</p>
              <p className="text-2xl font-bold text-orange-600">
                R {parseFloat(transaction.sendingAmount).toFixed(2)}
              </p>
              <p className="text-xs text-gray-500 mt-1">ZAR</p>
            </div>
            <div className="text-center p-4 bg-green-50 dark:bg-green-950 rounded-lg border border-green-200 dark:border-green-800">
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">They Receive</p>
              <p className="text-2xl font-bold text-green-600">
                $ {parseFloat(transaction.recipientAmount).toFixed(2)}
              </p>
              <p className="text-xs text-gray-500 mt-1">USD</p>
            </div>
          </div>
        )}

        {/* Transaction Details */}
        <div className="space-y-3 border-t pt-4">
          <h3 className="font-semibold flex items-center gap-2 text-gray-700 dark:text-gray-300">
            <Receipt className="h-4 w-4" />
            Transaction Details
          </h3>
          
          <div className="space-y-2 text-sm">
            <div className="flex items-center justify-between py-2 border-b">
              <span className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                <Calendar className="h-4 w-4" />
                Transaction Date:
              </span>
              <span className="font-medium">{formatDate(transaction.transactionDate)}</span>
            </div>
            
            <div className="flex items-center justify-between py-2 border-b">
              <span className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                <Clock className="h-4 w-4" />
                Expires On:
              </span>
              <span className="font-medium">{formatDate(transaction.expiryDate)}</span>
            </div>
            
            {transaction.promocode && (
              <div className="flex items-center justify-between py-2">
                <span className="text-gray-600 dark:text-gray-400">Promo Code:</span>
                <Badge variant="success">{transaction.promocode}</Badge>
              </div>
            )}
          </div>
        </div>

        {/* Important Notice */}
        <div className="flex items-start gap-2 p-4 bg-blue-50 dark:bg-blue-950 border border-blue-200 dark:border-blue-800 rounded-lg">
          <AlertCircle className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
          <div className="text-sm text-gray-700 dark:text-gray-300">
            <p className="font-medium mb-2">What happens next?</p>
            <ul className="space-y-1 text-xs">
              <li>• Your recipient will be notified shortly</li>
              <li>• Funds typically arrive within minutes</li>
              <li>• Transaction expires in 24 hours if not collected</li>
              <li>• Keep this receipt for your records</li>
            </ul>
          </div>
        </div>

        {/* Reference number note */}
        <div className="text-center text-xs text-gray-500">
          Reference this transaction ID for any inquiries or support
        </div>
      </CardContent>

      {/* Actions Footer */}
      {(onShare || onDownload) && (
        <CardFooter className="flex gap-3 p-6 bg-gray-50 dark:bg-gray-900 border-t">
          {onDownload && (
            <Button 
              variant="outline" 
              className="flex-1"
              onClick={onDownload}
            >
              <Download className="h-4 w-4 mr-2" />
              Download Receipt
            </Button>
          )}
          {onShare && (
            <Button 
              variant="outline" 
              className="flex-1"
              onClick={onShare}
            >
              <Share2 className="h-4 w-4 mr-2" />
              Share
            </Button>
          )}
        </CardFooter>
      )}
    </Card>
  );
};
