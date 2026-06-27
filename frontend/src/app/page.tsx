'use client';

import React, { useState, useEffect } from 'react';
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
}

export default function Home() {
  const [isMounted, setIsMounted] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const posthog = usePostHog(); // GROWTH ANALYTICS

  useEffect(() => setIsMounted(true), []);

  const sessionId = useAppStore((state) => state.sessionId);
  const addToHistory = useAppStore((state) => state.addToHistory);

  const [mood, setMood] = useState('');
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState<string[]>([]);
  const [results, setResults] = useState<RecommendationData[]>([]);
  const [detectedEmotions, setDetectedEmotions] = useState<Emotion[]>([]);

  const fetchRecommendations = async (searchQuery: string) => {
    setLoading(true);
    setResults([]); 
    setDetectedEmotions([]);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || '';
      const response = await fetch(`${apiUrl}/api/v1/recommend`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          query: searchQuery, 
          limit: 4, 
          session_id: sessionId,
          medium_filters: filters 
        })
      });

      if (!response.ok) throw new Error(`API Error: ${response.status}`);

      const data = await response.json();
      
      setResults(data.recommendations || []);
      setDetectedEmotions(data.detected_emotions || []);
      
      addToHistory({
        mood: searchQuery,
        timestamp: new Date().toISOString(),
        topEmotions: data.detected_emotions || []
      });
    } catch (error) {
      console.error("Pipeline Search Error:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (!mood.trim()) return;
    
    // GROWTH ANALYTICS: Track what users are feeling
    posthog?.capture('mood_searched', {
      mood: mood,
      filters: filters,
    });

    fetchRecommendations(mood);
  };

  const handleRefinement = (title: string, refinementContext: string) => {
    const refinedQuery = `${mood}. But specifically regarding ${title}: ${refinementContext}`;
    
    // GROWTH ANALYTICS: Track how users refine their results
    posthog?.capture('mood_refined', {
      original_mood: mood,
      title: title,
      refinement: refinementContext
    });

    setMood(refinedQuery); 
    fetchRecommendations(refinedQuery);
  };

  if (!isMounted) return null;

  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-950 via-slate-900 to-black text-white px-4 py-12 md:p-24 relative overflow-x-hidden flex flex-col items-center">
      {/* Navbar / Tool Bar */}
      <div className="absolute top-6 right-6 z-20">
        <button 
          onClick={() => setIsSidebarOpen(true)}
          className="flex items-center gap-2 px-4 py-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-full text-sm font-medium transition-all backdrop-blur-md shadow-lg"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
          Mood Journal
        </button>
      </div>

      <MoodJournalSidebar isOpen={isSidebarOpen} onClose={() => setIsSidebarOpen(false)} />

      {/* Ambient Orbs */}
      <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-indigo-600/10 rounded-full blur-[160px] pointer-events-none" />
      <div className="absolute bottom-10 right-1/4 w-[500px] h-[500px] bg-purple-600/10 rounded-full blur-[160px] pointer-events-none" />

      {/* Hero Section */}
      <motion.div 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center w-full max-w-3xl mb-12 z-10"
      >
        <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight mb-4 bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 via-violet-400 to-purple-400">
          SentiVerse
        </h1>
        <p className="text-lg md:text-xl text-gray-400 font-light">
          Describe your exact state of mind. We will find the art that matches it.
        </p>
      </motion.div>

      {/* Search Input & Filters Area */}
      <div className="w-full max-w-2xl z-10 mb-12">
        <MediaFilters selectedFilters={filters} onChange={setFilters} />
        
        <form onSubmit={handleSearch} className="relative w-full flex items-center">
          <input 
            type="text"
            value={mood}
            onChange={(e) => setMood(e.target.value)}
            placeholder="I feel utterly heartbroken but I want to find hope..."
            className="w-full pl-6 pr-40 py-5 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500/50 shadow-2xl transition-all text-base md:text-lg"
          />
          
          <VoiceInput onTranscript={(text) => setMood(text)} />

          <button 
            type="submit"
            disabled={loading}
            className="absolute right-3 top-3 bottom-3 px-6 bg-indigo-600 hover:bg-indigo-500 active:scale-95 rounded-xl font-medium tracking-wide transition-all disabled:opacity-50 flex items-center justify-center min-w-[120px]"
          >
            {loading ? (
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                <span>Sensing</span>
              </div>
            ) : 'Analyze'}
          </button>
        </form>
      </div>

      <AnimatePresence mode="wait">
        {detectedEmotions.length > 0 && !loading && (
          <motion.div
            key="emotion-visualizer"
            initial={{ opacity: 0, height: 0, marginBottom: 0 }}
            animate={{ opacity: 1, height: 'auto', marginBottom: 48 }}
            exit={{ opacity: 0, height: 0, marginBottom: 0 }}
            className="w-full max-w-2xl z-10 overflow-hidden"
          >
            <EmotionVisualizer emotions={detectedEmotions} />
          </motion.div>
        )}
      </AnimatePresence>

      <div className="w-full max-w-6xl z-10">
        <AnimatePresence mode="wait">
          {results.length > 0 && !loading && (
            <motion.div
              key="results-grid"
              initial="hidden"
              animate="visible"
              exit={{ opacity: 0 }}
              variants={{ visible: { transition: { staggerChildren: 0.1 } } }}
              className="grid grid-cols-1 md:grid-cols-2 gap-6"
            >
              {results.map((item) => (
                <RecommendationCard 
                  key={item.id} 
                  item={item} 
                  onRefine={handleRefinement} 
                />
              ))}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </main>
  );
}