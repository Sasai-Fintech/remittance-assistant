"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { CheckCircle2, HeadphonesIcon } from "lucide-react";

export interface Transaction {
  id: string;
  date?: string;
  merchant?: string;
  description?: string;
  amount: number;
  currency?: string;
}

interface TransactionCardProps {
  transaction: Transaction;
  onSupportClick?: (transaction: Transaction) => void;
}

export function TransactionCard({ transaction, onSupportClick }: TransactionCardProps) {
  const displayDate = transaction.date || "N/A";
  const displayName = transaction.merchant || transaction.description || "Transaction";
  const currency = transaction.currency || "USD";
  const amount = transaction.amount || 0;
  const isNegative = amount < 0;
  const isPositive = amount > 0;

  // Format date to be more readable (e.g., "19 Nov 2025")
  const formatDate = (dateStr: string) => {
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString("en-GB", { 
        day: "numeric", 
        month: "short", 
        year: "numeric" 
      });
    } catch {
      return dateStr;
    }
  };

  const handleSupportClick = () => {
    if (onSupportClick) {
      onSupportClick(transaction);
    }
  };

  return (
    <Card className="min-w-[240px] sm:min-w-[260px] md:min-w-[280px] max-w-[240px] sm:max-w-[260px] md:max-w-[280px] flex-shrink-0 bg-white dark:bg-zinc-800 border border-gray-200 dark:border-zinc-700 card-hover">
      <CardContent className="p-2.5 sm:p-3 md:p-4">
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-2 flex-1 min-w-0">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center flex-shrink-0">
              <span className="text-white font-semibold text-sm">
                {displayName.charAt(0).toUpperCase()}
              </span>
            </div>
            <div className="flex-1 min-w-0">
              <p className="font-semibold text-sm text-gray-900 dark:text-gray-100 truncate">
                {displayName}
              </p>
              <div className="flex items-center gap-1.5 mt-0.5">
                <CheckCircle2 className="w-3 h-3 text-green-500 flex-shrink-0" />
                <span className="text-xs text-gray-500 dark:text-gray-400">
                  paid on {formatDate(displayDate)}
                </span>
              </div>
            </div>
          </div>
        </div>

        <div className="flex items-center justify-between mb-3">
          <div className="flex-1">
            <p className={`text-lg font-bold ${isNegative ? "text-red-600 dark:text-red-400" : "text-green-600 dark:text-green-400"}`}>
              {isNegative ? "-" : isPositive ? "+" : ""}
              {Math.abs(amount).toLocaleString("en-US", { 
                style: "currency", 
                currency,
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
              })}
            </p>
          </div>
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8 rounded-full hover:bg-indigo-100 dark:hover:bg-indigo-900/30 text-gray-600 dark:text-gray-400 hover:text-indigo-600 dark:hover:text-indigo-400"
            onClick={handleSupportClick}
            aria-label={`Get support for transaction ${transaction.id}`}
          >
            <HeadphonesIcon className="h-4 w-4" />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

