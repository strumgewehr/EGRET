"""
Multi-source news ingestion: RSS parsing, duplicate filtering, metadata extraction.
"""
import hashlib
import logging
from datetime import datetime, timezone
from typing import List, Optional, Tuple

import feedparser
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import Article, Source, IngestionLog
from app.services.sentiment_service import analyze_sentiment
from app.services.bias_service import bias_index
from app.services.headline_detector import headline_manipulation_score
from app.models.analysis import SentimentResult, HeadlineFlag

logger = logging.getLogger(__name__)
settings = get_settings()


def _external_id(source_id: int, url: str) -> str:
    """Stable external_id for deduplication."""
    return hashlib.sha256(f"{source_id}:{url}".encode()).hexdigest()[:64]


def _parse_feed(feed_url: str, limit: int = 50) -> List[dict]:
    """Fetch and parse RSS/Atom feed. Returns list of entry dicts."""
    try:
        import urllib.request
        req = urllib.request.Request(feed_url, headers={"User-Agent": "NewsSentimentBot/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()
        feed = feedparser.parse(data)
        entries = getattr(feed, "entries", [])[:limit]
        out = []
        for e in entries:
            link = e.get("link") or ""
            if not link:
                continue
            published = e.get("published_parsed")
            if published:
                from time import mktime
                pub_dt = datetime.fromtimestamp(mktime(published), tz=timezone.utc)
            else:
                pub_dt = datetime.now(timezone.utc)
            title = (e.get("title") or "").strip()
            summary = (e.get("summary") or e.get("description") or "").strip()
            if len(summary) > 5000:
                summary = summary[:5000]
            out.append({
                "url": link,
                "title": title,
                "summary": summary,
                "published_at": pub_dt,
                "author": e.get("author"),
                "link": link,
            })
        return out
    except Exception as e:
        logger.warning("Feed parse error %s: %s", feed_url, e)
        return []


def discover_news(db: Session, keyword: str, limit: int = 10) -> List[Article]:
    """
    Live Discovery: Fetch real-time news for ANY keyword via search-based RSS.
    Ensures 'any word in existence' returns relevant data.
    """
    if not keyword or len(keyword) < 2:
        return []

    import urllib.parse
    # Google News RSS search URL
    search_url = f"https://news.google.com/rss/search?q={urllib.parse.quote(keyword)}&hl=en-US&gl=US&ceid=US:en"
    
    # We use source_id=1 (BBC News) as a placeholder for discovery, or create a 'Discovery' source
    discovery_source = db.query(Source).filter(Source.slug == "discovery").first()
    if not discovery_source:
        discovery_source = Source(
            name="Global Discovery",
            slug="discovery",
            base_url="https://news.google.com",
            is_active=False # Not for regular scheduler
        )
        db.add(discovery_source)
        db.commit()
        db.refresh(discovery_source)

    entries = _parse_feed(search_url, limit=limit)
    new_articles = []
    
    for entry in entries:
        ext_id = _external_id(discovery_source.id, entry["url"])
        if db.query(Article).filter(Article.external_id == ext_id).first():
            continue
            
        article = Article(
            source_id=discovery_source.id,
            external_id=ext_id,
            title=entry["title"],
            summary=entry.get("summary") or "",
            url=entry["url"],
            published_at=entry["published_at"],
            author=entry.get("author"),
        )
        db.add(article)
        db.flush()
        
        # Run sentiment + bias + headline
        text = (entry.get("summary") or entry["title"]) or ""
        score, conf, emotion = analyze_sentiment(text)
        bias = bias_index(text)
        db.add(SentimentResult(article_id=article.id, score=score, confidence=conf, emotion=emotion, bias_index=bias))
        
        manip_score, trigger_words = headline_manipulation_score(entry["title"])
        if manip_score > 0:
            import json
            db.add(HeadlineFlag(article_id=article.id, manipulation_score=manip_score, trigger_words=json.dumps(trigger_words)))
        
        new_articles.append(article)
    
    if new_articles:
        db.commit()
        logger.info("Live Discovery: Found %d new articles for '%s'", len(new_articles), keyword)
        
    return new_articles


def fetch_source(db: Session, source: Source, triggered_by: str = "scheduler") -> IngestionLog:
    """Fetch one source, dedupe, insert new articles, run sentiment/headline/bias."""
    log = IngestionLog(
        source_id=source.id,
        status="started",
        started_at=datetime.now(timezone.utc),
        triggered_by=triggered_by,
    )
    db.add(log)
    db.commit()
    db.refresh(log)

    feed_url = source.feed_url or ""
    if not feed_url:
        log.status = "failed"
        log.error_message = "No feed_url"
        log.completed_at = datetime.now(timezone.utc)
        db.commit()
        return log

    entries = _parse_feed(feed_url, limit=settings.default_fetch_limit_per_source)
    log.articles_fetched = len(entries)
    new_count = 0
    dup_count = 0

    for entry in entries:
        ext_id = _external_id(source.id, entry["url"])
        existing = db.query(Article).filter(Article.external_id == ext_id).first()
        if existing:
            dup_count += 1
            continue
        article = Article(
            source_id=source.id,
            external_id=ext_id,
            title=entry["title"],
            summary=entry.get("summary"),
            url=entry["url"],
            published_at=entry["published_at"],
            author=entry.get("author"),
        )
        db.add(article)
        db.flush()
        # Run sentiment + bias + headline
        text = (entry.get("summary") or entry["title"]) or ""
        score, conf, emotion = analyze_sentiment(text)
        bias = bias_index(text)
        db.add(SentimentResult(article_id=article.id, score=score, confidence=conf, emotion=emotion, bias_index=bias))
        manip_score, trigger_words = headline_manipulation_score(entry["title"])
        if manip_score > 0:
            import json
            db.add(HeadlineFlag(article_id=article.id, manipulation_score=manip_score, trigger_words=json.dumps(trigger_words)))
        new_count += 1

    source.last_fetched_at = datetime.now(timezone.utc)
    log.articles_new = new_count
    log.articles_duplicates = dup_count
    log.status = "success"
    log.completed_at = datetime.now(timezone.utc)
    db.commit()
    return log


def run_all_sources(db: Session, triggered_by: str = "scheduler") -> List[IngestionLog]:
    """Run ingestion for all active sources."""
    sources = db.query(Source).filter(Source.is_active == True).all()
    logs = []
    for s in sources:
        try:
            logs.append(fetch_source(db, s, triggered_by=triggered_by))
        except Exception as e:
            logger.exception("Ingestion failed for source %s: %s", s.id, e)
            log = db.query(IngestionLog).filter(IngestionLog.source_id == s.id).order_by(IngestionLog.started_at.desc()).first()
            if log and log.status == "started":
                log.status = "failed"
                log.error_message = str(e)[:2000]
                log.completed_at = datetime.now(timezone.utc)
                db.commit()
                logs.append(log)
    return logs
