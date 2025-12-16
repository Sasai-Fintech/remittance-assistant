"use client";

import { useState, useEffect, createContext, useContext, ReactNode } from "react";

type Language = "en" | "sn";

interface Translations {
  [key: string]: any;
}

const TranslationContext = createContext<{
  language: Language;
  setLanguage: (lang: Language) => void;
  t: (key: string) => string;
}>({
  language: "en",
  setLanguage: () => {},
  t: () => "",
});

export function TranslationProvider({ children }: { children: ReactNode }) {
  const [language, setLanguageState] = useState<Language>("en");
  const [translations, setTranslations] = useState<Translations>({});

  useEffect(() => {
    // Load translations based on current language
    const loadTranslations = async () => {
      try {
        const translationsModule = await import(`@/lib/translations/${language}.json`);
        setTranslations(translationsModule.default || translationsModule);
      } catch (error) {
        console.error(`Failed to load translations for ${language}:`, error);
        // Fallback to English
        if (language !== "en") {
          try {
            const enTranslations = await import(`@/lib/translations/en.json`);
            setTranslations(enTranslations.default || enTranslations);
          } catch (e) {
            console.error("Failed to load English translations:", e);
          }
        }
      }
    };

    loadTranslations();
  }, [language]);

  useEffect(() => {
    // Load saved language preference from localStorage
    const savedLanguage = localStorage.getItem("remittance_language") as Language;
    if (savedLanguage && (savedLanguage === "en" || savedLanguage === "sn")) {
      setLanguageState(savedLanguage);
    }
  }, []);

  const setLanguage = (lang: Language) => {
    setLanguageState(lang);
    localStorage.setItem("remittance_language", lang);
  };

  const t = (key: string): string => {
    const keys = key.split(".");
    let value: any = translations;

    for (const k of keys) {
      if (value && typeof value === "object" && k in value) {
        value = value[k];
      } else {
        // Fallback to English if key not found
        return key;
      }
    }

    return typeof value === "string" ? value : key;
  };

  return (
    <TranslationContext.Provider value={{ language, setLanguage, t }}>
      {children}
    </TranslationContext.Provider>
  );
}

export function useTranslations() {
  const context = useContext(TranslationContext);
  if (!context) {
    throw new Error("useTranslations must be used within TranslationProvider");
  }
  return context;
}

