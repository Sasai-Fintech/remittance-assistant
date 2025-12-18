import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { User, Phone, CreditCard, Banknote, Smartphone } from "lucide-react";
import Image from 'next/image';

interface PayoutAccount {
  id: string;
  mobileMoneyMsisdn: string | null;
  beneficiaryPayoutMethod: string;
  recipientType: string;
  mobileMoneyProvider: string | null;
  nickname: string;
  beneficiaryType: string;
  linkedProducts: Array<{
    productId: number;
    accountName: string;
  }>;
  accountName: string;
}

interface Recipient {
  firstName: string;
  middleName?: string;
  lastName: string;
  mobile: string;
  countryIsdCode: string;
  relationship: string;
  relationshipValue: string;
  beneficiaryId: string;
  accounts: PayoutAccount[];
  isSasaiUser: boolean;
  profileImage?: string;
  customerId: string;
}

interface RecipientListCardProps {
  items: Recipient[];
  total: number;
  page: number;
  count: number;
  onSelectRecipient?: (recipient: Recipient, account: PayoutAccount) => void;
}

const getPayoutIcon = (method: string) => {
  if (method.toLowerCase().includes('cash')) {
    return <Banknote className="h-4 w-4" />;
  } else if (method.toLowerCase().includes('mobile') || method.toLowerCase().includes('ecocash')) {
    return <Smartphone className="h-4 w-4" />;
  }
  return <CreditCard className="h-4 w-4" />;
};

const getPayoutBadgeVariant = (method: string): "default" | "secondary" | "success" | "warning" => {
  if (method.toLowerCase().includes('cash')) {
    return "warning";
  } else if (method.toLowerCase().includes('mobile') || method.toLowerCase().includes('ecocash')) {
    return "success";
  }
  return "default";
};

export const RecipientListCard: React.FC<RecipientListCardProps> = ({ 
  items, 
  total, 
  page, 
  count,
  onSelectRecipient 
}) => {
  return (
    <Card className="w-full max-w-4xl mx-auto shadow-lg">
      <CardHeader className="bg-gradient-to-r from-blue-500 to-purple-600 text-white">
        <CardTitle className="flex items-center gap-2">
          <User className="h-6 w-6" />
          Your Recipients ({total})
        </CardTitle>
        <p className="text-sm text-blue-100">
          Select a recipient and payout method to continue
        </p>
      </CardHeader>
      <CardContent className="p-6">
        {items.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <User className="h-16 w-16 mx-auto mb-4 opacity-20" />
            <p className="text-lg font-medium">No recipients found</p>
            <p className="text-sm">Add a recipient to start sending money</p>
          </div>
        ) : (
          <div className="space-y-4">
            {items.map((recipient) => (
              <Card key={recipient.beneficiaryId} className="border-2 hover:border-blue-300 transition-colors">
                <CardContent className="p-4">
                  <div className="flex items-start gap-4">
                    {/* Profile Image */}
                    <div className="flex-shrink-0">
                      {recipient.profileImage ? (
                        <Image
                          src={recipient.profileImage}
                          alt={`${recipient.firstName} ${recipient.lastName}`}
                          width={64}
                          height={64}
                          className="rounded-full border-2 border-gray-200"
                        />
                      ) : (
                        <div className="w-16 h-16 rounded-full bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center text-white font-bold text-xl">
                          {recipient.firstName.charAt(0)}{recipient.lastName.charAt(0)}
                        </div>
                      )}
                    </div>

                    {/* Recipient Details */}
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <h3 className="text-lg font-semibold">
                          {recipient.firstName} {recipient.middleName} {recipient.lastName}
                        </h3>
                        {recipient.isSasaiUser && (
                          <Badge variant="success" className="text-xs">
                            Sasai User ✓
                          </Badge>
                        )}
                      </div>
                      
                      <div className="flex items-center gap-4 text-sm text-gray-600 mb-3">
                        <div className="flex items-center gap-1">
                          <Phone className="h-4 w-4" />
                          +{recipient.countryIsdCode} {recipient.mobile}
                        </div>
                        <Badge variant="outline" className="text-xs">
                          {recipient.relationshipValue}
                        </Badge>
                      </div>

                      {/* Payout Methods */}
                      <div className="space-y-2">
                        <p className="text-xs font-medium text-gray-500 uppercase">
                          Payout Methods ({recipient.accounts.length})
                        </p>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                          {recipient.accounts.map((account) => (
                            <div
                              key={account.id}
                              className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-200 hover:bg-blue-50 hover:border-blue-300 transition-colors"
                            >
                              <div className="flex items-center gap-2 flex-1">
                                {getPayoutIcon(account.beneficiaryPayoutMethod)}
                                <div className="flex-1 min-w-0">
                                  <p className="text-sm font-medium truncate">
                                    {account.nickname || account.accountName}
                                  </p>
                                  {account.mobileMoneyProvider && (
                                    <p className="text-xs text-gray-500">
                                      via {account.mobileMoneyProvider}
                                    </p>
                                  )}
                                </div>
                              </div>
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => onSelectRecipient?.(recipient, account)}
                                className="ml-2"
                              >
                                Select
                              </Button>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* Pagination Info */}
        {total > count && (
          <div className="mt-6 text-center text-sm text-gray-500">
            Showing {(page - 1) * count + 1}-{Math.min(page * count, total)} of {total} recipients
          </div>
        )}
      </CardContent>
    </Card>
  );
};
