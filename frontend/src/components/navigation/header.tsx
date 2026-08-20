"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter, usePathname } from "next/navigation";
import { useSession, useLogout } from "@/hooks/use-auth";
import { useCart } from "@/hooks/use-cart";
import { siteConfig } from "@/config/site";
import Image from "next/image";
import { Menu, X, User, ShoppingCart, ShoppingBag } from "lucide-react";
import MobileNav from "./mobile-nav";
import { useCartDrawer } from "@/providers/cart-drawer-provider";

/* Navigation items matching the reference design */
const NAV_LINKS = [
  { title: "Home", href: "/" },
  { title: "About Us", href: "/about" },
  { title: "Products", href: "/shop" },
  { title: "Our Promise", href: "/trust" },
  { title: "Contact Us", href: "/contact" },
];

export const Header: React.FC = () => {
  const router = useRouter();
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);
  const { openCart } = useCartDrawer();

  /* Scroll detection for subtle shadow */
  useEffect(() => {
    const handleScroll = () => setIsScrolled(window.scrollY > 8);
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const { data: sessionData } = useSession({ staleTime: 5 * 60 * 1000 });
  const user = sessionData?.data?.user;

  const logoutMutation = useLogout();
  const handleLogout = () => {
    logoutMutation.mutate(undefined, {
      onSuccess: () => router.push("/"),
    });
  };

  const { data: cartData } = useCart();
  const cartItemCount = cartData?.data?.summary?.quantity_total || 0;

  return (
    <>
      <header
        className={`sticky top-0 z-40 w-full bg-white transition-shadow duration-300 ${
          isScrolled ? "shadow-[0_2px_16px_rgba(30,53,47,0.09)]" : "shadow-none"
        }`}
        style={{ borderBottom: "1px solid rgba(196,154,69,0.15)" }}
      >
        <div className="w-full max-w-[1400px] mx-auto px-4 sm:px-6 lg:px-10 h-[var(--header-height)] flex items-center justify-between relative">

          {/* ── Logo (Left) ───────────────────────────────── */}
          <Link
            href="/"
            className="flex items-center gap-2.5 select-none group py-1 shrink-0 z-10"
          >
            {/* BD Monogram Logo */}
            <Image
              src="/images/logo.png"
              alt="Bharath Delight"
              width={42}
              height={42}
              className="transition-transform duration-300 group-hover:scale-105"
              priority
            />
            <div className="flex flex-col leading-none">
              <span className="font-serif text-[20px] font-bold text-[#1E352F] tracking-wide">
                Bharath
              </span>
              <span className="font-script text-[22px] text-[#C49A45] font-medium leading-none -mt-0.5">
                Delight
              </span>
              <span className="text-[8px] font-sans font-semibold tracking-[0.14em] text-[#C49A45]/70 uppercase mt-0.5">
                Authenticity in Every Delight
              </span>
            </div>
          </Link>

          {/* ── Nav Links (Center — absolutely positioned) ── */}
          <nav className="hidden md:flex items-center gap-7 lg:gap-10 absolute left-1/2 -translate-x-1/2">
            {NAV_LINKS.map((item) => {
              const isActive =
                item.href === "/"
                  ? pathname === "/"
                  : pathname.startsWith(item.href);
              return (
                <Link
                  key={item.title}
                  href={item.href}
                  className={`relative font-sans text-[14px] font-medium tracking-wide transition-colors duration-150 pb-0.5 ${
                    isActive
                      ? "text-[#1E352F] after:absolute after:bottom-0 after:left-0 after:right-0 after:h-[2px] after:bg-[#1E352F] after:rounded-full"
                      : "text-[#1E352F]/65 hover:text-[#1E352F]"
                  }`}
                >
                  {item.title}
                </Link>
              );
            })}
            {user && (
              <Link
                href="/account"
                className={`relative font-sans text-[14px] font-medium tracking-wide transition-colors duration-150 pb-0.5 ${
                  pathname.startsWith("/account")
                    ? "text-[#1E352F] after:absolute after:bottom-0 after:left-0 after:right-0 after:h-[2px] after:bg-[#1E352F] after:rounded-full"
                    : "text-[#1E352F]/65 hover:text-[#1E352F]"
                }`}
              >
                My Account
              </Link>
            )}
          </nav>

          {/* ── Right Actions ─────────────────────────────── */}
          <div className="hidden md:flex items-center gap-3 shrink-0 z-10">
            {/* Cart Icon */}
            <button
              onClick={openCart}
              className="relative p-2 text-[#1E352F] hover:text-[#C49A45] transition-colors outline-none"
              aria-label="Shopping Cart"
            >
              <ShoppingCart className="w-5 h-5" />
              {cartItemCount > 0 && (
                <span className="absolute -top-1 -right-1 bg-[#C49A45] text-white text-[9px] font-bold rounded-full w-[17px] h-[17px] flex items-center justify-center border border-white shadow-sm">
                  {cartItemCount}
                </span>
              )}
            </button>

            {/* Account / CTA */}
            {user ? (
              <div className="relative">
                <button
                  onClick={() => setDropdownOpen(!dropdownOpen)}
                  className="flex items-center gap-2 px-4 py-2 border border-[#1E352F]/20 hover:border-[#C49A45] rounded-full font-sans text-xs font-semibold text-[#1E352F] hover:text-[#C49A45] transition-all duration-200"
                >
                  <User className="w-3.5 h-3.5" />
                  <span>{user.personal_details?.first_name}</span>
                </button>
                {dropdownOpen && (
                  <>
                    <div className="fixed inset-0 z-30" onClick={() => setDropdownOpen(false)} />
                    <div className="absolute right-0 mt-2 w-44 bg-white border border-[#C49A45]/25 rounded-lg shadow-lg py-1 z-40">
                      <Link
                        href="/account"
                        onClick={() => setDropdownOpen(false)}
                        className="block px-4 py-2.5 text-xs font-medium text-[#1E352F] hover:bg-[#FAF8F3] border-b border-[#C49A45]/10 transition-colors"
                      >
                        My Account
                      </Link>
                      <button
                        onClick={() => { setDropdownOpen(false); handleLogout(); }}
                        disabled={logoutMutation.isPending}
                        className="block w-full px-4 py-2.5 text-left text-xs font-medium text-[#1E352F] hover:bg-[#FAF8F3] transition-colors disabled:opacity-50"
                      >
                        {logoutMutation.isPending ? "Signing Out…" : "Sign Out"}
                      </button>
                    </div>
                  </>
                )}
              </div>
            ) : (
              /* Primary CTA — "Explore Products" matching reference */
              <Link
                href="/shop"
                className="inline-flex items-center gap-2 px-5 py-2.5 bg-[#1E352F] text-white rounded-full font-sans text-[13px] font-semibold hover:bg-[#355E3B] hover:shadow-[0_4px_14px_rgba(30,53,47,0.25)] transition-all duration-300"
              >
                <ShoppingBag className="w-4 h-4" />
                <span>Explore Products</span>
              </Link>
            )}
          </div>

          {/* ── Mobile actions ────────────────────────────── */}
          <div className="flex md:hidden items-center gap-2 z-10">
            <button
              onClick={openCart}
              className="relative p-2 text-[#1E352F] hover:text-[#C49A45] transition-colors outline-none"
              aria-label="Shopping Cart"
            >
              <ShoppingCart className="w-5 h-5" />
              {cartItemCount > 0 && (
                <span className="absolute -top-1 -right-1 bg-[#C49A45] text-white text-[9px] font-bold rounded-full w-[17px] h-[17px] flex items-center justify-center border border-white shadow-sm">
                  {cartItemCount}
                </span>
              )}
            </button>
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 text-[#1E352F] hover:text-[#C49A45] focus:outline-none transition-colors"
              aria-label="Toggle menu"
            >
              {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
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