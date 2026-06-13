"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import Image from "next/image";
import { useRouter } from "next/navigation";
import PublicLayout from "@/components/layout/public-layout";
import { useProducts } from "@/hooks/use-products";
import { useMe } from "@/hooks/use-auth";
import { useWishlist, useAddToWishlist, useRemoveFromWishlist } from "@/hooks/use-wishlist";
import { formatINR, optimizeCloudinaryUrl } from "@/lib/utils";
import { 
  ShieldCheck, 
  ArrowRight, 
  Compass, 
  Check,
  ChevronRight,
  Flame,
  Globe,
  Loader2,
  Heart
} from "lucide-react";
import { useMediaAsset } from "@/hooks/use-media";

function HomeProductImage({ mediaId, alt, fallbackSrc }: { mediaId?: string; alt: string; fallbackSrc: string }) {
  const isUrl = mediaId && (mediaId.startsWith("http://") || mediaId.startsWith("https://") || mediaId.startsWith("/"));
  const { data: mediaRes, isError } = useMediaAsset(isUrl ? "" : (mediaId || ""), { enabled: !!mediaId && !isUrl });
  const url = isUrl ? mediaId : ((!isError && mediaRes?.success && mediaRes?.data?.public_url) ? mediaRes.data.public_url : fallbackSrc);
  
  return (
    <Image
      src={optimizeCloudinaryUrl(url, 600)}
      alt={alt}
      fill
      className="object-cover object-center transition-transform duration-500 ease-out group-hover:scale-[1.04] select-none pointer-events-none"
    />
  );
}

export default function HomePage() {
  const { data: productsData, isPending: isLoadingProducts } = useProducts({ is_featured: true, limit: 4 });
  const dbProducts = productsData?.data || [];

  // Display only active featured products from the database
  const displayProducts = dbProducts.filter((product: any) => product.is_featured === true);

  const { data: meData } = useMe();
  const user = meData?.data;
  const isCustomer = user?.role === "customer";
  const router = useRouter();

  const { data: wishlistRes } = useWishlist();
  const wishlistItems = wishlistRes?.data?.items || [];

  const addToWishlistMutation = useAddToWishlist();
  const removeFromWishlistMutation = useRemoveFromWishlist();

  const [scrollY, setScrollY] = useState(0);
  const [useParallax, setUseParallax] = useState(false);

  useEffect(() => {
    const motionQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
    const handleScroll = () => {
      setScrollY(window.scrollY);
    };

    const checkParallax = () => {
      const isLarge = window.innerWidth >= 1024;
      const prefersReduced = motionQuery.matches;
      setUseParallax(isLarge && !prefersReduced);
    };

    checkParallax();
    window.addEventListener("scroll", handleScroll, { passive: true });
    window.addEventListener("resize", checkParallax);
    motionQuery.addEventListener("change", checkParallax);

    return () => {
      window.removeEventListener("scroll", handleScroll);
      window.removeEventListener("resize", checkParallax);
      motionQuery.removeEventListener("change", checkParallax);
    };
  }, []);

  const parallaxStyle = useParallax
    ? { transform: `translateY(${scrollY * 0.12}px) scale(1.05)`, transformOrigin: "center" }
    : {};

  return (
    <PublicLayout>
      <div className="bg-richCream text-indianInk min-h-screen selection:bg-deodharForest/10">
        
        {/* SECTION 1: HERO SECTION */}
        <section className="relative overflow-hidden w-full flex items-center min-h-[calc(100vh-var(--header-height))] h-[calc(100vh-var(--header-height))] border-b border-burnishedGold/25">
          {/* Background Image Container */}
          <div className="absolute inset-0 z-0 overflow-hidden">
            <Image
              src="/images/hero-bg.jpg"
              alt="Selecting the Best to Serve the Best"
              fill
              priority
              unoptimized
              className="object-cover object-center max-lg:object-[60%_50%] max-md:object-[68%_50%] transition-transform duration-100 ease-out select-none pointer-events-none"
              style={parallaxStyle}
            />
            {/* Left side dark gradient overlay for text readability */}
            <div 
              className="absolute inset-0 z-10 pointer-events-none select-none"
              style={{
                background: 'linear-gradient(90deg, rgba(0,0,0,0.55) 0%, rgba(0,0,0,0.35) 30%, rgba(0,0,0,0.05) 60%, rgba(0,0,0,0) 100%)'
              }}
            />
          </div>

          {/* Text Overlay Content */}
          <div className="relative z-20 w-full mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="max-w-[290px] sm:max-w-xl lg:max-w-2xl text-left md:-translate-y-8 min-[1440px]:translate-y-0 flex flex-col justify-center select-text">
              
              {/* Eyebrow with motion-safe fade-up */}
              <span className="text-xs sm:text-sm font-semibold uppercase tracking-[0.25em] text-[#D9A441] mb-4 motion-safe:animate-fade-up block font-sans">
                HERITAGE FOOD SELECTIONS
              </span>

              {/* Heading with motion-safe fade-up */}
              <h1 className="font-serif text-4xl sm:text-5xl md:text-6xl min-[1440px]:text-[72px] font-semibold text-[#FAF9F6] leading-[1.1] tracking-tight mb-6 motion-safe:animate-fade-up">
                Selecting the <span className="text-[#D9A441]">Best</span><br />
                to Serve the <span className="text-[#D9A441]">Best</span>
              </h1>

              {/* Description with motion-safe fade-up */}
              <p className="font-sans text-sm sm:text-base md:text-lg mb-8 max-w-md md:max-w-lg leading-relaxed text-[#FAF9F6]/90 motion-safe:animate-fade-up">
                Bharath Delight Foods brings carefully selected Indian food products to families with a focus on quality, responsibility, and trust.
              </p>

              {/* Stacking Buttons with motion-safe fade-up */}
              <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-4 pt-2 w-full sm:w-auto motion-safe:animate-fade-up">
                <Link
                  href="/shop"
                  className="relative overflow-hidden group px-8 py-4 bg-deodharForest text-warmIvory border border-gheeGold/40 hover:border-gheeGold rounded-[4px] font-sans text-xs font-bold tracking-[0.2em] uppercase transition-all duration-300 motion-safe:hover:-translate-y-0.5 hover:shadow-[0_4px_20px_rgba(217,164,65,0.25)] text-center focus-visible:ring-2 focus-visible:ring-burnishedGold outline-none"
                >
                  <span className="relative z-10">SHOP CATALOG</span>
                  <span className="absolute inset-0 w-full h-full bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000 ease-out" />
                </Link>

                <Link
                  href="/about"
                  className="px-8 py-4 border border-[rgba(255,255,255,0.45)] bg-[rgba(255,255,255,0.16)] text-white hover:border-[#D9A441] hover:text-[#D9A441] hover:bg-[rgba(255,255,255,0.25)] rounded-[4px] font-sans text-xs font-bold tracking-[0.2em] uppercase transition-all duration-300 motion-safe:hover:-translate-y-0.5 hover:shadow-[0_4px_20px_rgba(255,255,255,0.15)] text-center focus-visible:ring-2 focus-visible:ring-burnishedGold outline-none"
                >
                  LEARN OUR SELECTION PROCESS
                </Link>
              </div>

            </div>
          </div>
        </section>

        {/* BRAND STORY & OUR PROMISE SECTION */}
        <section className="py-20 bg-richCream border-b border-burnishedGold/15">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 space-y-16">
            
            {/* Brand Story */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-12 items-start animate-fade-up">
              <div className="lg:col-span-5 space-y-3">
                <span className="text-[10px] uppercase tracking-[0.25em] text-burnishedGold font-bold font-sans">
                  Our Journey
                </span>
                <h2 className="font-serif text-3xl sm:text-4xl font-bold text-deodharForest">
                  Welcome to Bharath Delight Foods
                </h2>
                <div className="w-12 h-0.5 bg-gheeGold" />
              </div>
              <div className="lg:col-span-7 space-y-4 font-sans text-sm sm:text-base text-indianInk/75 leading-relaxed">
                <p>
                  Bharath Delight Foods was founded with a simple belief: every family deserves access to food products they can trust.
                </p>
                <p>
                  In a market filled with countless choices, we focus on selecting products with care, consistency, and responsibility. Our aim is not to offer everything — our aim is to offer the right products.
                </p>
              </div>
            </div>

            {/* Our Promise Divider */}
            <div className="w-full h-px bg-burnishedGold/15 pt-4" />

            {/* Our Promise Cards */}
            <div className="space-y-10 animate-fade-up" style={{ animationDelay: "100ms" }}>
              <div className="text-center">
                <h3 className="font-serif text-2xl sm:text-3xl font-bold text-deodharForest">
                  Our Promise
                </h3>
                <div className="w-8 h-0.5 bg-gheeGold mx-auto mt-3" />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 sm:gap-8 max-w-5xl mx-auto">
                {/* Promise Card 1 */}
                <div className="bg-white border border-burnishedGold/15 rounded-lg p-6 shadow-sm hover:shadow-md hover:-translate-y-1 transition-all duration-300 flex flex-col gap-4 group">
                  <div className="w-10 h-10 bg-deodharForest/5 border border-burnishedGold/15 rounded-full flex items-center justify-center text-deodharForest group-hover:bg-deodharForest group-hover:text-richCream transition-all duration-300">
                    <Check className="w-5 h-5" />
                  </div>
                  <div className="space-y-2">
                    <h4 className="font-serif text-lg font-bold text-deodharForest">Carefully Selected</h4>
                    <p className="font-sans text-xs sm:text-sm text-indianInk/70 leading-relaxed">
                      We choose products that align with our expectations for taste, quality, and everyday family use.
                    </p>
                  </div>
                </div>

                {/* Promise Card 2 */}
                <div className="bg-white border border-burnishedGold/15 rounded-lg p-6 shadow-sm hover:shadow-md hover:-translate-y-1 transition-all duration-300 flex flex-col gap-4 group">
                  <div className="w-10 h-10 bg-deodharForest/5 border border-burnishedGold/15 rounded-full flex items-center justify-center text-deodharForest group-hover:bg-deodharForest group-hover:text-richCream transition-all duration-300">
                    <Compass className="w-5 h-5" />
                  </div>
                  <div className="space-y-2">
                    <h4 className="font-serif text-lg font-bold text-deodharForest">Responsible Presentation</h4>
                    <p className="font-sans text-xs sm:text-sm text-indianInk/70 leading-relaxed">
                      Every product is presented with clear details so customers can make confident purchase decisions.
                    </p>
                  </div>
                </div>

                {/* Promise Card 3 */}
                <div className="bg-white border border-burnishedGold/15 rounded-lg p-6 shadow-sm hover:shadow-md hover:-translate-y-1 transition-all duration-300 flex flex-col gap-4 group">
                  <div className="w-10 h-10 bg-deodharForest/5 border border-burnishedGold/15 rounded-full flex items-center justify-center text-deodharForest group-hover:bg-deodharForest group-hover:text-richCream transition-all duration-300">
                    <ShieldCheck className="w-5 h-5" />
                  </div>
                  <div className="space-y-2">
                    <h4 className="font-serif text-lg font-bold text-deodharForest">Built on Trust</h4>
                    <p className="font-sans text-xs sm:text-sm text-[#0F3D2E]/70 leading-relaxed">
                      From product selection to delivery, our process is designed to protect customer confidence.
                    </p>
                  </div>
                </div>
              </div>
            </div>

          </div>
        </section>

        {/* SECTION 2: FEATURED PRODUCTS SECTION */}
        <section 
          className="py-20 border-b border-burnishedGold/15"
          style={{ background: "radial-gradient(circle at center, #FFFDF0 0%, #FAF9F6 70%, #FFF7E8 100%)" }}
        >
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            
            <div className="text-center max-w-xl mx-auto mb-12 animate-fade-up">
              <span className="text-[10px] uppercase tracking-[0.25em] text-burnishedGold font-bold font-sans">
                Heritage Sourced
              </span>
              <h2 className="font-serif text-3xl font-bold text-deodharForest mt-1">
                Featured Products
              </h2>
              <p className="font-sans text-xs text-indianInk/70 mt-2">
                Our carefully selected food products.
              </p>
              <div className="w-12 h-0.5 bg-burnishedGold mx-auto mt-4" />
            </div>

            {/* Showcase only two product cards */}
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
              <div className="text-center py-10 text-indianInk/50 text-sm font-sans">
                Products coming soon.
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

                const firstVariantId = product.variants?.[0]?.variant_id;
                const isWishlisted = firstVariantId ? wishlistItems.some((item: any) => item.variant_id === firstVariantId) : false;

                return (
                  <div 
                    key={product.id || product.slug}
                    className="flex flex-col w-full max-w-[520px] bg-white border border-burnishedGold/20 rounded-lg overflow-hidden hover:border-gheeGold/40 hover:shadow-[0_12px_30px_rgba(25,25,25,0.08)] hover:-translate-y-2 transition-all duration-300 ease-out group shadow-[0_4px_20px_rgba(0,0,0,0.03)] motion-safe:animate-fade-up"
                    style={{ animationDelay: `${index * 100}ms`, animationFillMode: "both" }}
                  >
                    
                    {/* Product Image Container */}
                    <div className="w-full h-[260px] md:h-[300px] border-b border-burnishedGold/15 relative overflow-hidden select-none bg-gradient-to-br from-gheeGold/5 to-richCream/10">
                      <HomeProductImage
                        mediaId={product.media_ids?.[0]}
                        alt={product.name}
                        fallbackSrc={imageSrc}
                      />

                      {/* Wishlist Heart Toggle Icon */}
                      {firstVariantId && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            e.preventDefault();
                            if (!isCustomer) {
                              router.push("/login");
                              return;
                            }
                            if (isWishlisted) {
                              removeFromWishlistMutation.mutate(firstVariantId);
                            } else {
                              addToWishlistMutation.mutate({ productId: product.id, variantId: firstVariantId });
                            }
                          }}
                          className="absolute top-4 right-4 z-30 p-2.5 bg-white/95 backdrop-blur-sm hover:bg-white text-indianInk rounded-full border border-burnishedGold/15 shadow-md transition-all duration-300 hover:scale-110 active:scale-95 group/heart"
                          title={isWishlisted ? "Remove from Wishlist" : "Add to Wishlist"}
                        >
                          <Heart
                            className={`w-4 h-4 transition-all duration-300 ${
                              isWishlisted
                                ? "fill-red-600 text-red-600 scale-110"
                                : "text-burnishedGold/80 group-hover/heart:text-red-500 group-hover/heart:fill-red-50/50"
                            }`}
                          />
                        </button>
                      )}
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
        </section>

        {/* BOTTOM CTA SECTION */}
        <section className="py-20 border-b border-burnishedGold/15 bg-richCream">
          <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8 text-center space-y-6">
            <h2 className="font-serif text-3xl sm:text-4xl font-bold text-deodharForest leading-tight">
              Food products selected with care.
            </h2>
            <p className="font-sans text-sm sm:text-base text-indianInk/70 leading-relaxed max-w-2xl mx-auto">
              Explore our carefully selected range and choose products made for everyday family trust.
            </p>
            <div className="pt-4">
              <Link
                href="/shop"
                className="relative overflow-hidden group inline-flex px-8 py-4 bg-deodharForest text-warmIvory border border-gheeGold/40 hover:border-gheeGold rounded-[4px] font-sans text-xs font-bold tracking-[0.2em] uppercase transition-all duration-300 hover:shadow-[0_4px_20px_rgba(217,164,65,0.25)] text-center focus-visible:ring-2 focus-visible:ring-burnishedGold outline-none"
              >
                <span className="relative z-10">Shop Products</span>
                <span className="absolute inset-0 w-full h-full bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000 ease-out" />
              </Link>
            </div>
          </div>
        </section>

      </div>
    </PublicLayout>
  );
}