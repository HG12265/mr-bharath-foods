import { Metadata } from "next";

export const metadata: Metadata = {
  title: "Order Status | Bharath Delight Foods",
  robots: { index: false, follow: false },
};

export default function OrderLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
