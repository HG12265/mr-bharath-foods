"use client";

import React, { useState } from "react";
import { useMe } from "@/hooks/use-auth";
import { useAdminOrders, useAdminUpdateOrderStatus } from "@/hooks/use-orders";
import { Loader2, RefreshCw, Edit2, Check, X, ShieldAlert } from "lucide-react";

export default function AdminOrdersPage() {
  const { data: meData } = useMe();
  const user = meData?.data;
  const role = user?.role;
  const isAdmin = role === "admin";

  const { data: ordersRes, isPending, refetch, isRefetching } = useAdminOrders();
  const updateStatusMutation = useAdminUpdateOrderStatus();

  const [editingOrderId, setEditingOrderId] = useState<string | null>(null);
  const [editForm, setEditForm] = useState({
    order_status: "",
    payment_status: "",
    fulfillment_status: ""
  });

  const orders = ordersRes?.data || [];

  const handleStartEdit = (order: any) => {
    setEditingOrderId(order.id);
    setEditForm({
      order_status: order.order_status,
      payment_status: order.payment_status,
      fulfillment_status: order.fulfillment_status
    });
  };

  const handleCancelEdit = () => {
    setEditingOrderId(null);
  };

  const handleSave = async (orderId: string) => {
    // For warehouse role, make sure they aren't submitting changes to payment_status
    const payload: any = {
      order_status: editForm.order_status,
      fulfillment_status: editForm.fulfillment_status
    };

    if (isAdmin) {
      payload.payment_status = editForm.payment_status;
    }

    await updateStatusMutation.mutateAsync({
      orderId,
      payload
    });
    setEditingOrderId(null);
  };

  const formatCurrency = (val: number) => {
    return new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR"
    }).format(val);
  };

  const getStatusBadge = (type: "order" | "payment" | "fulfillment", status: string) => {
    let classes = "px-2.5 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ";
    if (type === "order") {
      switch (status) {
        case "confirmed": classes += "bg-green-50 text-green-800 border border-green-200"; break;
        case "cancelled": classes += "bg-red-50 text-red-800 border border-red-200"; break;
        case "closed": classes += "bg-gray-100 text-gray-800 border border-gray-200"; break;
        default: classes += "bg-yellow-50 text-yellow-800 border border-yellow-200";
      }
    } else if (type === "payment") {
      switch (status) {
        case "paid": classes += "bg-green-100 text-green-800"; break;
        case "failed": classes += "bg-red-100 text-red-800"; break;
        case "refunded": classes += "bg-purple-100 text-purple-800"; break;
        default: classes += "bg-yellow-100 text-yellow-800";
      }
    } else {
      switch (status) {
        case "delivered": classes += "bg-emerald-100 text-emerald-800"; break;
        case "shipped": classes += "bg-blue-100 text-blue-800"; break;
        case "packed": classes += "bg-amber-100 text-amber-800"; break;
        case "cancelled": classes += "bg-red-100 text-red-800"; break;
        default: classes += "bg-gray-100 text-gray-800";
      }
    }
    return <span className={classes}>{status}</span>;
  };

  if (isPending) {
    return (
      <div className="flex justify-center items-center py-20">
        <Loader2 className="w-8 h-8 animate-spin text-burnishedGold" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-burnishedGold/10 pb-4">
        <div>
          <h1 className="font-serif text-2xl sm:text-3xl font-bold text-deodharForest">
            Order Management
          </h1>
          <p className="text-xs sm:text-sm text-indianInk/60 mt-1">
            {role === "warehouse" 
              ? "Operational view: Update order and fulfillment statuses." 
              : "Full view: Manage order, payment, and fulfillment statuses."
            }
          </p>
        </div>
        <div>
          <button
            onClick={() => refetch()}
            disabled={isRefetching}
            className="flex items-center gap-2 px-3 py-1.5 border border-burnishedGold/30 hover:border-burnishedGold bg-white text-deodharForest font-sans text-xs font-bold uppercase tracking-wider rounded transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isRefetching ? "animate-spin" : ""}`} />
            Refresh
          </button>
        </div>
      </div>

      {/* Orders Table Container */}
      <div className="bg-white border border-burnishedGold/15 rounded shadow-sm overflow-hidden">
        
        {/* Table itself - horizontally scrollable */}
        <div className="overflow-x-auto w-full">
          <table className="w-full text-left font-sans text-xs border-collapse min-w-[800px]">
            <thead>
              <tr className="bg-[#FAF9F6] border-b border-burnishedGold/10 text-indianInk/60">
                <th className="px-4 py-3 font-bold uppercase tracking-wider w-[120px]">Order No</th>
                <th className="px-4 py-3 font-bold uppercase tracking-wider w-[180px]">Customer</th>
                <th className="px-4 py-3 font-bold uppercase tracking-wider w-[100px]">Total</th>
                <th className="px-4 py-3 font-bold uppercase tracking-wider w-[150px]">Order Status</th>
                <th className="px-4 py-3 font-bold uppercase tracking-wider w-[150px]">Payment Status</th>
                <th className="px-4 py-3 font-bold uppercase tracking-wider w-[150px]">Fulfillment Status</th>
                <th className="px-4 py-3 font-bold uppercase tracking-wider w-[120px] text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-burnishedGold/10">
              {orders.length > 0 ? (
                orders.map((order) => {
                  const isEditing = editingOrderId === order.id;
                  return (
                    <tr key={order.id} className="hover:bg-richCream/5 transition-colors">
                      
                      {/* Order Number */}
                      <td className="px-4 py-3.5 font-bold text-deodharForest">
                        #{order.order_number}
                      </td>
                      
                      {/* Customer Snapshot */}
                      <td className="px-4 py-3.5">
                        <div className="font-semibold text-indianInk text-xs truncate max-w-[170px]">
                          {order.customer_snapshot.first_name || ""} {order.customer_snapshot.last_name || ""}
                        </div>
                        <div className="text-[10px] text-indianInk/50 truncate max-w-[170px]">
                          {order.customer_snapshot.email}
                        </div>
                      </td>

                      {/* Total */}
                      <td className="px-4 py-3.5 font-semibold text-indianInk">
                        {formatCurrency(order.pricing.grand_total)}
                      </td>

                      {/* Order Status */}
                      <td className="px-4 py-3.5">
                        {isEditing ? (
                          <select
                            value={editForm.order_status}
                            onChange={(e) => setEditForm({ ...editForm, order_status: e.target.value })}
                            className="bg-white border border-burnishedGold/30 rounded px-2 py-1 text-xs font-semibold focus:outline-none focus:border-burnishedGold"
                          >
                            <option value="pending_payment">pending_payment</option>
                            <option value="confirmed">confirmed</option>
                            <option value="cancelled">cancelled</option>
                            <option value="closed">closed</option>
                          </select>
                        ) : (
                          getStatusBadge("order", order.order_status)
                        )}
                      </td>

                      {/* Payment Status */}
                      <td className="px-4 py-3.5">
                        {isEditing ? (
                          isAdmin ? (
                            <select
                              value={editForm.payment_status}
                              onChange={(e) => setEditForm({ ...editForm, payment_status: e.target.value })}
                              className="bg-white border border-burnishedGold/30 rounded px-2 py-1 text-xs font-semibold focus:outline-none focus:border-burnishedGold"
                            >
                              <option value="pending">pending</option>
                              <option value="paid">paid</option>
                              <option value="failed">failed</option>
                              <option value="refunded">refunded</option>
                            </select>
                          ) : (
                            <div className="flex items-center gap-1">
                              {getStatusBadge("payment", order.payment_status)}
                              <span title="Warehouse cannot change payments">
                                <ShieldAlert className="w-3.5 h-3.5 text-indianInk/40" />
                              </span>
                            </div>
                          )
                        ) : (
                          getStatusBadge("payment", order.payment_status)
                        )}
                      </td>

                      {/* Fulfillment Status */}
                      <td className="px-4 py-3.5">
                        {isEditing ? (
                          <select
                            value={editForm.fulfillment_status}
                            onChange={(e) => setEditForm({ ...editForm, fulfillment_status: e.target.value })}
                            className="bg-white border border-burnishedGold/30 rounded px-2 py-1 text-xs font-semibold focus:outline-none focus:border-burnishedGold"
                          >
                            <option value="pending">pending</option>
                            <option value="packed">packed</option>
                            <option value="shipped">shipped</option>
                            <option value="delivered">delivered</option>
                            <option value="cancelled">cancelled</option>
                          </select>
                        ) : (
                          getStatusBadge("fulfillment", order.fulfillment_status)
                        )}
                      </td>

                      {/* Actions */}
                      <td className="px-4 py-3.5 text-right">
                        {isEditing ? (
                          <div className="flex justify-end gap-1.5">
                            <button
                              onClick={() => handleSave(order.id)}
                              disabled={updateStatusMutation.isPending}
                              className="p-1 text-green-700 hover:bg-green-50 rounded"
                              title="Save Changes"
                            >
                              <Check className="w-4 h-4" />
                            </button>
                            <button
                              onClick={handleCancelEdit}
                              className="p-1 text-red-600 hover:bg-red-50 rounded"
                              title="Cancel Edit"
                            >
                              <X className="w-4 h-4" />
                            </button>
                          </div>
                        ) : (
                          <button
                            onClick={() => handleStartEdit(order)}
                            className="p-1.5 text-burnishedGold hover:bg-richCream/10 border border-burnishedGold/20 rounded inline-flex items-center gap-1 font-bold uppercase tracking-widest text-[9px] hover:border-burnishedGold"
                          >
                            <Edit2 className="w-3 h-3" />
                            <span>Edit</span>
                          </button>
                        )}
                      </td>

                    </tr>
                  );
                })
              ) : (
                <tr>
                  <td colSpan={7} className="px-4 py-8 text-center text-indianInk/40 italic">
                    No orders registered in the system.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

      </div>

    </div>
  );
}
