"""Multi-provider live media catalogues for mood-based discovery.

Provider adapters are isolated so one unavailable API does not break the full response.
Image dimensions: movie/TV/anime/book cover 2:3; game cover 3:4; backdrop 16:9.
"""
import asyncio
import re
from collections.abc import Sequence

import httpx

from app.core.config import settings
from app.schemas.media import RecommendationResponse
from app.services.tmdb_catalogue import tmdb_catalogue

JIKAN = "https://api.jikan.moe/v4"
GOOGLE_BOOKS = "https://www.googleapis.com/books/v1/volumes"
ITUNES = "https://itunes.apple.com/search"
RAWG = "https://api.rawg.io/api"


def _score(query: str, title: str, description: str, rating: float = 0.0) -> int:
    tokens = set(re.findall(r"[a-z]{3,}", query.lower()))
    searchable = set(re.findall(r"[a-z]{3,}", f"{title} {description}".lower()))
    return int(min(98, max(58, 64 + len(tokens & searchable) * 5 + min(10, rating))))


def _clean_html(value: str) -> str:
    return re.sub(r"<[^>]+>", " ", value or "").replace("&nbsp;", " ").strip()


class MediaProviderHub:
    async def _get(self, client: httpx.AsyncClient, url: str, params: dict) -> dict:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    async def anime(self, client: httpx.AsyncClient, query: str, limit: int) -> list[RecommendationResponse]:
        data = {"data": []}
        # Jikan caps each page at 25; fetch multiple pages for large batches.
        for page in range(1, max(2, (limit + 24) // 25 + 1)):
            remaining = limit - len(data["data"])
            if remaining <= 0:
                break
            batch = await self._get(client, f"{JIKAN}/anime", {
                "q": query, "limit": min(25, remaining), "page": page,
                "sfw": "true", "order_by": "popularity", "sort": "desc",
            })
            page_items = batch.get("data", [])
            data["data"].extend(page_items)
            if len(page_items) < min(25, remaining):
                break
        results = []
        for item in data.get("data", []):
            title = item.get("title_english") or item.get("title") or "Anime"
            synopsis = item.get("synopsis") or ""
            images = item.get("images", {}).get("jpg", {})
            year = item.get("year")
            rating = float(item.get("score") or 0)
            results.append(RecommendationResponse(
                id=f"jikan-anime-{item.get('mal_id')}", title=title, medium="Anime",
                themes=[g.get("name", "") for g in item.get("genres", [])[:4] if g.get("name")],
                tone="anime", pacing="varied", ending_type="varied",
                confidence_score=_score(query, title, synopsis, rating),
                ai_explanation=f"Anime discovery based on your mood: {query}. {synopsis[:420]}".strip(),
                streaming_links={"MyAnimeList": item.get("url", "https://myanimelist.net/anime.php")},
                poster_url=images.get("large_image_url") or images.get("image_url"),
                backdrop_url=None, overview=synopsis, release_year=str(year) if year else None,
                vote_average=rating or None,
            ))
        return results

    async def books(self, client: httpx.AsyncClient, query: str, limit: int, language: str = "all") -> list[RecommendationResponse]:
        data = {"items": []}
        # Google Books allows up to 40 results per request.
        for start_index in range(0, limit, 40):
            page_limit = min(40, limit - start_index)
            params = {
                "q": query, "maxResults": page_limit, "startIndex": start_index,
                "printType": "books",
            }
            if language not in {"all", "regional"}:
                params["langRestrict"] = language
            if settings.GOOGLE_BOOKS_API_KEY:
                params["key"] = settings.GOOGLE_BOOKS_API_KEY
            batch = await self._get(client, GOOGLE_BOOKS, params)
            page_items = batch.get("items", [])
            data["items"].extend(page_items)
            if len(page_items) < page_limit:
                break
        results = []
        for item in data.get("items", []):
            info = item.get("volumeInfo", {})
            title = info.get("title") or "Untitled book"
            description = _clean_html(info.get("description", ""))
            image = info.get("imageLinks", {}).get("thumbnail") or info.get("imageLinks", {}).get("smallThumbnail")
            if image:
                image = image.replace("http://", "https://").replace("zoom=1", "zoom=2")
            authors = info.get("authors", [])
            results.append(RecommendationResponse(
                id=f"google-book-{item.get('id')}", title=title, medium="Book",
                themes=(authors[:3] + (info.get("categories") or [])[:2]),
                tone="reading", pacing="self-paced", ending_type="varied",
                confidence_score=_score(query, title, description, float(info.get("averageRating") or 0)),
                ai_explanation=f"Book discovery for your mood: {query}. {description[:420]}".strip(),
                streaming_links={"Google Books": info.get("infoLink", "https://books.google.com/")},
                poster_url=image, backdrop_url=None, overview=description,
                release_year=(info.get("publishedDate") or "")[:4] or None,
                vote_average=info.get("averageRating"),
            ))
        return results

    async def podcasts(self, client: httpx.AsyncClient, query: str, limit: int, region: str = "IN") -> list[RecommendationResponse]:
        country = "us" if region == "GLOBAL" else region.lower()
        data = await self._get(client, ITUNES, {"term": query, "media": "podcast", "entity": "podcast", "limit": min(limit, 200), "country": country})
        results = []
        for item in data.get("results", []):
            title = item.get("collectionName") or item.get("trackName") or "Podcast"
            description = item.get("primaryGenreName") or ""
            image = item.get("artworkUrl600") or item.get("artworkUrl100")
            if image:
                image = image.replace("100x100bb", "600x600bb")
            results.append(RecommendationResponse(
                id=f"itunes-podcast-{item.get('collectionId')}", title=title, medium="Podcast",
                themes=[description] if description else [], tone="audio", pacing="self-paced",
                ending_type="ongoing", confidence_score=_score(query, title, description),
                ai_explanation=f"Podcast discovery for your mood: {query}. Browse the show to find an episode that fits.",
                streaming_links={"Apple Podcasts": item.get("collectionViewUrl", "https://podcasts.apple.com/")},
                poster_url=image, backdrop_url=None, overview=description,
                release_year=None, vote_average=None,
            ))
        return results

    async def games(self, client: httpx.AsyncClient, query: str, limit: int) -> list[RecommendationResponse]:
        if not settings.RAWG_API_KEY:
            return []
        data = {"results": []}
        # RAWG page_size is capped at 40, so follow its next-page sequence.
        for page in range(1, max(2, (limit + 39) // 40 + 1)):
            remaining = limit - len(data["results"])
            if remaining <= 0:
                break
            batch = await self._get(client, f"{RAWG}/games", {
                "key": settings.RAWG_API_KEY, "search": query,
                "page_size": min(40, remaining), "page": page, "ordering": "-rating",
            })
            page_items = batch.get("results", [])
            data["results"].extend(page_items)
            if len(page_items) < min(40, remaining) or not batch.get("next"):
                break
        results = []
        for item in data.get("results", []):
            title = item.get("name") or "Game"
            rating = float(item.get("rating") or 0)
            released = item.get("released") or ""
            results.append(RecommendationResponse(
                id=f"rawg-game-{item.get('id')}", title=title, medium="Game",
                themes=[g.get("name", "") for g in item.get("genres", [])[:4] if g.get("name")],
                tone="interactive", pacing="player-led", ending_type="varied",
                confidence_score=_score(query, title, " ".join(g.get("name", "") for g in item.get("genres", [])), rating),
                ai_explanation=f"Game discovery based on your mood: {query}. Explore its genre and gameplay details before choosing.",
                streaming_links={"RAWG": item.get("slug") and f"https://rawg.io/games/{item['slug']}" or "https://rawg.io/"},
                poster_url=item.get("background_image"), backdrop_url=None,
                overview=", ".join(g.get("name", "") for g in item.get("genres", []) if g.get("name")),
                release_year=released[:4] or None, vote_average=rating or None,
            ))
        return results

    async def recommend(self, query: str, limit: int, medium_filters: Sequence[str] | None = None,
                        region: str = "IN", language: str = "all") -> list[RecommendationResponse]:
        aliases = {
            "movie": "movie", "movies": "movie", "tv": "tv", "series": "tv", "show": "tv",
            "anime": "anime", "game": "game", "games": "game", "book": "book", "books": "book",
            "novel": "book", "podcast": "podcast", "podcasts": "podcast",
        }
        selected = {aliases.get(value.strip().lower(), value.strip().lower()) for value in (medium_filters or [])}
        providers = {
            "movie": lambda client: tmdb_catalogue.recommend(query, limit, ["Movie"], region, language),
            "tv": lambda client: tmdb_catalogue.recommend(query, limit, ["TV"], region, language),
            "anime": lambda client: self.anime(client, query, limit),
            "game": lambda client: self.games(client, query, limit),
            "book": lambda client: self.books(client, query, limit, language),
            "podcast": lambda client: self.podcasts(client, query, limit, region),
        }
        requested = selected or set(providers)
        async with httpx.AsyncClient(timeout=12.0, headers={"User-Agent": "SentiVerseAI/1.0 (media discovery)"}) as client:
            async def safe_fetch(name: str):
                try:
                    return await providers[name](client)
                except (httpx.HTTPError, ValueError, KeyError, TypeError):
                    return []
            names = [name for name in providers if name in requested]
            batches = await asyncio.gather(*(safe_fetch(name) for name in names))
        unique = {}
        for batch in batches:
            for item in batch:
                unique.setdefault(item.id, item)
        grouped = list(unique.values())
        if not selected:
            interleaved = []
            while any(batches):
                for batch in batches:
                    if batch:
                        candidate = batch.pop(0)
                        if all(item.id != candidate.id for item in interleaved):
                            interleaved.append(candidate)
            grouped = interleaved
        return grouped[:max(1, min(limit, 100))]


media_provider_hub = MediaProviderHub()
