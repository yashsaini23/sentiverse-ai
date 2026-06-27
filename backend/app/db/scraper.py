from pytrends.request import TrendReq
from app.services.content_generator import generate_seo_article

# Initialize connection to Google
pytrends = TrendReq(hl='en-US', tz=360)

def get_trending_moods():
    # Fetch trending searches related to emotional states
    kw_list = ["feeling lonely", "feeling anxious", "feeling motivated", "feeling nostalgic"]
    pytrends.build_payload(kw_list, timeframe='now 1-d')
    
    # Get rising related queries
    related_queries = pytrends.related_queries()
    
    trending_list = []
    for mood in kw_list:
        # Extract rising topics to create fresh content ideas
        rising = related_queries[mood]['rising']
        if not rising.empty:
            top_term = rising.iloc[0]['query']
            trending_list.append(top_term)
            
    return trending_list

def run_content_factory():
    moods = get_trending_moods()
    categories = ["movies", "books", "podcasts"]
    
    for mood in moods:
        for cat in categories:
            print(f"Generating content for: {mood} - {cat}")
            article = generate_seo_article(mood, cat)
            # Save to your database (MongoDB/PostgreSQL)
            # db.articles.insert({"mood": mood, "category": cat, "body": article})
            
if __name__ == "__main__":
    run_content_factory()