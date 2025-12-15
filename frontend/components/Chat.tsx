"use client";

import { useCopilotAction } from "@copilotkit/react-core";
import { BalanceCard } from "./widgets/BalanceCard";
import { TransactionTable } from "./widgets/TransactionTable";
import { TicketConfirmation } from "./widgets/TicketConfirmation";

export function Chat() {
    useCopilotAction({
        name: "show_balance_widget",
        description: "Show the balance card widget",
        parameters: [
            {
                name: "accounts",
                type: "object[]",
                description: "List of accounts with balance",
            },
        ],
        render: (props: any) => {
            return <BalanceCard accounts={props.accounts} />;
        },
    });

    useCopilotAction({
        name: "show_transactions_widget",
        description: "Show the transactions table widget",
        parameters: [
            {
                name: "transactions",
                type: "object[]",
                description: "List of transactions",
            },
        ],
        render: (props: any) => {
            return <TransactionTable transactions={props.transactions} />;
        },
    });

    useCopilotAction({
        name: "request_ticket_confirmation",
        description: "Request ticket confirmation",
        parameters: [
            {
                name: "issue",
                type: "string",
                description: "The issue title",
            },
            {
                name: "description",
                type: "string",
                description: "The issue description",
            },
        ],
        render: (props: any) => {
            return <TicketConfirmation
                issue={props.issue}
                description={props.description}
                status={props.status}
                handler={props.handler}
            />;
        },
    });

    return null;
}
