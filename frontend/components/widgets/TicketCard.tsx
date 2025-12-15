"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CheckCircle2, Clock, AlertCircle } from "lucide-react";
import { useTranslations } from "@/lib/hooks/use-translations";

export interface Ticket {
  id?: string;
  ticketId?: string;
  ticket_id?: string;
  subject?: string;
  type?: string;
  description?: string;
  status?: string;
  createdAt?: string;
  created_at?: string;
  createdDate?: string;
  name?: string;
  phone?: string;
  message?: string;
}

interface TicketCardProps {
  ticket: Ticket;
}

export function TicketCard({ ticket }: TicketCardProps) {
  const { t } = useTranslations();
  // Extract ticket ID from various possible fields
  const ticketId = ticket.id || ticket.ticketId || ticket.ticket_id || "N/A";
  
  // Extract subject
  const subject = ticket.subject || t("widgets.ticket.title");
  
  // Extract description
  const description = ticket.description || ticket.message || "";
  
  // Extract status
  const status = ticket.status || "pending";
  const statusColor = status.toLowerCase() === "resolved" || status.toLowerCase() === "closed" 
    ? "text-green-600" 
    : status.toLowerCase() === "in_progress" || status.toLowerCase() === "in progress"
    ? "text-blue-600"
    : "text-yellow-600";
  
  // Extract type
  const ticketType = ticket.type || "General Enquiry";
  
  // Extract creation date
  const createdAt = ticket.createdAt || ticket.created_at || ticket.createdDate || new Date().toISOString();
  const formattedDate = new Date(createdAt).toLocaleDateString("en-GB", {
    day: "numeric",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit"
  });

  return (
    <Card className="w-full max-w-md border-l-4 border-l-indigo-600">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <CardTitle className="text-lg font-semibold text-gray-900 dark:text-gray-100">
            {t("widgets.ticket.title")}
          </CardTitle>
          {status.toLowerCase() === "resolved" || status.toLowerCase() === "closed" ? (
            <CheckCircle2 className="h-5 w-5 text-green-600 flex-shrink-0" />
          ) : status.toLowerCase() === "in_progress" || status.toLowerCase() === "in progress" ? (
            <Clock className="h-5 w-5 text-blue-600 flex-shrink-0" />
          ) : (
            <AlertCircle className="h-5 w-5 text-yellow-600 flex-shrink-0" />
          )}
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        <div>
          <span className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide">
            {t("widgets.ticket.ticketId")}
          </span>
          <p className="mt-1 text-sm font-mono text-gray-900 dark:text-gray-100">
            {ticketId}
          </p>
        </div>
        
        <div>
          <span className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide">
            {t("widgets.ticket.subject")}
          </span>
          <p className="mt-1 text-sm font-semibold text-gray-900 dark:text-gray-100">
            {subject}
          </p>
        </div>
        
        {description && (
          <div>
            <span className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide">
              {t("widgets.transactions.description")}
            </span>
            <p className="mt-1 text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
              {description}
            </p>
          </div>
        )}
        
        <div className="flex items-center justify-between pt-2 border-t border-gray-200 dark:border-gray-700">
          <div>
            <span className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide">
              {t("widgets.ticket.type")}
            </span>
            <p className="mt-1 text-xs text-gray-600 dark:text-gray-400">
              {ticketType}
            </p>
          </div>
          <div className="text-right">
            <span className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide">
              {t("widgets.ticket.status")}
            </span>
            <p className={`mt-1 text-xs font-semibold ${statusColor}`}>
              {status.charAt(0).toUpperCase() + status.slice(1)}
            </p>
          </div>
        </div>
        
        <div className="pt-2 border-t border-gray-200 dark:border-gray-700">
          <span className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide">
            {t("widgets.ticket.created")}
          </span>
          <p className="mt-1 text-xs text-gray-600 dark:text-gray-400">
            {formattedDate}
          </p>
        </div>
      </CardContent>
    </Card>
  );
}

