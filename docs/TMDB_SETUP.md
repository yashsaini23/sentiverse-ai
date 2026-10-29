# Live media catalogue (TMDB)

SentiVerse can use The Movie Database (TMDB) as its live movie and TV catalogue. It fetches real titles, poster artwork, backdrops, release years, ratings, and overview text at request time instead of requiring the local Chroma catalogue for movie/TV recommendations.

## Configure locally

1. Create a free TMDB account and request an API key from your account settings: https://www.themoviedb.org/settings/api
2. Open `backend/.env` (copy `backend/.env.example` if needed) and set:

   ```dotenv
   TMDB_API_KEY=your_tmdb_v3_api_key
   ```

3. Restart the backend container so the environment variable is loaded:

   ```powershell
   docker compose up -d --build backend
   ```

4. Submit a mood from http://localhost:3000. When `TMDB_API_KEY` is set, the recommendation endpoint prefers live TMDB results. Without the key, it retains the existing local catalogue as a development fallback.

Never commit `backend/.env` or publish the key in frontend code. TMDB images use the documented image CDN with poster paths rendered at `w500` (portrait poster ratio 2:3) and backdrops at `w1280` (wide 16:9).

## Scope and attribution

The current live provider returns movies and TV series. Other media types (anime, games, books, and podcasts) need their own provider adapters to avoid pretending that one catalogue covers every medium. TMDB usage and attribution must follow its terms: https://www.themoviedb.org/terms-of-use
