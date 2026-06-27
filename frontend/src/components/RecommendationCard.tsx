import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface RecommendationProps {
  item: {
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
  };
  onRefine: (title: string, context: string) => void;
}

export const RecommendationCard: React.FC<RecommendationProps> = ({ item, onRefine }) => {
  const [isRefining, setIsRefining] = useState(false);
  const [refineText, setRefineText] = useState('');

  const handleRefineSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!refineText.trim()) return;
    onRefine(item.title, refineText);
    setIsRefining(false);
    setRefineText('');
  };

  return (
    <motion.div
      variants={{
        hidden: { opacity: 0, y: 20 },
        visible: { opacity: 1, y: 0 }
      }}
      className="group relative rounded-2xl border border-white/10 bg-white/5 backdrop-blur-xl p-6 transition-all duration-300 hover:border-indigo-500/40 hover:bg-white/[0.07] flex flex-col"
    >
      {/* Upper Meta Bar */}
      <div className="flex items-center justify-between mb-4">
        <span className="px-3 py-1 rounded-full text-xs font-semibold tracking-wide bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 uppercase">
          {item.medium}
        </span>
        <div className="flex items-center space-x-1.5">
          <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span className="text-sm font-mono text-emerald-400 font-bold">{item.confidence_score}% Match</span>
        </div>
      </div>

      <h3 className="text-2xl font-bold tracking-tight text-white mb-2 group-hover:text-indigo-300 transition-colors">
        {item.title}
      </h3>

      <div className="flex flex-wrap gap-1.5 mb-4">
        {item.themes.map((theme, idx) => (
          <span key={idx} className="text-xs bg-slate-800/80 text-gray-300 px-2 py-0.5 rounded border border-gray-700/50">
            {theme}
          </span>
        ))}
      </div>

      <div className="rounded-xl bg-black/40 p-3.5 border border-white/[0.03] flex-grow mb-4">
        <p className="text-sm text-gray-400 leading-relaxed font-light">
          <span className="font-semibold text-indigo-400">AI Note: </span>
          {item.ai_explanation}
        </p>
      </div>

      {/* Streaming Links */}
      {item.streaming_links && Object.keys(item.streaming_links).length > 0 && (
        <div className="mb-4 flex flex-wrap gap-2">
          {Object.entries(item.streaming_links).map(([provider, link]) => (
            <a
              key={provider}
              href={link}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 text-xs font-medium text-gray-300 transition-colors"
            >
              Watch on {provider}
            </a>
          ))}
        </div>
      )}

      {/* Conversational Refinement UI */}
      <div className="border-t border-white/10 pt-4">
        <AnimatePresence mode="wait">
          {!isRefining ? (
            <motion.button
              key="btn"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsRefining(true)}
              className="w-full py-2 rounded-xl bg-white/5 hover:bg-white/10 border border-white/5 text-sm font-medium text-gray-400 hover:text-white transition-colors flex items-center justify-center gap-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" /></svg>
              Adjust Recommendation
            </motion.button>
          ) : (
            <motion.form
              key="form"
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              onSubmit={handleRefineSubmit}
              className="flex gap-2"
            >
              <input
                type="text"
                autoFocus
                value={refineText}
                onChange={(e) => setRefineText(e.target.value)}
                placeholder="e.g. Too dark, make it happier..."
                className="flex-1 bg-black/50 border border-white/10 rounded-xl px-4 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-indigo-500/50"
              />
              <button 
                type="submit"
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 rounded-xl text-sm font-medium transition-colors"
              >
                Send
              </button>
            </motion.form>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
};