import { Metadata } from "next";
import { siteConfig } from "@/config/site";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const APP_URL = siteConfig.url;

interface LayoutProps {
  params: Promise<{ slug: string }>;
  children: React.ReactNode;
}

/**
 * Server-side metadata for product pages.
 * Fetches real product data — no hardcoded values.
 * Falls back to brand defaults if product is unavailable.
 */
export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}): Promise<Metadata> {
  const { slug } = await params;

  try {
    const res = await fetch(`${API_URL}/api/v1/products/slug/${slug}`, {
      next: { revalidate: 3600 },
    });

    if (!res.ok) throw new Error("Product not found");

    const json = await res.json();
    const product = json?.data;

    if (!product) throw new Error("No product data");

    // Title: prefer product SEO meta_title, fallback to product name
    const title =
      product.seo?.meta_title ||
      `${product.name} | Bharath Delight Foods`;

    // Description: prefer SEO meta_description, fallback to short_description
    const description =
      product.seo?.meta_description ||
      product.short_description ||
      siteConfig.description;

    // Keywords: merge product SEO + tags + search_keywords
    const keywords: string[] = [
      ...(product.seo?.meta_keywords || []),
      ...(product.tags || []),
      ...(product.search_keywords || []),
    ].filter(Boolean);

    // OG Image: use first media asset public URL if available
    let ogImageUrl = siteConfig.ogImage;
    if (product.media_ids && product.media_ids.length > 0) {
      try {
        const mediaRes = await fetch(
          `${API_URL}/api/v1/media/${product.media_ids[0]}`,
          { next: { revalidate: 86400 } }
        );
        if (mediaRes.ok) {
          const mediaJson = await mediaRes.json();
          if (mediaJson?.data?.public_url) {
            ogImageUrl = mediaJson.data.public_url;
          }
        }
      } catch {
        // Fallback to site OG image
      }
    }

    const canonicalUrl = `${APP_URL}/products/${slug}`;

    return {
      title,
      description,
      keywords: keywords.length > 0 ? keywords : siteConfig.keywords,
      alternates: {
        canonical: canonicalUrl,
      },
      openGraph: {
        title,
        description,
        url: canonicalUrl,
        siteName: siteConfig.name,
        images: [
          {
            url: ogImageUrl,
            width: 1200,
            height: 630,
            alt: product.name,
          },
        ],
        locale: "en_IN",
        type: "website",
      },
      twitter: {
        card: "summary_large_image",
        title,
        description,
        images: [ogImageUrl],
        creator: siteConfig.twitterHandle,
      },
    };
  } catch {
    // Safe fallback when product fetch fails
    return {
      title: `${siteConfig.name} — Premium Ghee`,
      description: siteConfig.description,
      alternates: { canonical: `${APP_URL}/products/${slug}` },
    };
  }
}

export default function ProductLayout({ children }: LayoutProps) {
  return <>{children}</>;
}
