import React, { useRef, useEffect } from 'react';
import { X, Moon, Sun, Check } from 'lucide-react';
import { themes, ThemeId } from '../src/themes';

interface SettingsModalProps {
    isOpen: boolean;
    onClose: () => void;
    theme: 'light' | 'dark';
    onThemeChange: (theme: 'light' | 'dark') => void;
    currentThemeId: ThemeId;
    onThemeIdChange: (id: ThemeId) => void;
}

const SettingsModal: React.FC<SettingsModalProps> = ({
    isOpen,
    onClose,
    theme,
    onThemeChange,
    currentThemeId,
    onThemeIdChange
}) => {
    const modalRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const handleEscape = (e: KeyboardEvent) => {
            if (e.key === 'Escape') onClose();
        };

        if (isOpen) {
            document.addEventListener('keydown', handleEscape);
            document.body.style.overflow = 'hidden';
        }

        return () => {
            document.removeEventListener('keydown', handleEscape);
            document.body.style.overflow = 'unset';
        };
    }, [isOpen, onClose]);

    const handleBackdropClick = (e: React.MouseEvent) => {
        if (modalRef.current && !modalRef.current.contains(e.target as Node)) {
            onClose();
        }
    };

    if (!isOpen) return null;

    return (
        <div
            className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200"
            onClick={handleBackdropClick}
        >
            <div
                ref={modalRef}
                className="bg-white dark:bg-slate-900 w-full max-w-md rounded-2xl shadow-2xl scale-100 opacity-100 overflow-hidden ring-1 ring-slate-900/5 transition-all"
            >
                {/* Header */}
                <div className="flex items-center justify-between p-6 border-b border-slate-100 dark:border-slate-800">
                    <h2 className="text-xl font-bold text-slate-900 dark:text-white">Settings</h2>
                    <button
                        onClick={onClose}
                        className="p-2 text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors"
                    >
                        <X className="w-5 h-5" />
                    </button>
                </div>

                {/* Content */}
                <div className="p-6 space-y-8">
                    {/* Mode Section */}
                    <section>
                        <h3 className="text-sm font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-4">Mode</h3>

                        <div className="grid grid-cols-2 gap-3">
                            <button
                                onClick={() => onThemeChange('light')}
                                className={`flex items-center justify-center gap-3 p-4 rounded-xl border-2 transition-all ${theme === 'light'
                                    ? 'border-brand-500 bg-brand-50 dark:bg-brand-900/20 text-brand-700 dark:text-brand-300'
                                    : 'border-slate-200 dark:border-slate-700 hover:border-brand-200 dark:hover:border-slate-600 text-slate-700 dark:text-slate-300'
                                    }`}
                            >
                                <Sun className="w-5 h-5" />
                                <span className="font-medium">Light</span>
                                {theme === 'light' && <Check className="w-4 h-4 ml-auto text-brand-600 dark:text-brand-400" />}
                            </button>

                            <button
                                onClick={() => onThemeChange('dark')}
                                className={`flex items-center justify-center gap-3 p-4 rounded-xl border-2 transition-all ${theme === 'dark'
                                    ? 'border-brand-500 bg-brand-50 dark:bg-brand-900/20 text-brand-700 dark:text-brand-300'
                                    : 'border-slate-200 dark:border-slate-700 hover:border-brand-200 dark:hover:border-slate-600 text-slate-700 dark:text-slate-300'
                                    }`}
                            >
                                <Moon className="w-5 h-5" />
                                <span className="font-medium">Dark</span>
                                {theme === 'dark' && <Check className="w-4 h-4 ml-auto text-brand-600 dark:text-brand-400" />}
                            </button>
                        </div>
                    </section>

                    {/* Theme Style Section */}
                    <section>
                        <h3 className="text-sm font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-4">Visual Theme</h3>
                        <div className="grid grid-cols-1 gap-3">
                            {themes.map(t => (
                                <button
                                    key={t.id}
                                    onClick={() => onThemeIdChange(t.id)}
                                    className={`flex items-center justify-between p-4 rounded-xl border-2 transition-all ${currentThemeId === t.id
                                        ? 'border-brand-500 bg-brand-50 dark:bg-brand-900/20 text-brand-700 dark:text-brand-300'
                                        : 'border-slate-200 dark:border-slate-700 hover:border-brand-200 dark:hover:border-slate-600 text-slate-700 dark:text-slate-300'
                                        }`}
                                >
                                    <span className="font-medium">{t.name}</span>
                                    {currentThemeId === t.id && <Check className="w-4 h-4 text-brand-600 dark:text-brand-400" />}
                                </button>
                            ))}
                        </div>
                    </section>
                </div>
            </div>
        </div>
    );
};

export default SettingsModal;
