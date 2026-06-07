"use client";

import React from "react";
import Link from "next/link";
import AccountShell from "@/components/features/account/account-shell";
import OrderStatusBadge from "@/components/features/account/order-status-badge";
import { useMe } from "@/hooks/use-auth";
import { useOrders } from "@/hooks/use-orders";
import { useNotifications } from "@/hooks/use-notifications";
import { formatINR } from "@/lib/utils";
import { 
  ShoppingBag, 
  CreditCard, 
  Truck, 
  Bell, 
  User, 
  ArrowRight,
  ShieldCheck
} from "lucide-react";

export default function AccountPage() {
  const { data: meData } = useMe();
  const { data: ordersData } = useOrders();
  const { data: notificationsData } = useNotifications();

  const user = meData?.data;
  const orders = ordersData?.data || [];
  const notifications = notificationsData?.data || [];

  // Compute stat card numbers dynamically
  const totalOrders = orders.length;
  
  const pendingPaymentsCount = orders.filter(
    (o) => o.order_status === "pending_payment" && o.payment_status !== "paid"
  ).length;

  const activeShipmentsCount = orders.filter(
    (o) => o.fulfillment_status === "shipped" || o.fulfillment_status === "packed"
  ).length;

  const unreadCount = notifications.filter((n) => !n.is_read).length;

  // Retrieve 2 most recent orders
  const recentOrders = [...orders]
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    .slice(0, 2);

  const formatDate = (isoString: string) => {
    try {
      return new Date(isoString).toLocaleDateString("en-IN", {
        day: "numeric",
        month: "long",
        year: "numeric"
      });
    } catch {
      return isoString;
    }
  };

  return (
    <AccountShell 
      title="Customer Dashboard" 
      description="Welcome to your account portal. Monitor your orders, notifications, and profile details."
    >
      <div className="space-y-8 animate-fade-up">
        
        {/* STATS GRID */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          
          {/* Card 1: Total Orders */}
          <div className="bg-[#FAF9F6] border border-burnishedGold/15 rounded-lg p-4 flex items-center gap-3 shadow-sm hover:border-burnishedGold/30 transition-colors">
            <div className="w-10 h-10 bg-deodharForest/5 border border-burnishedGold/15 rounded-full flex items-center justify-center shrink-0 text-deodharForest">
              <ShoppingBag className="w-5 h-5 text-gheeGold" />
            </div>
            <div>
              <span className="text-[10px] uppercase font-sans font-bold tracking-wider text-indianInk/50 block">
                Total Orders
              </span>
              <span className="text-xl font-bold font-sans text-deodharForest">
                {totalOrders}
              </span>
            </div>
          </div>

          {/* Card 2: Pending Payments */}
          <div className="bg-[#FAF9F6] border border-burnishedGold/15 rounded-lg p-4 flex items-center gap-3 shadow-sm hover:border-burnishedGold/30 transition-colors">
            <div className="w-10 h-10 bg-deodharForest/5 border border-burnishedGold/15 rounded-full flex items-center justify-center shrink-0 text-deodharForest">
              <CreditCard className="w-5 h-5 text-gheeGold" />
            </div>
            <div>
              <span className="text-[10px] uppercase font-sans font-bold tracking-wider text-indianInk/50 block">
                Unpaid Orders
              </span>
              <span className="text-xl font-bold font-sans text-deodharForest">
                {pendingPaymentsCount}
              </span>
            </div>
          </div>

          {/* Card 3: Active Shipments */}
          <div className="bg-[#FAF9F6] border border-burnishedGold/15 rounded-lg p-4 flex items-center gap-3 shadow-sm hover:border-burnishedGold/30 transition-colors">
            <div className="w-10 h-10 bg-deodharForest/5 border border-burnishedGold/15 rounded-full flex items-center justify-center shrink-0 text-deodharForest">
              <Truck className="w-5 h-5 text-gheeGold" />
            </div>
            <div>
              <span className="text-[10px] uppercase font-sans font-bold tracking-wider text-indianInk/50 block">
                In Dispatch
              </span>
              <span className="text-xl font-bold font-sans text-deodharForest">
                {activeShipmentsCount}
              </span>
            </div>
          </div>

          {/* Card 4: Unread Notifications */}
          <div className="bg-[#FAF9F6] border border-burnishedGold/15 rounded-lg p-4 flex items-center gap-3 shadow-sm hover:border-burnishedGold/30 transition-colors">
            <div className="w-10 h-10 bg-deodharForest/5 border border-burnishedGold/15 rounded-full flex items-center justify-center shrink-0 text-deodharForest">
              <Bell className="w-5 h-5 text-gheeGold" />
            </div>
            <div>
              <span className="text-[10px] uppercase font-sans font-bold tracking-wider text-indianInk/50 block">
                Unread Inbox
              </span>
              <span className="text-xl font-bold font-sans text-deodharForest">
                {unreadCount}
              </span>
            </div>
          </div>

        </div>

        {/* TWO PANEL CONTENT */}
        <div className="grid grid-cols-1 md:grid-cols-12 gap-6 items-start">
          
          {/* Profile Details Block (Left) */}
          <div className="md:col-span-5 bg-white border border-burnishedGold/15 rounded-lg p-5 shadow-sm space-y-4">
            <h3 className="font-serif text-base font-bold text-deodharForest border-b border-burnishedGold/10 pb-2 flex items-center gap-1.5">
              <User className="w-4 h-4 text-burnishedGold" /> Personal Profile
            </h3>

            {user && (
              <div className="space-y-3 font-sans text-xs">
                <div>
                  <span className="text-indianInk/50 block font-semibold uppercase tracking-wider text-[9px]">
                    First Name
                  </span>
                  <span className="text-sm font-semibold text-indianInk">
                    {user.personal_details?.first_name || "N/A"}
                  </span>
                </div>
                
                <div>
                  <span className="text-indianInk/50 block font-semibold uppercase tracking-wider text-[9px]">
                    Last Name
                  </span>
                  <span className="text-sm font-semibold text-indianInk">
                    {user.personal_details?.last_name || "N/A"}
                  </span>
                </div>

                <div>
                  <span className="text-indianInk/50 block font-semibold uppercase tracking-wider text-[9px]">
                    Email Address
                  </span>
                  <span className="text-sm font-semibold text-indianInk truncate block">
                    {user.email || "N/A"}
                  </span>
                </div>

                <div>
                  <span className="text-indianInk/50 block font-semibold uppercase tracking-wider text-[9px]">
                    Phone Number
                  </span>
                  <span className="text-sm font-semibold text-indianInk">
                    {user.phone || "N/A"}
                  </span>
                </div>

                <div>
                  <span className="text-indianInk/50 block font-semibold uppercase tracking-wider text-[9px]">
                    Account Role
                  </span>
                  <span className="text-sm font-semibold text-indianInk uppercase tracking-wide flex items-center gap-1">
                    <ShieldCheck className="w-3.5 h-3.5 text-success inline" /> {user.role}
                  </span>
                </div>
              </div>
            )}
          </div>

          {/* Recent Orders Preview Block (Right) */}
          <div className="md:col-span-7 bg-white border border-burnishedGold/15 rounded-lg p-5 shadow-sm space-y-4">
            <div className="flex justify-between items-center border-b border-burnishedGold/10 pb-2">
              <h3 className="font-serif text-base font-bold text-deodharForest flex items-center gap-1.5">
                <ShoppingBag className="w-4 h-4 text-burnishedGold" /> Recent Orders
              </h3>
              {orders.length > 2 && (
                <Link
                  href="/account/orders"
                  className="text-[10px] font-sans font-bold uppercase tracking-wider text-burnishedGold hover:text-deodharForest flex items-center gap-1"
                >
                  See All <ArrowRight className="w-3 h-3" />
                </Link>
              )}
            </div>

            {recentOrders.length === 0 ? (
              <div className="py-10 text-center space-y-2">
                <p className="text-xs text-indianInk/60 font-sans">
                  You haven't placed any orders yet.
                </p>
                <Link
                  href="/shop"
                  className="inline-block px-4 py-2 bg-deodharForest text-richCream font-sans text-[10px] font-bold tracking-widest uppercase rounded-[4px] border border-transparent hover:border-gheeGold"
                >
                  Shop Ghee
                </Link>
              </div>
            ) : (
              <div className="space-y-4">
                {recentOrders.map((order) => (
                  <div 
                    key={order.id} 
                    className="p-3 border border-burnishedGold/10 rounded-[4px] hover:border-burnishedGold/25 transition-all duration-200 flex flex-col sm:flex-row justify-between sm:items-center gap-4 text-xs font-sans"
                  >
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-deodharForest">
                          #{order.order_number}
                        </span>
                        <span className="text-[10px] text-indianInk/40">
                          {formatDate(order.created_at)}
                        </span>
                      </div>
                      <div className="flex flex-wrap gap-1.5 items-center">
                        <OrderStatusBadge type="order" value={order.order_status} />
                        <OrderStatusBadge type="payment" value={order.payment_status} />
                      </div>
                    </div>

                    <div className="flex justify-between sm:justify-end items-center gap-4 sm:text-right shrink-0">
                      <div>
                        <span className="text-indianInk/50 block text-[9px] uppercase tracking-wider">
                          Amount
                        </span>
                        <span className="font-bold text-indianInk">
                          {formatINR(order.pricing.grand_total)}
                        </span>
                      </div>
                      <Link
                        href={`/order/${order.id}`}
                        className="px-3 py-1.5 bg-deodharForest/5 border border-burnishedGold/15 hover:border-deodharForest text-deodharForest font-semibold text-[10px] uppercase tracking-widest rounded transition-colors"
                      >
                        Details
                      </Link>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

        </div>

      </div>
    </AccountShell>
  );
}
