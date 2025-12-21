import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "OMNI-CAST | AI Debate Platform",
  description: "Bharat-First AI Debate Simulator",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body
        className="antialiased bg-black"
        suppressHydrationWarning
      >
        {children}
      </body>
    </html>
  );
}
