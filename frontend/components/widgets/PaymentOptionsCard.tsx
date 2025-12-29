import React from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { CreditCard, Building2, Wallet, Smartphone } from "lucide-react";

export interface PaymentOption {
  code: string;
  name: string;
  description?: string;
  icon?: string;
}

export interface PaymentOptionsData {
  paymentOptions?: PaymentOption[];
  success?: boolean;
  error?: string;
}

interface PaymentOptionsCardProps {
  options: PaymentOptionsData;
  onSelectPayment: (paymentMethodCode: string, paymentMethodName: string) => void;
}

/**
 * Payment Options Selection Card - displays available payment methods
 * User must select one before completing the transaction
 */
export function PaymentOptionsCard({ options, onSelectPayment }: PaymentOptionsCardProps) {
  // Extract payment options from response
  const paymentOptions = options?.paymentOptions || [];

  // Handle error state
  if (options?.error || !options?.success) {
    return (
      <Card className="w-full max-w-md border-red-200 dark:border-red-800">
        <CardHeader>
          <CardTitle className="text-red-600 dark:text-red-400">❌ Payment Options Error</CardTitle>
          <CardDescription>{options?.error || "Failed to load payment options"}</CardDescription>
        </CardHeader>
      </Card>
    );
  }

  // Handle no options available
  if (paymentOptions.length === 0) {
    return (
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>No Payment Options Available</CardTitle>
          <CardDescription>
            No payment methods are currently available. Please try again later.
          </CardDescription>
        </CardHeader>
      </Card>
    );
  }

  // Helper function to get icon based on payment method code or name
  const getPaymentIcon = (option: PaymentOption) => {
    const code = option.code?.toUpperCase() || "";
    const name = option.name?.toUpperCase() || "";

    if (code.includes("EFT") || name.includes("BANK") || name.includes("TRANSFER")) {
      return <Building2 className="h-6 w-6" />;
    }
    if (code.includes("CARD") || name.includes("CARD") || name.includes("CREDIT") || name.includes("DEBIT")) {
      return <CreditCard className="h-6 w-6" />;
    }
    if (code.includes("WALLET") || name.includes("WALLET") || name.includes("MOBILE")) {
      return <Wallet className="h-6 w-6" />;
    }
    if (name.includes("PHONE") || name.includes("MOBILE")) {
      return <Smartphone className="h-6 w-6" />;
    }
    // Default icon
    return <CreditCard className="h-6 w-6" />;
  };

  return (
    <Card className="w-full max-w-md shadow-lg">
      <CardHeader className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-950 dark:to-indigo-950">
        <CardTitle className="text-2xl font-bold">💳 Select Payment Method</CardTitle>
        <CardDescription className="text-base">
          Choose how you'd like to pay for this transfer
        </CardDescription>
      </CardHeader>
      <CardContent className="p-6 space-y-3">
        {paymentOptions.map((option) => (
          <div
            key={option.code}
            className="border rounded-lg p-4 hover:border-blue-500 hover:shadow-md transition-all cursor-pointer group"
            onClick={() => onSelectPayment(option.code, option.name)}
          >
            <div className="flex items-start gap-4">
              <div className="p-3 rounded-lg bg-blue-50 dark:bg-blue-900/20 group-hover:bg-blue-100 dark:group-hover:bg-blue-900/40 transition-colors">
                {getPaymentIcon(option)}
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="font-semibold text-lg mb-1 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                  {option.name}
                </h3>
                {option.description && (
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {option.description}
                  </p>
                )}
                <p className="text-xs text-gray-500 dark:text-gray-500 mt-2">
                  Code: {option.code}
                </p>
              </div>
              <Button
                variant="outline"
                size="sm"
                className="self-center group-hover:bg-blue-600 group-hover:text-white group-hover:border-blue-600 transition-colors"
                onClick={(e) => {
                  e.stopPropagation();
                  onSelectPayment(option.code, option.name);
                }}
              >
                Select
              </Button>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
