"use client";

import React, { useState } from "react";
import { useAdminShipments, useAdminUpdateShipmentStatus, useCreateShipment } from "@/hooks/use-shipments";
import { useAdminOrders } from "@/hooks/use-orders";
import { Loader2, RefreshCw, Plus, Truck, Calendar, MapPin, Clipboard } from "lucide-react";

export default function AdminShipmentsPage() {
  const { data: shipmentsRes, isPending, refetch, isRefetching } = useAdminShipments();
  const { data: ordersRes } = useAdminOrders();

  const updateStatusMutation = useAdminUpdateShipmentStatus();
  const createShipmentMutation = useCreateShipment();

  const [activeTab, setActiveTab] = useState<"list" | "create">("list");
  const [editingShipmentId, setEditingShipmentId] = useState<string | null>(null);

  // Status update form states
  const [statusForm, setStatusForm] = useState({
    status: "packed",
    message: "",
    location: ""
  });
  const [statusError, setStatusError] = useState("");

  // Create shipment form states
  const [createForm, setCreateForm] = useState({
    orderId: "",
    carrier_name: "",
    tracking_number: "",
    awb_number: ""
  });
  const [createError, setCreateError] = useState("");
  const [createSuccess, setCreateSuccess] = useState("");

  const shipments = shipmentsRes?.data || [];
  const orders = ordersRes?.data || [];

  // Filter orders that are confirmed and need shipment
  // (We check if there's no shipment matching order_id)
  const pendingOrders = orders.filter(
    (order) => 
      order.order_status === "confirmed" && 
      !shipments.some((s) => s.order_id === order.id)
  );

  const handleStartUpdate = (shipment: any) => {
    setEditingShipmentId(shipment.id);
    setStatusForm({
      status: shipment.status,
      message: `Shipment status updated to ${shipment.status}`,
      location: ""
    });
    setStatusError("");
  };

  const handleSaveStatus = async (shipmentId: string) => {
    if (!statusForm.message.trim()) {
      setStatusError("Please enter a status update update message.");
      return;
    }

    await updateStatusMutation.mutateAsync({
      id: shipmentId,
      payload: {
        status: statusForm.status as any,
        message: statusForm.message,
        location: statusForm.location || undefined
      }
    });

    setEditingShipmentId(null);
    refetch();
  };

  const handleCreateShipment = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreateError("");
    setCreateSuccess("");

    if (!createForm.orderId) {
      setCreateError("Please select a target order.");
      return;
    }
    if (!createForm.carrier_name.trim()) {
      setCreateError("Carrier name is required.");
      return;
    }
    if (!createForm.tracking_number.trim()) {
      setCreateError("Tracking/AWB number is required.");
      return;
    }

    try {
      await createShipmentMutation.mutateAsync({
        orderId: createForm.orderId,
        payload: {
          carrier_name: createForm.carrier_name,
          tracking_number: createForm.tracking_number,
          awb_number: createForm.awb_number || undefined
        }
      });
      setCreateSuccess("Shipment registration record created successfully!");
      setCreateForm({ orderId: "", carrier_name: "", tracking_number: "", awb_number: "" });
      refetch();
      setTimeout(() => {
        setActiveTab("list");
        setCreateSuccess("");
      }, 1500);
    } catch (err: any) {
      setCreateError(err?.response?.data?.message || "Failed to create shipment.");
    }
  };

  const formatCurrency = (val: number) => {
    return new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR"
    }).format(val);
  };

  const getShipmentBadge = (status: string) => {
    let classes = "px-2.5 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ";
    switch (status) {
      case "delivered": classes += "bg-green-100 text-green-800"; break;
      case "shipped": classes += "bg-blue-100 text-blue-800"; break;
      case "out_for_delivery": classes += "bg-indigo-100 text-indigo-800"; break;
      case "packed": classes += "bg-amber-100 text-amber-800"; break;
      case "failed": classes += "bg-red-100 text-red-800"; break;
      case "returned": classes += "bg-purple-100 text-purple-800"; break;
      default: classes += "bg-gray-100 text-gray-800";
    }
    return <span className={classes}>{status.replace(/_/g, " ")}</span>;
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
            Shipment & Fulfillment
          </h1>
          <p className="text-xs sm:text-sm text-indianInk/60 mt-1">
            Dispatch orders, assign carrier routing details, and post tracking updates.
          </p>
        </div>
        
        {/* Toggle buttons */}
        <div className="flex gap-2">
          <button
            onClick={() => setActiveTab("list")}
            className={`px-4 py-2 font-sans text-xs font-bold uppercase tracking-wider rounded border transition ${
              activeTab === "list"
                ? "bg-deodharForest text-richCream border-transparent"
                : "bg-white text-deodharForest border-burnishedGold/30 hover:border-burnishedGold"
            }`}
          >
            All Shipments
          </button>
          <button
            onClick={() => setActiveTab("create")}
            className={`px-4 py-2 font-sans text-xs font-bold uppercase tracking-wider rounded border transition flex items-center gap-1.5 ${
              activeTab === "create"
                ? "bg-deodharForest text-richCream border-transparent"
                : "bg-white text-deodharForest border-burnishedGold/30 hover:border-burnishedGold"
            }`}
          >
            <Plus className="w-3.5 h-3.5" /> Dispatch Shipment
          </button>
        </div>
      </div>

      {activeTab === "list" ? (
        <div className="space-y-6">
          
          {/* Table Container */}
          <div className="bg-white border border-burnishedGold/15 rounded shadow-sm overflow-hidden">
            <div className="p-4 bg-[#FAF9F6] border-b border-burnishedGold/10 flex justify-between items-center">
              <h2 className="font-serif text-sm font-bold text-deodharForest">
                Fulfillment Registry
              </h2>
              <button
                onClick={() => refetch()}
                disabled={isRefetching}
                className="p-1.5 hover:bg-richCream/10 rounded text-deodharForest disabled:opacity-50"
                title="Refresh Shipments"
              >
                <RefreshCw className={`w-4 h-4 ${isRefetching ? "animate-spin" : ""}`} />
              </button>
            </div>

            <div className="overflow-x-auto w-full">
              <table className="w-full text-left font-sans text-xs border-collapse min-w-[800px]">
                <thead>
                  <tr className="border-b border-burnishedGold/10 text-indianInk/60 bg-[#FAF9F6]/50">
                    <th className="px-4 py-2.5 font-bold uppercase tracking-wider w-[120px]">Order No</th>
                    <th className="px-4 py-2.5 font-bold uppercase tracking-wider w-[150px]">Carrier Name</th>
                    <th className="px-4 py-2.5 font-bold uppercase tracking-wider w-[180px]">Tracking / AWB</th>
                    <th className="px-4 py-2.5 font-bold uppercase tracking-wider w-[120px]">Status</th>
                    <th className="px-4 py-2.5 font-bold uppercase tracking-wider">Latest Location</th>
                    <th className="px-4 py-2.5 font-bold uppercase tracking-wider text-right w-[150px]">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-burnishedGold/10">
                  {shipments.length > 0 ? (
                    shipments.map((shipment) => {
                      const isEditing = editingShipmentId === shipment.id;
                      const lastEvent = shipment.timeline?.[shipment.timeline.length - 1];

                      return (
                        <tr key={shipment.id} className="hover:bg-richCream/5 transition-colors">
                          
                          {/* Order Number */}
                          <td className="px-4 py-3.5 font-bold text-deodharForest">
                            #{shipment.order_number}
                          </td>

                          {/* Carrier */}
                          <td className="px-4 py-3.5 font-medium">
                            {shipment.carrier_name}
                          </td>

                          {/* Tracking & AWB */}
                          <td className="px-4 py-3.5 space-y-0.5">
                            <div className="flex items-center gap-1.5 font-semibold text-indianInk">
                              <Clipboard className="w-3.5 h-3.5 text-burnishedGold" />
                              <span>{shipment.tracking_number}</span>
                            </div>
                            {shipment.awb_number && (
                              <div className="text-[10px] text-indianInk/50">
                                AWB: {shipment.awb_number}
                              </div>
                            )}
                          </td>

                          {/* Status */}
                          <td className="px-4 py-3.5">
                            {getShipmentBadge(shipment.status)}
                          </td>

                          {/* Latest Location */}
                          <td className="px-4 py-3.5 text-indianInk/70">
                            {lastEvent ? (
                              <div className="space-y-0.5">
                                <div className="font-semibold text-indianInk flex items-center gap-1 truncate max-w-[200px]">
                                  {lastEvent.event_name.replace(/_/g, " ")}
                                </div>
                                <div className="text-[10px] text-indianInk/50 flex items-center gap-1 truncate max-w-[200px]">
                                  <MapPin className="w-3 h-3 text-red-500" />
                                  {lastEvent.description || "In Transit"}
                                </div>
                              </div>
                            ) : (
                              <span className="text-indianInk/40 italic">No events logged</span>
                            )}
                          </td>

                          {/* Actions */}
                          <td className="px-4 py-3.5 text-right">
                            {isEditing ? (
                              <span className="text-xs text-burnishedGold font-semibold">Editing Below...</span>
                            ) : (
                              <button
                                onClick={() => handleStartUpdate(shipment)}
                                className="bg-deodharForest hover:bg-deodharForest/95 text-richCream font-bold uppercase tracking-wider text-[9px] px-2.5 py-1.5 rounded transition"
                              >
                                Update Status
                              </button>
                            )}
                          </td>

                        </tr>
                      );
                    })
                  ) : (
                    <tr>
                      <td colSpan={6} className="px-4 py-8 text-center text-indianInk/40 italic">
                        No shipments have been dispatched yet.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>

          {/* Edit status section inline */}
          {editingShipmentId && (
            <div className="bg-white border border-burnishedGold/15 rounded shadow-sm p-5 space-y-4 animate-fade-up font-sans">
              <h2 className="font-serif text-base font-bold text-deodharForest border-b border-burnishedGold/10 pb-2">
                Update Shipment Status
              </h2>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                
                {/* Select status */}
                <div className="space-y-1">
                  <label className="text-[10px] font-bold uppercase tracking-wider text-indianInk/60">
                    New Status
                  </label>
                  <select
                    value={statusForm.status}
                    onChange={(e) => setStatusForm({ ...statusForm, status: e.target.value })}
                    className="w-full text-xs border border-burnishedGold/30 focus:border-burnishedGold rounded p-2 focus:outline-none"
                  >
                    <option value="packed">Packed</option>
                    <option value="shipped">Shipped</option>
                    <option value="out_for_delivery">Out for Delivery</option>
                    <option value="delivered">Delivered</option>
                    <option value="failed">Failed / Undelivered</option>
                    <option value="returned">Returned</option>
                  </select>
                </div>

                {/* Location code */}
                <div className="space-y-1">
                  <label className="text-[10px] font-bold uppercase tracking-wider text-indianInk/60">
                    Current Location (City/Hub)
                  </label>
                  <input
                    type="text"
                    value={statusForm.location}
                    onChange={(e) => setStatusForm({ ...statusForm, location: e.target.value })}
                    placeholder="e.g. Chennai Central Sorting Hub"
                    className="w-full text-xs border border-burnishedGold/30 focus:border-burnishedGold rounded p-2 focus:outline-none"
                  />
                </div>

                {/* Log message */}
                <div className="space-y-1">
                  <label className="text-[10px] font-bold uppercase tracking-wider text-indianInk/60">
                    Timeline Message log
                  </label>
                  <input
                    type="text"
                    value={statusForm.message}
                    onChange={(e) => setStatusForm({ ...statusForm, message: e.target.value })}
                    placeholder="e.g. Package dispatched from Madras sorting facility"
                    className="w-full text-xs border border-burnishedGold/30 focus:border-burnishedGold rounded p-2 focus:outline-none"
                  />
                </div>

              </div>

              {statusError && (
                <p className="text-[10px] font-semibold text-red-600">{statusError}</p>
              )}

              <div className="flex justify-end gap-3 pt-2">
                <button
                  onClick={() => setEditingShipmentId(null)}
                  className="px-4 py-2 font-sans text-xs font-bold uppercase tracking-wider border border-burnishedGold/30 hover:bg-richCream/5 text-indianInk rounded transition"
                >
                  Cancel
                </button>
                <button
                  onClick={() => handleSaveStatus(editingShipmentId)}
                  disabled={updateStatusMutation.isPending}
                  className="px-4 py-2 font-sans text-xs font-bold uppercase tracking-wider bg-deodharForest text-richCream hover:bg-deodharForest/90 rounded transition shadow-sm"
                >
                  Post Timeline Update
                </button>
              </div>
            </div>
          )}

        </div>
      ) : (
        
        /* Create shipment dispatch form */
        <div className="bg-white border border-burnishedGold/15 rounded shadow-sm p-6 max-w-xl mx-auto">
          <h2 className="font-serif text-lg font-bold text-deodharForest border-b border-burnishedGold/10 pb-3 flex items-center gap-2">
            <Truck className="w-5 h-5 text-burnishedGold" /> Register Dispatch (New Shipment)
          </h2>

          <form onSubmit={handleCreateShipment} className="space-y-4 pt-4 font-sans text-xs">
            
            {/* Target Order Selection */}
            <div className="space-y-1">
              <label className="text-[10px] font-bold uppercase tracking-wider text-indianInk/60">
                Select Order (Paid & Confirmed)
              </label>
              {pendingOrders.length > 0 ? (
                <select
                  value={createForm.orderId}
                  onChange={(e) => setCreateForm({ ...createForm, orderId: e.target.value })}
                  className="w-full text-xs border border-burnishedGold/30 focus:border-burnishedGold rounded p-2.5 focus:outline-none"
                >
                  <option value="">-- Choose Order --</option>
                  {pendingOrders.map((o) => (
                    <option key={o.id} value={o.id}>
                      Order #{o.order_number} — {o.customer_snapshot.first_name || "Guest"} ({formatCurrency(o.pricing.grand_total)})
                    </option>
                  ))}
                </select>
              ) : (
                <div className="p-3 border border-yellow-200 bg-yellow-50 text-yellow-800 rounded font-medium italic">
                  No confirmed orders are waiting for shipment dispatch. Check if payment approvals are pending.
                </div>
              )}
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              
              {/* Carrier Name */}
              <div className="space-y-1">
                <label className="text-[10px] font-bold uppercase tracking-wider text-indianInk/60">
                  Carrier Name
                </label>
                <input
                  type="text"
                  value={createForm.carrier_name}
                  onChange={(e) => setCreateForm({ ...createForm, carrier_name: e.target.value })}
                  placeholder="e.g. Professional Couriers / Delhivery"
                  className="w-full text-xs border border-burnishedGold/30 focus:border-burnishedGold rounded p-2 focus:outline-none"
                />
              </div>

              {/* Tracking Number */}
              <div className="space-y-1">
                <label className="text-[10px] font-bold uppercase tracking-wider text-indianInk/60">
                  Tracking / Consignment Number
                </label>
                <input
                  type="text"
                  value={createForm.tracking_number}
                  onChange={(e) => setCreateForm({ ...createForm, tracking_number: e.target.value })}
                  placeholder="e.g. DX57682910IN"
                  className="w-full text-xs border border-burnishedGold/30 focus:border-burnishedGold rounded p-2 focus:outline-none"
                />
              </div>

            </div>

            {/* AWB Number */}
            <div className="space-y-1">
              <label className="text-[10px] font-bold uppercase tracking-wider text-indianInk/60">
                Air Waybill (AWB) Number (Optional)
              </label>
              <input
                type="text"
                value={createForm.awb_number}
                onChange={(e) => setCreateForm({ ...createForm, awb_number: e.target.value })}
                placeholder="e.g. AWB-9938210"
                className="w-full text-xs border border-burnishedGold/30 focus:border-burnishedGold rounded p-2 focus:outline-none"
              />
            </div>

            {createError && (
              <p className="text-[10px] font-semibold text-red-600">{createError}</p>
            )}

            {createSuccess && (
              <p className="text-[10px] font-semibold text-green-700">{createSuccess}</p>
            )}

            <div className="flex gap-4 pt-2">
              <button
                type="button"
                onClick={() => setActiveTab("list")}
                className="flex-1 py-2.5 text-center font-sans text-xs font-bold uppercase tracking-wider border border-burnishedGold/30 hover:bg-richCream/5 text-indianInk rounded transition"
              >
                Back to List
              </button>
              <button
                type="submit"
                disabled={createShipmentMutation.isPending || pendingOrders.length === 0}
                className="flex-1 py-2.5 text-center font-sans text-xs font-bold uppercase tracking-wider bg-deodharForest text-richCream hover:bg-deodharForest/90 rounded transition shadow-sm disabled:opacity-50"
              >
                {createShipmentMutation.isPending ? "Creating Shipment..." : "Register Dispatch"}
              </button>
            </div>

          </form>
        </div>

      )}

    </div>
  );
}
