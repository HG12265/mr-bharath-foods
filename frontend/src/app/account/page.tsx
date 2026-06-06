"use client";

import AuthGuard from "@/components/features/auth/auth-guard";
import { useMe, useLogout } from "@/hooks/use-auth";
import { useRouter } from "next/navigation";

export default function AccountPage() {
  const router = useRouter();
  const { data } = useMe();
  const logoutMutation = useLogout();

  const handleLogout = () => {
    logoutMutation.mutate(undefined, {
      onSuccess: () => {
        router.push("/login");
      },
    });
  };

  const user = data?.data;

  return (
    <AuthGuard requireAuth={true}>
      <main className="min-h-screen bg-warmIvory flex flex-col justify-center items-center px-4 py-12">
        <div className="w-full max-w-[560px] bg-white border border-indianInk/5 rounded-lg shadow-[0_4px_16px_rgba(28,35,33,0.04)] overflow-hidden">
          {/* Header */}
          <div className="bg-trustNavy text-warmIvory px-8 py-8 border-b border-indianInk/5 flex justify-between items-center">
            <div>
              <span className="text-xs uppercase tracking-widest text-warmIvory/80 font-sans block mb-1">
                Customer Profile Portal
              </span>
              <h1 className="text-warmIvory font-serif text-3xl font-medium tracking-tight">
                Welcome, {user?.personal_details?.first_name || "Valued Member"}
              </h1>
            </div>
            <span className="px-3 py-1 bg-burnishedGold text-indianInk text-xs uppercase font-sans font-semibold tracking-wider rounded-[4px]">
              {user?.role || "Customer"}
            </span>
          </div>

          {/* User Details Grid */}
          <div className="px-8 py-8 md:px-10 md:py-10 flex flex-col gap-6">
            <h2 className="font-serif text-xl font-semibold text-indianInk border-b border-indianInk/5 pb-2">
              Personal Credentials Details
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Full Name */}
              <div className="flex flex-col gap-1">
                <span className="text-xs uppercase tracking-wider text-indianInk/50 font-sans font-medium">
                  Full Name
                </span>
                <span className="text-base text-indianInk font-sans font-medium">
                  {user?.personal_details?.first_name} {user?.personal_details?.last_name}
                </span>
              </div>

              {/* Phone Coordinate */}
              <div className="flex flex-col gap-1">
                <span className="text-xs uppercase tracking-wider text-indianInk/50 font-sans font-medium">
                  Phone Number
                </span>
                <span className="text-base text-indianInk font-sans font-medium">
                  {user?.phone || "Not Configured"}
                </span>
              </div>

              {/* Email Coordinator */}
              <div className="flex flex-col gap-1 md:col-span-2">
                <span className="text-xs uppercase tracking-wider text-indianInk/50 font-sans font-medium">
                  Email Address
                </span>
                <span className="text-base text-indianInk font-sans font-medium">
                  {user?.email || "Not Configured"}
                </span>
              </div>
            </div>

            {/* Logout Action */}
            <div className="mt-6 pt-6 border-t border-indianInk/5 flex justify-end">
              <button
                type="button"
                onClick={handleLogout}
                disabled={logoutMutation.isPending}
                className="px-6 py-3 border border-indianInk text-indianInk hover:bg-indianInk/5 disabled:opacity-50 transition-colors duration-200 rounded-[4px] font-sans text-xs font-semibold tracking-widest uppercase"
              >
                {logoutMutation.isPending ? "Logging Out..." : "Sign Out Account"}
              </button>
            </div>
          </div>
        </div>
      </main>
    </AuthGuard>
  );
}