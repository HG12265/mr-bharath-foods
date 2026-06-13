"use client";

import React from "react";
import Link from "next/link";
import PublicLayout from "@/components/layout/public-layout";
import { 
  ShieldCheck, 
  ArrowRight, 
  Sparkles,
  ClipboardCheck,
  CheckSquare,
  Package,
  Truck,
  Headphones
} from "lucide-react";

export default function TrustPage() {
  const steps = [
    {
      number: "01",
      title: "Product Selection",
      content: "We begin by choosing products that match our quality expectations, customer needs, and brand values. We focus on products that are suitable for everyday family use and align with our promise of responsibility.",
      icon: CheckSquare,
    },
    {
      number: "02",
      title: "Quality Review",
      content: "Before a product is presented to customers, we review its basic quality, packaging condition, product details, and overall suitability. We avoid unnecessary variety and focus on products we are confident to offer.",
      icon: ClipboardCheck,
    },
    {
      number: "03",
      title: "Safe Handling",
      content: "Products are handled with care to protect their condition before dispatch. We maintain a clean and organized handling process so that every order is prepared responsibly.",
      icon: ShieldCheck,
    },
    {
      number: "04",
      title: "Secure Packing",
      content: "Each order is packed carefully to reduce movement and protect the product during transit. Our packing approach is designed to keep the product safe until it reaches the customer.",
      icon: Package,
    },
    {
      number: "05",
      title: "Shipping & Delivery",
      content: "Once packed, orders are dispatched through available delivery partners. Customers can track order progress from confirmation to shipment updates and delivery.",
      icon: Truck,
    },
    {
      number: "06",
      title: "Support After Purchase",
      content: "Our responsibility does not end after dispatch. Customers can reach out for order support, delivery concerns, payment updates, and product-related assistance.",
      icon: Headphones,
    },
  ];

  return (
    <PublicLayout>
      <div 
        className="min-h-screen text-indianInk py-12 md:py-20 border-b border-burnishedGold/15"
        style={{ background: "radial-gradient(circle at center, #FFFDF0 0%, #FAF9F6 70%, #FFF7E8 100%)" }}
      >
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 space-y-16 md:space-y-24">
          
          {/* Page Hero */}
          <div className="text-center max-w-3xl mx-auto space-y-4 animate-fade-up">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 bg-deodharForest/5 border border-deodharForest/15 rounded-full text-[10px] font-sans font-bold uppercase tracking-wider text-deodharForest mb-2">
              <Sparkles className="w-3 h-3 text-gheeGold" /> Established 2026
            </div>
            <h1 className="font-serif text-4xl sm:text-5xl md:text-6xl font-bold text-deodharForest leading-tight">
              Our Trust Process
            </h1>
            <p className="font-serif text-lg sm:text-xl text-burnishedGold font-semibold italic tracking-wide">
              How we select, handle, pack, and deliver products with care.
            </p>
            <div className="w-16 h-0.5 bg-gheeGold mx-auto my-4" />
            <p className="font-sans text-sm sm:text-base text-indianInk/70 leading-relaxed max-w-2xl mx-auto">
              Trust is not built through words alone. At Bharath Delight Foods, we follow a careful process to ensure every product we present is selected responsibly, handled safely, and delivered with attention.
            </p>
          </div>

          {/* Process Timeline Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {steps.map((step, idx) => {
              const IconComponent = step.icon;
              return (
                <div 
                  key={step.number}
                  className="bg-white border border-burnishedGold/15 hover:border-burnishedGold/30 rounded-lg p-6 md:p-8 shadow-sm hover:shadow-md hover:-translate-y-1 transition-all duration-300 flex flex-col justify-between group relative overflow-hidden"
                  style={{ animationDelay: `${idx * 75}ms` }}
                >
                  {/* Subtle top color strip */}
                  <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-deodharForest to-gheeGold opacity-80" />
                  
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <span className="font-serif text-3xl font-bold text-gheeGold/40 group-hover:text-gheeGold transition-colors duration-300">
                        {step.number}
                      </span>
                      <div className="w-10 h-10 bg-deodharForest/5 border border-burnishedGold/15 rounded-full flex items-center justify-center text-deodharForest group-hover:bg-deodharForest group-hover:text-richCream transition-all duration-300">
                        <IconComponent className="w-5 h-5" />
                      </div>
                    </div>
                    
                    <h3 className="font-serif text-xl font-bold text-deodharForest">
                      {step.title}
                    </h3>
                    
                    <p className="font-sans text-xs sm:text-sm text-indianInk/70 leading-relaxed">
                      {step.content}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Closing CTA */}
          <div className="max-w-4xl mx-auto bg-deodharForest text-richCream rounded-lg p-8 md:p-12 shadow-md relative overflow-hidden text-center md:text-left flex flex-col md:flex-row items-center justify-between gap-8 animate-fade-up" style={{ animationDelay: "300ms" }}>
            {/* Background design elements */}
            <div className="absolute right-0 bottom-0 w-64 h-64 bg-radial-gradient from-gheeGold/10 to-transparent pointer-events-none rounded-full blur-2xl" />
            <div className="absolute top-0 left-0 w-32 h-32 bg-richCream/5 pointer-events-none rounded-full blur-xl" />

            <div className="relative z-10 space-y-4 max-w-xl">
              <h2 className="font-serif text-2xl sm:text-3xl font-bold text-white relative inline-block pb-2 group cursor-default">
                Built for confidence. Selected with care.
              </h2>
              <p className="font-sans text-sm sm:text-base text-warmIvory/80 leading-relaxed">
                Every product we offer is part of a simple promise: to serve families with responsibility, clarity, and trust.
              </p>
            </div>
            
            <div className="relative z-10 shrink-0">
              <Link
                href="/shop"
                className="inline-flex items-center gap-2 px-8 py-4 bg-gheeGold text-deodharForest hover:bg-white border border-transparent rounded-[4px] font-sans text-xs font-bold tracking-[0.2em] uppercase transition-all duration-300 text-center"
              >
                Explore Products <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          </div>

        </div>
      </div>
    </PublicLayout>
  );
}
