"use client";

import React from "react";
import { 
  useAdminReviews, 
  useAdminApproveReview, 
  useAdminRejectReview 
} from "@/hooks/use-reviews";
import { Loader2, Check, X, RefreshCw, Star, MessageSquare } from "lucide-react";

export default function AdminReviewsPage() {
  const { data: reviewsRes, isPending, refetch, isRefetching } = useAdminReviews();
  const approveMutation = useAdminApproveReview();
  const rejectMutation = useAdminRejectReview();

  const reviews = reviewsRes?.data || [];

  const handleApprove = async (id: string) => {
    if (confirm("Are you sure you want to APPROVE this review? It will be published to the product details page.")) {
      await approveMutation.mutateAsync(id);
      refetch();
    }
  };

  const handleReject = async (id: string) => {
    if (confirm("Are you sure you want to REJECT this review? It will be removed from the public display.")) {
      await rejectMutation.mutateAsync(id);
      refetch();
    }
  };

  const renderStars = (rating: number) => {
    return (
      <div className="flex items-center gap-0.5 text-gheeGold">
        {[...Array(5)].map((_, i) => (
          <Star
            key={i}
            className={`w-3.5 h-3.5 ${i < rating ? "fill-gheeGold" : "text-gray-300"}`}
          />
        ))}
      </div>
    );
  };

  const getModerationBadge = (status: string) => {
    let classes = "px-2.5 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ";
    switch (status) {
      case "approved": classes += "bg-green-100 text-green-800 border border-green-200"; break;
      case "rejected": classes += "bg-red-100 text-red-800 border border-red-200"; break;
      default: classes += "bg-yellow-100 text-yellow-800 border border-yellow-200";
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
    <div className="space-y-6 font-sans">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-burnishedGold/10 pb-4">
        <div>
          <h1 className="font-serif text-2xl sm:text-3xl font-bold text-deodharForest">
            Review Moderation
          </h1>
          <p className="text-xs sm:text-sm text-indianInk/60 mt-1">
            Moderate customer feedback. Approved reviews are displayed publicly on the storefront product detail pages.
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

      {/* Reviews Table Container */}
      <div className="bg-white border border-burnishedGold/15 rounded shadow-sm overflow-hidden">
        <div className="overflow-x-auto w-full">
          <table className="w-full text-left text-xs border-collapse min-w-[750px]">
            <thead>
              <tr className="bg-[#FAF9F6] border-b border-burnishedGold/10 text-indianInk/60">
                <th className="px-4 py-3 font-bold uppercase tracking-wider w-[120px]">Rating</th>
                <th className="px-4 py-3 font-bold uppercase tracking-wider w-[180px]">Title & Comment</th>
                <th className="px-4 py-3 font-bold uppercase tracking-wider w-[120px]">Purchase Status</th>
                <th className="px-4 py-3 font-bold uppercase tracking-wider w-[120px]">Moderation</th>
                <th className="px-4 py-3 font-bold uppercase tracking-wider text-right w-[150px]">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-burnishedGold/10">
              {reviews.length > 0 ? (
                reviews.map((review) => (
                  <tr key={review.id} className="hover:bg-richCream/5 transition-colors">
                    
                    {/* Rating Stars */}
                    <td className="px-4 py-3.5">
                      {renderStars(review.rating)}
                      <span className="text-[10px] font-bold text-indianInk/50 mt-1 block">
                        Score: {review.rating} / 5
                      </span>
                    </td>

                    {/* Title & Comment */}
                    <td className="px-4 py-3.5 max-w-[280px]">
                      <div className="font-bold text-indianInk text-xs">
                        "{review.title}"
                      </div>
                      <p className="text-indianInk/70 text-xs mt-1 leading-relaxed whitespace-pre-line">
                        {review.comment}
                      </p>
                      <div className="text-[9px] text-indianInk/40 mt-1.5 flex items-center gap-1 font-semibold uppercase tracking-wider">
                        <MessageSquare className="w-3 h-3 text-burnishedGold" />
                        ID: {review.id} | Date: {new Date(review.created_at).toLocaleDateString("en-IN")}
                      </div>
                    </td>

                    {/* Verified Purchase Status */}
                    <td className="px-4 py-3.5">
                      {review.is_verified_purchase ? (
                        <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-green-50 text-green-800 border border-green-200">
                          Verified Buy
                        </span>
                      ) : (
                        <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-gray-50 text-gray-600 border border-gray-200">
                          Standard Review
                        </span>
                      )}
                    </td>

                    {/* Moderation Status */}
                    <td className="px-4 py-3.5">
                      {getModerationBadge(review.moderation_status)}
                    </td>

                    {/* Action buttons */}
                    <td className="px-4 py-3.5 text-right">
                      <div className="flex justify-end gap-2">
                        {review.moderation_status !== "approved" && (
                          <button
                            onClick={() => handleApprove(review.id)}
                            disabled={approveMutation.isPending || rejectMutation.isPending}
                            className="bg-green-700 hover:bg-green-800 text-white font-bold uppercase tracking-wider text-[9px] px-2.5 py-1.5 rounded transition shadow-sm inline-flex items-center gap-1"
                          >
                            <Check className="w-3 h-3" /> Approve
                          </button>
                        )}
                        {review.moderation_status !== "rejected" && (
                          <button
                            onClick={() => handleReject(review.id)}
                            disabled={approveMutation.isPending || rejectMutation.isPending}
                            className="bg-red-600 hover:bg-red-700 text-white font-bold uppercase tracking-wider text-[9px] px-2.5 py-1.5 rounded transition shadow-sm inline-flex items-center gap-1"
                          >
                            <X className="w-3 h-3" /> Reject
                          </button>
                        )}
                      </div>
                    </td>

                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={5} className="px-4 py-8 text-center text-indianInk/40 italic">
                    No product reviews are pending moderation.
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
