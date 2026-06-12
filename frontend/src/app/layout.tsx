import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  variable: "--font-geist-sans",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "TubeMind — Chat with Any YouTube Video",
  description:
    "AI-powered YouTube video intelligence. Paste any video URL, get instant summaries, and have intelligent conversations with video content using RAG.",
  keywords: [
    "YouTube",
    "AI",
    "RAG",
    "video analysis",
    "transcript",
    "chatbot",
    "Gemini",
  ],
  openGraph: {
    title: "TubeMind — Chat with Any YouTube Video",
    description:
      "AI-powered YouTube video intelligence platform",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${inter.variable} h-full antialiased`}>
      <body suppressHydrationWarning className="min-h-full flex flex-col font-geist-sans">
        {children}
      </body>
    </html>
  );
}
