"use client";

import React, { useState } from "react";
import Link from "next/link";
import PublicLayout from "@/components/layout/public-layout";
import { usePublicSettings } from "@/hooks/use-settings";
import { siteConfig } from "@/config/site";
import contactService from "@/services/contact-service";
import { 
  Mail, 
  Phone, 
  Clock, 
  HelpCircle, 
  CheckCircle2, 
  Loader2, 
  ShieldAlert,
  Send
} from "lucide-react";

export default function ContactPage() {
  const { data: settingsData } = usePublicSettings();
  const settings = settingsData?.data;

  // Extract support details dynamically from correct fields with fallbacks
  const supportEmail = settings?.public_support_email || siteConfig.links.supportEmail;
  const supportPhone = settings?.public_support_phone || "+91 90927 48525";
  const workingHours = settings?.working_hours || "Mon – Sat, 9 AM – 6 PM";

  const fssaiNumber = settings?.fssai_number;
  const gstNumber = settings?.gst_number;

  // Form states
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [phoneVal, setPhoneVal] = useState("");
  const [inquiryType, setInquiryType] = useState("Order Support");
  const [message, setMessage] = useState("");

  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);

  // Form validation handler
  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};

    if (!fullName.trim()) {
      errors.fullName = "Full name is required";
    } else if (fullName.trim().length < 2) {
      errors.fullName = "Name must be at least 2 characters";
    }

    const cleanEmail = email.trim();
    if (!cleanEmail) {
      errors.email = "Email address is required";
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(cleanEmail)) {
      errors.email = "Please enter a valid email address";
    }

    const cleanPhone = phoneVal.trim().replace(/\s+/g, "");
    if (!cleanPhone) {
      errors.phone = "Phone number is required";
    } else if (!(/^[6-9]\d{9}$/.test(cleanPhone) || /^\+91[6-9]\d{9}$/.test(cleanPhone))) {
      errors.phone = "Please enter a valid 10-digit Indian phone number (optionally with +91)";
    }

    if (!message.trim()) {
      errors.message = "Message cannot be empty";
    } else if (message.trim().length < 10) {
      errors.message = "Message must be at least 10 characters";
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleFieldChange = (field: string, value: string) => {
    if (validationErrors[field]) {
      setValidationErrors((prev) => ({ ...prev, [field]: "" }));
    }
    switch (field) {
      case "fullName": setFullName(value); break;
      case "email": setEmail(value); break;
      case "phone": setPhoneVal(value); break;
      case "inquiryType": setInquiryType(value); break;
      case "message": setMessage(value); break;
    }
  };

  const [formError, setFormError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm()) return;

    setIsLoading(true);
    setFormError("");
    try {
      await contactService.submitInquiry({
        full_name: fullName.trim(),
        email: email.trim(),
        phone: phoneVal.trim(),
        inquiry_type: inquiryType,
        message: message.trim(),
      });
      setIsSuccess(true);
      setFullName("");
      setEmail("");
      setPhoneVal("");
      setInquiryType("Order Support");
      setMessage("");
    } catch (err: any) {
      setFormError(
        err?.response?.data?.message ||
        "Something went wrong. Please try again or email us directly."
      );
    } finally {
      setIsLoading(false);
    }
  };


  return (
    <PublicLayout>
      <div 
        className="min-h-screen text-indianInk py-12 md:py-20 border-b border-burnishedGold/15"
        style={{ background: "radial-gradient(circle at center, #FFFDF0 0%, #FAF9F6 70%, #FFF7E8 100%)" }}
      >
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 space-y-12 md:space-y-16">
          
          {/* Hero Section */}
          <div className="text-center max-w-3xl mx-auto space-y-3 animate-fade-up">
            <h1 className="font-serif text-4xl sm:text-5xl font-bold text-deodharForest">
              Contact Us
            </h1>
            <p className="font-sans text-sm sm:text-base text-indianInk/65 max-w-xl mx-auto leading-relaxed">
              We are here to help with orders, support, and business enquiries. Reach out to us through any of the channels below.
            </p>
            <div className="w-12 h-0.5 bg-gheeGold mx-auto mt-4" />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-start max-w-6xl mx-auto">
            
            {/* Left Column: Cards & Compliance */}
            <div className="lg:col-span-5 space-y-6 animate-fade-up" style={{ animationDelay: "100ms" }}>
              
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                
                {/* Email Card */}
                <div className="bg-white border border-burnishedGold/15 rounded-lg p-5 shadow-sm space-y-2.5">
                  <div className="w-8 h-8 bg-deodharForest/5 border border-burnishedGold/15 rounded-full flex items-center justify-center text-deodharForest">
                    <Mail className="w-4 h-4 text-gheeGold" />
                  </div>
                  <div>
                    <h3 className="text-xs font-sans font-bold uppercase tracking-wider text-indianInk/55">
                      Support Email
                    </h3>
                    <a 
                      href={`mailto:${supportEmail}`}
                      className="text-sm font-semibold text-deodharForest hover:underline truncate block mt-0.5"
                    >
                      {supportEmail}
                    </a>
                  </div>
                </div>

                {/* Phone Card */}
                <div className="bg-white border border-burnishedGold/15 rounded-lg p-5 shadow-sm space-y-2.5">
                  <div className="w-8 h-8 bg-deodharForest/5 border border-burnishedGold/15 rounded-full flex items-center justify-center text-deodharForest">
                    <Phone className="w-4 h-4 text-gheeGold" />
                  </div>
                  <div>
                    <h3 className="text-xs font-sans font-bold uppercase tracking-wider text-indianInk/55">
                      Support Phone
                    </h3>
                    <a 
                      href={`tel:${supportPhone.replace(/\s+/g, "")}`}
                      className="text-sm font-semibold text-deodharForest hover:underline block mt-0.5"
                    >
                      {supportPhone}
                    </a>
                  </div>
                </div>

                {/* Enquiries Card */}
                <div className="bg-white border border-burnishedGold/15 rounded-lg p-5 shadow-sm space-y-2.5">
                  <div className="w-8 h-8 bg-deodharForest/5 border border-burnishedGold/15 rounded-full flex items-center justify-center text-deodharForest">
                    <HelpCircle className="w-4 h-4 text-gheeGold" />
                  </div>
                  <div>
                    <h3 className="text-xs font-sans font-bold uppercase tracking-wider text-indianInk/55">
                      Business Enquiries
                    </h3>
                    <a 
                      href={`mailto:enquiries@bharathdelightfoods.in`}
                      className="text-sm font-semibold text-deodharForest hover:underline truncate block mt-0.5"
                    >
                      enquiries@bharathdelightfoods.in
                    </a>
                  </div>
                </div>

                {/* Working Hours Card */}
                <div className="bg-white border border-burnishedGold/15 rounded-lg p-5 shadow-sm space-y-2.5">
                  <div className="w-8 h-8 bg-deodharForest/5 border border-burnishedGold/15 rounded-full flex items-center justify-center text-deodharForest">
                    <Clock className="w-4 h-4 text-gheeGold" />
                  </div>
                  <div>
                    <h3 className="text-xs font-sans font-bold uppercase tracking-wider text-indianInk/55">
                      Working Hours
                    </h3>
                    <p className="text-xs font-semibold text-deodharForest mt-0.5 leading-relaxed">
                      {workingHours}
                    </p>
                  </div>
                </div>

              </div>

              {/* Compliance Mini Section (Hides gracefully if FSSAI and GST are not configured) */}
              {(fssaiNumber || gstNumber) && (
                <div className="bg-white border border-burnishedGold/15 rounded-lg p-5 shadow-sm space-y-3">
                  <h4 className="font-serif text-sm font-bold text-deodharForest flex items-center gap-1.5 border-b border-burnishedGold/10 pb-2">
                    <CheckCircle2 className="w-4 h-4 text-gheeGold shrink-0" /> Compliance Details
                  </h4>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs font-sans">
                    {fssaiNumber && (
                      <div>
                        <span className="text-indianInk/55 block">FSSAI License No.</span>
                        <span className="font-bold text-indianInk">{fssaiNumber}</span>
                      </div>
                    )}
                    {gstNumber && (
                      <div>
                        <span className="text-indianInk/55 block">GSTIN Registration</span>
                        <span className="font-bold text-indianInk">{gstNumber}</span>
                      </div>
                    )}
                  </div>
                </div>
              )}

            </div>

            {/* Right Column: Contact Form */}
            <div className="lg:col-span-7 animate-fade-up" style={{ animationDelay: "150ms" }}>
              <div className="bg-white border border-burnishedGold/15 rounded-lg p-6 md:p-8 shadow-sm">
                
                {isSuccess ? (
                  <div className="py-12 flex flex-col items-center justify-center text-center gap-4">
                    <div className="w-14 h-14 bg-success/10 border border-success/20 rounded-full flex items-center justify-center text-success animate-bounce">
                      <CheckCircle2 className="w-8 h-8" />
                    </div>
                    <div className="space-y-1">
                      <h3 className="font-serif text-2xl font-bold text-deodharForest">Inquiry Submitted</h3>
                      <p className="text-sm text-indianInk/60 max-w-[320px] mx-auto leading-relaxed">
                        Thank you. Our team will contact you shortly.
                      </p>
                    </div>
                    <button
                      onClick={() => setIsSuccess(false)}
                      className="px-5 py-2 border border-deodharForest/20 hover:border-deodharForest text-deodharForest font-sans text-xs font-bold tracking-widest uppercase rounded-[4px] transition-colors mt-3"
                    >
                      Send Another Message
                    </button>
                  </div>
                ) : (
                  <form onSubmit={handleSubmit} className="space-y-4">
                    <h3 className="font-serif text-xl font-bold text-deodharForest border-b border-burnishedGold/10 pb-3 mb-4">
                      Send Us a Message
                    </h3>

                    {/* Full Name */}
                    <div className="flex flex-col gap-1.5">
                      <label className="text-xs font-sans font-bold uppercase tracking-wider text-indianInk/70">
                        Full Name *
                      </label>
                      <input
                        type="text"
                        disabled={isLoading}
                        value={fullName}
                        onChange={(e) => handleFieldChange("fullName", e.target.value)}
                        placeholder="Your Name"
                        className={`w-full px-4 py-3 bg-white text-indianInk border rounded-[4px] font-sans text-base transition-colors duration-200 focus-visible:outline-none focus-visible:border-burnishedGold focus-visible:ring-1 focus-visible:ring-burnishedGold ${
                          validationErrors.fullName ? "border-destructive focus-visible:ring-destructive focus-visible:border-destructive" : "border-indianInk/15"
                        }`}
                      />
                      {validationErrors.fullName && (
                        <span className="text-xs text-destructive font-sans font-medium">
                          {validationErrors.fullName}
                        </span>
                      )}
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      {/* Email */}
                      <div className="flex flex-col gap-1.5">
                        <label className="text-xs font-sans font-bold uppercase tracking-wider text-indianInk/70">
                          Email Address *
                        </label>
                        <input
                          type="email"
                          disabled={isLoading}
                          value={email}
                          onChange={(e) => handleFieldChange("email", e.target.value)}
                          placeholder="email@example.com"
                          className={`w-full px-4 py-3 bg-white text-indianInk border rounded-[4px] font-sans text-base transition-colors duration-200 focus-visible:outline-none focus-visible:border-burnishedGold focus-visible:ring-1 focus-visible:ring-burnishedGold ${
                            validationErrors.email ? "border-destructive focus-visible:ring-destructive focus-visible:border-destructive" : "border-indianInk/15"
                          }`}
                        />
                        {validationErrors.email && (
                          <span className="text-xs text-destructive font-sans font-medium">
                            {validationErrors.email}
                          </span>
                        )}
                      </div>

                      {/* Phone */}
                      <div className="flex flex-col gap-1.5">
                        <label className="text-xs font-sans font-bold uppercase tracking-wider text-indianInk/70">
                          Phone Number *
                        </label>
                        <input
                          type="tel"
                          disabled={isLoading}
                          value={phoneVal}
                          onChange={(e) => handleFieldChange("phone", e.target.value)}
                          placeholder="+91 98765 43210"
                          className={`w-full px-4 py-3 bg-white text-indianInk border rounded-[4px] font-sans text-base transition-colors duration-200 focus-visible:outline-none focus-visible:border-burnishedGold focus-visible:ring-1 focus-visible:ring-burnishedGold ${
                            validationErrors.phone ? "border-destructive focus-visible:ring-destructive focus-visible:border-destructive" : "border-indianInk/15"
                          }`}
                        />
                        {validationErrors.phone && (
                          <span className="text-xs text-destructive font-sans font-medium">
                            {validationErrors.phone}
                          </span>
                        )}
                      </div>
                    </div>

                    {/* Inquiry Type Dropdown */}
                    <div className="flex flex-col gap-1.5">
                      <label className="text-xs font-sans font-bold uppercase tracking-wider text-indianInk/70">
                        Inquiry Type
                      </label>
                      <select
                        disabled={isLoading}
                        value={inquiryType}
                        onChange={(e) => handleFieldChange("inquiryType", e.target.value)}
                        className="w-full px-4 py-3 bg-white text-indianInk border border-indianInk/15 rounded-[4px] font-sans text-base transition-colors duration-200 focus-visible:outline-none focus-visible:border-burnishedGold focus-visible:ring-1 focus-visible:ring-burnishedGold cursor-pointer"
                      >
                        <option value="Order Support">Order Support</option>
                        <option value="Product Enquiry">Product Enquiry</option>
                        <option value="Bulk / Wholesale">Bulk / Wholesale</option>
                        <option value="Partnership">Partnership</option>
                        <option value="General">General</option>
                      </select>
                    </div>

                    {/* Message */}
                    <div className="flex flex-col gap-1.5">
                      <label className="text-xs font-sans font-bold uppercase tracking-wider text-indianInk/70">
                        Your Message *
                      </label>
                      <textarea
                        disabled={isLoading}
                        rows={4}
                        value={message}
                        onChange={(e) => handleFieldChange("message", e.target.value)}
                        placeholder="Tell us what you need support with..."
                        className={`w-full px-4 py-3 bg-white text-indianInk border rounded-[4px] font-sans text-base transition-colors duration-200 focus-visible:outline-none focus-visible:border-burnishedGold focus-visible:ring-1 focus-visible:ring-burnishedGold resize-none ${
                          validationErrors.message ? "border-destructive focus-visible:ring-destructive focus-visible:border-destructive" : "border-indianInk/15"
                        }`}
                      />
                      {validationErrors.message && (
                        <span className="text-xs text-destructive font-sans font-medium">
                          {validationErrors.message}
                        </span>
                      )}
                    </div>

                    {/* API Error Banner */}
                    {formError && (
                      <div className="flex items-start gap-2.5 bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded text-xs font-sans">
                        <ShieldAlert className="w-4 h-4 shrink-0 mt-0.5 text-red-500" />
                        <span>{formError}</span>
                      </div>
                    )}

                    {/* Submit Button */}
                    <button
                      type="submit"
                      disabled={isLoading}
                      className="w-full relative overflow-hidden py-4 bg-deodharForest text-richCream rounded-[4px] font-sans text-xs font-bold tracking-[0.2em] uppercase transition-all duration-300 border border-transparent hover:border-gheeGold hover:shadow-[0_6px_20px_rgba(15,61,46,0.2)] disabled:opacity-50 text-center flex items-center justify-center mt-2"
                    >
                      {isLoading ? (
                        <>
                          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                          <span>Sending Inquiry...</span>
                        </>
                      ) : (
                        <>
                          <Send className="w-3.5 h-3.5 mr-2" />
                          <span>Submit Message</span>
                        </>
                      )}
                      <span className="absolute inset-0 w-full h-full bg-gradient-to-r from-transparent via-gheeGold/20 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000 ease-out" />
                    </button>
                  </form>

                )}

              </div>
            </div>

          </div>

        </div>
      </div>
    </PublicLayout>
  );
}
