// Single recipe post detail pages with product card callouts
interface PageProps {
  params: Promise<{ slug: string }>;
}

export default async function BlogPostPage({ params }: PageProps) {
  const { slug } = await params;
  return <div>Blog Recipe Post: {slug}</div>;
}