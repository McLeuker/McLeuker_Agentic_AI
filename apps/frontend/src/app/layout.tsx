import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "@/contexts/AuthContext";
import { SectorProvider } from "@/contexts/SectorContext";
import { ChatProvider } from "@/contexts/ChatContext";
import { Toaster } from "@/components/ui/toaster";
import { CookieConsent } from "@/components/CookieConsent";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "McLeuker AI - Fashion Intelligence Platform",
  description: "AI-powered fashion intelligence platform. From trend analysis to supplier sourcing — structured, professional, and ready to act on.",
  keywords: ["fashion AI", "trend forecasting", "supplier research", "fashion intelligence", "beauty", "skincare", "sustainability", "market analysis"],
  icons: {
    icon: [
      { url: "/favicon.ico", sizes: "any" },
      { url: "/favicon-16x16.png", sizes: "16x16", type: "image/png" },
      { url: "/favicon-32x32.png", sizes: "32x32", type: "image/png" },
    ],
    apple: [
      { url: "/apple-touch-icon.png", sizes: "180x180", type: "image/png" },
    ],
  },
  manifest: "/site.webmanifest",
  openGraph: {
    type: "website",
    locale: "en_US",
    url: "https://www.mcleukerai.com",
    siteName: "McLeuker AI",
    title: "McLeuker AI - Fashion Intelligence Platform",
    description: "AI-powered fashion intelligence platform. From trend analysis to supplier sourcing — structured, professional, and ready to act on.",
    images: [
      {
        url: "https://www.mcleukerai.com/og-image-wide.jpg",
        width: 1200,
        height: 630,
        alt: "McLeuker AI - Fashion Intelligence Platform",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "McLeuker AI - Fashion Intelligence Platform",
    description: "AI-powered fashion intelligence platform. From trend analysis to supplier sourcing — structured, professional, and ready to act on.",
    images: ["https://www.mcleukerai.com/og-image-wide.jpg"],
    creator: "@mcleuker",
  },
  metadataBase: new URL("https://www.mcleukerai.com"),
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <head>
        <link rel="icon" href="/favicon.ico" sizes="any" />
        <link rel="icon" href="/favicon-32x32.png" type="image/png" sizes="32x32" />
        <link rel="icon" href="/favicon-16x16.png" type="image/png" sizes="16x16" />
        <link rel="apple-touch-icon" href="/apple-touch-icon.png" sizes="180x180" />
      </head>
      <body className={`${inter.variable} font-sans antialiased`}>
        <AuthProvider>
          <SectorProvider>
            <ChatProvider>
              {children}
              <Toaster />
              <CookieConsent />
            </ChatProvider>
          </SectorProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
