import React from "react";
import Header from "../navigation/header";
import Footer from "../navigation/footer";
import CartDrawer from "../features/cart/cart-drawer";

interface PublicLayoutProps {
  children: React.ReactNode;
}

export const PublicLayout: React.FC<PublicLayoutProps> = ({ children }) => {
  return (
    <div className="flex flex-col min-h-screen bg-richCream text-indianInk">
      {/* Shared sticky Header */}
      <Header />

      {/* Global Slideout Cart Drawer */}
      <CartDrawer />

      {/* Main Content Area */}
      <main className="flex-grow">
        {children}
      </main>

      {/* Shared Footer */}
      <Footer />
    </div>
  );
};

export default PublicLayout;
