/**
 * Financial schema types for EcoCash widgets
 * Inlined from @ecocash/schemas to avoid monorepo workspace dependency
 */

export interface FinancialCategory {
  name: string;
  amount: number;
  percentage: number;
  color: string;
}

export interface Period {
  start_date: string;
  end_date: string;
  label: string;
}

export interface CashFlowOverview {
  category: "overview";
  period: Period;
  currency: string;
  categories: Array<{
    name: string;
    amount: number;
    color: string;
  }>;
}

export interface FinancialInsightsDetail {
  category: "incoming" | "investment" | "spends";
  period: Period;
  total_amount: number;
  currency: string;
  upcoming_spends?: number;
  categories: FinancialCategory[];
}

export type FinancialInsights = FinancialInsightsDetail | CashFlowOverview;

export interface Balance {
  currency: string;
  amount: number;
}

export interface BalanceCard {
  accounts: Array<{
    id: string;
    label: string;
    balance: Balance;
  }>;
}

export interface Transaction {
  id: string;
  date: string;
  merchant: string;
  amount: number;
  currency: string;
}

export interface TransactionTable {
  transactions: Transaction[];
}

export interface TicketForm {
  issue: string;
  description: string;
}

export interface ConfirmationDialog {
  title: string;
  message: string;
  confirmLabel: string;
  cancelLabel: string;
}
