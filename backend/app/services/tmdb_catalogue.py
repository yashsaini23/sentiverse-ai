"""Live TMDB catalogue used when TMDB_API_KEY is configured.

TMDB API docs: https://developer.themoviedb.org/docs
Poster assets are rendered in their intended 2:3 portrait ratio; backdrops use 16:9.
"""
import re
from collections.abc import Sequence

import httpx

from app.core.config import settings
from app.schemas.media import RecommendationResponse

TMDB_API = "https://api.themoviedb.org/3"
IMAGE_BASE = "https://image.tmdb.org/t/p"


class TMDBCatalogue:
    async def recommend(
        self, query: str, limit: int = 4, medium_filters: Sequence[str] | None = None
    ) -> list[RecommendationResponse]:
        if not settings.TMDB_API_KEY:
            return []

        filters = {value.strip().lower() for value in (medium_filters or [])}
        want_movies = not filters or bool(filters & {"movie", "movies", "film", "films"})
        want_tv = not filters or bool(filters & {"tv", "tv show", "tv shows", "series", "show"})
        tokens = {token for token in re.findall(r"[a-z]{3,}", query.lower())}
        endpoints = []
        if want_movies:
            endpoints.append(("Movie", "/discover/movie"))
        if want_tv:
            endpoints.append(("TV", "/discover/tv"))
        if not endpoints:
            return []

        async with httpx.AsyncClient(timeout=12.0) as client:
            async def fetch(kind: str, endpoint: str):
                response = await client.get(
                    f"{TMDB_API}{endpoint}",
                    params={
                        "api_key": settings.TMDB_API_KEY,
                        "language": "en-US",
                        "sort_by": "popularity.desc",
                        "include_adult": "false",
                        "page": 1,
                    },
                )
                response.raise_for_status()
                return kind, response.json().get("results", [])

            responses = await __import__("asyncio").gather(
                *(fetch(kind, endpoint) for kind, endpoint in endpoints)
            )

        ranked = []
        for kind, items in responses:
            for item in items:
                title = item.get("title") or item.get("name") or "Untitled"
                overview = item.get("overview") or ""
                searchable = set(re.findall(r"[a-z]{3,}", f"{title} {overview}".lower()))
                overlap = len(tokens & searchable)
                popularity = float(item.get("popularity") or 0)
                rating = float(item.get("vote_average") or 0)
                score = min(99, max(55, 62 + overlap * 5 + min(12, popularity / 30) + rating / 2))
                ranked.append((overlap, popularity, kind, item, title, overview, score))

        ranked.sort(key=lambda row: (row[0], row[1]), reverse=True)
        output = []
        for _, _, kind, item, title, overview, score in ranked[: max(1, min(limit, 20))]:
            media_id = item.get("id")
            poster = item.get("poster_path")
            backdrop = item.get("backdrop_path")
            release_date = item.get("release_date") or item.get("first_air_date") or ""
            genres = item.get("genre_ids") or []
            output.append(RecommendationResponse(
                id=f"tmdb-{kind.lower()}-{media_id}",
                title=title,
                medium=kind,
                themes=[f"Genre {genre_id}" for genre_id in genres[:4]],
                tone="mood-matched",
                pacing="moderate",
                ending_type="discover",
                confidence_score=int(score),
                ai_explanation=overview or "A popular title from the live TMDB catalogue. Explore its details to see if it fits your mood.",
                streaming_links={"TMDB": f"https://www.themoviedb.org/{'movie' if kind == 'Movie' else 'tv'}/{media_id}"},
                poster_url=f"{IMAGE_BASE}/w500{poster}" if poster else None,
                backdrop_url=f"{IMAGE_BASE}/w1280{backdrop}" if backdrop else None,
                overview=overview,
                release_year=release_date[:4] if release_date else None,
                vote_average=float(item.get("vote_average") or 0),
            ))
        return output


tmdb_catalogue = TMDBCatalogue()
