import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { v4 as uuidv4 } from 'uuid';

interface EmotionEntry {
  mood: string;
  timestamp: string;
  topEmotions: { label: string; score: number }[];
}

interface AppState {
  sessionId: string;
  moodHistory: EmotionEntry[];
  addToHistory: (entry: EmotionEntry) => void;
  clearHistory: () => void;
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      sessionId: uuidv4(), // Generates a unique ID on initial load
      moodHistory: [],
      addToHistory: (entry) => 
        set((state) => ({ 
          // Keep only the last 50 queries to prevent LocalStorage bloat
          moodHistory: [entry, ...state.moodHistory].slice(0, 50) 
        })),
      clearHistory: () => set({ moodHistory: [] }),
    }),
    {
      name: 'sentiverse-session-storage',
    }
  )
);