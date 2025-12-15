"use client";

import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { RenderFunctionStatus } from "@copilotkit/react-core";
import { useTranslations } from "@/lib/hooks/use-translations";

export type TicketConfirmationProps = {
  issue: string;
  description: string;
  status: RenderFunctionStatus;
  handler?: (response: string) => void;
};

export function TicketConfirmation({ issue, description, status, handler }: TicketConfirmationProps) {
    const { t } = useTranslations();
    
    const handleConfirm = () => {
        if (status === "complete" || status === "inProgress") {
            return; // Prevent double submission
        }
        handler?.("CONFIRM");
    };

    const handleCancel = () => {
        if (status === "complete" || status === "inProgress") {
            return;
        }
        handler?.("CANCEL");
    };
    
    // Show loading state when processing
    const isProcessing = status === "complete" || status === "inProgress";

    return (
        <Card className="w-full max-w-md">
            <CardHeader>
                <CardTitle>{t("widgets.confirmation.title")}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
                <div>
                    <span className="font-semibold text-sm text-gray-700 dark:text-gray-300">Issue:</span>
                    <p className="mt-1 text-sm text-gray-900 dark:text-gray-100">{issue}</p>
                </div>
                <div>
                    <span className="font-semibold text-sm text-gray-700 dark:text-gray-300">{t("widgets.transactions.description")}:</span>
                    <p className="mt-1 text-sm text-gray-900 dark:text-gray-100 whitespace-pre-wrap">{description}</p>
                </div>
            </CardContent>
            <CardFooter className="flex justify-end gap-2">
                <Button 
                    variant="outline" 
                    onClick={handleCancel}
                    disabled={isProcessing}
                >
                    {t("widgets.confirmation.cancel")}
                </Button>
                <Button 
                    onClick={handleConfirm}
                    disabled={isProcessing}
                    className={isProcessing ? "opacity-50 cursor-not-allowed" : ""}
                >
                    {isProcessing ? t("common.loading") : t("widgets.confirmation.confirm")}
                </Button>
            </CardFooter>
        </Card>
    );
}
