import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

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
  const isCloudinary = url.includes("res.cloudinary.com") || url.includes("pub-media.mrbharathfoods.in");
  if (isCloudinary && url.includes("/image/upload/")) {
    return url.replace("/image/upload/", `/image/upload/f_auto,q_auto,w_${width}/`);
  }
  return url;
}