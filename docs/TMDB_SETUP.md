# Live multi-media catalogue

SentiVerse can fetch live recommendations from dedicated catalogues instead of relying only on the starter Chroma catalogue.

## Provider coverage

| Media type | Provider | API key |
| --- | --- | --- |
| Movies and TV | TMDB | Required |
| Anime | Jikan API (MyAnimeList data) | Not required |
| Games | RAWG | Required |
| Books | Google Books | Optional |
| Podcasts | Apple iTunes Search API | Not required |

Providers are isolated: if one service is temporarily unavailable, the other catalogue requests can still succeed. With **All** selected, results are interleaved across provider categories where data is available.

## Configure keys locally

1. Request a TMDB API key: https://www.themoviedb.org/settings/api
2. For live game search, request a RAWG API key: https://rawg.io/apidocs
3. Copy `backend/.env.example` to `backend/.env` and fill in any keys you have:

   ```dotenv
   TMDB_API_KEY=your_tmdb_v3_api_key
   RAWG_API_KEY=your_rawg_api_key
   GOOGLE_BOOKS_API_KEY=
   ```

   TMDB is needed for movies/TV; RAWG is needed for live game search. Google Books works without a key for light usage, but an API key can be added for quota management.

4. Rebuild/restart the backend so environment changes load:

   ```powershell
   docker compose up -d --build backend
   ```

5. Open http://localhost:3000 and choose **All**, **Movie**, **TV**, **Anime**, **Game**, **Book**, or **Podcast**.

Never commit `backend/.env`, API keys, or credentials to GitHub. Put keys only in backend environment configuration or a deployment secret store.

## Media artwork sizing

- Movie, TV, anime, and book covers use portrait-friendly artwork in cards (CSS `aspect-ratio: 2 / 3`).
- Game covers use a portrait crop when available (CSS card still reserves the same poster frame).
- Wide backdrops use 16:9 when supplied.
- Artwork is lazy-loaded, uses `object-fit: cover`, and has a designed gradient fallback if a provider has no image or an image fails.

## Provider notes and attribution

- TMDB images use its image CDN; review TMDB's terms and attribution requirements: https://www.themoviedb.org/terms-of-use
- Jikan is an unofficial MyAnimeList API: https://docs.api.jikan.moe/
- RAWG terms and API docs: https://rawg.io/apidocs
- Google Books API docs: https://developers.google.com/books/docs/v1/using
- Apple iTunes Search API docs: https://developer.apple.com/library/archive/documentation/AudioVideo/Conceptual/iTuneSearchAPI/
