import React, { useState, useRef, useEffect } from 'react';
import {
  MessageSquare,
  Plus,
  LogOut,
  LayoutDashboard,
  PanelLeftClose,
  Settings,
  HelpCircle,
  User as UserIcon,
  ChevronUp,
  Edit
} from 'lucide-react';
import { ChatSession, User } from '../types';

interface SidebarProps {
  user: User | null;
  sessions: ChatSession[];
  currentSessionId: string | null;
  onSelectSession: (id: string) => void;
  onNewChat: () => void;
  onLogout: () => void;
  onClose: () => void;
  onOpenSettings: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({
  user,
  sessions,
  currentSessionId,
  onSelectSession,
  onNewChat,
  onLogout,
  onClose,
  onOpenSettings
}) => {
  const [isProfileMenuOpen, setIsProfileMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsProfileMenuOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  if (!user) {
    return (
      <div className="hidden md:flex flex-col w-full h-full bg-brand-50/50 border-r border-blue-100 p-6 items-center justify-center text-center relative">
        <button
          onClick={onClose}
          className="absolute top-4 left-4 p-2 text-brand-400 hover:text-brand-600 hover:bg-brand-100 rounded-lg transition-colors"
          title="Close sidebar"
        >
          <PanelLeftClose className="w-5 h-5" />
        </button>
        <div className="bg-blue-100 p-4 rounded-full mb-4">
          <LayoutDashboard className="w-8 h-8 text-brand-600" />
        </div>
        <h3 className="text-lg font-semibold text-brand-900 mb-2">Unlock History</h3>
        <p className="text-sm text-brand-700/70 mb-6">Log in to save your thoughts, ideas, and conversations across devices.</p>
        {/* Placeholder for visual balance */}
        <div className="w-full h-32 bg-gradient-to-b from-white/50 to-transparent rounded-lg border border-white/60"></div>
      </div>
    );
  }

  return (
    <div className="hidden md:flex flex-col w-full h-full bg-slate-50 dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800 transition-colors">
      {/* Header */}
      <div className="p-4 border-b border-slate-200/60 dark:border-slate-800/60 bg-white/50 dark:bg-slate-900/50 backdrop-blur-sm">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-sm font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider pl-1">History</h2>
          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors"
            title="Close sidebar"
          >
            <PanelLeftClose className="w-5 h-5" />
          </button>
        </div>
        <button
          onClick={onNewChat}
          className="w-full flex items-center justify-center gap-2 bg-brand-600 hover:bg-brand-700 text-white py-3 px-4 rounded-xl shadow-sm transition-all duration-200 ease-in-out font-medium"
        >
          <Plus className="w-5 h-5" />
          <span>New Idea</span>
        </button>
      </div>

      {/* Session List */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        <div className="text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider px-3 py-2">Recents</div>
        {sessions.length === 0 ? (
          <div className="text-slate-400 dark:text-slate-500 text-sm text-center py-8">
            No history yet. Start thinking!
          </div>
        ) : (
          sessions.map((session) => (
            <button
              key={session.id}
              onClick={() => onSelectSession(session.id)}
              className={`w-full text-left flex items-start gap-3 p-3 rounded-lg transition-colors duration-200 ${currentSessionId === session.id
                ? 'bg-white dark:bg-slate-800 shadow-sm ring-1 ring-brand-100 dark:ring-slate-700'
                : 'hover:bg-brand-50/50 dark:hover:bg-slate-800/50 text-slate-600 dark:text-slate-400'
                }`}
            >
              <MessageSquare className={`w-5 h-5 mt-0.5 ${currentSessionId === session.id ? 'text-brand-600 dark:text-brand-400' : 'text-slate-400'}`} />
              <div className="flex-1 min-w-0">
                <h4 className={`text-sm font-medium truncate ${currentSessionId === session.id ? 'text-brand-900 dark:text-slate-200' : 'text-slate-700 dark:text-slate-300'}`}>
                  {session.title}
                </h4>
                <p className="text-xs text-slate-400 truncate mt-0.5">
                  {new Date(session.updatedAt).toLocaleDateString()}
                </p>
              </div>
            </button>
          ))
        )}
      </div>

      {/* User Footer with Dropdown Menu */}
      <div className="p-4 border-t border-slate-200 dark:border-slate-800 bg-white/50 dark:bg-slate-900/50 relative" ref={menuRef}>

        {/* Profile Menu Popup */}
        {isProfileMenuOpen && (
          <div className="absolute bottom-[calc(100%-8px)] left-3 right-3 mb-2 bg-white dark:bg-slate-800 rounded-xl shadow-xl shadow-brand-900/10 border border-slate-100 dark:border-slate-700 py-1.5 z-20 animate-in fade-in slide-in-from-bottom-2 duration-200">
            <button
              className="w-full text-left px-4 py-2.5 text-sm text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-700 hover:text-brand-600 dark:hover:text-brand-400 flex items-center gap-3 transition-colors"
              onClick={() => setIsProfileMenuOpen(false)}
            >
              <Edit className="w-4 h-4 text-slate-400" />
              Edit Profile
            </button>
            <button
              className="w-full text-left px-4 py-2.5 text-sm text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-700 hover:text-brand-600 dark:hover:text-brand-400 flex items-center gap-3 transition-colors"
              onClick={() => {
                setIsProfileMenuOpen(false);
                onOpenSettings();
              }}
            >
              <Settings className="w-4 h-4 text-slate-400" />
              Settings
            </button>
            <button
              className="w-full text-left px-4 py-2.5 text-sm text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-700 hover:text-brand-600 dark:hover:text-brand-400 flex items-center gap-3 transition-colors"
              onClick={() => setIsProfileMenuOpen(false)}
            >
              <HelpCircle className="w-4 h-4 text-slate-400" />
              Help Center
            </button>
            <div className="h-px bg-slate-100 dark:bg-slate-700 my-1 mx-2"></div>
            <button
              onClick={() => {
                setIsProfileMenuOpen(false);
                onLogout();
              }}
              className="w-full text-left px-4 py-2.5 text-sm text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 flex items-center gap-3 transition-colors rounded-b-lg"
            >
              <LogOut className="w-4 h-4" />
              Log out
            </button>
          </div>
        )}

        <button
          onClick={() => setIsProfileMenuOpen(!isProfileMenuOpen)}
          className={`flex items-center gap-3 w-full p-2 rounded-xl transition-all duration-200 group ${isProfileMenuOpen ? 'bg-white dark:bg-slate-800 shadow-md ring-1 ring-slate-100 dark:ring-slate-700' : 'hover:bg-white dark:hover:bg-slate-800 hover:shadow-sm'}`}
        >
          <div className="w-10 h-10 rounded-full bg-brand-100 dark:bg-brand-900/50 flex items-center justify-center text-brand-700 dark:text-brand-300 font-bold text-sm ring-2 ring-white dark:ring-slate-800 shadow-sm group-hover:ring-brand-50 dark:group-hover:ring-slate-700 transition-all">
            {user.name.charAt(0).toUpperCase()}
          </div>
          <div className="flex-1 min-w-0 text-left">
            <p className="text-sm font-medium text-slate-900 dark:text-slate-200 truncate">{user.name}</p>
            <p className="text-xs text-slate-500 dark:text-slate-400 truncate">{user.email}</p>
          </div>
          <ChevronUp className={`w-4 h-4 text-slate-400 transition-transform duration-200 ${isProfileMenuOpen ? 'rotate-0' : 'rotate-180'}`} />
        </button>
      </div>
    </div>
  );
};

export default Sidebar;