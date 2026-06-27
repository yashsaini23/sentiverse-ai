import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

// Declare global types to satisfy the TypeScript compiler
declare global {
  interface Window {
    SpeechRecognition: any;
    webkitSpeechRecognition: any;
  }
}

interface VoiceInputProps {
  onTranscript: (text: string) => void;
}

export const VoiceInput: React.FC<VoiceInputProps> = ({ onTranscript }) => {
  const [isListening, setIsListening] = useState(false);
  const [recognition, setRecognition] = useState<any>(null);

  useEffect(() => {
    // Initialize Web Speech API safely
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (SpeechRecognition) {
      const rec = new SpeechRecognition();
      rec.continuous = false;
      rec.interimResults = false;
      rec.lang = 'en-US';

      rec.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        onTranscript(transcript);
        setIsListening(false);
      };

      rec.onerror = (event: any) => {
        console.error("Speech recognition error", event.error);
        setIsListening(false);
      };

      rec.onend = () => setIsListening(false);
      setRecognition(rec);
    }
  }, [onTranscript]);

  const toggleListen = () => {
    if (isListening) {
      recognition?.stop();
      setIsListening(false);
    } else {
      recognition?.start();
      setIsListening(true);
    }
  };

  if (!recognition) return null; // Fallback if browser doesn't support Voice

  return (
    <motion.button
      type="button"
      onClick={toggleListen}
      whileTap={{ scale: 0.9 }}
      className={`absolute right-36 top-3 bottom-3 px-4 rounded-xl flex items-center justify-center transition-all ${
        isListening 
          ? 'bg-red-500/20 text-red-400 border border-red-500/50' 
          : 'bg-white/5 text-gray-400 hover:text-white border border-transparent'
      }`}
    >
      {isListening ? (
        <span className="flex items-center gap-2">
          <motion.div animate={{ opacity: [1, 0.5, 1] }} transition={{ repeat: Infinity }} className="w-2 h-2 rounded-full bg-red-400" />
          Listening...
        </span>
      ) : (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
        </svg>
      )}
    </motion.button>
  );
};