"use client";

import React, { useState, useEffect } from "react";
import { useAdminSettings, useUpdateAdminSettings } from "@/hooks/use-settings";
import { Loader2, Save, RefreshCw, HelpCircle, ShieldCheck } from "lucide-react";

export default function AdminSettingsPage() {
  const { data: settingsRes, isPending, refetch, isRefetching } = useAdminSettings();
  const updateSettingsMutation = useUpdateAdminSettings();

  // Form states
  const [form, setForm] = useState({
    upi_id: "",
    tax_percentage: 0,
    shipping_fee: 0,
    free_shipping_threshold: 0,
    support_contact: "",
    fssai_number: "",
    gst_number: ""
  });

  const [formSuccess, setFormSuccess] = useState("");
  const [formError, setFormError] = useState("");

  // Sync loaded settings data with form state
  useEffect(() => {
    if (settingsRes?.success && settingsRes.data) {
      const s = settingsRes.data;
      setForm({
        upi_id: s.upi_id || "",
        tax_percentage: s.tax_percentage || 0,
        shipping_fee: s.shipping_fee || 0,
        free_shipping_threshold: s.free_shipping_threshold || 0,
        support_contact: s.support_contact || "",
        fssai_number: s.fssai_number || "",
        gst_number: s.gst_number || ""
      });
    }
  }, [settingsRes]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormSuccess("");
    setFormError("");

    if (!form.upi_id.trim()) {
      setFormError("UPI ID cannot be blank.");
      return;
    }
    if (!form.support_contact.trim()) {
      setFormError("Support contact email/phone is required.");
      return;
    }

    try {
      await updateSettingsMutation.mutateAsync({
        upi_id: form.upi_id,
        tax_percentage: Number(form.tax_percentage),
        shipping_fee: Number(form.shipping_fee),
        free_shipping_threshold: Number(form.free_shipping_threshold),
        support_contact: form.support_contact,
        fssai_number: form.fssai_number || undefined,
        gst_number: form.gst_number || undefined
      });
      setFormSuccess("Global settings updated successfully!");
      refetch();
      setTimeout(() => setFormSuccess(""), 3000);
    } catch (err: any) {
      setFormError(err?.response?.data?.message || "Failed to update configurations.");
    }
  };

  if (isPending) {
    return (
      <div className="flex justify-center items-center py-20">
        <Loader2 className="w-8 h-8 animate-spin text-burnishedGold" />
      </div>
    );
  }

  return (
    <div className="space-y-6 font-sans">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-burnishedGold/10 pb-4">
        <div>
          <h1 className="font-serif text-2xl sm:text-3xl font-bold text-deodharForest">
            Application Settings
          </h1>
          <p className="text-xs sm:text-sm text-indianInk/60 mt-1">
            Configure financial variables, logistics criteria, support contacts, and legal identifiers.
          </p>
        </div>
        <div>
          <button
            onClick={() => refetch()}
            disabled={isRefetching}
            className="flex items-center gap-2 px-3 py-1.5 border border-burnishedGold/30 hover:border-burnishedGold bg-white text-deodharForest text-xs font-bold uppercase tracking-wider rounded transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isRefetching ? "animate-spin" : ""}`} />
            Sync Config
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        
        {/* Form panel */}
        <div className="lg:col-span-8 bg-white border border-burnishedGold/15 rounded shadow-sm p-6">
          <form onSubmit={handleSubmit} className="space-y-6 text-xs">
            
            {/* Financial Parameters */}
            <div className="space-y-4">
              <h2 className="font-serif text-base font-bold text-deodharForest border-b border-burnishedGold/10 pb-2">
                Financial Configurations
              </h2>
              
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                
                {/* UPI ID */}
                <div className="space-y-1">
                  <label className="text-[10px] font-bold uppercase tracking-wider text-indianInk/60 flex items-center gap-1">
                    Merchant UPI ID
                    <span title="UPI ID used for QR code generation and display on manual payment portal.">
                      <HelpCircle className="w-3 h-3 text-indianInk/40 cursor-help" />
                    </span>
                  </label>
                  <input
                    type="text"
                    value={form.upi_id}
                    onChange={(e) => setForm({ ...form, upi_id: e.target.value })}
                    placeholder="e.g. bharathfoods@ybl"
                    className="w-full text-xs border border-burnishedGold/30 focus:border-burnishedGold rounded p-2.5 focus:outline-none"
                    required
                  />
                </div>

                {/* Tax Percentage */}
                <div className="space-y-1">
                  <label className="text-[10px] font-bold uppercase tracking-wider text-indianInk/60">
                    GST Tax Percentage (%)
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    max="100"
                    value={form.tax_percentage}
                    onChange={(e) => setForm({ ...form, tax_percentage: parseFloat(e.target.value) || 0 })}
                    placeholder="e.g. 5"
                    className="w-full text-xs border border-burnishedGold/30 focus:border-burnishedGold rounded p-2.5 focus:outline-none"
                    required
                  />
                </div>

              </div>
            </div>

            {/* Logistics Parameters */}
            <div className="space-y-4">
              <h2 className="font-serif text-base font-bold text-deodharForest border-b border-burnishedGold/10 pb-2">
                Shipping & Fulfillment Fees
              </h2>
              
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                
                {/* Shipping Fee */}
                <div className="space-y-1">
                  <label className="text-[10px] font-bold uppercase tracking-wider text-indianInk/60">
                    Standard Shipping Fee (₹)
                  </label>
                  <input
                    type="number"
                    min="0"
                    value={form.shipping_fee}
                    onChange={(e) => setForm({ ...form, shipping_fee: parseFloat(e.target.value) || 0 })}
                    placeholder="e.g. 50"
                    className="w-full text-xs border border-burnishedGold/30 focus:border-burnishedGold rounded p-2.5 focus:outline-none"
                    required
                  />
                </div>

                {/* Free Shipping Threshold */}
                <div className="space-y-1">
                  <label className="text-[10px] font-bold uppercase tracking-wider text-indianInk/60">
                    Free Shipping Threshold (₹)
                  </label>
                  <input
                    type="number"
                    min="0"
                    value={form.free_shipping_threshold}
                    onChange={(e) => setForm({ ...form, free_shipping_threshold: parseFloat(e.target.value) || 0 })}
                    placeholder="e.g. 999"
                    className="w-full text-xs border border-burnishedGold/30 focus:border-burnishedGold rounded p-2.5 focus:outline-none"
                    required
                  />
                </div>

              </div>
            </div>

            {/* Support Contact and Regulatory Certifications */}
            <div className="space-y-4">
              <h2 className="font-serif text-base font-bold text-deodharForest border-b border-burnishedGold/10 pb-2">
                Brand Contacts & Licenses
              </h2>
              
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                
                {/* Support Contact */}
                <div className="space-y-1">
                  <label className="text-[10px] font-bold uppercase tracking-wider text-indianInk/60">
                    Support Phone / Email
                  </label>
                  <input
                    type="text"
                    value={form.support_contact}
                    onChange={(e) => setForm({ ...form, support_contact: e.target.value })}
                    placeholder="e.g. support@bharathfoods.com"
                    className="w-full text-xs border border-burnishedGold/30 focus:border-burnishedGold rounded p-2.5 focus:outline-none"
                    required
                  />
                </div>

                {/* FSSAI Number */}
                <div className="space-y-1">
                  <label className="text-[10px] font-bold uppercase tracking-wider text-indianInk/60">
                    FSSAI License Number (Optional)
                  </label>
                  <input
                    type="text"
                    value={form.fssai_number}
                    onChange={(e) => setForm({ ...form, fssai_number: e.target.value })}
                    placeholder="e.g. 12345678901234"
                    className="w-full text-xs border border-burnishedGold/30 focus:border-burnishedGold rounded p-2.5 focus:outline-none"
                  />
                </div>

                {/* GST Number */}
                <div className="space-y-1">
                  <label className="text-[10px] font-bold uppercase tracking-wider text-indianInk/60">
                    GSTIN Number (Optional)
                  </label>
                  <input
                    type="text"
                    value={form.gst_number}
                    onChange={(e) => setForm({ ...form, gst_number: e.target.value })}
                    placeholder="e.g. 33AABCM1122D1Z5"
                    className="w-full text-xs border border-burnishedGold/30 focus:border-burnishedGold rounded p-2.5 focus:outline-none"
                  />
                </div>

              </div>
            </div>

            {formError && (
              <p className="text-[10px] font-semibold text-red-600">
                {formError}
              </p>
            )}

            {formSuccess && (
              <p className="text-[10px] font-semibold text-green-700 bg-green-50 border border-green-200 p-2.5 rounded">
                {formSuccess}
              </p>
            )}

            <div className="border-t border-burnishedGold/10 pt-4 flex justify-end">
              <button
                type="submit"
                disabled={updateSettingsMutation.isPending}
                className="bg-deodharForest hover:bg-deodharForest/95 text-richCream font-bold uppercase tracking-wider text-xs px-6 py-3 rounded transition flex items-center gap-2 shadow-sm disabled:opacity-50"
              >
                {updateSettingsMutation.isPending ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin text-gheeGold" />
                    Saving...
                  </>
                ) : (
                  <>
                    <Save className="w-4 h-4 text-gheeGold" />
                    Save Settings
                  </>
                )}
              </button>
            </div>

          </form>
        </div>

        {/* Informational sidebar */}
        <div className="lg:col-span-4 bg-white border border-burnishedGold/15 rounded p-5 space-y-4 text-xs font-sans">
          <h2 className="font-serif text-sm font-bold text-deodharForest border-b border-burnishedGold/10 pb-2 flex items-center gap-1.5">
            <ShieldCheck className="w-4 h-4 text-green-600" />
            Security & Controls
          </h2>
          <p className="text-indianInk/70 leading-relaxed">
            These variables govern active billing workflows on the storefront:
          </p>
          <ul className="list-disc pl-4 space-y-2 text-indianInk/60">
            <li>Updating <strong>Merchant UPI ID</strong> immediately adjusts QR payment codes shown during checkout order confirmations.</li>
            <li>Changing <strong>GST Tax</strong> adjusts invoice calculations dynamically.</li>
            <li>Shipping fee structures apply when cart balances fall below the <strong>Free Threshold</strong>.</li>
            <li>Regulatory credentials like <strong>FSSAI</strong> and <strong>GSTIN</strong> display dynamically inside the footer disclosures.</li>
          </ul>
        </div>

      </div>

    </div>
  );
}
