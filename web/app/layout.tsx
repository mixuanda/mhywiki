import type { Metadata } from "next";
import Link from "next/link";
import { Bitter, Space_Grotesk } from "next/font/google";
import type { ReactNode } from "react";

import "./globals.css";

const headingFont = Space_Grotesk({
  subsets: ["latin"],
  variable: "--font-heading",
  weight: ["500", "700"],
});

const bodyFont = Bitter({
  subsets: ["latin"],
  variable: "--font-body",
  weight: ["400", "500", "700"],
});

export const metadata: Metadata = {
  title: "Combat Wiki",
  description: "Combat-focused GI and SR wiki from normalized one-entity-per-file data.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body className={`${headingFont.variable} ${bodyFont.variable}`}>
        <div className="bg-layer" />
        <header className="topbar">
          <Link href="/" className="brand">
            Combat Wiki
          </Link>
          <nav>
            <Link href="/gi">GI</Link>
            <Link href="/sr">SR</Link>
          </nav>
        </header>
        <main className="page-shell">{children}</main>
      </body>
    </html>
  );
}
