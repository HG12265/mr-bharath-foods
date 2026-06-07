"use client";

import React from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useLogout } from "@/hooks/use-auth";
import { siteConfig } from "@/config/site";
import { X, User, LogIn, ChevronRight, LogOut } from "lucide-react";

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
            {user && (
              <Link
                href="/account"
                onClick={onClose}
                className="flex items-center justify-between text-xs uppercase font-semibold tracking-widest text-indianInk/85 hover:text-deodharForest pb-2.5 border-b border-burnishedGold/10 transition-colors duration-150"
              >
                <span>My Account</span>
                <ChevronRight className="w-4 h-4 text-burnishedGold" />
              </Link>
            )}

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
            <div className="flex flex-col gap-2 w-full">
              <Link
                href="/account"
                onClick={onClose}
                className="flex items-center justify-center gap-2 w-full py-3 bg-deodharForest text-richCream border border-transparent rounded-[4px] font-sans text-xs font-semibold tracking-widest uppercase transition-all duration-200 shadow-sm text-center"
              >
                <User className="w-4 h-4 text-gheeGold" />
                <span>My Account</span>
              </Link>
              <button
                onClick={() => {
                  onClose();
                  handleLogout();
                }}
                disabled={logoutMutation.isPending}
                className="flex items-center justify-center gap-2 w-full py-3 bg-warmSaffron/5 border border-warmSaffron/15 hover:border-warmSaffron rounded-[4px] font-sans text-xs font-semibold tracking-widest text-warmSaffron uppercase transition-all duration-200 disabled:opacity-50"
              >
                <LogOut className="w-4 h-4 text-warmSaffron" />
                <span>{logoutMutation.isPending ? "Signing Out..." : `Sign Out`}</span>
              </button>
            </div>
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