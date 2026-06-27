import openai

def generate_seo_article(mood: str, category: str):
    prompt = f"""
    Write a 500-word SEO-optimized blog post titled "Top 5 {category} to Watch When Feeling {mood.title()}".
    Include a short intro on the psychology of the mood, 5 specific recommendations with reasons, and a conclusion.
    Format the output in Markdown.
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content