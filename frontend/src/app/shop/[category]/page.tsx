// Dynamic category navigation list pages
interface PageProps {
  params: Promise<{ category: string }>;
}

export default async function CategoryPage({ params }: PageProps) {
  const { category } = await params;
  return <div>Category Page: {category}</div>;
}