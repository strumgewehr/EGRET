"""Seed database with default sources and sample data for development."""
import os
import sys
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models import Source, Article, SentimentResult
from app.services.sentiment_service import analyze_sentiment
from app.services.bias_service import bias_index
import hashlib

def _ext_id(sid: int, url: str) -> str:
    return hashlib.sha256(f"{sid}:{url}".encode()).hexdigest()[:64]


def main():
    db = SessionLocal()
    try:
        if db.query(Source).first():
            print("Sources already exist, skipping seed.")
            return
        # Default RSS sources - Expanded pool
        sources = [
            Source(name="BBC News", slug="bbc-news", base_url="https://www.bbc.com", feed_url="https://feeds.bbci.co.uk/news/rss.xml", fetch_interval_minutes=30),
            Source(name="Reuters", slug="reuters", base_url="https://www.reuters.com", feed_url="https://www.reutersagency.com/feed/?taxonomy=best-topics&post_type=best", fetch_interval_minutes=30),
            Source(name="Al Jazeera", slug="al-jazeera", base_url="https://www.aljazeera.com", feed_url="https://www.aljazeera.com/xml/rss/all.xml", fetch_interval_minutes=30),
            Source(name="The Guardian", slug="the-guardian", base_url="https://www.theguardian.com", feed_url="https://www.theguardian.com/world/rss", fetch_interval_minutes=30),
            Source(name="NPR News", slug="npr", base_url="https://www.npr.org", feed_url="https://feeds.npr.org/1001/rss.xml", fetch_interval_minutes=30),
            Source(name="Wall Street Journal", slug="wsj", base_url="https://www.wsj.com", feed_url="https://feeds.a.dj.com/rss/RSSWorldNews.xml", fetch_interval_minutes=30),
            Source(name="TechCrunch", slug="techcrunch", base_url="https://techcrunch.com", feed_url="https://techcrunch.com/feed/", fetch_interval_minutes=30),
        ]
        for s in sources:
            db.add(s)
        db.commit()
        for s in sources:
            db.refresh(s)

        # MASSIVE keyword dictionary to ensure search relevance
        topics_map = {
            "Economy": ["inflation", "market", "stock", "trade", "banking", "finance", "currency", "gold", "debt", "interest", "recession", "growth", "tax", "budget", "startup", "venture", "crypto", "bitcoin", "ethereum", "jobs", "unemployment", "wages", "salary", "wealth", "poverty", "insurance", "real estate", "housing"],
            "Technology": ["AI", "artificial intelligence", "robot", "automation", "chip", "semiconductor", "software", "app", "cloud", "server", "data", "privacy", "cybersecurity", "hacking", "encryption", "internet", "5G", "satellite", "space", "NASA", "Mars", "rocket", "quantum", "computer", "mobile", "gadget", "battery", "electric", "Tesla", "Apple", "Google", "Microsoft", "Meta"],
            "Politics": ["election", "vote", "campaign", "senate", "congress", "parliament", "government", "policy", "law", "court", "justice", "protest", "democracy", "freedom", "human rights", "corruption", "sanction", "diplomacy", "treaty", "alliance", "NATO", "UN", "border", "immigration", "refugee", "war", "peace", "conflict", "military", "defense", "iran", "israel", "china", "russia", "ukraine", "middle east", "geopolitics"],
            "Environment": ["climate", "warming", "carbon", "emission", "pollution", "plastic", "ocean", "forest", "wildfire", "drought", "flood", "storm", "hurricane", "energy", "solar", "wind", "renewable", "oil", "gas", "coal", "mining", "nature", "wildlife", "extinction", "conservation", "sustainable", "green"],
            "Health": ["virus", "pandemic", "vaccine", "medicine", "doctor", "hospital", "patient", "cancer", "disease", "mental health", "fitness", "nutrition", "diet", "FDA", "WHO", "biotech", "genetics", "longevity", "aging", "brain", "heart", "surgery", "therapy"],
            "Crisis": ["emergency", "disaster", "catastrophe", "tragedy", "accident", "crash", "explosion", "fire", "earthquake", "tsunami", "famine", "shortage", "scandal", "leak", "exposed", "warning", "threat", "danger", "risk", "failure"]
        }
        
        # Add 500+ sample articles spread over 7 days
        print(f"Adding 500+ articles for {len(sources)} sources across {sum(len(v) for v in topics_map.values())} keywords...")
        
        import random
        for day_offset in range(10): # Today + last 9 days
            date = datetime.now(timezone.utc) - timedelta(days=day_offset)
            
            for source in sources:
                # Add 6-10 articles per source per day to reach ~500 total
                num_articles = random.randint(6, 10)
                for i in range(num_articles):
                    category = random.choice(list(topics_map.keys()))
                    keywords = topics_map[category]
                    
                    # Pick 2-3 related keywords to weave into the title and summary
                    sampled_keywords = random.sample(keywords, k=min(3, len(keywords)))
                    primary_kw = sampled_keywords[0]
                    secondary_kw = sampled_keywords[1] if len(sampled_keywords) > 1 else primary_kw
                    
                    sentiment_base = random.uniform(-0.9, 0.9)
                    
                    # Create some category-specific sentiment trends
                    if category == "Crisis": sentiment_base = random.uniform(-1.0, -0.5)
                    if category == "Technology": sentiment_base = random.uniform(0.2, 1.0)
                    
                    title = f"Special Report: {primary_kw.capitalize()} and {secondary_kw.capitalize()} Trends in {category}"
                    summary = f"In-depth analysis from {source.name} regarding the latest developments in {primary_kw}. " \
                              f"Our experts examine how {secondary_kw} is impacting the broader {category.lower()} landscape. " \
                              f"Recent data suggests a significant shift in the {sampled_keywords[-1]} sector."
                    
                    url = f"https://example.com/{source.slug}/{day_offset}/{category.lower()}_{primary_kw}_{i}"
                    ext_id = _ext_id(source.id, url)
                    
                    if db.query(Article).filter(Article.external_id == ext_id).first():
                        continue
                        
                    a = Article(
                        source_id=source.id,
                        external_id=ext_id,
                        title=title,
                        summary=summary,
                        url=url,
                        published_at=date,
                    )
                    db.add(a)
                    db.flush()
                    
                    # Sentiment result
                    db.add(SentimentResult(
                        article_id=a.id, 
                        score=round(sentiment_base, 4), 
                        confidence=0.9, 
                        emotion="joy" if sentiment_base > 0 else "anger" if sentiment_base < 0 else "neutral", 
                        bias_index=random.uniform(0.05, 0.5)
                    ))
        db.commit()
        print(f"Seed completed: sources and {db.query(Article).count()} sample articles added.")
        print("Seed completed: sources and sample articles added.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
