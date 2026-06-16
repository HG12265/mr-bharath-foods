import { Cormorant_Garamond, Outfit } from "next/font/google";
import { defaultMetadata } from "./metadata";
import { AppProvider } from "@/providers/app-provider";
import { siteConfig } from "@/config/site";
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

// Organization JSON-LD — rendered on every page
const organizationJsonLd = {
  "@context": "https://schema.org",
  "@type": "Organization",
  name: "Bharath Delight Foods",
  url: `${siteConfig.url}/`,
  logo: {
    "@type": "ImageObject",
    url: `${siteConfig.url}/logo.png`,
    width: 200,
    height: 60,
  },
  description: siteConfig.description,
  contactPoint: {
    "@type": "ContactPoint",
    contactType: "customer service",
    email: siteConfig.links.supportEmail,
    availableLanguage: ["English", "Tamil"],
  },
};

// WebSite JSON-LD — enables Sitelinks Searchbox potential
const webSiteJsonLd = {
  "@context": "https://schema.org",
  "@type": "WebSite",
  name: "Bharath Delight Foods",
  alternateName: ["Bharath Delight", "BDF"],
  url: `${siteConfig.url}/`,
  description: siteConfig.description,
};

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
        {/* Global Structured Data */}
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(organizationJsonLd) }}
        />
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(webSiteJsonLd) }}
        />
        <AppProvider>{children}</AppProvider>
      </body>
    </html>
  );
}