"use client";

import { CashFlowOverview } from "@/types/schemas";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface CashFlowBarChartProps {
  overview: CashFlowOverview;
}

export function CashFlowBarChart({ overview }: CashFlowBarChartProps) {
  const { period, currency, categories } = overview;
  
  // Find max amount for scaling
  const maxAmount = Math.max(...categories.map(cat => cat.amount));
  
  // Format currency
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: currency || "USD",
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  return (
    <Card className="w-full max-w-2xl mx-auto shadow-lg">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-xl font-semibold text-gray-800">
            CASH FLOW
          </CardTitle>
          <div className="text-sm text-gray-500">
            {period.label}
          </div>
        </div>
        {period.start_date && period.end_date && (
          <div className="text-sm text-gray-500 mt-1">
            {new Date(period.start_date).toLocaleDateString("en-GB", {
              day: "numeric",
              month: "short",
              year: "numeric",
            })} - {new Date(period.end_date).toLocaleDateString("en-GB", {
              day: "numeric",
              month: "short",
              year: "numeric",
            })}
          </div>
        )}
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Bar Chart */}
        <div className="space-y-4">
          {categories.map((cat, index) => {
            const percentage = (cat.amount / maxAmount) * 100;
            
            return (
              <div key={index} className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div
                      className="w-3 h-3 rounded"
                      style={{ backgroundColor: cat.color }}
                    />
                    <span className="text-sm font-medium text-gray-700">
                      {cat.name}
                    </span>
                  </div>
                  <span className="text-sm font-semibold text-gray-800">
                    {formatCurrency(cat.amount)}
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-8 overflow-hidden">
                  <div
                    className="h-full rounded-full transition-all duration-500 flex items-center justify-end pr-2"
                    style={{
                      width: `${percentage}%`,
                      backgroundColor: cat.color,
                    }}
                  >
                    {percentage > 15 && (
                      <span className="text-xs font-semibold text-white">
                        {formatCurrency(cat.amount)}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Summary */}
        <div className="pt-4 border-t border-gray-200">
          <div className="flex items-center justify-between">
            <span className="text-sm font-semibold text-gray-700">Total</span>
            <span className="text-lg font-bold text-gray-800">
              {formatCurrency(categories.reduce((sum, cat) => sum + cat.amount, 0))}
            </span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

