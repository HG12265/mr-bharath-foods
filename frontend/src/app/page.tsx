"use client";

import { useTheme } from "next-themes";
import React, { useEffect, useState } from "react";
import { siteConfig } from "@/config/site";
import { formatINR } from "@/lib/utils";

/**
 * Interactive foundation page displaying brand design tokens and layout settings.
 */
export default function HomePage() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background text-foreground">
        <p className="font-serif text-lg tracking-wide animate-pulse">
          MR. BHARATH FOODS
        </p>
      </div>
    );
  }

  const brandColors = [
    { name: "Indian Ink", hex: "#1C2321", bgClass: "bg-indianInk text-white" },
    { name: "Warm Ivory", hex: "#FAF9F6", bgClass: "bg-warmIvory text-black border border-gray-200" },
    { name: "Kashmir Saffron", hex: "#9E4624", bgClass: "bg-kashmirSaffron text-white" },
    { name: "Deodhar Forest", hex: "#1E352F", bgClass: "bg-deodharForest text-white" },
    { name: "Trust Navy", hex: "#18324B", bgClass: "bg-trustNavy text-white" },
    { name: "Burnished Gold", hex: "#C49A45", bgClass: "bg-burnishedGold text-black" },
    { name: "Muted Sage", hex: "#E2EAE5", bgClass: "bg-mutedSage text-black" },
    { name: "Terracotta Blush", hex: "#F7EFE9", bgClass: "bg-terracottaBlush text-black" },
  ];

  return (
    <div className="mx-auto max-w-5xl px-6 py-12 space-y-12 bg-background transition-colors duration-300">
      {/* Header */}
      <header className="flex flex-col sm:flex-row items-start sm:items-center justify-between border-b pb-6 gap-4">
        <div>
          <h1 className="font-serif text-4xl font-semibold uppercase tracking-tight text-foreground">
            {siteConfig.name}
          </h1>
          <p className="font-sans text-xs tracking-widest uppercase text-muted-foreground mt-1">
            {siteConfig.tagline}
          </p>
        </div>
        <button
          onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
          className="rounded border border-primary px-4 py-2 font-sans text-xs font-semibold uppercase tracking-wider text-foreground hover:bg-muted/40 transition-colors focus:outline-none focus:ring-1 focus:ring-ring"
        >
          Toggle Theme (Current: {theme})
        </button>
      </header>

      {/* Typography Section */}
      <section className="space-y-6">
        <h2 className="font-serif text-2xl border-b pb-2">Typography & Editorial Grid</h2>
        <div className="grid md:grid-cols-2 gap-8">
          <div className="space-y-4">
            <h3 className="font-serif text-4xl">Display Heading 1</h3>
            <h4 className="font-serif text-3xl">Sub Heading H2</h4>
            <h5 className="font-serif text-xl">Section Title H3</h5>
          </div>
          <div className="space-y-4 font-sans">
            <p className="text-lg font-light text-foreground leading-relaxed">
              Body Large: Used for intro summaries and editorial openings. Elegant and spacious spacing details.
            </p>
            <p className="text-sm text-muted-foreground leading-relaxed">
              Body Small: Used for metadata annotations. For example, verifying co-packer FSSAI license codes: {siteConfig.fssaiLicenseNumber}.
            </p>
            <span className="inline-block text-xs font-semibold uppercase tracking-widest bg-muted px-2.5 py-1 rounded">
              Button / Badge uppercase label tracking
            </span>
          </div>
        </div>
      </section>

      {/* Design System Colors */}
      <section className="space-y-4">
        <h2 className="font-serif text-2xl border-b pb-2">Digital Design Tokens</h2>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          {brandColors.map((color) => (
            <div
              key={color.name}
              className={`p-4 rounded shadow-sm flex flex-col justify-between aspect-square ${color.bgClass}`}
            >
              <span className="font-serif text-sm font-semibold">{color.name}</span>
              <span className="font-sans text-xs tracking-wider opacity-90">{color.hex}</span>
            </div>
          ))}
        </div>
      </section>

      {/* Status Indicators & Helpers */}
      <section className="space-y-4">
        <h2 className="font-serif text-2xl border-b pb-2">Functional Status Badges</h2>
        <div className="flex flex-wrap gap-4 font-sans text-xs">
          <span className="rounded bg-success/15 text-success border border-success/20 px-3 py-1.5 font-medium">
            ✓ QA Approved
          </span>
          <span className="rounded bg-warning/15 text-warning border border-warning/20 px-3 py-1.5 font-medium">
            ⚠ Audit Pending
          </span>
          <span className="rounded bg-destructive/15 text-destructive border border-destructive/20 px-3 py-1.5 font-medium">
            ✗ Verification Failed
          </span>
          <span className="rounded bg-info/15 text-info border border-info/20 px-3 py-1.5 font-medium">
            ℹ In Transit
          </span>
        </div>
      </section>

      {/* INR Formatting utility demo */}
      <section className="space-y-4 font-sans">
        <h2 className="font-serif text-2xl border-b pb-2">Utility Functions Test</h2>
        <p className="text-sm">
          Currency Utility Output for 599: <strong className="text-base text-kashmirSaffron">{formatINR(599)}</strong>
        </p>
      </section>

      {/* Footer */}
      <footer className="border-t pt-6 text-center font-sans text-xs text-muted-foreground">
        <p>© 2026 {siteConfig.name}. FSSAI License No: {siteConfig.fssaiLicenseNumber}</p>
      </footer>
    </div>
  );
}