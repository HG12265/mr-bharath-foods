import { Metadata } from "next";
import { siteConfig } from "@/config/site";

export const metadata: Metadata = {
  title: "Contact Us | Mr. Bharath Foods",
  description:
    "Get in touch with Mr. Bharath Foods for order support, product enquiries, bulk orders, or business partnerships. We respond within 24 hours.",
  keywords: [
    "contact mr bharath foods",
    "ghee order support",
    "bulk ghee enquiry",
    "mr bharath foods support",
    "food brand contact india",
  ],
  alternates: {
    canonical: `${siteConfig.url}/contact`,
  },
  openGraph: {
    title: "Contact Us | Mr. Bharath Foods",
    description:
      "Order support, product queries, and business enquiries. Reach Mr. Bharath Foods today.",
    url: `${siteConfig.url}/contact`,
    siteName: siteConfig.name,
    images: [{ url: siteConfig.ogImage, width: 1200, height: 630, alt: "Contact Mr. Bharath Foods" }],
    locale: "en_IN",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Contact Mr. Bharath Foods",
    description: "Order support, product queries, and business enquiries.",
    images: [siteConfig.ogImage],
    creator: siteConfig.twitterHandle,
  },
};

export default function ContactLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
