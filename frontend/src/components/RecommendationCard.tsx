'use client';

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
    poster_url?: string | null;
    backdrop_url?: string | null;
    overview?: string | null;
    release_year?: string | null;
    vote_average?: number | null;
  };
  onRefine: (title: string, context: string) => void;
}

const mediaArt: Record<string, { icon: string; caption: string; gradient: string }> = {
  movie: { icon: '▶', caption: 'A story on screen', gradient: 'from-indigo-500/30 via-violet-500/20 to-slate-950' },
  tv: { icon: '▣', caption: 'A world to return to', gradient: 'from-fuchsia-500/30 via-violet-500/20 to-slate-950' },
  anime: { icon: '✦', caption: 'An animated world', gradient: 'from-fuchsia-500/30 via-violet-500/20 to-slate-950' },
  game: { icon: '⌘', caption: 'A world to step into', gradient: 'from-cyan-500/30 via-indigo-500/20 to-slate-950' },
  novel: { icon: '▤', caption: 'A world between pages', gradient: 'from-amber-500/25 via-violet-500/20 to-slate-950' },
  podcast: { icon: '♫', caption: 'A voice to keep you company', gradient: 'from-emerald-500/25 via-teal-500/20 to-slate-950' },
};

export const RecommendationCard: React.FC<RecommendationProps> = ({ item, onRefine }) => {
  const [isRefining, setIsRefining] = useState(false);
  const [refineText, setRefineText] = useState('');
  const [imageFailed, setImageFailed] = useState(false);
  const art = mediaArt[item.medium.toLowerCase()] || mediaArt.movie;

  const handleRefineSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!refineText.trim()) return;
    onRefine(item.title, refineText.trim());
    setIsRefining(false);
    setRefineText('');
  };

  const validLinks = Object.entries(item.streaming_links || {}).filter(([, link]) => {
    try {
      const url = new URL(link);
      return url.protocol === 'https:' || url.protocol === 'http:';
    } catch {
      return false;
    }
  });

  return (
    <motion.article
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -5 }}
      transition={{ duration: 0.24 }}
      className="group h-full overflow-hidden rounded-xl border border-white/[0.09] bg-[#11111d] shadow-[0_12px_35px_rgba(0,0,0,.22)] transition-colors hover:border-violet-300/30"
    >
      <div className="relative aspect-[2/3] overflow-hidden bg-gradient-to-br from-slate-800 via-violet-950 to-slate-950">
        {item.poster_url && !imageFailed ? (
          <img
            src={item.poster_url}
            alt={`${item.title} poster`}
            loading="lazy"
            onError={() => setImageFailed(true)}
            className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-[1.04]"
          />
        ) : (
          <div className={`absolute inset-0 grid place-items-center bg-gradient-to-br ${art.gradient}`}>
            <div className="text-center">
              <span className="text-6xl text-white/70">{art.icon}</span>
              <p className="mt-3 px-5 text-lg font-semibold text-white/90">{item.title}</p>
            </div>
          </div>
        )}
        <div className="absolute inset-0 bg-gradient-to-t from-[#090912] via-transparent to-black/25" />
        <div className="absolute left-3 top-3 flex flex-wrap gap-2">
          <span className="rounded-md border border-white/15 bg-black/65 px-2.5 py-1.5 text-[10px] font-bold uppercase tracking-[.14em] text-white backdrop-blur">{item.medium}</span>
          {item.release_year && <span className="rounded-md bg-black/60 px-2.5 py-1.5 text-xs text-white/90 backdrop-blur">{item.release_year}</span>}
        </div>
        <div className="absolute right-3 top-3 rounded-md border border-emerald-200/20 bg-emerald-950/75 px-2 py-1.5 text-xs font-bold text-emerald-200 backdrop-blur">
          ★ {item.vote_average ? item.vote_average.toFixed(1) : `${item.confidence_score}%`}
        </div>
        <div className="absolute inset-x-0 bottom-0 p-4 sm:p-5">
          <p className="mb-2 text-[10px] font-bold uppercase tracking-[.18em] text-violet-200">{art.caption}</p>
          <h3 className="text-base font-bold leading-tight tracking-tight text-white drop-shadow sm:text-lg">{item.title}</h3>
          <div className="mt-3 flex items-center gap-2 text-xs text-white/80">
            <span className="rounded bg-violet-500 px-2 py-1 font-bold text-white">{item.confidence_score}% match</span>
            <span>Picked for your mood</span>
          </div>
        </div>
      </div>

      <div className="space-y-3 p-3">
        {(item.overview || item.ai_explanation) && (
          <p className="line-clamp-3 text-xs leading-5 text-slate-300">{item.overview || item.ai_explanation}</p>
        )}
        {item.themes.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {item.themes.slice(0, 4).map((theme) => (
              <span key={theme} className="rounded-md border border-white/[0.08] bg-white/[0.035] px-2 py-1 text-[10px] text-slate-300">{theme}</span>
            ))}
          </div>
        )}
        <div className="rounded-lg border border-violet-200/[0.09] bg-violet-300/[0.04] p-3">
          <p className="mb-1.5 text-[10px] font-bold uppercase tracking-[.16em] text-violet-200">✦ Why it fits</p>
          <p className="line-clamp-3 text-xs leading-5 text-slate-300">{item.ai_explanation}</p>
          <div className="mt-3 flex flex-wrap gap-x-3 gap-y-1 text-[10px] text-slate-500">
            <span>Tone <strong className="capitalize text-slate-300">{item.tone}</strong></span>
            <span>Pacing <strong className="capitalize text-slate-300">{item.pacing}</strong></span>
          </div>
        </div>
        {validLinks.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {validLinks.map(([provider, link]) => (
              <a key={provider} href={link} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-2 rounded-lg bg-white px-3 py-2 text-xs font-bold text-slate-950 transition hover:bg-violet-100">
                View on {provider} <span aria-hidden="true">↗</span>
              </a>
            ))}
          </div>
        )}
        <div className="border-t border-white/[0.08] pt-3">
          <AnimatePresence mode="wait">
            {!isRefining ? (
              <motion.button key="refine-button" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} type="button" onClick={() => setIsRefining(true)} className="w-full rounded-lg border border-white/10 bg-white/[0.035] py-2.5 text-xs font-semibold text-slate-300 transition hover:border-violet-300/30 hover:text-white">
                ↗ Refine this pick
              </motion.button>
            ) : (
              <motion.form key="refine-form" initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} exit={{ opacity: 0, height: 0 }} onSubmit={handleRefineSubmit} className="flex flex-col gap-2">
                <input autoFocus value={refineText} onChange={(event) => setRefineText(event.target.value)} placeholder="More hopeful, less intense…" className="min-w-0 rounded-lg border border-white/10 bg-black/30 px-3 py-2.5 text-sm text-white placeholder:text-slate-600 focus:border-violet-300/40 focus:outline-none" />
                <div className="flex gap-2">
                  <button type="submit" disabled={!refineText.trim()} className="flex-1 rounded-lg bg-violet-600 px-3 py-2.5 text-xs font-bold text-white hover:bg-violet-500 disabled:opacity-50">Refine ↗</button>
                  <button type="button" onClick={() => setIsRefining(false)} className="rounded-lg border border-white/10 px-3 py-2.5 text-xs text-slate-400 hover:text-white">Cancel</button>
                </div>
              </motion.form>
            )}
          </AnimatePresence>
        </div>
      </div>
    </motion.article>
  );
};
