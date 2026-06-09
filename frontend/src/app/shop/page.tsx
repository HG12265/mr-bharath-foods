"use client";

import React from "react";
import Link from "next/link";
import Image from "next/image";
import PublicLayout from "@/components/layout/public-layout";
import { useProducts } from "@/hooks/use-products";
import { formatINR } from "@/lib/utils";

export default function ShopPage() {
  const { data: productsData, isPending: isLoadingProducts } = useProducts({ limit: 10 });
  const dbProducts = productsData?.data || [];

  // Only show real ghee products — no mock fallback
  const displayProducts = dbProducts.filter(p => p.slug.includes("ghee")).slice(0, 2);

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
          {isLoadingProducts ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto justify-items-center w-full">
              {[0, 1].map((i) => (
                <div key={i} className="w-full max-w-[520px] bg-white border border-burnishedGold/20 rounded-lg overflow-hidden shadow-sm animate-pulse">
                  <div className="w-full h-[260px] md:h-[300px] bg-burnishedGold/10" />
                  <div className="p-6 space-y-3">
                    <div className="flex justify-between">
                      <div className="h-5 w-28 bg-burnishedGold/10 rounded" />
                      <div className="h-5 w-12 bg-burnishedGold/10 rounded" />
                    </div>
                    <div className="h-6 w-3/4 bg-burnishedGold/10 rounded" />
                    <div className="space-y-1.5">
                      <div className="h-3 w-full bg-burnishedGold/10 rounded" />
                      <div className="h-3 w-5/6 bg-burnishedGold/10 rounded" />
                    </div>
                    <div className="flex justify-between items-center pt-4 border-t border-burnishedGold/10">
                      <div className="h-6 w-20 bg-burnishedGold/10 rounded" />
                      <div className="h-8 w-28 bg-burnishedGold/10 rounded" />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : displayProducts.length === 0 ? (
            <div className="text-center py-16 text-indianInk/50 text-sm font-sans">
              Products coming soon. Check back shortly.
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto justify-items-center">
              {displayProducts.map((product: any, index: number) => {
                const priceValue = product.variants?.[0]?.price || 0;
                const volumeText = product.variants?.[0]?.volume_weight || "250ml";
                const regionName = product.sourcing?.region || "Tamil Nadu";
                const shortDesc = product.short_description;

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
          )}

        </div>
      </div>
    </PublicLayout>
  );
}