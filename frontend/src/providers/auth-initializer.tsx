"use client";

import React, { useEffect, useState } from "react";
import axios from "axios";
import { env } from "@/lib/env";
import { setAccessToken } from "@/services/api-client";
import { Envelope, Token } from "@/types";

/**
 * AuthInitializer — attempts a silent token refresh on every app mount
 * (page load / refresh) using the HttpOnly refresh_token cookie.
 *
 * This ensures that if a user was previously logged in, their access token
 * is restored before any data queries (like cart) fire. Without this,
 * the in-memory access token is lost on refresh, and the cart API
 * would treat the user as a new guest — losing their existing cart.
 */
export function AuthInitializer({ children }: { children: React.ReactNode }) {
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    let cancelled = false;

    const tryRefresh = async () => {
      const wasLoggedIn = typeof window !== "undefined" && localStorage.getItem("was_logged_in") === "true";
      if (!wasLoggedIn) {
        setAccessToken(null);
        if (!cancelled) {
          setIsReady(true);
        }
        return;
      }

      try {
        const response = await axios.post<Envelope<Token>>(
          `${env.NEXT_PUBLIC_API_URL}/api/v1/auth/refresh`,
          {},
          { withCredentials: true }
        );
        if (!cancelled && response.data?.data?.access_token) {
          setAccessToken(response.data.data.access_token);
        }
      } catch {
        // No valid refresh token — user is a guest, that's fine
        setAccessToken(null);
        if (typeof window !== "undefined") {
          localStorage.removeItem("was_logged_in");
        }
      } finally {
        if (!cancelled) {
          setIsReady(true);
        }
      }
    };

    tryRefresh();
    return () => {
      cancelled = true;
    };
  }, []);

  // Show nothing while auth state is being resolved (very brief — typically < 100ms)
  if (!isReady) {
    return null;
  }

  return <>{children}</>;
}
