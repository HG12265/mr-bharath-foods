import { Metadata } from "next";

export const metadata: Metadata = {
  title: "Shopping Cart | Bharath Delight Foods",
  robots: { index: false, follow: false },
};

export default function CartLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
