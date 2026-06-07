"use client";

import React from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useLogout } from "@/hooks/use-auth";
import { siteConfig } from "@/config/site";
import { X, User, LogIn, ChevronRight } from "lucide-react";

interface MobileNavProps {
  isOpen: boolean;
  onClose: () => void;
  user: any;
}

export const MobileNav: React.FC<MobileNavProps> = ({ isOpen, onClose, user }) => {
  const router = useRouter();
  const logoutMutation = useLogout();

  const handleLogout = () => {
    logoutMutation.mutate(undefined, {
      onSuccess: () => {
        router.push("/");
      },
    });
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 md:hidden flex justify-end">
      {/* Overlay Backdrop */}
      <div 
        className="absolute inset-0 bg-indianInk/40 backdrop-blur-sm transition-opacity duration-300"
        onClick={onClose}
      />

      {/* Drawer */}
      <div className="relative w-full max-w-[300px] h-full bg-richCream text-indianInk p-6 shadow-2xl flex flex-col justify-between z-10 transition-transform duration-300 border-l border-burnishedGold/15 animate-slide-in">
        <div>
          {/* Header */}
          <div className="flex items-center justify-between pb-6 border-b border-burnishedGold/15">
            <span className="font-serif text-lg font-bold text-deodharForest">Menu</span>
            <button 
              onClick={onClose}
              className="p-1 hover:text-burnishedGold text-deodharForest transition-colors"
              aria-label="Close menu"
            >
              <X className="w-6 h-6" />
            </button>
          </div>

          {/* Nav Links */}
          <nav className="mt-8 flex flex-col gap-5">
            {siteConfig.nav.main.map((item) => (
              <Link
                key={item.title}
                href={item.href}
                onClick={onClose}
                className="flex items-center justify-between text-xs uppercase font-semibold tracking-widest text-indianInk/85 hover:text-deodharForest pb-2.5 border-b border-burnishedGold/10 transition-colors duration-150"
              >
                <span>{item.title}</span>
                <ChevronRight className="w-4 h-4 text-burnishedGold" />
              </Link>
            ))}

            {/* Cart Link */}
            <Link
              href="/cart"
              onClick={onClose}
              className="flex items-center justify-between text-xs uppercase font-semibold tracking-widest text-indianInk/85 hover:text-deodharForest pb-2.5 border-b border-burnishedGold/10 transition-colors duration-150"
            >
              <span>Cart</span>
              <ChevronRight className="w-4 h-4 text-burnishedGold" />
            </Link>
          </nav>
        </div>

        {/* Footer Area */}
        <div className="mt-auto pt-6 border-t border-burnishedGold/15 flex flex-col gap-4">
          {user ? (
            <button
              onClick={() => {
                onClose();
                handleLogout();
              }}
              disabled={logoutMutation.isPending}
              className="flex items-center justify-center gap-2 w-full py-3 bg-deodharForest/5 border border-deodharForest/15 hover:border-burnishedGold rounded-[4px] font-sans text-xs font-semibold tracking-widest text-deodharForest hover:text-burnishedGold uppercase transition-all duration-200 disabled:opacity-50"
            >
              <User className="w-4 h-4" />
              <span>{logoutMutation.isPending ? "Signing Out..." : `Sign Out (${user.personal_details?.first_name})`}</span>
            </button>
          ) : (
            <Link
              href="/login"
              onClick={onClose}
              className="flex items-center justify-center gap-2 w-full py-3 bg-deodharForest text-richCream border border-transparent hover:border-burnishedGold rounded-[4px] font-sans text-xs font-semibold tracking-widest uppercase transition-all duration-200 shadow-sm"
            >
              <LogIn className="w-4 h-4 text-gheeGold" />
              <span>Sign In</span>
            </Link>
          )}

          <p className="text-[9px] text-center text-indianInk/55 font-sans tracking-widest uppercase">
            © 2026 Mr. Bharath Foods
          </p>
        </div>
      </div>
    </div>
  );
};

export default MobileNav;