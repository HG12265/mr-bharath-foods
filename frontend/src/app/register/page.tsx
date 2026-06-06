import AuthGuard from "@/components/features/auth/auth-guard";
import AuthCard from "@/components/features/auth/auth-card";
import RegisterForm from "@/components/features/auth/register-form";

export default function RegisterPage() {
  return (
    <AuthGuard requireAuth={false}>
      <main className="min-h-screen bg-background flex justify-center items-center px-4 py-12 md:py-24">
        <AuthCard
          title="Create Your Account"
          subtitle="Join Mr. Bharath Foods to order premium lab-certified foods"
          footerText="Already have an account?"
          footerLinkText="Sign in instead"
          footerLinkHref="/login"
        >
          <RegisterForm />
        </AuthCard>
      </main>
    </AuthGuard>
  );
}
