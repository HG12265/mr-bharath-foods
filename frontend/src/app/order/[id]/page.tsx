// Post-purchase customer success page template
interface PageProps {
  params: Promise<{ id: string }>;
}

export default async function OrderSuccessPage({ params }: PageProps) {
  const { id } = await params;
  return <div>Order Success Page Placeholder: {id}</div>;
}