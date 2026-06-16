"use client";

import React, { useState } from "react";
import Link from "next/link";
import Image from "next/image";
import { useRouter, usePathname } from "next/navigation";
import { useSession, useLogout } from "@/hooks/use-auth";
import { useCart } from "@/hooks/use-cart";
import { siteConfig } from "@/config/site";
import { Menu, X, User, ShoppingCart } from "lucide-react";
import MobileNav from "./mobile-nav";
import { useCartDrawer } from "@/providers/cart-drawer-provider";

export const Header: React.FC = () => {
  const router = useRouter();
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const { openCart } = useCartDrawer();

  const { data: sessionData } = useSession({
    staleTime: 5 * 60 * 1000,
  });
  const user = sessionData?.data?.user;

  const logoutMutation = useLogout();
  const handleLogout = () => {
    logoutMutation.mutate(undefined, {
      onSuccess: () => {
        router.push("/");
      },
    });
  };

  const { data: cartData } = useCart();
  const cartItemCount = cartData?.data?.summary?.quantity_total || 0;

  return (
    <>
      <header 
        className="sticky top-0 z-40 w-full text-indianInk backdrop-blur-[12px] shadow-sm transition-shadow duration-300"
        style={{
          background: "rgba(255, 247, 232, 0.88)",
          borderBottom: "1px solid rgba(217, 164, 65, 0.18)",
        }}
      >
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 h-[var(--header-height)] flex items-center justify-between">
          
          <Link href="/" className="flex items-center gap-4 select-none group py-1">
            <Image
              src="/logo.png"
              alt="Bharath Delight Foods"
              width={56}
              height={56}
              priority
              className="h-14 w-auto object-contain mix-blend-multiply transition-transform duration-300 group-hover:scale-105"
            />
            <div className="flex flex-col justify-center border-l border-[#C89B3C]/25 pl-4">
              <span className="font-serif text-lg sm:text-xl font-bold tracking-tight text-[#0F3D2E] leading-none">
                BHARATH DELIGHT FOODS
              </span>
              <span className="text-[9px] uppercase tracking-[0.25em] text-[#C89B3C] font-bold mt-1.5">
                FOOD DONE RIGHT.
              </span>
            </div>
          </Link>

          {/* Navigation Links (Center) */}
          <nav className="hidden md:flex items-center gap-8">
            {siteConfig.nav.main.map((item) => {
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.title}
                  href={item.href}
                  className={`text-xs uppercase font-sans font-semibold tracking-widest transition-all duration-150 ${
                    isActive 
                      ? "text-[#0F3D2E] border-b-2 border-[#D9A441] pb-0.5" 
                      : "text-[#0F3D2E]/75 hover:text-[#0F3D2E]"
                  }`}
                >
                  {item.title}
                </Link>
              );
            })}
            {user && (
              <Link
                href="/account"
                className={`text-xs uppercase font-sans font-semibold tracking-widest transition-all duration-150 ${
                  pathname.startsWith("/account")
                    ? "text-[#0F3D2E] border-b-2 border-[#D9A441] pb-0.5" 
                    : "text-[#0F3D2E]/75 hover:text-[#0F3D2E]"
                }`}
              >
                My Account
              </Link>
            )}
          </nav>

          {/* Actions Portal (Right) */}
          <div className="hidden md:flex items-center gap-4">
            {/* Cart Icon Button */}
            <button
              onClick={openCart}
              className="relative p-2 text-[#0F3D2E] hover:text-[#D9A441] transition-colors mr-2 outline-none"
              aria-label="Shopping Cart"
            >
              <ShoppingCart className="w-5 h-5" />
              {cartItemCount > 0 && (
                <span className="absolute -top-1.5 -right-1.5 bg-gheeGold text-deodharForest text-[9px] font-sans font-bold rounded-full w-[18px] h-[18px] flex items-center justify-center border border-white shadow-sm">
                  {cartItemCount}
                </span>
              )}
            </button>

            {/* Account Dropdown */}
            {user ? (
              <div className="relative">
                <button
                  onClick={() => setDropdownOpen(!dropdownOpen)}
                  className="flex items-center gap-2 px-4 py-2 border border-deodharForest/10 hover:border-burnishedGold rounded-[4px] font-sans text-xs font-semibold tracking-widest uppercase text-deodharForest hover:text-burnishedGold transition-all duration-300"
                >
                  <User className="w-3.5 h-3.5" />
                  <span>{user.personal_details?.first_name}</span>
                </button>
                
                {dropdownOpen && (
                  <>
                    <div 
                      className="fixed inset-0 z-30" 
                      onClick={() => setDropdownOpen(false)}
                    />
                    <div className="absolute right-0 mt-2 w-48 bg-white border border-burnishedGold/30 rounded-[4px] shadow-md py-1 z-40 overflow-hidden">
                      <Link
                        href="/account"
                        onClick={() => setDropdownOpen(false)}
                        className="block w-full px-4 py-2.5 text-left font-sans text-xs font-semibold tracking-widest uppercase text-deodharForest hover:bg-richCream transition-colors duration-150 border-b border-burnishedGold/10"
                      >
                        My Account
                      </Link>
                      <button
                        onClick={() => {
                          setDropdownOpen(false);
                          handleLogout();
                        }}
                        disabled={logoutMutation.isPending}
                        className="block w-full px-4 py-2.5 text-left font-sans text-xs font-semibold tracking-widest uppercase text-deodharForest hover:bg-warmSaffron hover:text-white transition-colors duration-150 disabled:opacity-50"
                      >
                        {logoutMutation.isPending ? "Signing Out..." : "Sign Out"}
                      </button>
                    </div>
                  </>
                )}
              </div>
            ) : (
              <Link
                href="/login"
                className="flex items-center gap-2 px-5 py-2.5 bg-deodharForest text-richCream border border-transparent hover:border-burnishedGold hover:shadow-[0_4px_12px_rgba(15,61,46,0.15)] rounded-[4px] font-sans text-xs font-semibold tracking-widest uppercase transition-all duration-300"
              >
                <User className="w-3.5 h-3.5 text-gheeGold" />
                <span>Sign In</span>
              </Link>
            )}
          </div>

          {/* Mobile hamburger menu (Right) */}
          <div className="flex md:hidden items-center gap-3">
            {/* Cart Icon Button on mobile */}
            <button
              onClick={openCart}
              className="relative p-2 text-[#0F3D2E] hover:text-[#D9A441] transition-colors outline-none"
              aria-label="Shopping Cart"
            >
              <ShoppingCart className="w-5 h-5" />
              {cartItemCount > 0 && (
                <span className="absolute -top-1.5 -right-1.5 bg-gheeGold text-deodharForest text-[9px] font-sans font-bold rounded-full w-[18px] h-[18px] flex items-center justify-center border border-white shadow-sm">
                  {cartItemCount}
                </span>
              )}
            </button>


            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 text-deodharForest hover:text-burnishedGold focus:outline-none transition-colors"
              aria-label="Toggle menu"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>

        </div>
      </header>

      {/* Mobile Drawer */}
      <MobileNav
        isOpen={mobileMenuOpen}
        onClose={() => setMobileMenuOpen(false)}
        user={user}
      />
    </>
  );
};

export default Header;