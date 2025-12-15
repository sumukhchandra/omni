import React, { useState, useEffect } from 'react';
import { Sparkles, ArrowRight, Mic, MicOff } from 'lucide-react';
import useSpeechRecognition from '../src/hooks/useSpeechRecognition';

interface WelcomeScreenProps {
  onStartChat: (message: string) => void;
}

const WelcomeScreen: React.FC<WelcomeScreenProps> = ({ onStartChat }) => {
  const [input, setInput] = useState('');
  const { isListening, transcript, startListening, resetTranscript } = useSpeechRecognition();

  useEffect(() => {
    if (transcript) {
      const finalMessage = input + (input ? ' ' : '') + transcript;
      onStartChat(finalMessage);
      resetTranscript();
    }
  }, [transcript, resetTranscript, input, onStartChat]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim()) {
      onStartChat(input);
    }
  };

  const suggestions = [
    "Plan a healthy meal prep for next week",
    "Explain quantum computing like I'm 5",
    "Draft an email to a client about a delay",
    "Brainstorm names for a new coffee shop"
  ];

  return (
    <div className="flex-1 h-full flex flex-col items-center justify-center p-4 overflow-y-auto bg-transparent relative z-10">
      <div className="w-full max-w-2xl flex flex-col items-center text-center space-y-8 animate-fade-in-up">

        {/* Hero Icon */}
        <div className="w-16 h-16 bg-gradient-to-tr from-brand-500 to-brand-300 rounded-2xl shadow-lg flex items-center justify-center transform rotate-3 hover:rotate-6 transition-transform duration-300">
          <Sparkles className="w-8 h-8 text-white" />
        </div>

        {/* Headlines */}
        <div className="space-y-4">
          <h1 className="text-4xl md:text-5xl font-bold text-slate-900 dark:text-white tracking-tight">
            What are your <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand-600 to-brand-400">thoughts</span> or <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand-600 to-brand-400">ideas</span>?
          </h1>
          <p className="text-lg text-slate-500 max-w-lg mx-auto leading-relaxed">
            I'm here to help you brainstorm, organize, and create.
            Just start typing to begin your journey.
          </p>
        </div>

        {/* Input Area */}
        <div className="w-full max-w-xl">
          <form onSubmit={handleSubmit} className="relative group">
            <div className="absolute -inset-1 bg-gradient-to-r from-brand-300 to-brand-400 rounded-2xl blur opacity-20 group-hover:opacity-40 transition duration-500"></div>
            <div className="relative flex items-center bg-white dark:bg-slate-800 rounded-xl shadow-xl shadow-brand-100/50 dark:shadow-none border border-slate-100 dark:border-slate-700 overflow-hidden">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Type your idea here..."
                className="w-full p-5 text-lg text-slate-800 dark:text-white placeholder:text-slate-400 dark:placeholder:text-slate-500 bg-transparent focus:outline-none"
                autoFocus
              />
              <button
                type="button"
                onClick={startListening}
                className={`mr-2 p-3 rounded-lg transition-colors ${isListening
                  ? 'bg-red-500 text-white animate-pulse'
                  : 'text-slate-400 hover:text-brand-600'
                  }`}
              >
                {isListening ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
              </button>
              <button
                type="submit"
                disabled={!input.trim()}
                className="mr-2 p-3 bg-brand-600 hover:bg-brand-700 disabled:bg-slate-200 disabled:cursor-not-allowed text-white rounded-lg transition-colors duration-200"
              >
                <ArrowRight className="w-5 h-5" />
              </button>
            </div>
          </form>
        </div>

        {/* Suggestions */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full max-w-2xl mt-8 opacity-0 animate-[fadeIn_0.5s_ease-out_0.5s_forwards]">
          {suggestions.map((s, i) => (
            <button
              key={i}
              onClick={() => onStartChat(s)}
              className="text-sm text-left p-3 rounded-lg border border-slate-200 dark:border-slate-700 bg-white/60 dark:bg-slate-800/60 hover:bg-white dark:hover:bg-slate-800 hover:border-brand-200 dark:hover:border-slate-600 hover:shadow-md hover:shadow-brand-100/50 dark:hover:shadow-none text-slate-600 dark:text-slate-400 dark:hover:text-slate-200 transition-all duration-200"
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </div>
  );
};

export default WelcomeScreen;
