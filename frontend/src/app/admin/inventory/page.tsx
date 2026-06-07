"use client";

import React, { useState } from "react";
import { useProducts } from "@/hooks/use-products";
import { useInventoryBySku, useAdjustStock } from "@/hooks/use-inventory";
import { Loader2, Search, Edit3, ShieldAlert, AlertTriangle, CheckCircle } from "lucide-react";

export default function AdminInventoryPage() {
  const { data: productsRes, isPending: isProductsPending } = useProducts();
  const [searchQuery, setSearchQuery] = useState("");

  // Adjustment Modal States
  const [adjustingSku, setAdjustingSku] = useState<string | null>(null);
  const [adjustingTitle, setAdjustingTitle] = useState("");
  const [warehouseId, setWarehouseId] = useState("WH-MAIN");
  const [quantityDelta, setQuantityDelta] = useState(0);
  const [locationCode, setLocationCode] = useState("");
  const [adjustError, setAdjustError] = useState("");
  const [adjustSuccess, setAdjustSuccess] = useState("");

  const adjustStockMutation = useAdjustStock();

  const products = productsRes?.data || [];

  // Compile all variants from products
  const allVariants: Array<{
    productId: string;
    productName: string;
    variantId: string;
    sku: string;
    title: string;
    volume_weight: string;
    stock_status: string;
  }> = [];

  products.forEach((product) => {
    product.variants?.forEach((v) => {
      allVariants.push({
        productId: product.id,
        productName: product.name,
        variantId: v.variant_id,
        sku: v.sku,
        title: v.title,
        volume_weight: v.volume_weight,
        stock_status: v.stock_status
      });
    });
  });

  // Filter based on search query
  const filteredVariants = allVariants.filter(
    (v) =>
      v.sku.toLowerCase().includes(searchQuery.toLowerCase()) ||
      v.productName.toLowerCase().includes(searchQuery.toLowerCase()) ||
      v.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleOpenAdjust = (sku: string, title: string) => {
    setAdjustingSku(sku);
    setAdjustingTitle(title);
    setWarehouseId("WH-MAIN");
    setQuantityDelta(0);
    setLocationCode("");
    setAdjustError("");
    setAdjustSuccess("");
  };

  const handleSaveAdjustment = async (e: React.FormEvent) => {
    e.preventDefault();
    setAdjustError("");
    setAdjustSuccess("");

    if (!adjustingSku) return;

    if (quantityDelta === 0) {
      setAdjustError("Please specify a non-zero adjustment quantity delta.");
      return;
    }

    try {
      await adjustStockMutation.mutateAsync({
        sku: adjustingSku,
        payload: {
          warehouse_id: warehouseId,
          quantity: quantityDelta,
          location_code: locationCode || undefined
        }
      });
      setAdjustSuccess("Stock adjusted successfully!");
      setTimeout(() => {
        setAdjustingSku(null);
        setAdjustSuccess("");
      }, 1000);
    } catch (err: any) {
      setAdjustError(err?.response?.data?.message || "Failed to adjust stock. Check if result would be negative.");
    }
  };

  if (isProductsPending) {
    return (
      <div className="flex justify-center items-center py-20">
        <Loader2 className="w-8 h-8 animate-spin text-burnishedGold" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      
      {/* Title */}
      <div className="border-b border-burnishedGold/10 pb-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="font-serif text-2xl sm:text-3xl font-bold text-deodharForest">
            Inventory Registry
          </h1>
          <p className="text-xs sm:text-sm text-indianInk/60 mt-1">
            Check physical inventory counts across warehouse nodes and post audits or corrections.
          </p>
        </div>

        {/* Search Input */}
        <div className="relative max-w-xs w-full">
          <span className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-indianInk/40">
            <Search className="w-4 h-4" />
          </span>
          <input
            type="text"
            placeholder="Search SKU or Product..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2 font-sans text-xs border border-burnishedGold/30 focus:border-burnishedGold bg-white rounded focus:outline-none placeholder-indianInk/40"
          />
        </div>
      </div>

      {/* Inventory Table Container */}
      <div className="bg-white border border-burnishedGold/15 rounded shadow-sm overflow-hidden">
        <div className="overflow-x-auto w-full">
          <table className="w-full text-left font-sans text-xs border-collapse min-w-[850px]">
            <thead>
              <tr className="bg-[#FAF9F6] border-b border-burnishedGold/10 text-indianInk/60">
                <th className="px-4 py-3 font-bold uppercase tracking-wider w-[220px]">Product / Variant</th>
                <th className="px-4 py-3 font-bold uppercase tracking-wider w-[120px]">SKU</th>
                <th className="px-4 py-3 font-bold uppercase tracking-wider w-[90px]">On Hand</th>
                <th className="px-4 py-3 font-bold uppercase tracking-wider w-[90px]">Reserved</th>
                <th className="px-4 py-3 font-bold uppercase tracking-wider w-[90px]">Available</th>
                <th className="px-4 py-3 font-bold uppercase tracking-wider w-[90px]">Safety Lvl</th>
                <th className="px-4 py-3 font-bold uppercase tracking-wider w-[100px]">Alert Status</th>
                <th className="px-4 py-3 font-bold uppercase tracking-wider text-right w-[120px]">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-burnishedGold/10">
              {filteredVariants.length > 0 ? (
                filteredVariants.map((v) => (
                  <InventoryTableRow
                    key={v.sku}
                    variant={v}
                    onAdjust={() => handleOpenAdjust(v.sku, `${v.productName} (${v.title})`)}
                  />
                ))
              ) : (
                <tr>
                  <td colSpan={8} className="px-4 py-8 text-center text-indianInk/40 italic">
                    No matching variants or SKUs found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Adjust Stock Modal */}
      {adjustingSku && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 px-4">
          <form
            onSubmit={handleSaveAdjustment}
            className="bg-white border border-burnishedGold/20 rounded shadow-lg p-6 max-w-md w-full space-y-4 animate-fade-up font-sans text-xs"
          >
            <h3 className="font-serif text-lg font-bold text-deodharForest">
              Adjust Stock Level
            </h3>

            <div className="bg-[#FAF9F6] p-3 rounded border border-burnishedGold/10">
              <div className="font-bold text-deodharForest">{adjustingTitle}</div>
              <div className="text-[10px] text-indianInk/50 font-semibold uppercase mt-0.5">SKU: {adjustingSku}</div>
            </div>

            {/* Warehouse Select */}
            <div className="space-y-1">
              <label className="text-[10px] font-bold uppercase tracking-wider text-indianInk/60">
                Select Warehouse Node
              </label>
              <select
                value={warehouseId}
                onChange={(e) => setWarehouseId(e.target.value)}
                className="w-full text-xs border border-burnishedGold/30 focus:border-burnishedGold bg-white rounded p-2 focus:outline-none"
              >
                <option value="WH-MAIN">WH-MAIN (Main Warehouse)</option>
                <option value="WH-NORTH">WH-NORTH (North Facility)</option>
                <option value="WH-SOUTH">WH-SOUTH (South Facility)</option>
                <option value="WH-DEFAULT">WH-DEFAULT (Standard Depot)</option>
              </select>
            </div>

            <div className="grid grid-cols-2 gap-4">
              
              {/* Delta Input */}
              <div className="space-y-1">
                <label className="text-[10px] font-bold uppercase tracking-wider text-indianInk/60">
                  Adjustment Delta (+/-)
                </label>
                <input
                  type="number"
                  value={quantityDelta}
                  onChange={(e) => setQuantityDelta(parseInt(e.target.value) || 0)}
                  placeholder="e.g. 50 or -20"
                  className="w-full text-xs border border-burnishedGold/30 focus:border-burnishedGold rounded p-2 focus:outline-none"
                />
              </div>

              {/* Placement location */}
              <div className="space-y-1">
                <label className="text-[10px] font-bold uppercase tracking-wider text-indianInk/60">
                  Layout Code (Optional)
                </label>
                <input
                  type="text"
                  value={locationCode}
                  onChange={(e) => setLocationCode(e.target.value)}
                  placeholder="e.g. A-3-R5"
                  className="w-full text-xs border border-burnishedGold/30 focus:border-burnishedGold rounded p-2 focus:outline-none"
                />
              </div>

            </div>

            {adjustError && (
              <p className="text-[10px] font-semibold text-red-600">{adjustError}</p>
            )}

            {adjustSuccess && (
              <p className="text-[10px] font-semibold text-green-700">{adjustSuccess}</p>
            )}

            <div className="flex gap-3 pt-2">
              <button
                type="button"
                onClick={() => setAdjustingSku(null)}
                className="flex-1 py-2.5 text-center font-sans text-xs font-bold uppercase tracking-wider border border-burnishedGold/30 hover:bg-richCream/5 text-indianInk rounded transition"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={adjustStockMutation.isPending}
                className="flex-1 py-2.5 text-center font-sans text-xs font-bold uppercase tracking-wider bg-deodharForest text-richCream hover:bg-deodharForest/90 rounded transition shadow-sm disabled:opacity-50"
              >
                {adjustStockMutation.isPending ? "Posting..." : "Confirm Update"}
              </button>
            </div>

          </form>
        </div>
      )}

    </div>
  );
}

interface InventoryTableRowProps {
  variant: {
    productId: string;
    productName: string;
    variantId: string;
    sku: string;
    title: string;
    volume_weight: string;
    stock_status: string;
  };
  onAdjust: () => void;
}

function InventoryTableRow({ variant, onAdjust }: InventoryTableRowProps) {
  const { data: invRes, isPending, error } = useInventoryBySku(variant.sku);

  if (isPending) {
    return (
      <tr>
        <td className="px-4 py-3 font-semibold text-indianInk truncate max-w-[200px]">
          {variant.productName}
          <div className="text-[10px] text-indianInk/60 mt-0.5">{variant.title} ({variant.volume_weight})</div>
        </td>
        <td className="px-4 py-3 font-bold text-indianInk/70">{variant.sku}</td>
        <td colSpan={5} className="px-4 py-3 text-center text-indianInk/40 italic">
          <div className="flex items-center justify-center gap-1.5">
            <Loader2 className="w-3.5 h-3.5 animate-spin text-burnishedGold" />
            <span>Fetching SKU records...</span>
          </div>
        </td>
        <td className="px-4 py-3 text-right">
          <button disabled className="opacity-40 p-1.5 border border-burnishedGold/20 rounded font-bold uppercase tracking-widest text-[9px]">
            Adjust
          </button>
        </td>
      </tr>
    );
  }

  if (error || !invRes?.success || !invRes.data) {
    return (
      <tr className="bg-red-50/20">
        <td className="px-4 py-3 font-semibold text-indianInk truncate max-w-[200px]">
          {variant.productName}
          <div className="text-[10px] text-indianInk/60 mt-0.5">{variant.title} ({variant.volume_weight})</div>
        </td>
        <td className="px-4 py-3 font-bold text-indianInk/70">{variant.sku}</td>
        <td colSpan={5} className="px-4 py-3 text-red-600 font-semibold italic flex items-center gap-1.5">
          <ShieldAlert className="w-4 h-4 text-red-500" />
          <span>No database record found (needs setup)</span>
        </td>
        <td className="px-4 py-3 text-right">
          <button
            onClick={onAdjust}
            className="p-1.5 border border-burnishedGold/20 rounded font-bold uppercase tracking-widest text-[9px] text-burnishedGold hover:bg-richCream/10 hover:border-burnishedGold"
          >
            Adjust
          </button>
        </td>
      </tr>
    );
  }

  const stock = invRes.data;

  return (
    <tr className="hover:bg-richCream/5 transition-colors">
      
      {/* Product & Variant */}
      <td className="px-4 py-3.5 font-semibold text-indianInk truncate max-w-[220px]">
        {variant.productName}
        <div className="text-[10px] text-indianInk/60 mt-0.5 font-normal">
          {variant.title} ({variant.volume_weight})
        </div>
      </td>
      
      {/* SKU */}
      <td className="px-4 py-3.5 font-bold text-deodharForest">
        {variant.sku}
      </td>
      
      {/* On Hand */}
      <td className="px-4 py-3.5 font-semibold text-indianInk">
        {stock.on_hand_total}
      </td>

      {/* Reserved */}
      <td className="px-4 py-3.5 text-indianInk/60">
        {stock.reserved_total}
      </td>

      {/* Available */}
      <td className="px-4 py-3.5 font-bold text-indianInk">
        {stock.available_total}
      </td>

      {/* Safety Stock */}
      <td className="px-4 py-3.5 text-indianInk/60">
        {stock.safety_stock_level}
      </td>

      {/* Alert Status */}
      <td className="px-4 py-3.5">
        {stock.is_low_stock ? (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-red-100 text-red-800 animate-pulse border border-red-200">
            <AlertTriangle className="w-3 h-3" /> Low Stock
          </span>
        ) : (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-green-100 text-green-800 border border-green-200">
            <CheckCircle className="w-3 h-3" /> Healthy
          </span>
        )}
      </td>

      {/* Actions */}
      <td className="px-4 py-3.5 text-right">
        <button
          onClick={onAdjust}
          className="p-1.5 border border-burnishedGold/25 hover:border-burnishedGold bg-white hover:bg-richCream/10 rounded inline-flex items-center gap-1 font-bold uppercase tracking-widest text-[9px] text-burnishedGold"
        >
          <Edit3 className="w-3 h-3" />
          <span>Adjust</span>
        </button>
      </td>

    </tr>
  );
}
