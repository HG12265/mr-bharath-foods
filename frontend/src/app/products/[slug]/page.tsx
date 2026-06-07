"use client";

import React, { use, useState } from "react";
import Link from "next/link";
import Image from "next/image";
import PublicLayout from "@/components/layout/public-layout";
import { useProductBySlug } from "@/hooks/use-products";
import { useAddToCart } from "@/hooks/use-cart";
import { formatINR } from "@/lib/utils";
import { ShieldCheck, Check, ArrowLeft, Plus, Minus, Loader2 } from "lucide-react";

// Fallback details for static display
const STATIC_PRODUCTS: Record<string, any> = {
  rasipuram: {
    id: "mock-rasipuram",
    name: "Rasipuram Pure Ghee",
    slug: "rasipuram-ghee",
    description: "Prepared through traditional slow-simmering methods. Celebrated for its deep aroma, nuttiness, and rich golden color.",
    volume: "250ml",
    price: 390.00,
    region: "Rasipuram, Tamil Nadu",
    texture: "Golden & Deeply Simmered"
  },
  uthukuli: {
    id: "mock-uthukuli",
    name: "Uthukuli A2 Cow Ghee",
    slug: "uthukuli-ghee",
    description: "Traditionally churned from milk of historical grass-fed herds. Notable for its delicate, natural white-to-yellow granules.",
    volume: "250ml",
    price: 420.00,
    region: "Uthukuli, Tamil Nadu",
    texture: "Naturally Granular & Fragrant"
  }
};

interface PageProps {
  params: Promise<{ slug: string }>;
}

export default function ProductDetailPage({ params }: PageProps) {
  const { slug } = use(params);
  const { data: dbProductData, isPending } = useProductBySlug(slug);
  const dbProduct = dbProductData?.data;

  const [quantity, setQuantity] = useState(1);
  const [successMessage, setSuccessMessage] = useState("");
  const addToCartMutation = useAddToCart();

  // Slug matching to see if we fall back to Rasipuram or Uthukuli
  const isRasipuram = slug.toLowerCase().includes("rasipuram");
  const fallbackProduct = isRasipuram ? STATIC_PRODUCTS.rasipuram : STATIC_PRODUCTS.uthukuli;

  // Final display product
  const product = dbProduct || fallbackProduct;
  const isDbAvailable = !!dbProduct;

  const priceValue = isDbAvailable ? (product.variants?.[0]?.price || 0) : product.price;
  const volumeText = isDbAvailable ? (product.variants?.[0]?.volume_weight || "250ml") : product.volume;
  const regionName = isDbAvailable ? (product.sourcing?.region || "Tamil Nadu") : product.region;
  const descriptionText = isDbAvailable ? product.description : product.description;

  const imageSrc = isRasipuram ? "/images/rasipuram-ghee.jpg" : "/images/uthukuli-ghee.jpg";

  // Check if we can interact with real DB cart additions
  const productId = isDbAvailable ? product.id : null;
  const variantId = isDbAvailable ? (product.variants?.[0]?.id || null) : null;
  const isCartDisabled = !productId || !variantId;

  const handleAddToCart = () => {
    if (isCartDisabled) return;
    addToCartMutation.mutate(
      {
        payload: {
          product_id: productId,
          variant_id: variantId,
          quantity: quantity,
        },
      },
      {
        onSuccess: (res) => {
          if (res.success) {
            setSuccessMessage("Added to cart successfully!");
            setTimeout(() => setSuccessMessage(""), 3000);
          }
        },
      }
    );
  };

  if (isPending) {
    return (
      <PublicLayout>
        <div className="min-h-screen bg-richCream flex flex-col justify-center items-center font-sans py-16">
          <div className="flex flex-col items-center gap-4">
            <Loader2 className="w-10 h-10 text-burnishedGold animate-spin" />
            <p className="text-indianInk/60 text-xs tracking-wider uppercase font-semibold">
              Loading Product Details...
            </p>
          </div>
        </div>
      </PublicLayout>
    );
  }

  return (
    <PublicLayout>
      <div 
        className="min-h-screen text-indianInk py-12 md:py-20 border-b border-burnishedGold/15"
        style={{ background: "radial-gradient(circle at center, #FFFDF0 0%, #FAF9F6 70%, #FFF7E8 100%)" }}
      >
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          
          {/* Back button */}
          <div className="mb-8 animate-fade-up">
            <Link 
              href="/shop"
              className="inline-flex items-center gap-2 text-xs font-sans font-semibold tracking-widest uppercase text-deodharForest hover:text-burnishedGold transition-colors duration-150"
            >
              <ArrowLeft className="w-3.5 h-3.5" /> Back to Shop
            </Link>
          </div>

          {/* Main PDP Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-16 items-start max-w-6xl mx-auto">
            
            {/* Left Column: Product Image */}
            <div className="lg:col-span-6 animate-fade-up">
              <div className="bg-white border border-burnishedGold/20 rounded-lg overflow-hidden shadow-[0_8px_30px_rgba(25,25,25,0.04)] aspect-square relative select-none">
                <Image
                  src={imageSrc}
                  alt={product.name}
                  fill
                  priority
                  className="object-cover object-center select-none pointer-events-none"
                />
              </div>
            </div>

            {/* Right Column: Product Info */}
            <div className="lg:col-span-6 flex flex-col gap-6 animate-fade-up" style={{ animationDelay: "100ms" }}>
              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <span className="px-2.5 py-1 bg-deodharForest text-richCream text-[9px] uppercase tracking-widest font-semibold rounded-[2px] shadow-sm border border-burnishedGold/25">
                    {regionName}
                  </span>
                </div>
                <h1 className="font-serif text-3xl sm:text-4xl font-bold text-deodharForest leading-tight">
                  {product.name}
                </h1>
                <div className="font-sans text-2xl font-bold text-indianInk mt-1">
                  {formatINR(priceValue)}
                </div>
              </div>

              <div className="w-full h-px bg-burnishedGold/15" />

              <p className="font-sans text-sm text-indianInk/80 leading-relaxed">
                {descriptionText}
              </p>

              {/* Selector Areas */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 mt-2">
                {/* Size Selector */}
                <div className="space-y-2">
                  <span className="text-[10px] uppercase tracking-wider text-indianInk/60 font-semibold block font-sans">
                    Available Volume
                  </span>
                  <button className="px-5 py-2.5 border-2 border-gheeGold bg-[#FFFDF0] text-[#0F3D2E] rounded-[4px] font-sans text-xs font-bold tracking-widest uppercase shadow-sm select-none cursor-default">
                    {volumeText}
                  </button>
                </div>

                {/* Quantity Selector */}
                <div className="space-y-2">
                  <span className="text-[10px] uppercase tracking-wider text-indianInk/60 font-semibold block font-sans">
                    Quantity
                  </span>
                  <div className="flex items-center border border-burnishedGold/25 rounded-[4px] w-32 bg-white overflow-hidden shadow-sm h-[42px]">
                    <button 
                      onClick={() => setQuantity(q => Math.max(1, q - 1))}
                      className="p-2 hover:bg-richCream text-indianInk/70 transition-colors w-10 flex items-center justify-center border-r border-burnishedGold/15 h-full"
                      aria-label="Decrease quantity"
                    >
                      <Minus className="w-3.5 h-3.5" />
                    </button>
                    <span className="flex-grow text-center text-sm font-sans font-bold text-indianInk">
                      {quantity}
                    </span>
                    <button 
                      onClick={() => setQuantity(q => q + 1)}
                      className="p-2 hover:bg-richCream text-indianInk/70 transition-colors w-10 flex items-center justify-center border-l border-burnishedGold/15 h-full"
                      aria-label="Increase quantity"
                    >
                      <Plus className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="space-y-3 pt-4">
                <button
                  onClick={handleAddToCart}
                  disabled={isCartDisabled || addToCartMutation.isPending}
                  className="w-full relative overflow-hidden group py-4 bg-deodharForest text-richCream rounded-[4px] font-sans text-xs font-bold tracking-[0.2em] uppercase transition-all duration-300 border border-transparent hover:border-gheeGold hover:shadow-[0_6px_20px_rgba(15,61,46,0.2)] disabled:opacity-50 disabled:cursor-not-allowed text-center flex items-center justify-center gap-2"
                >
                  {addToCartMutation.isPending ? (
                    <span>Adding to Cart...</span>
                  ) : (
                    <>
                      <span>Add to Cart</span>
                      <span className="absolute inset-0 w-full h-full bg-gradient-to-r from-transparent via-gheeGold/20 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000 ease-out" />
                    </>
                  )}
                </button>

                {isCartDisabled && (
                  <p className="text-xs text-warmSaffron font-medium font-sans text-center mt-1.5 flex items-center justify-center gap-1.5">
                    Product setup is pending. Please check back soon.
                  </p>
                )}

                {successMessage && (
                  <p className="text-xs text-deodharForest font-semibold font-sans text-center mt-1.5">
                    {successMessage}
                  </p>
                )}
              </div>

              {/* Highlights & Trust Notes */}
              <div className="grid grid-cols-2 gap-4 border-t border-burnishedGold/15 pt-6 mt-4">
                <div className="flex items-center gap-2 text-xs font-sans text-indianInk/85">
                  <Check className="w-4 h-4 text-gheeGold shrink-0" />
                  <span>Carefully Selected</span>
                </div>
                <div className="flex items-center gap-2 text-xs font-sans text-indianInk/85">
                  <Check className="w-4 h-4 text-gheeGold shrink-0" />
                  <span>Regional Source</span>
                </div>
                <div className="flex items-center gap-2 text-xs font-sans text-indianInk/85">
                  <Check className="w-4 h-4 text-gheeGold shrink-0" />
                  <span>Batch Traceable</span>
                </div>
                <div className="flex items-center gap-2 text-xs font-sans text-indianInk/85">
                  <Check className="w-4 h-4 text-gheeGold shrink-0" />
                  <span>Quality Checked</span>
                </div>
              </div>

              <div className="bg-[#FFFDF0] border-l-2 border-gheeGold p-4 rounded-r-[4px] mt-2 flex items-start gap-3 shadow-[0_2px_10px_rgba(217,164,65,0.03)]">
                <ShieldCheck className="w-5 h-5 text-deodharForest shrink-0 mt-0.5" />
                <p className="text-xs font-sans text-indianInk/70 leading-relaxed italic">
                  Every product is selected with responsibility and checked before reaching customers.
                </p>
              </div>

            </div>

          </div>

        </div>
      </div>
    </PublicLayout>
  );
}