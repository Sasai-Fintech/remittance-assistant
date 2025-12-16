import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { TranslationProvider } from "@/lib/hooks/use-translations";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Remittance Assistant",
  description: "Your AI Financial Companion",
  icons: {
    icon: "/favicon.ico",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=5, user-scalable=yes, viewport-fit=cover" />
      </head>
      <body className={inter.className}>
        <TranslationProvider>
          {children}
        </TranslationProvider>
      </body>
    </html>
  );
}
