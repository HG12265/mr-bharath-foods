"use client";

import React, { useEffect, useRef, useState } from "react";
import Script from "next/script";
import { useRouter } from "next/navigation";
import { useGoogleLogin } from "@/hooks/use-auth";

declare global {
  interface Window {
    google?: {
      accounts: {
        id: {
          initialize: (config: {
            client_id: string;
            callback: (response: { credential: string }) => void;
            auto_select?: boolean;
            cancel_on_tap_outside?: boolean;
          }) => void;
          renderButton: (
            parent: HTMLElement,
            options: {
              type?: "standard" | "icon";
              theme?: "outline" | "filled_blue" | "filled_black";
              size?: "large" | "medium" | "small";
              text?: "signin_with" | "signup_with" | "continue_with" | "signin";
              shape?: "rectangular" | "pill" | "circle" | "square";
              logo_alignment?: "left" | "center";
              width?: number | string;
              locale?: string;
            }
          ) => void;
          prompt: () => void;
        };
      };
    };
  }
}

interface GoogleSignInButtonProps {
  mode?: "signin" | "signup" | "continue";
  onSuccess?: () => void;
  onError?: (errorMsg: string) => void;
}

export const GoogleSignInButton: React.FC<GoogleSignInButtonProps> = ({
  mode = "continue",
  onSuccess,
  onError,
}) => {
  const router = useRouter();
  const googleBtnRef = useRef<HTMLDivElement>(null);
  const [scriptLoaded, setScriptLoaded] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const googleClientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID || "";
  const googleLoginMutation = useGoogleLogin();

  const handleCredentialResponse = (response: { credential: string }) => {
    if (!response.credential) {
      const err = "No credential received from Google.";
      setErrorMessage(err);
      onError?.(err);
      return;
    }

    setErrorMessage(null);
    googleLoginMutation.mutate(response.credential, {
      onSuccess: (res) => {
        if (res.success) {
          onSuccess?.();
          const role = res.data?.role;
          if (role === "admin" || role === "warehouse") {
            router.push("/admin");
          } else {
            const redirectParam = typeof window !== "undefined"
              ? new URLSearchParams(window.location.search).get("redirect")
              : null;
            const targetUrl = (redirectParam && redirectParam !== "/account") ? redirectParam : "/shop";
            router.push(targetUrl);
          }
        } else {
          const err = res.message || "Failed to authenticate with Google.";
          setErrorMessage(err);
          onError?.(err);
        }
      },
      onError: (err: any) => {
        const msg = err.response?.data?.message || err.message || "Google sign-in error occurred.";
        setErrorMessage(msg);
        onError?.(msg);
      },
    });
  };

  // Initialize Google Identity Services
  useEffect(() => {
    if (!scriptLoaded || !googleClientId) return;

    if (window.google?.accounts?.id && googleBtnRef.current) {
      try {
        window.google.accounts.id.initialize({
          client_id: googleClientId,
          callback: handleCredentialResponse,
          auto_select: false,
          cancel_on_tap_outside: true,
        });

        // Clear previous buttons if any
        googleBtnRef.current.innerHTML = "";

        const containerWidth = googleBtnRef.current?.offsetWidth || 340;
        const buttonWidth = Math.min(Math.max(containerWidth, 200), 380);

        // Render official branded button
        window.google.accounts.id.renderButton(googleBtnRef.current, {
          type: "standard",
          theme: "outline",
          size: "large",
          text: mode === "signup" ? "signup_with" : mode === "signin" ? "signin_with" : "continue_with",
          shape: "rectangular",
          width: buttonWidth,
          logo_alignment: "left",
        });
      } catch (e) {
        console.error("Google Sign-In initialization error:", e);
      }
    }
  }, [scriptLoaded, googleClientId, mode]);

  const handleCustomButtonClick = () => {
    if (!googleClientId) {
      setErrorMessage("Google Client ID is not configured yet. Please add NEXT_PUBLIC_GOOGLE_CLIENT_ID to your environment.");
      return;
    }

    if (window.google?.accounts?.id) {
      try {
        window.google.accounts.id.prompt();
      } catch (err) {
        console.error("Google prompt error:", err);
      }
    }
  };

  const isPending = googleLoginMutation.isPending;

  return (
    <div className="w-full flex flex-col items-center">
      {/* Load Google Identity Services script */}
      <Script
        src="https://accounts.google.com/gsi/client"
        strategy="afterInteractive"
        onLoad={() => setScriptLoaded(true)}
      />

      {/* Error message */}
      {errorMessage && (
        <div className="w-full mb-3 p-3 bg-red-50 border border-red-200 text-red-700 text-xs font-sans rounded-md leading-relaxed">
          {errorMessage}
        </div>
      )}

      {/* When Google Client ID is configured and script loaded: show official renderButton container */}
      {googleClientId ? (
        <div className="w-full flex justify-center min-h-[44px] relative">
          {isPending && (
            <div className="absolute inset-0 bg-white/80 backdrop-blur-[1px] flex items-center justify-center z-10 rounded-md">
              <div className="flex items-center gap-2 text-xs font-sans text-indianInk">
                <div className="w-4 h-4 border-2 border-deodharForest border-t-transparent rounded-full animate-spin" />
                <span>Signing in with Google...</span>
              </div>
            </div>
          )}
          <div ref={googleBtnRef} className="w-full flex justify-center" />
        </div>
      ) : (
        /* Fallback branded button when Client ID is pending user setup */
        <button
          type="button"
          onClick={handleCustomButtonClick}
          className="w-full h-11 px-4 bg-white hover:bg-neutral-50 text-[#3c4043] border border-[#dadce0] rounded-md font-sans text-sm font-medium transition-colors duration-150 flex items-center justify-center gap-3 shadow-sm hover:shadow"
        >
          {/* Official Google multi-color G SVG logo */}
          <svg className="w-4 h-4 shrink-0" viewBox="0 0 24 24">
            <path
              fill="#4285F4"
              d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
            />
            <path
              fill="#34A853"
              d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
            />
            <path
              fill="#FBBC05"
              d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
            />
            <path
              fill="#EA4335"
              d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"
            />
          </svg>
          <span>
            {mode === "signup"
              ? "Sign up with Google"
              : mode === "signin"
              ? "Sign in with Google"
              : "Continue with Google"}
          </span>
        </button>
      )}
    </div>
  );
};

export default GoogleSignInButton;

