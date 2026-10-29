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

const mediaArt: Record<string, { icon: string; caption: string; gradient: string }> = {
  movie: { icon: '▸', caption: 'A story on screen', gradient: 'from-indigo-500/20 via-violet-500/10 to-transparent' },
  anime: { icon: '✦', caption: 'An animated world', gradient: 'from-fuchsia-500/20 via-violet-500/10 to-transparent' },
  game: { icon: '⌘', caption: 'A world to step into', gradient: 'from-cyan-500/20 via-indigo-500/10 to-transparent' },
  novel: { icon: '▤', caption: 'A world between pages', gradient: 'from-amber-500/15 via-violet-500/10 to-transparent' },
  podcast: { icon: '♫', caption: 'A voice to keep you company', gradient: 'from-emerald-500/15 via-teal-500/10 to-transparent' },
};

export const RecommendationCard: React.FC<RecommendationProps> = ({ item, onRefine }) => {
  const [isRefining, setIsRefining] = useState(false);
  const [refineText, setRefineText] = useState('');
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
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -3 }}
      transition={{ duration: 0.22 }}
      className="group relative h-full overflow-hidden rounded-3xl border border-white/[0.09] bg-[#11111d]/90 p-5 shadow-[0_20px_70px_rgba(0,0,0,0.16)] transition-colors hover:border-violet-300/25 sm:p-6"
    >
      <div aria-hidden="true" className={`pointer-events-none absolute inset-x-0 top-0 h-36 bg-gradient-to-br ${art.gradient}`} />
      <div aria-hidden="true" className="pointer-events-none absolute -right-10 -top-16 h-40 w-40 rounded-full border border-white/[0.05]" />
      <div aria-hidden="true" className="pointer-events-none absolute -right-2 -top-8 h-24 w-24 rounded-full border border-white/[0.06]" />

      <div className="relative">
        <div className="flex items-center justify-between gap-3">
          <span className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-black/20 px-3 py-1.5 text-[10px] font-bold uppercase tracking-[0.15em] text-violet-200">
            <span className="text-sm">{art.icon}</span>{item.medium}
          </span>
          <span className="inline-flex items-center gap-1.5 rounded-full border border-emerald-300/15 bg-emerald-300/[0.07] px-3 py-1.5 text-xs font-semibold text-emerald-200">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-300" /> {item.confidence_score}% match
          </span>
        </div>

        <div className="mb-5 mt-7 flex items-end justify-between gap-3">
          <div>
            <p className="mb-2 text-[10px] font-semibold uppercase tracking-[0.16em] text-slate-500">{art.caption}</p>
            <h3 className="max-w-xl text-2xl font-semibold leading-tight tracking-[-0.035em] text-white transition-colors group-hover:text-violet-100 sm:text-[1.7rem]">{item.title}</h3>
          </div>
          <span aria-hidden="true" className="hidden text-4xl font-light text-white/15 sm:block">✳</span>
        </div>

        <div className="mb-5 flex flex-wrap gap-1.5">
          {item.themes.slice(0, 6).map((theme) => (
            <span key={theme} className="rounded-lg border border-white/[0.07] bg-white/[0.035] px-2.5 py-1 text-[11px] text-slate-300">{theme}</span>
          ))}
        </div>

        <div className="rounded-2xl border border-violet-200/[0.09] bg-black/20 p-4 sm:p-5">
          <div className="mb-2 flex items-center gap-2">
            <span className="grid h-6 w-6 place-items-center rounded-lg bg-violet-400/10 text-sm text-violet-200">✦</span>
            <p className="text-[10px] font-bold uppercase tracking-[0.16em] text-violet-200/80">Why it may resonate</p>
          </div>
          <p className="text-sm leading-6 text-slate-300">{item.ai_explanation}</p>
          <div className="mt-4 flex flex-wrap gap-x-4 gap-y-1 text-[11px] text-slate-500">
            <span>Tone <strong className="ml-1 font-medium capitalize text-slate-300">{item.tone}</strong></span>
            <span>Pacing <strong className="ml-1 font-medium capitalize text-slate-300">{item.pacing}</strong></span>
            <span>Ending <strong className="ml-1 font-medium capitalize text-slate-300">{item.ending_type}</strong></span>
          </div>
        </div>

        {validLinks.length > 0 && (
          <div className="mt-4 flex flex-wrap gap-2">
            {validLinks.map(([provider, link]) => (
              <a key={provider} href={link} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-2 rounded-xl border border-white/10 bg-white/[0.04] px-3 py-2 text-xs font-medium text-slate-200 transition-colors hover:border-violet-300/25 hover:bg-violet-300/[0.08]">
                Watch on {provider}<span aria-hidden="true" className="text-slate-500">↗</span>
              </a>
            ))}
          </div>
        )}

        <div className="mt-5 border-t border-white/[0.08] pt-4">
          <AnimatePresence mode="wait">
            {!isRefining ? (
              <motion.button
                key="refine-button"
                initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                type="button"
                onClick={() => setIsRefining(true)}
                className="flex w-full items-center justify-center gap-2 rounded-xl border border-white/[0.08] bg-white/[0.035] py-3 text-xs font-semibold text-slate-300 transition-all hover:border-violet-300/20 hover:bg-violet-300/[0.06] hover:text-white"
              >
                <span aria-hidden="true">⌁</span> Refine this recommendation
              </motion.button>
            ) : (
              <motion.form
                key="refine-form"
                initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} exit={{ opacity: 0, height: 0 }}
                onSubmit={handleRefineSubmit}
                className="flex flex-col gap-2 sm:flex-row"
              >
                <input
                  type="text"
                  autoFocus
                  value={refineText}
                  onChange={(event) => setRefineText(event.target.value)}
                  placeholder="Make it lighter, deeper, funnier…"
                  className="min-w-0 flex-1 rounded-xl border border-white/10 bg-black/30 px-3 py-2.5 text-sm text-white placeholder:text-slate-600 focus:border-violet-300/40 focus:outline-none"
                />
                <button type="submit" disabled={!refineText.trim()} className="rounded-xl bg-violet-600 px-4 py-2.5 text-xs font-semibold text-white transition-colors hover:bg-violet-500 disabled:opacity-50">Refine ↗</button>
                <button type="button" onClick={() => setIsRefining(false)} className="rounded-xl border border-white/10 px-3 py-2.5 text-xs text-slate-400 hover:text-white">Cancel</button>
              </motion.form>
            )}
          </AnimatePresence>
        </div>
      </div>
    </motion.article>
  );
};
