'use client';

import { useCallback, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { usePostHog } from 'posthog-js/react';
import { RecommendationCard } from '@/components/RecommendationCard';
import { EmotionVisualizer, Emotion } from '@/components/EmotionVisualizer';
import { MoodJournalSidebar } from '@/components/MoodJournalSidebar';
import { MediaFilters } from '@/components/MediaFilters';
import { VoiceInput } from '@/components/VoiceInput';
import { useAppStore } from '@/store/useAppStore';

interface RecommendationData {
  id: string;
  title: string;
  medium: string;
  themes: string[];
  tone: string;
  pacing: string;
  ending_type: string;
  confidence_score: number;
  ai_explanation: string;
  streaming_links: Record<string, string>;
  poster_url?: string | null;
  backdrop_url?: string | null;
  overview?: string | null;
  release_year?: string | null;
  vote_average?: number | null;
}

const starterMoods = [
  { icon: '🌧️', label: 'I feel lonely, but I want a little hope.', tag: 'Find hope' },
  { icon: '🌿', label: 'I am overwhelmed and need something calming.', tag: 'Slow down' },
  { icon: '🔥', label: 'I need motivation to keep pushing forward.', tag: 'Get inspired' },
  { icon: '🌙', label: 'I want something deep, thoughtful, and bittersweet.', tag: 'Feel deeply' },
];

export default function Home() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [mood, setMood] = useState('');
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState<string[]>([]);
  const [region, setRegion] = useState('IN');
  const [language, setLanguage] = useState('all');
  const [results, setResults] = useState<RecommendationData[]>([]);
  const [detectedEmotions, setDetectedEmotions] = useState<Emotion[]>([]);
  const [errorMessage, setErrorMessage] = useState('');
  const [hasSearched, setHasSearched] = useState(false);
  const posthog = usePostHog();
  const sessionId = useAppStore((state) => state.sessionId);
  const addToHistory = useAppStore((state) => state.addToHistory);

  const fetchRecommendations = useCallback(async (searchQuery: string) => {
    const query = searchQuery.trim();
    if (!query) {
      setErrorMessage('Tell us a little about how you feel first.');
      return;
    }

    setLoading(true);
    setErrorMessage('');
    setHasSearched(true);
    setResults([]);
    setDetectedEmotions([]);

    try {
      const apiUrl = (process.env.NEXT_PUBLIC_API_URL || '').replace(/\/$/, '');
      const response = await fetch(`${apiUrl}/api/v1/recommend`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query,
          limit: 100,
          session_id: sessionId,
          medium_filters: filters,
          region,
          language,
        }),
      });

      const payload = await response.json().catch(() => null);
      if (!response.ok) {
        const detail = payload?.detail;
        throw new Error(typeof detail === 'string' ? detail : `The API returned error ${response.status}. Check that the backend is running.`);
      }

      setResults(Array.isArray(payload?.recommendations) ? payload.recommendations : []);
      setDetectedEmotions(Array.isArray(payload?.detected_emotions) ? payload.detected_emotions : []);
      addToHistory({
        mood: query,
        timestamp: new Date().toISOString(),
        topEmotions: Array.isArray(payload?.detected_emotions) ? payload.detected_emotions : [],
      });
      posthog?.capture('mood_searched', { mood: query, filters });
    } catch (error) {
      console.error('SentiVerse recommendation request failed:', error);
      setErrorMessage(
        error instanceof TypeError
          ? 'Could not reach the SentiVerse API. Make sure Docker containers are running, then retry.'
          : error instanceof Error
            ? error.message
            : 'Something went wrong while analyzing your mood. Please try again.'
      );
    } finally {
      setLoading(false);
    }
  }, [addToHistory, filters, language, posthog, region, sessionId]);

  const handleSearch = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    void fetchRecommendations(mood);
  };

  const handleVoiceTranscript = useCallback((transcript: string) => {
    setMood(transcript);
  }, []);

  const handleRefinement = (title: string, refinementContext: string) => {
    const refinedQuery = `${mood}. For ${title}, please find something that is ${refinementContext}.`;
    setMood(refinedQuery);
    void fetchRecommendations(refinedQuery);
    posthog?.capture('mood_refined', { original_mood: mood, title, refinement: refinementContext });
  };

  return (
    <main className="sv-shell min-h-screen overflow-hidden text-white">
      <div className="sv-noise" aria-hidden="true" />
      <div className="sv-glow sv-glow-one" aria-hidden="true" />
      <div className="sv-glow sv-glow-two" aria-hidden="true" />

      <header className="relative z-20 mx-auto flex w-full max-w-7xl items-center justify-between px-5 py-5 sm:px-8 lg:px-12">
        <a href="/" className="flex items-center gap-3" aria-label="SentiVerse home">
          <span className="sv-logo-mark"><span>✳</span></span>
          <span className="text-lg font-semibold tracking-tight">senti<span className="text-violet-300">verse</span></span>
        </a>
        <div className="flex items-center gap-3">
          <span className="hidden items-center gap-2 rounded-full border border-white/10 bg-white/[0.035] px-3 py-2 text-xs text-slate-300 sm:flex">
            <span className="sv-status-dot" /> Made for your mood
          </span>
          <button onClick={() => setIsSidebarOpen(true)} className="sv-journal-button" type="button">
            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 4.75A1.75 1.75 0 0 1 6.75 3h11.5A1.75 1.75 0 0 1 20 4.75v15.5A1.75 1.75 0 0 1 18.25 22H6.75A1.75 1.75 0 0 1 5 20.25zM8 7h8M8 11h8M8 15h5" /></svg>
            <span>My journal</span>
          </button>
        </div>
      </header>

      <MoodJournalSidebar isOpen={isSidebarOpen} onClose={() => setIsSidebarOpen(false)} />

      <section className="relative z-10 mx-auto flex w-full max-w-7xl flex-col items-center px-5 pb-20 pt-10 sm:px-8 sm:pt-16 lg:px-12 lg:pt-20">
        <motion.div initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }} className="w-full max-w-4xl text-center">
          <div className="sv-eyebrow mx-auto mb-6"><span className="sv-spark">✦</span> YOUR FEELINGS, YOUR NEXT FAVOURITE</div>
          <h1 className="sv-hero-title mx-auto max-w-4xl">
            Find the story that <span>feels like you.</span>
          </h1>
          <p className="mx-auto mt-6 max-w-2xl text-base leading-7 text-slate-400 sm:text-lg sm:leading-8">
            A streaming-style universe for the mood you can’t explain. Discover films and series that meet you exactly where you are.
          </p>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.12, duration: 0.6 }} className="sv-search-panel mt-10 w-full max-w-3xl sm:mt-12">
          <div className="mb-4 flex items-center justify-between gap-3">
            <label htmlFor="mood-input" className="text-sm font-medium text-slate-200">What’s on your mind?</label>
            <span className="text-xs text-slate-500">Be real. There’s no wrong answer.</span>
          </div>
          <form onSubmit={handleSearch}>
            <div className="sv-input-wrap">
              <textarea
                id="mood-input"
                value={mood}
                onChange={(event) => setMood(event.target.value)}
                placeholder="I’ve had a long week. I feel a little lost, but I want something that reminds me things can get better..."
                maxLength={500}
                rows={3}
                className="sv-mood-input"
                aria-describedby="mood-help"
              />
              <div className="flex items-center justify-between gap-3 border-t border-white/[0.07] px-4 py-3 sm:px-5">
                <span id="mood-help" className="text-xs text-slate-500">{mood.length}/500 characters</span>
                <div className="flex items-center gap-2">
                  <VoiceInput onTranscript={handleVoiceTranscript} />
                  <button type="submit" disabled={loading || !mood.trim()} className="sv-analyze-button">
                    {loading ? <><span className="sv-spinner" /> Finding your story…</> : <>Find my story <span aria-hidden="true">↗</span></>}
                  </button>
                </div>
              </div>
            </div>
          </form>

          <div className="mt-5">
            <p className="mb-3 text-xs font-medium uppercase tracking-[0.16em] text-slate-500">Need a starting point?</p>
            <div className="flex flex-wrap gap-2">
              {starterMoods.map((starter) => (
                <button key={starter.tag} type="button" onClick={() => setMood(starter.label)} className="sv-prompt-chip">
                  <span>{starter.icon}</span>{starter.tag}
                </button>
              ))}
            </div>
          </div>

          <div className="mt-6 grid grid-cols-1 gap-3 border-t border-white/[0.07] pt-5 sm:grid-cols-2">
            <label className="flex flex-col gap-2 text-left text-xs font-medium text-slate-300">
              Discovery region
              <select value={region} onChange={(event) => setRegion(event.target.value)} className="rounded-xl border border-white/10 bg-[#10101d] px-3 py-3 text-sm text-white outline-none focus:border-violet-400/60">
                <option value="IN">India</option>
                <option value="US">United States</option>
                <option value="GB">United Kingdom</option>
                <option value="CA">Canada</option>
                <option value="AU">Australia</option>
                <option value="JP">Japan</option>
                <option value="KR">South Korea</option>
                <option value="GLOBAL">Global</option>
              </select>
            </label>
            <label className="flex flex-col gap-2 text-left text-xs font-medium text-slate-300">
              Original language
              <select value={language} onChange={(event) => setLanguage(event.target.value)} className="rounded-xl border border-white/10 bg-[#10101d] px-3 py-3 text-sm text-white outline-none focus:border-violet-400/60">
                <option value="all">Any language</option>
                <option value="hi">Hindi</option>
                <option value="ta">Tamil</option>
                <option value="te">Telugu</option>
                <option value="ml">Malayalam</option>
                <option value="kn">Kannada</option>
                <option value="bn">Bengali</option>
                <option value="mr">Marathi</option>
                <option value="pa">Punjabi</option>
                <option value="gu">Gujarati</option>
                <option value="en">English</option>
                <option value="ja">Japanese</option>
                <option value="ko">Korean</option>
              </select>
            </label>
            <p className="text-xs leading-5 text-slate-500 sm:col-span-2">Regional settings influence movie/TV discovery and supported book/podcast catalogues. Availability depends on each provider.</p>
          </div>
        </motion.div>

        <AnimatePresence>
          {errorMessage && (
            <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} role="alert" className="sv-error-banner mt-6 w-full max-w-3xl">
              <span className="sv-error-icon">!</span>
              <div className="flex-1">
                <p className="font-semibold text-rose-100">We couldn’t finish that request</p>
                <p className="mt-1 text-sm leading-6 text-rose-200/80">{errorMessage}</p>
              </div>
              <button type="button" onClick={() => void fetchRecommendations(mood)} disabled={loading || !mood.trim()} className="sv-retry-button">Retry</button>
            </motion.div>
          )}
        </AnimatePresence>

        {loading && (
          <div className="sv-loading-panel mt-8 w-full max-w-3xl" role="status">
            <span className="sv-loading-orbit">✳</span>
            <div>
              <p className="font-medium text-white">Tuning into your mood</p>
              <p className="mt-1 text-sm text-slate-400">Reading the feeling, searching stories, finding your match. First-time model loading can take a little while.</p>
            </div>
          </div>
        )}

        {!loading && detectedEmotions.length > 0 && (
          <div className="mt-10 w-full max-w-3xl">
            <div className="mb-4 flex items-end justify-between gap-4">
              <div><p className="sv-section-kicker">THE FEELING BEHIND THE WORDS</p><h2 className="mt-1 text-xl font-semibold">Your emotional signature</h2></div>
            </div>
            <EmotionVisualizer emotions={detectedEmotions} />
          </div>
        )}

        {!loading && results.length > 0 && (
          <section className="mt-12 w-full max-w-[1600px]" aria-live="polite">
            <div className="mb-6 flex flex-col justify-between gap-3 sm:flex-row sm:items-end">
              <div><p className="sv-section-kicker">CURATED FOR THIS MOMENT</p><h2 className="mt-1 text-2xl font-semibold tracking-tight sm:text-3xl">Your next favourite stories.</h2><p className="mt-2 text-sm text-slate-400">Picked for the mood you shared — not just a genre.</p></div>
              <div className="w-full sm:w-auto"><MediaFilters selectedFilters={filters} onChange={setFilters} /></div>
            </div>
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 sm:gap-4 lg:grid-cols-4 xl:grid-cols-5 2xl:grid-cols-6">
              {results.map((item, index) => <motion.div key={item.id} initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: index < 12 ? index * 0.025 : 0 }}><RecommendationCard item={item} onRefine={handleRefinement} /></motion.div>)}
            </div>
          </section>
        )}

        {!loading && hasSearched && !errorMessage && results.length === 0 && (
          <div className="sv-empty-state mt-10 w-full max-w-3xl" aria-live="polite">
            <span className="sv-empty-icon">✧</span>
            <div><h2 className="text-lg font-semibold text-white">We found your mood, but not a match yet.</h2><p className="mt-2 text-sm leading-6 text-slate-400">The recommendation library may still be warming up or needs its starter catalogue. Try again in a moment; if this keeps happening, check the backend logs.</p></div>
            <button type="button" onClick={() => void fetchRecommendations(mood)} className="sv-retry-button">Try again</button>
          </div>
        )}

        {!hasSearched && (
          <div className="mt-14 grid w-full max-w-4xl grid-cols-1 gap-3 sm:grid-cols-3">
            <div className="sv-value-card"><span className="sv-value-icon">01</span><div><p className="font-medium text-slate-100">Start with a feeling</p><p className="mt-1 text-sm leading-5 text-slate-500">No genres or complicated filters needed.</p></div></div>
            <div className="sv-value-card"><span className="sv-value-icon">02</span><div><p className="font-medium text-slate-100">Get thoughtful picks</p><p className="mt-1 text-sm leading-5 text-slate-500">Stories matched to your words and themes.</p></div></div>
            <div className="sv-value-card"><span className="sv-value-icon">03</span><div><p className="font-medium text-slate-100">Make it more you</p><p className="mt-1 text-sm leading-5 text-slate-500">Refine the results until they feel right.</p></div></div>
          </div>
        )}

        <footer className="mt-16 flex w-full max-w-4xl flex-col items-center justify-between gap-3 border-t border-white/[0.07] pt-6 text-xs text-slate-600 sm:flex-row">
          <span>✳ SentiVerse <span className="text-slate-700">·</span> Art for the way you feel.</span>
          <span>Your mood is personal. Your next story can be, too.</span>
        </footer>
      </section>
    </main>
  );
}
