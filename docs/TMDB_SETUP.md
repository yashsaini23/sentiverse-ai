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
   TMDB_API_KEY=your_rotated_tmdb_api_key
   RAWG_API_KEY=your_rawg_api_key
   GOOGLE_BOOKS_API_KEY=
   ```

   TMDB is needed for movies/TV; RAWG is needed for live game search. Google Books works without a key for light usage, but an API key can be added for quota management.

4. Rebuild/restart the backend so environment changes load:

   ```bash
   docker compose up -d --build backend
   ```

5. Open http://localhost:3000 and choose **All**, **Movie**, **TV**, **Anime**, **Game**, **Book**, or **Podcast**.

## Configure a deployed environment

A local `backend/.env` file only configures your local checkout. It does not automatically configure GitHub Actions or a hosted application.

- **Hosted backend:** open your hosting provider's service settings and add `TMDB_API_KEY` as a runtime environment variable. Add `RAWG_API_KEY` if you want live game search. Save the settings and redeploy/restart the backend.
- **GitHub Actions:** if a workflow needs the key during a CI job, add it under **Repository → Settings → Secrets and variables → Actions → New repository secret**. Name it `TMDB_API_KEY`, then explicitly map `${{ secrets.TMDB_API_KEY }}` to the workflow step/job environment that needs it. A GitHub Actions secret is **not** automatically passed to a separately hosted backend; configure the hosting provider too.
- Never put real keys in source files, commits, screenshots, issue comments, logs, or frontend `NEXT_PUBLIC_*` variables. The TMDB key belongs only on the backend.
- If a key has been pasted into chat, a public issue, or a repository commit, rotate/revoke it in the provider dashboard and use the replacement.

## Verify the integration

After setting the key, rebuild/restart the backend and inspect its logs for startup or provider errors:

```bash
docker compose logs --tail=100 backend
```

Then submit a recommendation request from the UI with **Movie** or **TV** selected. A successful backend startup alone does not prove the external TMDB request is working; check the response and logs as well.

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
