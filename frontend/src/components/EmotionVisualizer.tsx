import React from 'react';
import { motion } from 'framer-motion';

export interface Emotion {
  label: string;
  score: number;
}

interface EmotionVisualizerProps {
  emotions: Emotion[];
}

// Predefined semantic colors for common emotions
const semanticColors: Record<string, string> = {
  sadness: '#3b82f6', // blue-500
  joy: '#facc15',     // yellow-400
  anger: '#ef4444',   // red-500
  fear: '#9333ea',    // purple-600
  surprise: '#f472b6',// pink-400
  love: '#f43f5e',    // rose-500
  neutral: '#9ca3af', // gray-400
  nostalgia: '#818cf8',// indigo-400
  optimism: '#34d399',// emerald-400
};

// Deterministic string-to-hex generator for unexpected AI outputs
const stringToHexColor = (str: string): string => {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = str.charCodeAt(i) + ((hash << 5) - hash);
  }
  let color = '#';
  for (let i = 0; i < 3; i++) {
    // Generate a vibrant variation by enforcing a minimum brightness (128)
    const value = (hash >> (i * 8)) & 0xff;
    const vibrantValue = Math.max(128, value); 
    color += ('00' + vibrantValue.toString(16)).substr(-2);
  }
  return color;
};

export const EmotionVisualizer: React.FC<EmotionVisualizerProps> = ({ emotions }) => {
  if (!emotions || emotions.length === 0) return null;

  return (
    <motion.div 
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="w-full max-w-2xl mx-auto mb-12 p-6 rounded-3xl bg-white/5 border border-white/10 backdrop-blur-md"
    >
      <h4 className="text-sm font-mono text-gray-400 mb-4 uppercase tracking-widest text-center">
        Detected Emotional Signature
      </h4>
      <div className="flex flex-col space-y-4">
        {emotions.map((emotion, index) => {
          const percentage = Math.round(emotion.score * 100);
          const normalizedLabel = emotion.label.toLowerCase();
          const barColor = semanticColors[normalizedLabel] || stringToHexColor(normalizedLabel);

          return (
            <div key={emotion.label} className="relative w-full group">
              <div className="flex justify-between text-sm mb-1">
                <span className="font-semibold text-white capitalize">{emotion.label}</span>
                <span className="text-gray-400 font-mono">{percentage}%</span>
              </div>
              <div className="w-full h-2 bg-black/40 rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${percentage}%` }}
                  transition={{ duration: 1, delay: index * 0.15, ease: "easeOut" }}
                  className="h-full rounded-full shadow-[0_0_10px_currentColor] transition-opacity group-hover:opacity-100 opacity-90"
                  style={{ backgroundColor: barColor, color: barColor }} 
                />
              </div>
            </div>
          );
        })}
      </div>
    </motion.div>
  );
};