"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useTranslations } from "@/lib/hooks/use-translations";

interface Balance {
  currency: string;
  amount: number;
}

interface Account {
  id: string;
  label: string;
  balance: Balance;
}

interface BalanceCardProps {
  accounts: Account[];
}

export function BalanceCard({ accounts }: BalanceCardProps) {
  const { t } = useTranslations();
  // Calculate total balance across all accounts
  const totalBalance = accounts.reduce((sum, account) => sum + account.balance.amount, 0);
  const currency = accounts[0]?.balance.currency || "USD";

  return (
    <Card className="w-full max-w-md shadow-lg border-none bg-gradient-to-br from-indigo-600 to-purple-700 text-white">
      <CardHeader className="p-3 sm:p-6">
        <CardTitle className="text-indigo-100 text-sm sm:text-base">{t("widgets.balance.title")}</CardTitle>
      </CardHeader>
      <CardContent className="p-3 sm:p-6 pt-0">
        <div className="space-y-1">
          <p className="text-2xl sm:text-3xl md:text-4xl font-bold break-words">
            {totalBalance.toLocaleString("en-US", { style: "currency", currency })}
          </p>
          <p className="text-xs sm:text-sm text-indigo-200">{t("widgets.balance.available")}</p>
          {accounts.length > 1 && (
            <div className="mt-3 sm:mt-4 space-y-2">
              {accounts.map((account) => (
                <div key={account.id} className="flex justify-between text-xs sm:text-sm">
                  <span className="text-indigo-200 truncate pr-2">{account.label}:</span>
                  <span className="font-semibold flex-shrink-0">
                    {account.balance.amount.toLocaleString("en-US", { style: "currency", currency: account.balance.currency })}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
