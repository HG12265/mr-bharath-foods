import AuthGuard from "@/components/features/auth/auth-guard";
import AuthCard from "@/components/features/auth/auth-card";
import LoginForm from "@/components/features/auth/login-form";

export default function LoginPage() {
  return (
    <AuthGuard requireAuth={false}>
      <main className="min-h-screen bg-background flex justify-center items-center px-4 py-12 md:py-24">
        <AuthCard
          title="Sign In to Your Account"
          subtitle="Access your orders, track shipments, and manage settings"
          footerText="Don't have an account?"
          footerLinkText="Create one here"
          footerLinkHref="/register"
        >
          <LoginForm />
        </AuthCard>
      </main>
    </AuthGuard>
  );
}
