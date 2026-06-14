import { Metadata } from "next";
import { siteConfig } from "@/config/site";

export const metadata: Metadata = {
  title: "Shop Pure Ghee Online | Bharath Delight Foods",
  description:
    "Buy premium Rasipuram Pure Ghee and Uthukuli A2 Cow Ghee online. FSSAI licensed, lab-verified purity, trace-sealed batches. Free shipping above ₹1000.",
  keywords: [
    "buy ghee online",
    "pure ghee india",
    "rasipuram ghee",
    "uthukuli a2 ghee",
    "premium indian ghee shop",
    "lab verified ghee",
    "fssai licensed ghee online",
    "traditional ghee buy",
    "a2 cow ghee india",
  ],
  alternates: {
    canonical: `${siteConfig.url}/shop`,
  },
  openGraph: {
    title: "Shop Pure Ghee Online | Bharath Delight Foods",
    description:
      "Premium Rasipuram & Uthukuli ghee. Lab-verified, FSSAI licensed. Delivered to your door.",
    url: `${siteConfig.url}/shop`,
    siteName: siteConfig.name,
    images: [{ url: siteConfig.ogImage, width: 1200, height: 630, alt: "Bharath Delight Foods — Shop Ghee" }],
    locale: "en_IN",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Shop Pure Ghee Online | Bharath Delight Foods",
    description: "Premium Rasipuram & Uthukuli ghee. Lab-verified, FSSAI licensed.",
    images: [siteConfig.ogImage],
    creator: siteConfig.twitterHandle,
  },
};

export default function ShopLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
