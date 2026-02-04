import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "@/contexts/AuthContext";
import { SectorProvider } from "@/contexts/SectorContext";
import { ChatProvider } from "@/contexts/ChatContext";
import { Toaster } from "@/components/ui/toaster";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "McLeuker AI - Fashion Intelligence Platform",
  description: "Your intelligent assistant for fashion, beauty, skincare, and sustainability insights powered by real-time research.",
  keywords: ["fashion", "AI", "beauty", "skincare", "sustainability", "trends"],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.variable} font-sans antialiased`}>
        <AuthProvider>
          <SectorProvider>
            <ChatProvider>
              {children}
              <Toaster />
            </ChatProvider>
          </SectorProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
