import { Metadata } from "next";
import { siteConfig } from "@/config/site";

export const metadata: Metadata = {
  title: "Trust Process | Bharath Delight Foods",
  description:
    "Learn how Bharath Delight Foods selects, handles, packs, and ships food products with care and responsibility.",
  keywords: [
    "Bharath Delight Foods",
    "trust process",
    "food product quality",
    "safe packing",
    "responsible food brand"
  ],
  alternates: {
    canonical: `${siteConfig.url}/about`,
  },
  openGraph: {
    title: "Trust Process | Bharath Delight Foods",
    description:
      "Learn how Bharath Delight Foods selects, handles, packs, and ships food products with care and responsibility.",
    url: `${siteConfig.url}/about`,
    siteName: siteConfig.name,
    images: [{ url: siteConfig.ogImage, width: 1200, height: 630, alt: "Trust Process | Bharath Delight Foods" }],
    locale: "en_IN",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Trust Process | Bharath Delight Foods",
    description: "Learn how Bharath Delight Foods selects, handles, packs, and ships food products with care and responsibility.",
    images: [siteConfig.ogImage],
    creator: siteConfig.twitterHandle,
  },
};

export default function AboutLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
