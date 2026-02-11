import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Know Before You Vote | Epstein Accountability Voter Tool",
  description:
    "Enter your zip code. See your ballot. See which candidates have documented connections to the Epstein network. All data from public records with primary source links.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased bg-white text-gray-900`}
      >
        <header className="border-b border-gray-200 px-4 py-3">
          <nav className="max-w-4xl mx-auto flex items-center justify-between">
            <a href="/" className="text-lg font-semibold">
              Know Before You Vote
            </a>
            <a
              href="/methodology"
              className="text-sm text-gray-600 hover:text-gray-900"
            >
              How This Works
            </a>
          </nav>
        </header>
        <main className="max-w-4xl mx-auto px-4 py-8">{children}</main>
        <footer className="border-t border-gray-200 mt-16 px-4 py-6">
          <div className="max-w-4xl mx-auto text-center text-sm text-gray-500">
            <p>
              All data from public records. This tool does not accuse anyone of
              criminal conduct.
            </p>
            <p className="mt-1">
              <a
                href="https://github.com/wjcornelius/know-before-you-vote"
                className="underline hover:text-gray-700"
              >
                Open source
              </a>{" "}
              &middot; Built by W.J. Cornelius and Claude
            </p>
          </div>
        </footer>
      </body>
    </html>
  );
}
