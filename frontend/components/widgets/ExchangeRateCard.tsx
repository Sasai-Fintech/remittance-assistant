"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ArrowRight, DollarSign, TrendingUp, Banknote, Send } from "lucide-react";
import { useState } from "react";

interface ExchangeProduct {
  productName: string;
  productType: string;
  productGroupName: string;
  rate: string;
  reverseRate: string;
  fees: string;
  vat: string;
  surcharges: string;
  amountToPay: string;
  receivingAmount: string;
  sendingAmount: string;
  sendingMinLimit: string;
  sendingMaxLimit: string;
  receivingMinLimit: string;
  receivingMaxLimit: string;
  discountInSendingCurrency?: string;
  promocode?: string | null;
}

interface ExchangeRateCardProps {
  sendingCountry: string;
  receivingCountry: string;
  sendingCurrency: string;
  receivingCurrency: string;
  products: ExchangeProduct[];
  requestInfo?: {
    sending_country: string;
    sending_currency: string;
    receiving_country: string;
    receiving_currency: string;
    amount: number;
    receive: boolean;
  };
  onSendMoney?: (amount: number, selectedProduct: ExchangeProduct) => void;
}

export function ExchangeRateCard({
  sendingCountry,
  receivingCountry,
  sendingCurrency,
  receivingCurrency,
  products,
  requestInfo,
  onSendMoney,
}: ExchangeRateCardProps) {
  const [amount, setAmount] = useState<string>("100");
  const [selectedProduct, setSelectedProduct] = useState<ExchangeProduct>(products[0]);

  if (!products || products.length === 0) {
    return (
      <Card className="w-full max-w-2xl mx-auto">
        <CardContent className="pt-6">
          <p className="text-center text-gray-600 dark:text-gray-400">
            No exchange rates available for this route.
          </p>
        </CardContent>
      </Card>
    );
  }

  const mainProduct = selectedProduct;
  const rate = parseFloat(mainProduct.rate);
  const amountNum = parseFloat(amount) || 0;
  
  // Calculate amounts based on rate for 1 unit
  const receiveAmount = amountNum * rate;
  const fees = parseFloat(mainProduct.fees);
  const totalToPay = amountNum + fees;

  const handleSendMoney = () => {
    if (onSendMoney && amountNum > 0) {
      onSendMoney(amountNum, mainProduct);
    }
  };

  return (
    <Card className="w-full max-w-2xl mx-auto bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-blue-950 dark:to-indigo-950 shadow-xl border-2 border-blue-200 dark:border-blue-800">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-xl">
          <DollarSign className="h-6 w-6 text-blue-600 dark:text-blue-400" />
          Exchange Rate: {sendingCountry} → {receivingCountry}
        </CardTitle>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          Current rates and fees for your transfer
        </p>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Amount Input Section */}
        <div className="bg-white dark:bg-zinc-800 p-6 rounded-lg shadow-md space-y-4">
          <div className="space-y-2">
            <Label htmlFor="amount" className="text-sm font-medium">
              How much do you want to send?
            </Label>
            <div className="flex gap-2">
              <div className="relative flex-1">
                <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 font-medium">
                  {sendingCurrency}
                </span>
                <Input
                  id="amount"
                  type="number"
                  min="0"
                  step="0.01"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  className="pl-16 text-lg font-semibold"
                  placeholder="100"
                />
              </div>
            </div>
          </div>

          {/* Live Calculation Display */}
          <div className="flex items-center justify-between pt-2">
            <div className="text-center flex-1">
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">You Send</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                {sendingCurrency} {amountNum.toFixed(2)}
              </p>
            </div>
            
            <div className="px-4">
              <ArrowRight className="h-6 w-6 text-blue-600 dark:text-blue-400" />
            </div>
            
            <div className="text-center flex-1">
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">They Receive</p>
              <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                {receivingCurrency} {receiveAmount.toFixed(2)}
              </p>
            </div>
          </div>
        </div>

        {/* Best Rate Badge */}
        <div className="flex justify-center">
          <Badge className="bg-green-500 text-white px-4 py-1 text-sm font-medium">
            ⭐ Best Rate via {mainProduct.productName}
          </Badge>
        </div>

        {/* Rate Details Grid */}
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div className="bg-white dark:bg-zinc-800 p-4 rounded-lg">
            <div className="flex items-center gap-2 mb-1">
              <TrendingUp className="h-4 w-4 text-blue-600" />
              <p className="text-gray-600 dark:text-gray-400">Exchange Rate</p>
            </div>
            <p className="font-semibold text-lg">
              1 {sendingCurrency} = {rate.toFixed(4)} {receivingCurrency}
            </p>
          </div>
          
          <div className="bg-white dark:bg-zinc-800 p-4 rounded-lg">
            <div className="flex items-center gap-2 mb-1">
              <Banknote className="h-4 w-4 text-orange-600" />
              <p className="text-gray-600 dark:text-gray-400">Transfer Fee</p>
            </div>
            <p className="font-semibold text-lg">
              {sendingCurrency} {fees.toFixed(2)}
            </p>
          </div>
          
          <div className="bg-white dark:bg-zinc-800 p-4 rounded-lg">
            <p className="text-gray-600 dark:text-gray-400 mb-1">Total to Pay</p>
            <p className="font-semibold text-xl text-blue-600 dark:text-blue-400">
              {sendingCurrency} {totalToPay.toFixed(2)}
            </p>
          </div>
          
          <div className="bg-white dark:bg-zinc-800 p-4 rounded-lg">
            <p className="text-gray-600 dark:text-gray-400 mb-1">Delivery Method</p>
            <p className="font-semibold text-lg">{mainProduct.productGroupName}</p>
            <p className="text-xs text-gray-500 mt-1">{mainProduct.productName}</p>
          </div>
        </div>

        {/* Send Money Button */}
        <Button
          onClick={handleSendMoney}
          disabled={amountNum <= 0}
          className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-semibold py-6 text-lg shadow-lg"
        >
          <Send className="mr-2 h-5 w-5" />
          Send Money ({sendingCurrency} {amountNum.toFixed(2)})
        </Button>

        {/* Transfer Limits */}
        <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
          <p className="text-sm font-medium text-gray-900 dark:text-gray-100 mb-2">
            💡 Transfer Limits
          </p>
          <div className="grid grid-cols-2 gap-2 text-xs text-gray-700 dark:text-gray-300">
            <div>
              <span className="font-medium">Min:</span> {sendingCurrency} {parseFloat(mainProduct.sendingMinLimit).toFixed(2)}
            </div>
            <div>
              <span className="font-medium">Max:</span> {sendingCurrency} {parseFloat(mainProduct.sendingMaxLimit).toFixed(2)}
            </div>
          </div>
        </div>

        {/* Additional Products */}
        {products.length > 1 && (
          <div className="pt-4 border-t border-gray-300 dark:border-gray-700">
            <p className="text-sm font-medium mb-3 text-gray-900 dark:text-gray-100">
              📋 Other delivery options:
            </p>
            <div className="space-y-2">
              {products.slice(1).map((product, idx) => (
                <div 
                  key={idx} 
                  className="flex justify-between items-center text-sm bg-gray-50 dark:bg-zinc-900 p-3 rounded-lg hover:bg-gray-100 dark:hover:bg-zinc-800 transition-colors"
                >
                  <div className="flex-1">
                    <p className="font-medium text-gray-900 dark:text-gray-100">
                      {product.productName}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      {product.productGroupName}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="font-medium text-gray-900 dark:text-gray-100">
                      Rate: {parseFloat(product.rate).toFixed(4)}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      Fee: {sendingCurrency} {parseFloat(product.fees).toFixed(2)}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Footer Note */}
        <div className="text-xs text-center text-gray-500 dark:text-gray-400 pt-2">
          💳 Rates are indicative and may change. Final rate confirmed at payment.
        </div>
      </CardContent>
    </Card>
  );
}
