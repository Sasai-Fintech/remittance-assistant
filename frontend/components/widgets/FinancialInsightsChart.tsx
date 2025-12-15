"use client";

import { FinancialInsights, FinancialInsightsDetail } from "@/types/schemas";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface FinancialInsightsChartProps {
  insights: FinancialInsights;
}

export function FinancialInsightsChart({ insights }: FinancialInsightsChartProps) {
  // Don't render if it's overview - that should use CashFlowBarChart
  if (insights.category === "overview") {
    return null;
  }
  
  // Type guard: ensure it's FinancialInsightsDetail (not CashFlowOverview)
  const detail = insights as FinancialInsightsDetail;
  const { category, period, total_amount, currency, categories, upcoming_spends } = detail;
  
  // Calculate angles for donut chart
  let currentAngle = -90; // Start at top
  const total = categories.reduce((sum, cat) => sum + cat.percentage, 0);
  
  // Format currency
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: currency || "USD",
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  // Generate SVG path for donut chart
  const generateDonutPath = () => {
    const radius = 80;
    const centerX = 100;
    const centerY = 100;
    const strokeWidth = 20;
    const innerRadius = radius - strokeWidth;
    
    const paths = categories.map((cat, index) => {
      const percentage = cat.percentage;
      const angle = (percentage / 100) * 360;
      const startAngle = currentAngle;
      const endAngle = currentAngle + angle;
      
      currentAngle = endAngle;
      
      // Convert angles to radians
      const startAngleRad = (startAngle * Math.PI) / 180;
      const endAngleRad = (endAngle * Math.PI) / 180;
      
      // Calculate start and end points on outer circle
      const x1 = centerX + radius * Math.cos(startAngleRad);
      const y1 = centerY + radius * Math.sin(startAngleRad);
      const x2 = centerX + radius * Math.cos(endAngleRad);
      const y2 = centerY + radius * Math.sin(endAngleRad);
      
      // Calculate start and end points on inner circle
      const x3 = centerX + innerRadius * Math.cos(endAngleRad);
      const y3 = centerY + innerRadius * Math.sin(endAngleRad);
      const x4 = centerX + innerRadius * Math.cos(startAngleRad);
      const y4 = centerY + innerRadius * Math.sin(startAngleRad);
      
      // Create path
      const largeArcFlag = angle > 180 ? 1 : 0;
      const path = `M ${x1} ${y1} A ${radius} ${radius} 0 ${largeArcFlag} 1 ${x2} ${y2} L ${x3} ${y3} A ${innerRadius} ${innerRadius} 0 ${largeArcFlag} 0 ${x4} ${y4} Z`;
      
      return (
        <path
          key={index}
          d={path}
          fill={cat.color}
          stroke="white"
          strokeWidth="2"
        />
      );
    });
    
    return paths;
  };

  const categoryTitle = category.charAt(0).toUpperCase() + category.slice(1);

  return (
    <Card className="w-full max-w-2xl mx-auto shadow-lg">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-xl font-semibold text-gray-800">
            {categoryTitle.toUpperCase()}
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
        {/* Donut Chart */}
        <div className="flex justify-center">
          <svg width="200" height="200" viewBox="0 0 200 200">
            {generateDonutPath()}
            {/* Center text */}
            <text
              x="100"
              y="95"
              textAnchor="middle"
              className="text-2xl font-bold fill-gray-800"
            >
              {formatCurrency(total_amount)}
            </text>
            <text
              x="100"
              y="115"
              textAnchor="middle"
              className="text-sm fill-gray-500"
            >
              Total
            </text>
          </svg>
        </div>

        {/* Category List */}
        <div className="space-y-2">
          {categories.map((cat, index) => (
            <div
              key={index}
              className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 transition-colors border-b border-gray-100 last:border-0"
            >
              <div className="flex items-center gap-3 flex-1">
                <div
                  className="w-4 h-4 rounded"
                  style={{ backgroundColor: cat.color }}
                />
                <span className="text-sm font-medium text-gray-700 capitalize">
                  {cat.name.replace(/_/g, " ")}
                </span>
              </div>
              <div className="flex items-center gap-4">
                <span className="text-sm font-semibold text-gray-800">
                  {cat.percentage.toFixed(2)}%
                </span>
                <span className="text-sm text-gray-600 min-w-[80px] text-right">
                  {formatCurrency(cat.amount)}
                </span>
              </div>
            </div>
          ))}
        </div>

        {/* Upcoming Spends (only for spends category) */}
        {category === "spends" && upcoming_spends !== undefined && (
          <div className="mt-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
            <div className="text-sm text-blue-800">
              <span className="font-semibold">Upcoming spends:</span>{" "}
              {formatCurrency(upcoming_spends)}
            </div>
            <button className="mt-2 text-sm text-blue-600 hover:text-blue-800 underline">
              Tap to know more
            </button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

