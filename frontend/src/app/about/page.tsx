"use client";

import React from "react";
import Link from "next/link";
import PublicLayout from "@/components/layout/public-layout";
import { 
  Award, 
  ShieldCheck, 
  Heart, 
  Eye, 
  CheckCircle,
  ArrowRight,
  Sparkles
} from "lucide-react";

export default function AboutPage() {
  return (
    <PublicLayout>
      <div 
        className="min-h-screen text-indianInk py-12 md:py-20 border-b border-burnishedGold/15"
        style={{ background: "radial-gradient(circle at center, #FFFDF0 0%, #FAF9F6 70%, #FFF7E8 100%)" }}
      >
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 space-y-16 md:space-y-24">
          
          {/* SECTION 1: Page Hero */}
          <div className="text-center max-w-3xl mx-auto space-y-4 animate-fade-up">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 bg-deodharForest/5 border border-deodharForest/15 rounded-full text-[10px] font-sans font-bold uppercase tracking-wider text-deodharForest mb-2">
              <Sparkles className="w-3 h-3 text-gheeGold" /> Established 2026
            </div>
            <h1 className="font-serif text-4xl sm:text-5xl md:text-6xl font-bold text-deodharForest leading-tight">
              About Bharath Delight Foods
            </h1>
            <p className="font-serif text-lg sm:text-xl text-burnishedGold font-semibold italic tracking-wide">
              Selecting the Best to Serve the Best.
            </p>
            <div className="w-16 h-0.5 bg-gheeGold mx-auto my-4" />
            <p className="font-sans text-sm sm:text-base text-indianInk/70 leading-relaxed">
              We are a premium corporate food brand dedicated to the curation and delivery of pure, traditional Indian kitchen staples. By applying strict laboratory verification benchmarks, we build trust and ensure absolute quality in every pack.
            </p>
          </div>

          {/* SECTION 2: Our Story */}
          <div className="bg-white border border-burnishedGold/15 rounded-lg p-8 md:p-12 shadow-sm max-w-4xl mx-auto animate-fade-up" style={{ animationDelay: "100ms" }}>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 items-start">
              <div className="md:col-span-1 border-b md:border-b-0 md:border-r border-burnishedGold/15 pb-4 md:pb-0 md:pr-6">
                <h2 className="font-serif text-2xl sm:text-3xl font-bold text-deodharForest relative inline-block pb-2 group cursor-default">
                  Our Story
                  <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-gheeGold transition-all duration-300 group-hover:w-full" />
                </h2>
                <p className="text-[10px] uppercase font-sans font-bold tracking-widest text-burnishedGold mt-2">
                  The Roots of Trust
                </p>
              </div>
              <div className="md:col-span-2 space-y-4 font-sans text-sm sm:text-base text-indianInk/75 leading-relaxed">
                <p>
                  Bharath Delight Foods was founded with a simple belief: every family deserves access to genuinely good food products.
                </p>
                <p>
                  We begin with carefully selected ghee products and plan to expand thoughtfully into more Indian food categories.
                </p>
              </div>
            </div>
          </div>

          {/* SECTION 3: What We Do */}
          <div className="space-y-10 animate-fade-up" style={{ animationDelay: "200ms" }}>
            <div className="text-center">
              <h2 className="font-serif text-2xl sm:text-3xl font-bold text-deodharForest relative inline-block pb-2 group cursor-default">
                What We Do
                <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-gheeGold transition-all duration-300 group-hover:w-full" />
              </h2>
              <p className="text-xs uppercase font-sans font-semibold tracking-wider text-indianInk/55 mt-1">
                Our strict three-step quality lifecycle
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
              
              {/* Card 1: Select */}
              <div className="bg-white border border-burnishedGold/15 rounded-lg p-6 shadow-sm hover:shadow-md hover:-translate-y-1.5 transition-all duration-300 group flex flex-col items-center text-center space-y-4">
                <div className="w-12 h-12 bg-deodharForest/5 border border-burnishedGold/20 rounded-full flex items-center justify-center text-deodharForest group-hover:bg-deodharForest group-hover:text-richCream transition-all duration-300">
                  <Award className="w-5 h-5" />
                </div>
                <h3 className="font-serif text-lg font-bold text-deodharForest">Select</h3>
                <p className="font-sans text-xs sm:text-sm text-indianInk/65 leading-relaxed">
                  We locate and partner exclusively with regional manufacturing dairies that utilize traditional processing techniques.
                </p>
              </div>

              {/* Card 2: Verify */}
              <div className="bg-white border border-burnishedGold/15 rounded-lg p-6 shadow-sm hover:shadow-md hover:-translate-y-1.5 transition-all duration-300 group flex flex-col items-center text-center space-y-4">
                <div className="w-12 h-12 bg-deodharForest/5 border border-burnishedGold/20 rounded-full flex items-center justify-center text-deodharForest group-hover:bg-deodharForest group-hover:text-richCream transition-all duration-300">
                  <ShieldCheck className="w-5 h-5" />
                </div>
                <h3 className="font-serif text-lg font-bold text-deodharForest">Verify</h3>
                <p className="font-sans text-xs sm:text-sm text-indianInk/65 leading-relaxed">
                  Every batch of butter and ghee undergoes scientific laboratory tests to confirm purity, taste, and safety records.
                </p>
              </div>

              {/* Card 3: Serve */}
              <div className="bg-white border border-burnishedGold/15 rounded-lg p-6 shadow-sm hover:shadow-md hover:-translate-y-1.5 transition-all duration-300 group flex flex-col items-center text-center space-y-4">
                <div className="w-12 h-12 bg-deodharForest/5 border border-burnishedGold/20 rounded-full flex items-center justify-center text-deodharForest group-hover:bg-deodharForest group-hover:text-richCream transition-all duration-300">
                  <CheckCircle className="w-5 h-5" />
                </div>
                <h3 className="font-serif text-lg font-bold text-deodharForest">Serve</h3>
                <p className="font-sans text-xs sm:text-sm text-indianInk/65 leading-relaxed">
                  Shipped trace-sealed directly to your table, ensuring transparent access to genuine quality batch reports.
                </p>
              </div>

            </div>
          </div>

          {/* SECTION 4: Our Values */}
          <div className="bg-white border border-burnishedGold/15 rounded-lg p-8 md:p-12 shadow-sm max-w-5xl mx-auto space-y-10 animate-fade-up" style={{ animationDelay: "250ms" }}>
            <div className="text-center max-w-xl mx-auto space-y-2">
              <h2 className="font-serif text-2xl sm:text-3xl font-bold text-deodharForest relative inline-block pb-2 group cursor-default">
                Our Values
                <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-gheeGold transition-all duration-300 group-hover:w-full" />
              </h2>
              <p className="text-xs font-sans text-indianInk/55 leading-relaxed">
                The corporate pillars that define our relationship with farmers, packaging partners, and customers.
              </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
              
              {/* Value 1: Responsibility */}
              <div className="space-y-2 p-4 border border-burnishedGold/10 rounded-[4px] hover:border-burnishedGold/25 transition-colors duration-200">
                <div className="flex items-center gap-2 text-deodharForest">
                  <Heart className="w-4 h-4 text-gheeGold" />
                  <h4 className="font-serif text-base font-bold">Responsibility</h4>
                </div>
                <p className="font-sans text-xs text-indianInk/60 leading-relaxed">
                  Providing nutrition choices that contribute to structural wellness for families.
                </p>
              </div>

              {/* Value 2: Quality */}
              <div className="space-y-2 p-4 border border-burnishedGold/10 rounded-[4px] hover:border-burnishedGold/25 transition-colors duration-200">
                <div className="flex items-center gap-2 text-deodharForest">
                  <Award className="w-4 h-4 text-gheeGold" />
                  <h4 className="font-serif text-base font-bold">Quality</h4>
                </div>
                <p className="font-sans text-xs text-indianInk/60 leading-relaxed">
                  Meeting uncompromising standards on moisture, fat profile, and sealing logs.
                </p>
              </div>

              {/* Value 3: Authenticity */}
              <div className="space-y-2 p-4 border border-burnishedGold/10 rounded-[4px] hover:border-burnishedGold/25 transition-colors duration-200">
                <div className="flex items-center gap-2 text-deodharForest">
                  <Sparkles className="w-4 h-4 text-gheeGold" />
                  <h4 className="font-serif text-base font-bold">Authenticity</h4>
                </div>
                <p className="font-sans text-xs text-indianInk/60 leading-relaxed">
                  Honoring slow-simmering processes without colorings, fillers, or additives.
                </p>
              </div>

              {/* Value 4: Transparency */}
              <div className="space-y-2 p-4 border border-burnishedGold/10 rounded-[4px] hover:border-burnishedGold/25 transition-colors duration-200">
                <div className="flex items-center gap-2 text-deodharForest">
                  <Eye className="w-4 h-4 text-gheeGold" />
                  <h4 className="font-serif text-base font-bold">Transparency</h4>
                </div>
                <p className="font-sans text-xs text-indianInk/60 leading-relaxed">
                  Making laboratory testing parameters and manufacturing details fully transparent.
                </p>
              </div>

            </div>
          </div>

          {/* SECTION 5: Future Vision */}
          <div className="max-w-4xl mx-auto bg-deodharForest text-richCream rounded-lg p-8 md:p-12 shadow-md relative overflow-hidden animate-fade-up" style={{ animationDelay: "300ms" }}>
            
            {/* Background design elements */}
            <div className="absolute right-0 bottom-0 w-64 h-64 bg-radial-gradient from-gheeGold/10 to-transparent pointer-events-none rounded-full blur-2xl" />
            <div className="absolute top-0 left-0 w-32 h-32 bg-richCream/5 pointer-events-none rounded-full blur-xl" />

            <div className="relative z-10 space-y-4 max-w-xl">
              <h2 className="font-serif text-2xl sm:text-3xl font-bold text-white relative inline-block pb-2 group cursor-default">
                Future Vision
                <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-gheeGold transition-all duration-300 group-hover:w-full" />
              </h2>
              <p className="font-sans text-sm sm:text-base text-warmIvory/80 leading-relaxed">
                Today we work with trusted partners. Tomorrow we aim to expand into broader food categories while maintaining the same commitment to quality.
              </p>
              <div className="pt-2">
                <Link
                  href="/shop"
                  className="inline-flex items-center gap-2 text-xs font-sans font-bold tracking-widest uppercase text-gheeGold hover:text-white transition-colors duration-200"
                >
                  Explore Current Products <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </div>
          </div>

        </div>
      </div>
    </PublicLayout>
  );
}
