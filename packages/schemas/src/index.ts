import { z } from "zod";

export const BalanceSchema = z.object({
    currency: z.string(),
    amount: z.number(),
});

export const BalanceCardSchema = z.object({
    accounts: z.array(
        z.object({
            id: z.string(),
            label: z.string(),
            balance: BalanceSchema,
        })
    ),
});

export const TransactionSchema = z.object({
    id: z.string(),
    date: z.string(),
    merchant: z.string(),
    amount: z.number(),
    currency: z.string(),
});

export const TransactionTableSchema = z.object({
    transactions: z.array(TransactionSchema),
});

export const TicketFormSchema = z.object({
    issue: z.string().min(1, "Issue is required"),
    description: z.string().min(1, "Description is required"),
});

export const ConfirmationDialogSchema = z.object({
    title: z.string(),
    message: z.string(),
    confirmLabel: z.string(),
    cancelLabel: z.string(),
});

export const FinancialCategorySchema = z.object({
    name: z.string(),
    amount: z.number(),
    percentage: z.number(),
    color: z.string(),
});

export const CashFlowOverviewSchema = z.object({
    category: z.literal("overview"),
    period: z.object({
        start_date: z.string(),
        end_date: z.string(),
        label: z.string(),
    }),
    currency: z.string(),
    categories: z.array(
        z.object({
            name: z.string(),
            amount: z.number(),
            color: z.string(),
        })
    ),
});

// FinancialInsightsSchema can be either detailed insights or overview
export const FinancialInsightsSchema = z.union([
    z.object({
        category: z.enum(["incoming", "investment", "spends"]),
        period: z.object({
            start_date: z.string(),
            end_date: z.string(),
            label: z.string(),
        }),
        total_amount: z.number(),
        currency: z.string(),
        upcoming_spends: z.number().optional(),
        categories: z.array(FinancialCategorySchema),
    }),
    CashFlowOverviewSchema,
]);

export type BalanceCard = z.infer<typeof BalanceCardSchema>;
export type TransactionTable = z.infer<typeof TransactionTableSchema>;
export type TicketForm = z.infer<typeof TicketFormSchema>;
export type ConfirmationDialog = z.infer<typeof ConfirmationDialogSchema>;
export type FinancialInsights = z.infer<typeof FinancialInsightsSchema>;
export type FinancialCategory = z.infer<typeof FinancialCategorySchema>;
export type CashFlowOverview = z.infer<typeof CashFlowOverviewSchema>;
