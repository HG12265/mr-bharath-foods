import { MetadataRoute } from "next";
import { siteConfig } from "@/config/site";
import { env } from "@/lib/env";

/**
 * Dynamic sitemap generator — fetches all active products from the backend
 * and returns a sitemap that Google can crawl. Scales automatically with catalog.
 */
export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const appUrl = siteConfig.url;
  const apiUrl = env.NEXT_PUBLIC_API_URL;

  // Static pages
  const staticRoutes: MetadataRoute.Sitemap = [
    {
      url: appUrl,
      lastModified: new Date(),
      changeFrequency: "weekly",
      priority: 1.0,
    },
    {
      url: `${appUrl}/shop`,
      lastModified: new Date(),
      changeFrequency: "daily",
      priority: 0.9,
    },
    {
      url: `${appUrl}/about`,
      lastModified: new Date(),
      changeFrequency: "monthly",
      priority: 0.7,
    },
    {
      url: `${appUrl}/contact`,
      lastModified: new Date(),
      changeFrequency: "monthly",
      priority: 0.6,
    },
  ];

  // Dynamic product pages — fetch from backend
  let productRoutes: MetadataRoute.Sitemap = [];
  try {
    const res = await fetch(`${apiUrl}/api/v1/products?limit=200&status=active`, {
      next: { revalidate: 3600 }, // Re-fetch every hour
    });
    if (res.ok) {
      const json = await res.json();
      const products: Array<{ slug: string; updated_at: string }> = json?.data || [];
      productRoutes = products
        .filter((p) => p.slug)
        .map((p) => ({
          url: `${appUrl}/products/${p.slug}`,
          lastModified: p.updated_at ? new Date(p.updated_at) : new Date(),
          changeFrequency: "weekly" as const,
          priority: 0.8,
        }));
    }
  } catch {
    // Fallback: sitemap still works with static routes if backend is unavailable
  }

  return [...staticRoutes, ...productRoutes];
}
