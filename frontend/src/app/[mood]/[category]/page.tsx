// This file captures URLs like /seo/lonely/movies
export default async function MoodPage({ params }: { params: { mood: string, category: string } }) {
  const { mood, category } = params;
  
  // Fetch the AI-generated content for this specific slug
  const content = await fetch(`https://api.sentiverse.com/content/${mood}/${category}`).then(res => res.json());

  return (
    <article className="max-w-3xl mx-auto py-12 px-6">
      <h1 className="text-4xl font-bold mb-6">Best {category} for {mood}</h1>
      <div dangerouslySetInnerHTML={{ __html: content.html }} />
    </article>
  );
}