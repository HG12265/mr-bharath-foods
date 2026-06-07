"use client";

import React from "react";
import Link from "next/link";
import Image from "next/image";
import PublicLayout from "@/components/layout/public-layout";
import { useProducts } from "@/hooks/use-products";
import { formatINR } from "@/lib/utils";

// Static fallback products (Only Rasipuram & Uthukuli Ghee)
const GHEE_PRODUCTS = [
  {
    id: "mock-rasipuram",
    name: "Rasipuram Pure Ghee",
    slug: "rasipuram-ghee",
    description: "Prepared through traditional slow-simmering methods. Celebrated for its deep aroma, nuttiness, and rich golden color.",
    volume: "250ml",
    price: 390.00,
    region: "Rasipuram, Tamil Nadu",
    texture: "Golden & Deeply Simmered"
  },
  {
    id: "mock-uthukuli",
    name: "Uthukuli A2 Cow Ghee",
    slug: "uthukuli-ghee",
    description: "Traditionally churned from milk of historical grass-fed herds. Notable for its delicate, natural white-to-yellow granules.",
    volume: "250ml",
    price: 420.00,
    region: "Uthukuli, Tamil Nadu",
    texture: "Naturally Granular & Fragrant"
  }
];

export default function ShopPage() {
  const { data: productsData } = useProducts({ limit: 10 });
  const dbProducts = productsData?.data || [];

  // Filter or fall back to show only the two premium ghee selections
  const displayProducts = dbProducts.length > 0
    ? dbProducts.filter(p => p.slug.includes("ghee")).slice(0, 2)
    : GHEE_PRODUCTS;

  return (
    <PublicLayout>
      <div 
        className="min-h-screen text-indianInk py-16 border-b border-burnishedGold/15"
        style={{ background: "radial-gradient(circle at center, #FFFDF0 0%, #FAF9F6 70%, #FFF7E8 100%)" }}
      >
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          
          {/* Header Section */}
          <div className="text-center max-w-2xl mx-auto mb-16 animate-fade-up">
            <span className="text-[10px] uppercase tracking-[0.25em] text-burnishedGold font-bold font-sans">
              Pure Regional Selections
            </span>
            <h1 className="font-serif text-4xl sm:text-5xl font-bold text-deodharForest mt-2">
              Shop Ghee
            </h1>
            <p className="font-sans text-sm text-indianInk/70 mt-3 max-w-md mx-auto leading-relaxed">
              Carefully selected ghee products from trusted regional sources.
            </p>
            <div className="w-16 h-0.5 bg-burnishedGold mx-auto mt-5" />
          </div>

          {/* Product Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto justify-items-center">
            {displayProducts.map((product: any, index: number) => {
              const isFallback = !product.id || typeof product.id === "string" && product.id.startsWith("mock-");
              const priceValue = isFallback ? product.price : (product.variants?.[0]?.price || 0);
              const volumeText = isFallback ? product.volume : (product.variants?.[0]?.volume_weight || "250ml");
              const regionName = isFallback ? product.region : (product.sourcing?.region || "Tamil Nadu");
              const shortDesc = isFallback ? product.description : product.short_description;

              const isRasipuram = product.slug.toLowerCase().includes("rasipuram");
              const imageSrc = isRasipuram ? "/images/rasipuram-ghee.jpg" : "/images/uthukuli-ghee.jpg";

              return (
                <div 
                  key={product.id || product.slug}
                  className="flex flex-col w-full max-w-[520px] bg-white border border-burnishedGold/20 rounded-lg overflow-hidden hover:border-gheeGold/40 hover:shadow-[0_12px_30px_rgba(25,25,25,0.08)] hover:-translate-y-2 transition-all duration-300 ease-out group shadow-[0_4px_20px_rgba(0,0,0,0.03)] motion-safe:animate-fade-up"
                  style={{ animationDelay: `${index * 100}ms`, animationFillMode: "both" }}
                >
                  
                  {/* Product Image Container */}
                  <div className="w-full h-[260px] md:h-[300px] border-b border-burnishedGold/15 relative overflow-hidden select-none bg-gradient-to-br from-gheeGold/5 to-richCream/10">
                    <Image
                      src={imageSrc}
                      alt={product.name}
                      fill
                      priority={index === 0}
                      className="object-cover object-center transition-transform duration-500 ease-out group-hover:scale-[1.04] select-none pointer-events-none"
                    />
                  </div>

                  {/* Content Area */}
                  <div className="p-6 flex-grow flex flex-col justify-between gap-4">
                    <div className="space-y-3">
                      <div className="flex justify-between items-center">
                        <span className="px-2.5 py-1 bg-deodharForest text-richCream text-[9px] uppercase tracking-widest font-semibold rounded-[2px] shadow-sm border border-burnishedGold/25">
                          {regionName}
                        </span>
                        <span className="text-[10px] text-indianInk/60 font-sans tracking-widest uppercase font-semibold bg-warmIvory/60 px-2 py-0.5 rounded border border-burnishedGold/10">
                          {volumeText}
                        </span>
                      </div>

                      <h3 className="font-serif text-xl font-bold text-deodharForest leading-tight">
                        {product.name}
                      </h3>
                      <p className="font-sans text-xs text-indianInk/70 leading-relaxed">
                        {shortDesc}
                      </p>
                    </div>

                    <div className="flex items-center justify-between pt-4 border-t border-burnishedGold/10">
                      <div className="flex flex-col font-sans">
                        <span className="text-[9px] uppercase tracking-wider text-indianInk/45">Starting from</span>
                        <span className="font-sans text-sm font-bold text-indianInk">
                          {formatINR(priceValue)}
                        </span>
                      </div>
                      
                      <Link 
                        href={`/products/${product.slug}`}
                        className="relative overflow-hidden group/btn px-5 py-2.5 bg-deodharForest text-richCream rounded-[4px] font-sans text-[10px] font-semibold tracking-widest uppercase transition-all duration-300 ease-out border border-transparent hover:border-gheeGold hover:shadow-[0_4px_12px_rgba(15,61,46,0.15)] hover:-translate-y-0.5 text-center focus-visible:ring-2 focus-visible:ring-burnishedGold outline-none"
                      >
                        <span className="relative z-10">View Product</span>
                        <span className="absolute inset-0 w-full h-full bg-gradient-to-r from-transparent via-gheeGold/25 to-transparent -translate-x-full group-hover/btn:translate-x-full transition-transform duration-1000 ease-out" />
                      </Link>
                    </div>
                  </div>

                </div>
              );
            })}
          </div>

        </div>
      </div>
    </PublicLayout>
  );
}