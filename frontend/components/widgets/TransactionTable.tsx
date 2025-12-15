import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface Transaction {
    id: string;
    date?: string;
    merchant?: string;
    description?: string;
    amount: number;
    currency?: string;
}

interface TransactionTableProps {
    transactions: Transaction[];
}

export function TransactionTable({ transactions }: TransactionTableProps) {
    if (!transactions || transactions.length === 0) {
        return (
            <Card className="w-full max-w-md">
                <CardHeader>
                    <CardTitle>Recent Transactions</CardTitle>
                </CardHeader>
                <CardContent>
                    <p className="text-sm text-gray-500">No transactions found.</p>
                </CardContent>
            </Card>
        );
    }

    return (
        <Card className="w-full max-w-md">
            <CardHeader>
                <CardTitle>Recent Transactions</CardTitle>
            </CardHeader>
            <CardContent>
                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead>Date</TableHead>
                            <TableHead>Description</TableHead>
                            <TableHead className="text-right">Amount</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {transactions.map((txn) => {
                            const displayDate = txn.date || "N/A";
                            const displayDescription = txn.merchant || txn.description || "Transaction";
                            const currency = txn.currency || "USD";
                            const amount = txn.amount || 0;
                            const isNegative = amount < 0;
                            
                            return (
                                <TableRow key={txn.id}>
                                    <TableCell className="text-sm">{displayDate}</TableCell>
                                    <TableCell className="text-sm">{displayDescription}</TableCell>
                                    <TableCell className={`text-right text-sm font-medium ${isNegative ? "text-red-600" : "text-green-600"}`}>
                                        {isNegative ? "-" : "+"}{Math.abs(amount).toLocaleString("en-US", { style: "currency", currency })}
                                    </TableCell>
                                </TableRow>
                            );
                        })}
                    </TableBody>
                </Table>
            </CardContent>
        </Card>
    );
}
