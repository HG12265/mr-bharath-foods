import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";
import { env } from "./env";
import { siteConfig } from "@/config/site";

/**
 * Standard utility function to merge Tailwind classes safely with clsx and tailwind-merge.
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * Formats a given number into Indian Rupee currency standard formatting.
 */
export function formatINR(amount: number): string {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(amount);
}

/**
 * Optimizes Cloudinary or custom media delivery URLs with format, quality, and width resizing.
 */
export function optimizeCloudinaryUrl(url: string, width: number): string {
  if (!url) return url;
  
  const domainsToCheck = [...(siteConfig.mediaDomains || [])];
  if (env.NEXT_PUBLIC_MEDIA_BASE_URL) {
    try {
      const parsed = new URL(env.NEXT_PUBLIC_MEDIA_BASE_URL);
      domainsToCheck.push(parsed.hostname);
    } catch {
      domainsToCheck.push(env.NEXT_PUBLIC_MEDIA_BASE_URL);
    }
  }

  const isCloudinary = domainsToCheck.some((domain) => url.includes(domain));
  if (isCloudinary && url.includes("/image/upload/")) {
    return url.replace("/image/upload/", `/image/upload/f_auto,q_auto,w_${width}/`);
  }
  return url;
}