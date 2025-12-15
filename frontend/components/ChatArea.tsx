import React, { useRef, useEffect, useState } from 'react';
import { Send, Bot, User as UserIcon, Loader2, RotateCcw, Mic, MicOff } from 'lucide-react';
import { Message } from '../types';
import useSpeechRecognition from '../src/hooks/useSpeechRecognition';

interface ChatAreaProps {
  messages: Message[];
  isLoading: boolean;
  onSendMessage: (text: string) => void;
}

const ChatArea: React.FC<ChatAreaProps> = ({ messages, isLoading, onSendMessage }) => {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { isListening, transcript, startListening, resetTranscript } = useSpeechRecognition();

  useEffect(() => {
    if (transcript) {
      const finalMessage = input + (input ? ' ' : '') + transcript;
      onSendMessage(finalMessage);
      setInput('');
      resetTranscript();
    }
  }, [transcript, resetTranscript, input, onSendMessage]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !isLoading) {
      onSendMessage(input);
      setInput('');
    }
  };

  return (
    <div className="flex-1 flex flex-col h-full bg-white dark:bg-slate-900 relative">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 md:p-8 space-y-6">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex items-start gap-4 max-w-4xl mx-auto ${msg.role === 'user' ? 'justify-end' : ''}`}
          >
            {msg.role === 'model' && (
              <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-brand-500 to-brand-400 flex items-center justify-center text-white shrink-0 shadow-sm mt-1">
                <Bot className="w-5 h-5" />
              </div>
            )}

            <div
              className={`relative px-5 py-3.5 rounded-2xl text-sm md:text-base leading-relaxed shadow-sm max-w-[85%] sm:max-w-[75%] ${msg.role === 'user'
                ? 'bg-brand-600 text-white rounded-br-sm'
                : 'bg-slate-50 dark:bg-slate-800 border border-slate-100 dark:border-slate-700/50 text-slate-800 dark:text-slate-200 rounded-bl-sm'
                }`}
            >
              <div className="whitespace-pre-wrap">{msg.text}</div>
            </div>

            {msg.role === 'user' && (
              <div className="w-8 h-8 rounded-full bg-slate-200 dark:bg-slate-700 flex items-center justify-center text-slate-500 dark:text-slate-300 shrink-0 mt-1">
                <UserIcon className="w-5 h-5" />
              </div>
            )}
          </div>
        ))}

        {isLoading && (
          <div className="flex items-start gap-4 max-w-4xl mx-auto">
            <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-brand-500 to-brand-400 flex items-center justify-center text-white shrink-0 shadow-sm mt-1">
              <Bot className="w-5 h-5" />
            </div>
            <div className="bg-slate-50 border border-slate-100 rounded-2xl rounded-bl-sm px-5 py-4 shadow-sm">
              <div className="flex space-x-2">
                <div className="w-2 h-2 bg-brand-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                <div className="w-2 h-2 bg-brand-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                <div className="w-2 h-2 bg-brand-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 bg-white dark:bg-slate-900 border-t border-slate-100 dark:border-slate-800">
        <div className="max-w-4xl mx-auto">
          <form onSubmit={handleSubmit} className="relative flex items-center">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type a message..."
              disabled={isLoading}
              className="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-800 dark:text-white rounded-xl px-4 py-3.5 pr-12 focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 transition-all placeholder:text-slate-400 dark:placeholder:text-slate-500"
            />
            <button
              type="button"
              onClick={startListening}
              className={`absolute right-12 p-2 rounded-lg transition-colors ${isListening
                ? 'bg-red-500 text-white animate-pulse'
                : 'text-slate-400 hover:text-brand-600'
                }`}
            >
              {isListening ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
            </button>
            <button
              type="submit"
              disabled={!input.trim() || isLoading}
              className="absolute right-2 p-2 bg-brand-600 text-white rounded-lg hover:bg-brand-700 disabled:bg-slate-300 disabled:cursor-not-allowed transition-colors"
            >
              {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
            </button>
          </form>
          <div className="text-center mt-2">
            <p className="text-xs text-slate-400">
              BlueMind AI can make mistakes. Verify important information.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatArea;
