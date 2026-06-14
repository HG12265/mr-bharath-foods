import React from "react";
import Link from "next/link";
import { siteConfig } from "@/config/site";
import { Mail, ShieldCheck } from "lucide-react";

export const Footer: React.FC = () => {
  return (
    <footer className="bg-deodharForest text-warmIvory border-t border-burnishedGold/15 py-10">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        
        {/* Main Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 pb-8 border-b border-white/10">
          
          {/* Brand Info */}
          <div className="space-y-3">
            <h4 className="font-serif text-base font-bold tracking-tight text-warmIvory">
              Bharath Delight Foods
            </h4>
            <span className="block text-[9px] uppercase tracking-[0.2em] text-gheeGold font-semibold">
              FOOD DONE RIGHT.
            </span>
            <p className="text-xs text-warmIvory/70 leading-relaxed max-w-xs font-sans">
              Thoughtfully selected traditional Indian ingredients. Focused on traceability, quality, and purity.
            </p>
          </div>

          {/* Quick Info / Compliance */}
          <div className="space-y-2.5 text-xs text-warmIvory/80 font-sans">
            <h5 className="font-serif text-xs font-semibold tracking-wider text-gheeGold uppercase">
              Compliance & Support
            </h5>
            <div className="flex items-center gap-2">
              <Mail className="w-3.5 h-3.5 text-gheeGold shrink-0" />
              <span>{siteConfig.links.supportEmail}</span>
            </div>
            <div className="flex items-center gap-2">
              <ShieldCheck className="w-3.5 h-3.5 text-gheeGold shrink-0" />
              <span>FSSAI No: {siteConfig.fssaiLicenseNumber}</span>
            </div>
            <div className="text-[10px] text-warmIvory/60">
              GSTIN: 33AAFCM7409G1ZS (Verified Co-Packer)
            </div>
          </div>

          {/* Navigation Link Lists */}
          <div className="space-y-3">
            <h5 className="font-serif text-xs font-semibold tracking-wider text-gheeGold uppercase">
              Products & Trust
            </h5>
            <ul className="space-y-1.5 text-xs text-warmIvory/75 font-sans">
              <li>
                <Link href="/shop" className="hover:text-burnishedGold transition-colors">
                  Shop Catalog
                </Link>
              </li>
              <li>
                <Link href="/trust" className="hover:text-burnishedGold transition-colors">
                  Verify Batch Code
                </Link>
              </li>
              <li>
                <Link href="/compare" className="hover:text-burnishedGold transition-colors">
                  Purity Standards
                </Link>
              </li>
            </ul>
          </div>

          {/* Portal Links */}
          <div className="space-y-3">
            <h5 className="font-serif text-xs font-semibold tracking-wider text-gheeGold uppercase">
              Account & Portal
            </h5>
            <ul className="space-y-1.5 text-xs text-warmIvory/75 font-sans">
              <li>
                <Link href="/login" className="hover:text-burnishedGold transition-colors">
                  Sign In Portal
                </Link>
              </li>
              <li>
                <Link href="/register" className="hover:text-burnishedGold transition-colors">
                  Create Account
                </Link>
              </li>
            </ul>
          </div>

        </div>

        {/* Bottom Bar */}
        <div className="pt-6 flex flex-col sm:flex-row items-center justify-between gap-3 text-[10px] text-warmIvory/50 font-sans tracking-wide">
          <p>© {new Date().getFullYear()} Bharath Delight Foods. Sourced responsibly.</p>
          <div className="flex flex-wrap gap-x-4 gap-y-2 justify-center sm:justify-end text-center">
            <Link href="/privacy-policy" className="hover:text-warmIvory transition-colors">Privacy Policy</Link>
            <Link href="/terms-and-conditions" className="hover:text-warmIvory transition-colors">Terms & Conditions</Link>
            <Link href="/shipping-policy" className="hover:text-warmIvory transition-colors">Shipping Policy</Link>
            <Link href="/refund-cancellation-policy" className="hover:text-warmIvory transition-colors">Refund Policy</Link>
            <Link href="/contact" className="hover:text-warmIvory transition-colors">Contact Us</Link>
          </div>
        </div>

      </div>
    </footer>
  );
};

export default Footer;