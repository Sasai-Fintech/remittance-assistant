"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useState } from "react";
import { Send } from "lucide-react";

interface Currency {
  currencyCode: string;
  name: string;
  rounding: number;
}

interface Country {
  countryCode: string;
  name: string;
  flagUnicode: string;
  currencies: Currency[];
  mobileRegEx?: string;
}

interface CountrySelectorProps {
  countries: Country[];
  onSelect?: (countryCode: string, currencyCode: string, countryName: string) => void;
}

export function CountrySelector({ countries, onSelect }: CountrySelectorProps) {
  const [selectedCountry, setSelectedCountry] = useState<string>("");

  const handleSelect = () => {
    const country = countries.find(c => c.countryCode === selectedCountry);
    if (country && country.currencies.length > 0) {
      // Use the first currency if multiple are available
      const currency = country.currencies[0];
      if (onSelect) {
        onSelect(selectedCountry, currency.currencyCode, country.name);
      }
    }
  };

  return (
    <Card className="w-full max-w-md mx-auto shadow-lg border-2 border-blue-100 dark:border-blue-900">
      <CardContent className="pt-6">
        <div className="space-y-4">
          <div className="text-center mb-4">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
              💸 Select Destination Country
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
              Choose where you want to send money
            </p>
          </div>
          
          <div>
            <label className="text-sm font-medium mb-2 block text-gray-700 dark:text-gray-300">
              Destination Country
            </label>
            <Select value={selectedCountry} onValueChange={setSelectedCountry}>
              <SelectTrigger className="w-full">
                <SelectValue placeholder="Choose a country..." />
              </SelectTrigger>
              <SelectContent className="max-h-[300px]">
                {countries.map((country) => (
                  <SelectItem key={country.countryCode} value={country.countryCode}>
                    <div className="flex items-center gap-2">
                      <span className="text-xl">{country.flagUnicode}</span>
                      <span>{country.name}</span>
                      {country.currencies.length > 0 && (
                        <span className="text-xs text-gray-500">
                          ({country.currencies[0].currencyCode})
                        </span>
                      )}
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          
          <Button 
            onClick={handleSelect} 
            disabled={!selectedCountry}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send className="w-4 h-4 mr-2" />
            Check Exchange Rate
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
