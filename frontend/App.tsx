import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import WelcomeScreen from './components/WelcomeScreen';
import ChatArea from './components/ChatArea';
import LoginModal from './components/LoginModal';
import SettingsModal from './components/SettingsModal';
import CrystalBackground from './components/CrystalBackground';
import { User, ChatSession, Message } from './types';
import { generateResponseStream, generateTitle } from './services/geminiService';
import { LogIn, Menu } from 'lucide-react';
import { defaultThemeId, ThemeId } from './src/themes';

const App: React.FC = () => {
  // --- State ---
  const [user, setUser] = useState<User | null>(null);
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);

  // Auth State
  const [isAuthOpen, setIsAuthOpen] = useState(false);
  const [authMode, setAuthMode] = useState<'login' | 'signup'>('login');

  // Settings & Theme State
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [theme, setTheme] = useState<'light' | 'dark'>('dark');
  const [currentThemeId, setCurrentThemeId] = useState<ThemeId>(defaultThemeId);

  useEffect(() => {
    // Check local storage or system preference
    const savedTheme = localStorage.getItem('theme') as 'light' | 'dark' | null;
    if (savedTheme) {
      setTheme(savedTheme);
    } else {
      // Default to dark if no preference saved
      setTheme('dark');
    }
  }, []);

  useEffect(() => {
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
    localStorage.setItem('theme', theme);
  }, [theme]);

  // Sidebar State (Unified for mobile/desktop toggle)
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [streamingMessageId, setStreamingMessageId] = useState<string | null>(null);
  // Voice Agent State (Global to prevent excessive greeting on remounts)
  const [hasGreeted, setHasGreeted] = useState(false);

  // --- Derived State ---
  const currentSession = sessions.find(s => s.id === currentSessionId);
  const isWelcome = !currentSessionId;

  // --- Handlers ---

  const handleLogin = (newUser: User) => {
    setUser(newUser);
    // In a real app, fetch sessions here
    // For demo, we might merge guest sessions or just keep them
  };

  const handleLogout = () => {
    setUser(null);
    setCurrentSessionId(null);
    // In a real app, clear sessions
    setSessions([]);
  };

  const openAuth = (mode: 'login' | 'signup') => {
    setAuthMode(mode);
    setIsAuthOpen(true);
  };

  const createNewSession = (initialMessage?: string) => {
    const newSession: ChatSession = {
      id: Date.now().toString(),
      title: initialMessage ? initialMessage.slice(0, 30) + '...' : 'New Idea',
      messages: [],
      updatedAt: Date.now(),
    };
    setSessions(prev => [newSession, ...prev]);
    setCurrentSessionId(newSession.id);
    return newSession;
  };

  const updateSessionTitle = async (sessionId: string, firstMessage: string) => {
    const title = await generateTitle(firstMessage);
    setSessions(prev => prev.map(s => s.id === sessionId ? { ...s, title } : s));
  };

  const handleSendMessage = async (text: string) => {
    let session = currentSession;
    let isNew = false;

    if (!session) {
      session = createNewSession(text);
      isNew = true;
    }

    // Add user message
    const userMsg: Message = {
      id: Date.now().toString(),
      role: 'user',
      text,
      timestamp: Date.now()
    };

    // Optimistically update UI
    setSessions(prev => prev.map(s => {
      if (s.id === session!.id) {
        return {
          ...s,
          messages: [...s.messages, userMsg],
          updatedAt: Date.now()
        };
      }
      return s;
    }));

    // If it's a new session, try to generate a better title in background
    if (isNew) {
      updateSessionTitle(session.id, text);
    }

    // Prepare for streaming response
    const botMsgId = (Date.now() + 1).toString();
    setStreamingMessageId(botMsgId);

    // Initial bot message placeholder
    const botMsg: Message = {
      id: botMsgId,
      role: 'model',
      text: '', // Start empty
      timestamp: Date.now()
    };

    setSessions(prev => prev.map(s => {
      if (s.id === session!.id) {
        return { ...s, messages: [...s.messages, botMsg] };
      }
      return s;
    }));

    try {
      // Get history for context (exclude the message we just added manually as the prompt is passed separately usually, 
      // but generateResponseStream expects history. We need to pass previous messages.)
      // The service logic: prompt is sent as 'message', history is the context.
      const history = session.messages.map(m => ({
        role: m.role,
        parts: [{ text: m.text }]
      }));

      const stream = await generateResponseStream(text, history);

      let fullText = '';

      for await (const chunk of stream) {
        const chunkText = chunk.text();
        fullText += chunkText;

        // Update the specific message in state
        setSessions(prev => prev.map(s => {
          if (s.id === session!.id) {
            return {
              ...s,
              messages: s.messages.map(m =>
                m.id === botMsgId ? { ...m, text: fullText } : m
              )
            };
          }
          return s;
        }));
      }
    } catch (error) {
      console.error("Error generating response:", error);
      setSessions(prev => prev.map(s => {
        if (s.id === session!.id) {
          return {
            ...s,
            messages: s.messages.map(m =>
              m.id === botMsgId ? { ...m, text: "I'm sorry, I encountered an error. Please check your API key or connection." } : m
            )
          };
        }
        return s;
      }));
    } finally {
      setStreamingMessageId(null);
    }
  };

  return (
    <div className="flex h-screen bg-white dark:bg-slate-900 overflow-hidden font-sans transition-colors duration-200">
      <CrystalBackground theme={theme} themeId={currentThemeId} />
      {/* Mobile Overlay */}
      <div
        className={`${isSidebarOpen ? 'fixed inset-0 z-40 bg-black/20 md:hidden' : 'hidden'}`}
        onClick={() => setIsSidebarOpen(false)}
      />

      {/* Sidebar Container */}
      <div className={`
        fixed inset-y-0 left-0 z-50 w-64 bg-white transform transition-transform duration-300 ease-in-out
        ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full'}
        md:relative md:translate-x-0 
        ${isSidebarOpen ? 'md:w-1/4 md:min-w-[280px]' : 'md:w-0 md:hidden'} 
      `}>
        <Sidebar
          user={user}
          sessions={sessions}
          currentSessionId={currentSessionId}
          onSelectSession={(id) => {
            setCurrentSessionId(id);
            // On mobile, close sidebar after selection
            if (window.innerWidth < 768) {
              setIsSidebarOpen(false);
            }
          }}
          onNewChat={() => {
            setCurrentSessionId(null);
            if (window.innerWidth < 768) {
              setIsSidebarOpen(false);
            }
          }}
          onLogout={handleLogout}
          onClose={() => setIsSidebarOpen(false)}
          onOpenSettings={() => setIsSettingsOpen(true)}
        />
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col relative min-w-0">

        {/* Top Header Layer (Login/Menu) */}
        <div className="absolute top-0 left-0 right-0 p-4 flex justify-between items-center z-20 pointer-events-none bg-gradient-to-b from-white/90 via-white/50 to-transparent dark:from-slate-900/90 dark:via-slate-900/50 h-24">
          {/* Menu Toggle Button - Visible on mobile, OR on desktop if sidebar is closed */}
          <button
            onClick={() => setIsSidebarOpen(true)}
            className={`
              pointer-events-auto p-2 rounded-lg bg-white/80 backdrop-blur text-slate-600 shadow-sm border border-slate-200 hover:bg-white hover:text-brand-600 transition-colors
              ${isSidebarOpen ? 'md:hidden' : 'block'} 
            `}
          >
            <Menu className="w-5 h-5" />
          </button>

          {/* Login/Signup Buttons - Top Right */}
          {!user && (
            <div className="ml-auto pointer-events-auto flex items-center gap-2">
              <button
                onClick={() => openAuth('login')}
                className="px-5 py-2.5 bg-white/80 backdrop-blur hover:bg-slate-50 text-slate-700 font-medium rounded-full transition-all duration-300"
              >
                Log in
              </button>
              <button
                onClick={() => openAuth('signup')}
                className="px-5 py-2.5 bg-brand-600 hover:bg-brand-700 text-white font-medium rounded-full shadow-md shadow-brand-500/20 transition-all duration-300"
              >
                Sign up
              </button>
            </div>
          )}
        </div>

        {/* Content View Switcher */}
        {currentSessionId && currentSession ? (
          <ChatArea
            messages={currentSession.messages}
            isLoading={!!streamingMessageId}
            onSendMessage={handleSendMessage}
            user={user}
            hasGreeted={hasGreeted}
            setHasGreeted={setHasGreeted}
          />
        ) : (
          <WelcomeScreen onStartChat={handleSendMessage} />
        )}
      </div>

      {/* Auth Modal */}
      <LoginModal
        isOpen={isAuthOpen}
        initialMode={authMode}
        onClose={() => setIsAuthOpen(false)}
        onLogin={handleLogin}
      />

      {/* Settings Modal */}
      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        theme={theme}
        onThemeChange={setTheme}
        currentThemeId={currentThemeId}
        onThemeIdChange={setCurrentThemeId}
      />
    </div>
  );
};

export default App;