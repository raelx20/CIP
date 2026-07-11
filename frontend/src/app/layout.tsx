import type { Metadata } from "next";
import "./globals.css";
import { AuthProvider } from "@/lib/auth/context";

export const metadata: Metadata = {
  title: "CIP - Constituency Intelligence Platform",
  description: "AI-powered government decision-support platform for citizens and representatives",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
