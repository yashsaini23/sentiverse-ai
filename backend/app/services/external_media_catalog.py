import asyncio
import logging
import re
from typing import Any

import httpx

from app.schemas.media import RecommendationResponse

logger = logging.getLogger(__name__)

_TIMEOUT = httpx.Timeout(7.0, connect=3.0)
_HEADERS = {"User-Agent": "SentiVerseAI/1.0 (mood-based media discovery)"}
_STOP_WORDS = {
    "a", "an", "and", "are", "am", "be", "but", "by", "feel", "feeling",
    "for", "from", "have", "i", "im", "in", "is", "it", "me", "my", "need",
    "of", "on", "or", "something", "that", "the", "this", "to", "want", "with",
}
_MOOD_SEARCH_TERMS = (
    ({"lonely", "alone", "isolated", "connection"}, "friendship"),
    ({"hope", "hopeful", "inspired", "inspiration"}, "hope"),
    ({"anxious", "anxiety", "overwhelmed", "stress", "stressed"}, "healing"),
    ({"sad", "sadness", "heartbroken", "disappointed"}, "uplifting"),
    ({"motivation", "motivated", "determined"}, "inspiring"),
    ({"calm", "peaceful", "relax", "relaxed"}, "comfort"),
)


def _search_term(query: str) -> str:
    words = set(re.findall(r"[a-zA-Z]{3,}", query.lower()))
    for mood_words, term in _MOOD_SEARCH_TERMS:
        if words & mood_words:
            return term
    useful = [word for word in re.findall(r"[a-zA-Z]{3,}", query.lower()) if word not in _STOP_WORDS]
    return " ".join(useful[:3]) or "popular"


def _medium_allowed(medium: str, filters: list[str]) -> bool:
    if not filters:
        return True
    aliases = {
        "tv": {"tv", "tv show", "show", "series"},
        "movie": {"movie", "film", "movies", "films"},
        "anime": {"anime", "animation"},
        "novel": {"novel", "book", "books", "literature"},
        "podcast": {"podcast", "podcasts"},
    }
    normalized = medium.lower()
    return any(normalized == f.lower() or f.lower() in aliases.get(normalized, set()) for f in filters)


class ExternalMediaCatalog:
    """Discover media through public APIs; no local catalogue/database is required."""

    async def _get_json(self, client: httpx.AsyncClient, url: str, params: dict[str, Any]) -> Any:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    async def _tvmaze(self, client: httpx.AsyncClient, term: str) -> list[dict[str, Any]]:
        data = await self._get_json(client, "https://api.tvmaze.com/search/shows", {"q": term})
        items = []
        for entry in data[:6]:
            show = entry.get("show") or {}
            summary = re.sub(r"<[^>]+>", " ", show.get("summary") or "")
            if show.get("name"):
                items.append(self._item(
                    item_id=f"tvmaze-{show.get('id')}", title=show["name"], medium="TV Show",
                    summary=summary, genres=show.get("genres") or [],
                    link=show.get("url") or "", image=((show.get("image") or {}).get("medium") or ""),
                ))
        return items

    async def _jikan(self, client: httpx.AsyncClient, term: str) -> list[dict[str, Any]]:
        data = await self._get_json(client, "https://api.jikan.moe/v4/anime", {"q": term, "limit": 6, "sfw": "true"})
        items = []
        for anime in (data.get("data") or [])[:6]:
            if anime.get("title"):
                items.append(self._item(
                    item_id=f"jikan-{anime.get('mal_id')}", title=anime["title"], medium="Anime",
                    summary=anime.get("synopsis") or "", genres=[g.get("name", "") for g in anime.get("genres", [])],
                    link=((anime.get("url") or "")), image=(((anime.get("images") or {}).get("jpg") or {}).get("image_url") or ""),
                ))
        return items

    async def _open_library(self, client: httpx.AsyncClient, term: str) -> list[dict[str, Any]]:
        data = await self._get_json(
            client, "https://openlibrary.org/search.json",
            {"q": term, "limit": 6, "fields": "key,title,first_sentence,subject,author_name,cover_i"},
        )
        items = []
        for book in (data.get("docs") or [])[:6]:
            title = book.get("title")
            if title:
                sentences = book.get("first_sentence") or []
                summary = sentences[0] if sentences else ""
                subjects = (book.get("subject") or [])[:5]
                cover_id = book.get("cover_i")
                items.append(self._item(
                    item_id=f"openlibrary-{book.get('key', title)}", title=title, medium="Novel",
                    summary=summary, genres=subjects,
                    link=f"https://openlibrary.org{book.get('key', '')}",
                    image=f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg" if cover_id else "",
                ))
        return items

    async def _itunes(self, client: httpx.AsyncClient, term: str) -> list[dict[str, Any]]:
        data = await self._get_json(
            client, "https://itunes.apple.com/search",
            {"term": term, "entity": "podcast", "limit": 6, "media": "podcast"},
        )
        items = []
        for podcast in (data.get("results") or [])[:6]:
            title = podcast.get("collectionName")
            if title:
                items.append(self._item(
                    item_id=f"itunes-{podcast.get('collectionId')}", title=title, medium="Podcast",
                    summary=podcast.get("artistName") or "Podcast available through Apple Podcasts.",
                    genres=[podcast.get("primaryGenreName", "Podcast")],
                    link=podcast.get("collectionViewUrl") or "", image=podcast.get("artworkUrl600") or podcast.get("artworkUrl100") or "",
                ))
        return items

    @staticmethod
    def _item(item_id: str, title: str, medium: str, summary: str, genres: list[str], link: str, image: str) -> dict[str, Any]:
        return {"id": str(item_id), "title": title, "medium": medium, "summary": summary,
                "genres": genres, "link": link, "image": image}

    async def get_recommendations(
        self, mood_query: str, limit: int = 5, exclude_ids: list[str] | None = None,
        medium_filters: list[str] | None = None,
    ) -> list[RecommendationResponse]:
        if not mood_query.strip():
            return []
        term = _search_term(mood_query)
        excluded = set(exclude_ids or [])
        filters = list(medium_filters or [])
        async with httpx.AsyncClient(timeout=_TIMEOUT, headers=_HEADERS, follow_redirects=True) as client:
            calls = await asyncio.gather(
                self._tvmaze(client, term), self._jikan(client, term),
                self._open_library(client, term), self._itunes(client, term),
                return_exceptions=True,
            )

        items: list[dict[str, Any]] = []
        for result in calls:
            if isinstance(result, Exception):
                logger.warning("External media provider failed: %s", result)
                continue
            items.extend(result)

        unique: dict[str, dict[str, Any]] = {}
        for item in items:
            if item["id"] not in excluded and _medium_allowed(item["medium"], filters):
                unique[item["id"]] = item

        query_words = set(re.findall(r"[a-zA-Z]{3,}", (mood_query + " " + term).lower())) - _STOP_WORDS
        ranked = sorted(
            unique.values(),
            key=lambda item: len(query_words & set(re.findall(
                r"[a-zA-Z]{3,}", (item["title"] + " " + item["summary"] + " " + " ".join(item["genres"])).lower()
            ))),
            reverse=True,
        )
        recommendations = []
        for item in ranked[:max(1, min(int(limit), 20))]:
            themes = [str(theme) for theme in item["genres"] if theme][:5]
            summary = re.sub(r"\s+", " ", item["summary"]).strip()
            explanation = (
                f"Found via the {item['medium']} catalogue using the theme “{term}”. "
                + (summary[:240] if summary else "Explore this title and see whether its themes match your current mood.")
            )
            recommendations.append(RecommendationResponse(
                id=item["id"], title=item["title"], medium=item["medium"], themes=themes,
                tone="reflective", pacing="moderate", ending_type="unknown",
                confidence_score=65 if summary else 50, ai_explanation=explanation,
                streaming_links={k: v for k, v in {"details": item["link"], "poster": item["image"]}.items() if v},
            ))
        return recommendations


external_media_catalog = ExternalMediaCatalog()
