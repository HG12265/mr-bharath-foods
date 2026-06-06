import { Cormorant_Garamond, Outfit } from "next/font/google";
import { defaultMetadata } from "./metadata";
import { AppProvider } from "@/providers/app-provider";
import "./globals.css";

const fontSerif = Cormorant_Garamond({
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700"],
  variable: "--font-serif",
  display: "swap",
});

const fontSans = Outfit({
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700"],
  variable: "--font-sans",
  display: "swap",
});

export const metadata = defaultMetadata;

/**
 * Root Layout Wrapper configuring standard fonts settings and providers.
 */
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="en"
      className={`${fontSerif.variable} ${fontSans.variable}`}
      suppressHydrationWarning
    >
      <body className="min-h-screen bg-background text-foreground font-sans antialiased">
        <AppProvider>{children}</AppProvider>
      </body>
    </html>
  );
}