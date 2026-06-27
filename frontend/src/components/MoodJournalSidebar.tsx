import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAppStore } from '@/store/useAppStore';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

export const MoodJournalSidebar: React.FC<SidebarProps> = ({ isOpen, onClose }) => {
  const { moodHistory, clearHistory } = useAppStore();

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40"
          />

          {/* Sliding Sidebar */}
          <motion.div 
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', bounce: 0, duration: 0.4 }}
            className="fixed right-0 top-0 bottom-0 w-full max-w-md bg-gray-900 border-l border-white/10 shadow-2xl z-50 flex flex-col"
          >
            <div className="p-6 border-b border-white/10 flex justify-between items-center bg-black/20">
              <h2 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 to-purple-400">
                Mood Journal
              </h2>
              <button 
                onClick={onClose}
                className="p-2 rounded-full hover:bg-white/10 text-gray-400 hover:text-white transition-colors"
              >
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-6 space-y-6">
              {moodHistory.length === 0 ? (
                <div className="text-center text-gray-500 mt-10">
                  <p>Your journal is empty.</p>
                  <p className="text-sm mt-2">Search for something to record your mood.</p>
                </div>
              ) : (
                moodHistory.map((entry, idx) => {
                  const date = new Date(entry.timestamp);
                  const topEmotion = entry.topEmotions[0]?.label || "Complex";
                  
                  return (
                    <motion.div 
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: idx * 0.05 }}
                      key={idx} 
                      className="p-4 rounded-2xl bg-white/5 border border-white/5"
                    >
                      <div className="text-xs text-gray-500 mb-2 font-mono">
                        {date.toLocaleDateString()} at {date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                      </div>
                      <p className="text-gray-200 mb-3 italic">"{entry.mood}"</p>
                      <div className="flex items-center gap-2">
                        <span className="text-xs px-2 py-1 rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 capitalize">
                          Primary: {topEmotion}
                        </span>
                      </div>
                    </motion.div>
                  );
                })
              )}
            </div>

            {moodHistory.length > 0 && (
              <div className="p-6 border-t border-white/10 bg-black/20">
                <button 
                  onClick={clearHistory}
                  className="w-full py-3 rounded-xl border border-red-500/30 text-red-400 hover:bg-red-500/10 transition-colors font-medium text-sm"
                >
                  Clear History
                </button>
              </div>
            )}
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};