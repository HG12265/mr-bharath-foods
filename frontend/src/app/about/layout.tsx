import { Metadata } from "next";
import { siteConfig } from "@/config/site";

export const metadata: Metadata = {
  title: "About Us — Our Story | Bharath Delight Foods",
  description:
    "Learn the story behind Bharath Delight Foods — a brand built on trust, purity, and traditional Indian food sourcing. FSSAI licensed. Lab-verified products.",
  keywords: [
    "about bharath delight foods",
    "premium ghee brand india",
    "traditional indian food brand",
    "pure ghee sourcing",
    "fssai licensed food brand",
    "lab verified food india",
  ],
  alternates: {
    canonical: `${siteConfig.url}/about`,
  },
  openGraph: {
    title: "About Bharath Delight Foods — Selecting the Best to Serve the Best",
    description:
      "A brand dedicated to curating and delivering pure, traditional Indian kitchen staples with full batch-level transparency.",
    url: `${siteConfig.url}/about`,
    siteName: siteConfig.name,
    images: [{ url: siteConfig.ogImage, width: 1200, height: 630, alt: "About Bharath Delight Foods" }],
    locale: "en_IN",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "About Bharath Delight Foods",
    description: "Pure, traditional Indian food. Batch-verified. Trace-sealed.",
    images: [siteConfig.ogImage],
    creator: siteConfig.twitterHandle,
  },
};

export default function AboutLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
