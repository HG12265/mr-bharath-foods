"use client";

import React, { useState, useEffect, Suspense } from "react";
import Link from "next/link";
import Image from "next/image";
import { useRouter, useSearchParams } from "next/navigation";
import PublicLayout from "@/components/layout/public-layout";
import { useProducts } from "@/hooks/use-products";
import { useCategories } from "@/hooks/use-categories";
import { useSession } from "@/hooks/use-auth";
import { useWishlist, useAddToWishlist, useRemoveFromWishlist } from "@/hooks/use-wishlist";
import { formatINR, optimizeCloudinaryUrl, getProductFallbackImage } from "@/lib/utils";
import { Heart, Search, ChevronDown, SlidersHorizontal, X, Loader2 } from "lucide-react";
import { useMediaAsset } from "@/hooks/use-media";
import { Product } from "@/types";

function ShopProductImage({ mediaId, alt, productNameOrSlug, index }: { mediaId?: string; alt: string; productNameOrSlug?: string; index: number }) {
  const fallbackSrc = getProductFallbackImage(productNameOrSlug);
  const isUrl = mediaId && (mediaId.startsWith("http://") || mediaId.startsWith("https://") || mediaId.startsWith("/"));
  const { data: mediaRes, isError } = useMediaAsset(isUrl ? "" : (mediaId || ""), { enabled: !!mediaId && !isUrl });
  const url = isUrl ? mediaId : ((!isError && mediaRes?.success && mediaRes?.data?.public_url) ? mediaRes.data.public_url : fallbackSrc);
  
  return (
    <Image
      src={optimizeCloudinaryUrl(url, 600)}
      alt={alt}
      fill
      priority={index === 0}
      className="object-cover object-center transition-transform duration-500 ease-out group-hover:scale-[1.04] select-none pointer-events-none"
    />
  );
}

function ShopLoadingSkeleton() {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8 justify-items-center w-full">
      {[0, 1, 2, 3, 4, 5].map((i) => (
        <div key={i} className="w-full max-w-[380px] bg-white border border-burnishedGold/20 rounded-lg overflow-hidden shadow-sm animate-pulse">
          <div className="w-full h-[240px] bg-burnishedGold/10" />
          <div className="p-6 space-y-3">
            <div className="flex justify-between">
              <div className="h-5 w-24 bg-burnishedGold/10 rounded" />
              <div className="h-5 w-12 bg-burnishedGold/10 rounded" />
            </div>
            <div className="h-6 w-3/4 bg-burnishedGold/10 rounded" />
            <div className="space-y-1.5">
              <div className="h-3 w-full bg-burnishedGold/10 rounded" />
              <div className="h-3 w-5/6 bg-burnishedGold/10 rounded" />
            </div>
            <div className="flex justify-between items-center pt-4 border-t border-burnishedGold/10">
              <div className="h-6 w-16 bg-burnishedGold/10 rounded" />
              <div className="h-8 w-24 bg-burnishedGold/10 rounded" />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

function ShopContent() {
  const router = useRouter();
  const searchParams = useSearchParams();

  // Read URL values
  const urlCategory = searchParams.get("category") || "";
  const urlSearch = searchParams.get("search") || "";
  const urlSort = searchParams.get("sort") || "featured";
  const urlPage = parseInt(searchParams.get("page") || "1", 10);

  // States
  const [searchInput, setSearchInput] = useState(urlSearch);
  const [page, setPage] = useState(urlPage);
  const [productsList, setProductsList] = useState<Product[]>([]);
  const [mobileFilterOpen, setMobileFilterOpen] = useState(false);

  // Sync state page with URL page
  useEffect(() => {
    setPage(urlPage);
  }, [urlPage]);

  // Sync input text with URL search
  useEffect(() => {
    setSearchInput(urlSearch);
  }, [urlSearch]);

  // Fetch Categories
  const { data: categoriesRes } = useCategories();
  const categories = categoriesRes?.data || [];

  // Fetch Products
  const { data: productsRes, isPending: isLoadingProducts } = useProducts({
    category_slug: urlCategory || undefined,
    search: urlSearch || undefined,
    sort: urlSort,
    page: page,
    limit: 12
  });

  // Handle accumulative list appending
  useEffect(() => {
    if (productsRes?.success && productsRes?.data) {
      const newProds = productsRes.data.products || [];
      if (productsRes.data.page === 1) {
        setProductsList(newProds);
      } else {
        setProductsList((prev) => {
          const existingIds = new Set(prev.map((p) => p.id));
          const filteredNew = newProds.filter((p) => !existingIds.has(p.id));
          return [...prev, ...filteredNew];
        });
      }
    }
  }, [productsRes]);

  // Wishlist bindings
  const { data: sessionData } = useSession();
  const user = sessionData?.data?.user;
  const isCustomer = user?.role === "customer";
  const { data: wishlistRes } = useWishlist();
  const wishlistItems = wishlistRes?.data?.items || [];
  const addToWishlistMutation = useAddToWishlist();
  const removeFromWishlistMutation = useRemoveFromWishlist();

  // URL updating helper
  const updateUrl = (newParams: { category?: string; search?: string; sort?: string; page?: number }) => {
    const params = new URLSearchParams(searchParams.toString());
    
    if (newParams.category !== undefined) {
      if (newParams.category) params.set("category", newParams.category);
      else params.delete("category");
    }
    if (newParams.search !== undefined) {
      if (newParams.search) params.set("search", newParams.search.trim());
      else params.delete("search");
    }
    if (newParams.sort !== undefined) {
      params.set("sort", newParams.sort);
    }
    if (newParams.page !== undefined) {
      params.set("page", newParams.page.toString());
    } else {
      // Reset page to 1 on filter/search/sort change
      params.set("page", "1");
    }

    router.push(`/shop?${params.toString()}`, { scroll: false });
  };

  // Debounce search input
  useEffect(() => {
    const handler = setTimeout(() => {
      if (searchInput !== urlSearch) {
        updateUrl({ search: searchInput });
      }
    }, 500);

    return () => clearTimeout(handler);
  }, [searchInput]);

  const handleCategorySelect = (slug: string) => {
    setMobileFilterOpen(false);
    updateUrl({ category: slug });
  };

  const handleSortChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    updateUrl({ sort: e.target.value });
  };

  const handleLoadMore = () => {
    const nextPage = page + 1;
    updateUrl({ page: nextPage });
  };

  const clearAllFilters = () => {
    setSearchInput("");
    setMobileFilterOpen(false);
    router.push("/shop", { scroll: false });
  };

  const totalProducts = productsRes?.data?.total_count || 0;
  const hasMore = productsRes?.data?.has_more || false;

  return (
    <div className="min-h-screen text-indianInk py-12" style={{ background: "radial-gradient(circle at center, #FFFDF0 0%, #FAF9F6 70%, #FFF7E8 100%)" }}>
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        
        {/* Header Section */}
        <div className="text-center max-w-2xl mx-auto mb-12 animate-fade-up">
          <span className="text-[10px] uppercase tracking-[0.25em] text-burnishedGold font-bold font-sans">
            Pure Regional Selections
          </span>
          <h1 className="font-serif text-4xl sm:text-5xl font-bold text-deodharForest mt-2">
            Our Product Catalog
          </h1>
          <p className="font-sans text-sm text-indianInk/70 mt-3 max-w-md mx-auto leading-relaxed">
            Carefully selected food products from trusted regional sources, laboratory verified and fully traceable.
          </p>
          <div className="w-16 h-0.5 bg-burnishedGold mx-auto mt-5" />
        </div>

        {/* Toolbar (Mobile Filters / Search / Sort) */}
        <div className="bg-white border border-burnishedGold/15 rounded-lg p-4 mb-8 shadow-sm flex flex-col md:flex-row gap-4 justify-between items-center">
          {/* Search bar */}
          <div className="relative w-full md:max-w-xs">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-indianInk/40" />
            <input
              type="text"
              placeholder="Search products..."
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-[#FAF9F6] border border-burnishedGold/20 rounded-[4px] font-sans text-xs focus:outline-none focus:border-[#D9A441] text-indianInk transition-colors"
            />
            {searchInput && (
              <button 
                onClick={() => setSearchInput("")}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-indianInk/40 hover:text-indianInk"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            )}
          </div>

          <div className="flex items-center gap-3 w-full md:w-auto justify-between md:justify-end">
            {/* Mobile Filter Toggle */}
            <button
              onClick={() => setMobileFilterOpen(true)}
              className="flex md:hidden items-center gap-2 px-4 py-2 border border-burnishedGold/25 rounded-[4px] font-sans text-xs font-semibold text-deodharForest bg-[#FAF9F6] hover:bg-white"
            >
              <SlidersHorizontal className="w-3.5 h-3.5" />
              Filters
            </button>

            {/* Product count text */}
            <div className="text-[11px] font-sans font-semibold tracking-wider text-indianInk/50 uppercase">
              {productsList.length > 0 ? `Showing ${productsList.length} of ${totalProducts} products` : "0 products"}
            </div>

            {/* Sort Dropdown */}
            <div className="relative">
              <select
                value={urlSort}
                onChange={handleSortChange}
                className="appearance-none pl-4 pr-10 py-2 bg-[#FAF9F6] border border-burnishedGold/20 rounded-[4px] font-sans text-xs font-semibold text-deodharForest focus:outline-none focus:border-[#D9A441] cursor-pointer"
              >
                <option value="featured">Sort: Featured</option>
                <option value="price_asc">Price: Low to High</option>
                <option value="price_desc">Price: High to Low</option>
                <option value="newest">Newest Arrived</option>
              </select>
              <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-deodharForest/60 pointer-events-none" />
            </div>
          </div>
        </div>

        {/* Mobile Horizontal Category Chips */}
        <div className="md:hidden overflow-x-auto whitespace-nowrap pb-4 mb-4 -mx-4 px-4 scrollbar-none flex gap-2">
          <button
            onClick={() => handleCategorySelect("")}
            className={`px-4 py-1.5 rounded-full text-xs font-sans font-semibold uppercase tracking-wider transition-all border ${
              !urlCategory
                ? "bg-deodharForest text-richCream border-deodharForest"
                : "bg-white text-deodharForest border-burnishedGold/20 hover:border-burnishedGold/45"
            }`}
          >
            All Products
          </button>
          {categories.map((cat) => (
            <button
              key={cat.id}
              onClick={() => handleCategorySelect(cat.slug)}
              className={`px-4 py-1.5 rounded-full text-xs font-sans font-semibold uppercase tracking-wider transition-all border ${
                urlCategory === cat.slug
                  ? "bg-deodharForest text-richCream border-deodharForest"
                  : "bg-white text-deodharForest border-burnishedGold/20 hover:border-burnishedGold/45"
              }`}
            >
              {cat.name}
            </button>
          ))}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 items-start">
          
          {/* Desktop Categories Sidebar */}
          <aside className="hidden md:block col-span-1 bg-white border border-burnishedGold/15 rounded-lg p-6 shadow-sm sticky top-24">
            <h2 className="font-serif text-lg font-bold text-deodharForest border-b border-burnishedGold/15 pb-3 mb-4">
              Categories
            </h2>
            <nav className="flex flex-col gap-1.5">
              <button
                onClick={() => handleCategorySelect("")}
                className={`w-full text-left px-3 py-2 text-xs font-sans font-semibold tracking-wider uppercase rounded transition-colors ${
                  !urlCategory
                    ? "bg-deodharForest text-richCream"
                    : "text-indianInk/75 hover:bg-[#FAF9F6] hover:text-deodharForest"
                }`}
              >
                All Products
              </button>
              {categories.map((cat) => (
                <button
                  key={cat.id}
                  onClick={() => handleCategorySelect(cat.slug)}
                  className={`w-full text-left px-3 py-2 text-xs font-sans font-semibold tracking-wider uppercase rounded transition-colors ${
                    urlCategory === cat.slug
                      ? "bg-deodharForest text-richCream"
                      : "text-indianInk/75 hover:bg-[#FAF9F6] hover:text-deodharForest"
                  }`}
                >
                  {cat.name}
                </button>
              ))}
            </nav>
          </aside>

          {/* Product Grid Area */}
          <div className="col-span-1 md:col-span-3">
            {isLoadingProducts && productsList.length === 0 ? (
              <ShopLoadingSkeleton />
            ) : productsList.length === 0 ? (
              <div className="bg-white border border-burnishedGold/15 rounded-lg p-16 text-center shadow-sm max-w-xl mx-auto animate-fade-up">
                <SlidersHorizontal className="w-12 h-12 text-burnishedGold/40 mx-auto mb-4" />
                <h3 className="font-serif text-xl font-bold text-deodharForest">
                  No products found in this selection.
                </h3>
                <p className="font-sans text-xs text-indianInk/60 mt-2 max-w-sm mx-auto leading-relaxed">
                  Try adjusting your keywords, selecting another category, or resetting your filter.
                </p>
                <button
                  onClick={clearAllFilters}
                  className="mt-6 px-6 py-2.5 bg-deodharForest text-richCream rounded-[4px] font-sans text-[10px] font-semibold tracking-widest uppercase transition-all duration-300 border border-transparent hover:border-gheeGold"
                >
                  Clear All Filters
                </button>
              </div>
            ) : (
              <div className="space-y-12">
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8 justify-items-center">
                  {productsList.map((product, index) => {
                    const priceValue = product.variants?.[0]?.price || 0;
                    const volumeText = product.variants?.[0]?.volume_weight || "250ml";
                    const regionName = product.sourcing?.region || "Tamil Nadu";
                    const shortDesc = product.short_description;

                    const firstVariantId = product.variants?.[0]?.variant_id;
                    const isWishlisted = firstVariantId ? wishlistItems.some((item: any) => item.variant_id === firstVariantId) : false;

                    return (
                      <div
                        key={product.id || product.slug}
                        className="flex flex-col w-full max-w-[380px] bg-white border border-burnishedGold/20 rounded-lg overflow-hidden hover:border-gheeGold/40 hover:shadow-[0_12px_24px_rgba(25,25,25,0.06)] hover:-translate-y-1.5 transition-all duration-300 ease-out group shadow-[0_4px_12px_rgba(0,0,0,0.02)] motion-safe:animate-fade-up"
                        style={{ animationDelay: `${(index % 12) * 50}ms`, animationFillMode: "both" }}
                      >
                        {/* Product Image Container */}
                        <div className="w-full h-[240px] border-b border-burnishedGold/15 relative overflow-hidden select-none bg-gradient-to-br from-gheeGold/5 to-richCream/10">
                          <ShopProductImage
                            mediaId={product.media_urls?.[0] || product.media_ids?.[0]}
                            alt={product.name}
                            productNameOrSlug={product.slug}
                            index={index}
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
                              className="absolute top-4 right-4 z-30 p-2 bg-white/95 backdrop-blur-sm hover:bg-white text-indianInk rounded-full border border-burnishedGold/15 shadow-md transition-all duration-300 hover:scale-110 active:scale-95 group/heart"
                              title={isWishlisted ? "Remove from Wishlist" : "Add to Wishlist"}
                            >
                              <Heart
                                className={`w-3.5 h-3.5 transition-all duration-300 ${
                                  isWishlisted
                                    ? "fill-red-600 text-red-600 scale-110"
                                    : "text-burnishedGold/80 group-hover/heart:text-red-500 group-hover/heart:fill-red-50/50"
                                }`}
                              />
                            </button>
                          )}
                        </div>

                        {/* Content Area */}
                        <div className="p-5 flex-grow flex flex-col justify-between gap-4">
                          <div className="space-y-2.5">
                            <div className="flex justify-between items-center">
                              <span className="px-2 py-0.5 bg-deodharForest text-richCream text-[8px] uppercase tracking-widest font-semibold rounded-[2px] shadow-sm border border-burnishedGold/25">
                                {regionName}
                              </span>
                              <span className="text-[9px] text-indianInk/60 font-sans tracking-widest uppercase font-semibold bg-warmIvory/60 px-2 py-0.5 rounded border border-burnishedGold/10">
                                {volumeText}
                              </span>
                            </div>

                            <h3 className="font-serif text-lg font-bold text-deodharForest leading-tight">
                              {product.name}
                            </h3>
                            <p className="font-sans text-[11px] text-indianInk/70 leading-relaxed line-clamp-2">
                              {shortDesc}
                            </p>
                          </div>

                          <div className="flex items-center justify-between pt-3.5 border-t border-burnishedGold/10">
                            <div className="flex flex-col font-sans">
                              <span className="text-[8px] uppercase tracking-wider text-indianInk/45">Starting from</span>
                              <span className="font-sans text-xs font-bold text-indianInk">
                                {formatINR(priceValue)}
                              </span>
                            </div>
                            
                            <Link 
                              href={`/products/${product.slug}`}
                              className="relative overflow-hidden group/btn px-4 py-2 bg-deodharForest text-richCream rounded-[4px] font-sans text-[9px] font-semibold tracking-widest uppercase transition-all duration-300 ease-out border border-transparent hover:border-gheeGold hover:shadow-[0_4px_10px_rgba(15,61,46,0.12)] hover:-translate-y-0.5 text-center focus-visible:ring-2 focus-visible:ring-burnishedGold outline-none"
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

                {/* Load More Pagination */}
                {hasMore && (
                  <div className="text-center pt-4">
                    <button
                      onClick={handleLoadMore}
                      disabled={isLoadingProducts}
                      className="relative overflow-hidden group inline-flex items-center gap-2 px-8 py-3.5 bg-deodharForest text-warmIvory border border-gheeGold/40 hover:border-gheeGold rounded-[4px] font-sans text-xs font-bold tracking-[0.2em] uppercase transition-all duration-300 hover:shadow-[0_4px_20px_rgba(217,164,65,0.2)] text-center focus-visible:ring-2 focus-visible:ring-burnishedGold outline-none disabled:opacity-60 disabled:pointer-events-none"
                    >
                      {isLoadingProducts ? (
                        <>
                          <Loader2 className="w-3.5 h-3.5 animate-spin" />
                          Loading...
                        </>
                      ) : (
                        <>
                          <span className="relative z-10">LOAD MORE PRODUCTS</span>
                          <span className="absolute inset-0 w-full h-full bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000 ease-out" />
                        </>
                      )}
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Mobile Filter Drawer Overlay */}
        {mobileFilterOpen && (
          <div className="fixed inset-0 z-50 flex justify-end">
            <div 
              className="absolute inset-0 bg-black/40 backdrop-blur-sm transition-opacity" 
              onClick={() => setMobileFilterOpen(false)}
            />
            <div className="relative w-full max-w-xs bg-richCream h-full p-6 shadow-2xl flex flex-col justify-between animate-fade-in border-l border-burnishedGold/20">
              <div className="space-y-6">
                <div className="flex justify-between items-center border-b border-burnishedGold/15 pb-4">
                  <h3 className="font-serif text-lg font-bold text-deodharForest">Filter Categories</h3>
                  <button onClick={() => setMobileFilterOpen(false)} className="text-indianInk/60 hover:text-indianInk">
                    <X className="w-5 h-5" />
                  </button>
                </div>
                <nav className="flex flex-col gap-2">
                  <button
                    onClick={() => handleCategorySelect("")}
                    className={`w-full text-left px-4 py-2.5 text-xs font-sans font-semibold tracking-wider uppercase rounded transition-colors ${
                      !urlCategory
                        ? "bg-deodharForest text-richCream"
                        : "bg-white text-indianInk/75 border border-burnishedGold/15 hover:bg-[#FAF9F6]"
                    }`}
                  >
                    All Products
                  </button>
                  {categories.map((cat) => (
                    <button
                      key={cat.id}
                      onClick={() => handleCategorySelect(cat.slug)}
                      className={`w-full text-left px-4 py-2.5 text-xs font-sans font-semibold tracking-wider uppercase rounded transition-colors ${
                        urlCategory === cat.slug
                          ? "bg-deodharForest text-richCream"
                          : "bg-white text-indianInk/75 border border-burnishedGold/15 hover:bg-[#FAF9F6]"
                      }`}
                    >
                      {cat.name}
                    </button>
                  ))}
                </nav>
              </div>

              <button
                onClick={clearAllFilters}
                className="w-full py-3 bg-[#FAF9F6] border border-burnishedGold/20 text-deodharForest rounded font-sans text-xs font-bold tracking-wider uppercase hover:bg-white"
              >
                Clear All
              </button>
            </div>
          </div>
        )}

      </div>
    </div>
  );
}

export default function ShopPage() {
  return (
    <PublicLayout>
      <Suspense fallback={
        <div className="min-h-screen py-16 flex items-center justify-center bg-[#FAF9F6]">
          <Loader2 className="w-8 h-8 animate-spin text-[#D9A441]" />
        </div>
      }>
        <ShopContent />
      </Suspense>
    </PublicLayout>
  );
}