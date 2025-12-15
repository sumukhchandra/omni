import React, { useState, useEffect } from 'react';
import { X, Mail, Smartphone, ArrowRight, Lock, ArrowLeft } from 'lucide-react';
import { User } from '../types';

interface LoginModalProps {
  isOpen: boolean;
  initialMode: 'login' | 'signup';
  onClose: () => void;
  onLogin: (user: User) => void;
}

const LoginModal: React.FC<LoginModalProps> = ({ isOpen, initialMode, onClose, onLogin }) => {
  const [mode, setMode] = useState<'login' | 'signup'>(initialMode);
  const [signupStep, setSignupStep] = useState<1 | 2>(1);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  // Reset state when modal opens
  useEffect(() => {
    if (isOpen) {
      setMode(initialMode);
      setSignupStep(1);
      setEmail('');
      setPassword('');
      setError(null);
    }
  }, [isOpen, initialMode]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // Login Flow
    if (mode === 'login') {
      if (email && password) {
        setLoading(true);
        try {
          const res = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
          });
          const data = await res.json();

          if (res.ok) {
            onLogin(data);
            onClose();
          } else {
            setError(data.error || 'Login failed');
          }
        } catch (err) {
          setError('Connection failed');
        } finally {
          setLoading(false);
        }
      }
      return;
    }

    // Signup Flow
    if (mode === 'signup') {
      if (signupStep === 1) {
        // Step 1: Validate email then go to Step 2
        if (email) {
          setSignupStep(2);
        }
      } else {
        // Step 2: Validate password then finish
        if (password) {
          setLoading(true);
          try {
            const res = await fetch('/api/register', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ email, password })
            });
            const data = await res.json();

            if (res.ok) {
              onLogin(data);
              onClose();
            } else {
              setError(data.error || 'Registration failed');
            }
          } catch (err) {
            setError('Connection failed');
          } finally {
            setLoading(false);
          }
        }
      }
    }
  };

  const handleSocialLogin = (provider: string) => {
    // For Google, we simulate and ask for real implementation later if needed
    // The user requested: "if we login with google then the user name should be googles user name"
    // Since we don't have real Google Auth token, we mock it with a specific name as requested.
    let mockName = 'Demo User';
    let mockId = `user_${Date.now()}`;

    if (provider === 'Google') {
      mockName = 'Soorya'; // Simulated Google User Name
      mockId = 'google_user_id';
    }

    const mockUser: User = {
      id: mockId,
      name: mockName,
      email: `user@${provider.toLowerCase()}.com`
    };
    onLogin(mockUser);
    onClose();
  };

  const toggleMode = () => {
    setMode(mode === 'login' ? 'signup' : 'login');
    setSignupStep(1); // Reset step when toggling
    setPassword(''); // Clear password
  };

  if (!isOpen) return null;

  // Determine Headers
  let title = '';
  let subtitle = '';

  if (mode === 'login') {
    title = 'Welcome Back';
    subtitle = 'Enter your details to sign in.';
  } else if (mode === 'signup') {
    if (signupStep === 1) {
      title = 'Create Account';
      subtitle = 'Choose a method to start your journey.';
    } else {
      title = 'Set Password';
      subtitle = `Secure your account for ${email}`;
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Custom Scrollbar Styles */}
      <style>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 4px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: rgba(255, 255, 255, 0.1);
          border-radius: 4px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: rgba(255, 255, 255, 0.3);
          border-radius: 4px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: rgba(255, 255, 255, 0.5);
        }
      `}</style>

      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-slate-900/60 backdrop-blur-md transition-opacity duration-300"
        onClick={onClose}
      ></div>

      {/* Modal - GLASSMORPHISM APPLIED */}
      <div className="relative bg-white/10 backdrop-blur-xl border border-white/20 rounded-3xl shadow-2xl w-full max-w-md overflow-hidden animate-in fade-in zoom-in-95 duration-300">

        {/* Glow Effect behind */}
        <div className="absolute -top-20 -right-20 w-64 h-64 bg-blue-500/30 rounded-full blur-3xl pointer-events-none mix-blend-screen"></div>
        <div className="absolute -bottom-20 -left-20 w-64 h-64 bg-cyan-500/30 rounded-full blur-3xl pointer-events-none mix-blend-screen"></div>

        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-5 right-5 p-2 rounded-full text-white/60 hover:bg-white/10 hover:text-white transition-colors z-10"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Back Button (Only for Signup Step 2) */}
        {mode === 'signup' && signupStep === 2 && (
          <button
            onClick={() => setSignupStep(1)}
            className="absolute top-5 left-5 p-2 rounded-full text-white/60 hover:bg-white/10 hover:text-white transition-colors z-10"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
        )}

        <div className="p-8 md:p-10 max-h-[90vh] overflow-y-auto custom-scrollbar relative z-0">
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold text-white tracking-tight animate-in fade-in slide-in-from-top-2">{title}</h2>
            <p className="text-white/60 mt-2 text-sm animate-in fade-in slide-in-from-top-2 delay-75">{subtitle}</p>
            {error && (
              <div className="mt-4 p-3 bg-red-500/20 border border-red-500/50 rounded-xl text-red-200 text-sm animate-in fade-in zoom-in-95">
                {error}
              </div>
            )}
          </div>

          {/* SIGNUP STEP 1: Full Social List */}
          {mode === 'signup' && signupStep === 1 && (
            <div className="space-y-3 mb-8 animate-in fade-in slide-in-from-bottom-2 duration-300">
              {/* Google */}
              <button
                onClick={() => handleSocialLogin('Google')}
                className="w-full flex items-center justify-center gap-3 bg-white/5 border border-white/10 hover:bg-white/10 text-white font-medium py-3 rounded-2xl transition-all duration-200 group"
              >
                <svg className="w-5 h-5 opacity-90 group-hover:scale-110 transition-transform" viewBox="0 0 24 24">
                  <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4" />
                  <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853" />
                  <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05" />
                  <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335" />
                </svg>
                <span>Continue with Google</span>
              </button>

              {/* Apple */}
              <button
                onClick={() => handleSocialLogin('Apple')}
                className="w-full flex items-center justify-center gap-3 bg-white/5 border border-white/10 hover:bg-white/10 text-white font-medium py-3 rounded-2xl transition-all duration-200 group"
              >
                <svg className="w-5 h-5 text-white opacity-90 group-hover:scale-110 transition-transform" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M17.05 20.28c-.98.95-2.05.88-3.08.4-1.09-.5-2.08-.48-3.24 0-1.44.62-2.2.44-3.06-.4C2.79 15.25 3.51 7.59 9.05 7.31c1.35.07 2.29.74 3.08.74 1.18 0 2.21-1.23 3.6-1.14 1.35.08 2.35.66 3.03 1.63-2.57 1.57-2.12 6.03.49 7.04-.6 1.76-1.39 3.33-2.2 4.7zM12.03 7.25c-.15-2.23 1.66-4.07 3.74-4.25.29 2.58-2.34 4.5-3.74 4.25z" />
                </svg>
                <span>Continue with Apple</span>
              </button>

              {/* Microsoft */}
              <button
                onClick={() => handleSocialLogin('Microsoft')}
                className="w-full flex items-center justify-center gap-3 bg-white/5 border border-white/10 hover:bg-white/10 text-white font-medium py-3 rounded-2xl transition-all duration-200 group"
              >
                <svg className="w-5 h-5 group-hover:scale-110 transition-transform" viewBox="0 0 23 23">
                  <path fill="#f35325" d="M1 1h10v10H1z" />
                  <path fill="#81bc06" d="M12 1h10v10H12z" />
                  <path fill="#05a6f0" d="M1 12h10v10H1z" />
                  <path fill="#ffba08" d="M12 12h10v10H12z" />
                </svg>
                <span>Continue with Microsoft</span>
              </button>

              {/* Phone */}
              <button
                onClick={() => handleSocialLogin('Phone')}
                className="w-full flex items-center justify-center gap-3 bg-white/5 border border-white/10 hover:bg-white/10 text-white font-medium py-3 rounded-2xl transition-all duration-200 group"
              >
                <Smartphone className="w-5 h-5 text-white/90 group-hover:scale-110 transition-transform" />
                <span>Continue with Phone</span>
              </button>
            </div>
          )}

          {/* Divider (Only Step 1) */}
          {mode === 'signup' && signupStep === 1 && (
            <div className="relative my-8 animate-in fade-in slide-in-from-bottom-2 delay-100">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-white/10"></div>
              </div>
              <div className="relative flex justify-center text-xs uppercase tracking-widest">
                <span className="px-4 bg-transparent text-white/40">or sign up with email</span>
              </div>
            </div>
          )}

          {/* Main Form */}
          <form onSubmit={handleSubmit} className="space-y-5">

            {/* Email Field: Visible in Login AND Signup Step 1 */}
            {(mode === 'login' || (mode === 'signup' && signupStep === 1)) && (
              <div className="space-y-2 animate-in fade-in slide-in-from-bottom-2 delay-150">
                <label className="text-sm font-medium text-white/80 ml-1">Email address</label>
                <div className="relative group">
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full pl-11 pr-4 py-3.5 bg-black/20 border border-white/10 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 text-white transition-all placeholder:text-white/20 group-hover:bg-black/30 backdrop-blur-sm"
                    placeholder="name@example.com"
                    autoFocus={mode === 'signup'}
                  />
                  <Mail className="w-5 h-5 text-white/40 absolute left-3.5 top-3.5 group-focus-within:text-white transition-colors" />
                </div>
              </div>
            )}

            {/* Password Field: Visible in Login AND Signup Step 2 */}
            {(mode === 'login' || (mode === 'signup' && signupStep === 2)) && (
              <div className="space-y-2 animate-in fade-in slide-in-from-right-4 duration-300">
                <label className="text-sm font-medium text-white/80 ml-1">
                  {mode === 'signup' ? 'Create Password' : 'Password'}
                </label>
                <div className="relative group">
                  <input
                    type="password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full pl-11 pr-4 py-3.5 bg-black/20 border border-white/10 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 text-white transition-all placeholder:text-white/20 group-hover:bg-black/30 backdrop-blur-sm"
                    placeholder="••••••••"
                    autoFocus={mode === 'signup' && signupStep === 2}
                  />
                  <Lock className="w-5 h-5 text-white/40 absolute left-3.5 top-3.5 group-focus-within:text-white transition-colors" />
                </div>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white font-bold py-3.5 rounded-2xl shadow-lg shadow-blue-500/20 flex items-center justify-center gap-2 transition-all active:scale-[0.98] mt-4 animate-in fade-in slide-in-from-bottom-2 delay-200 border border-white/10 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span>{loading ? 'Processing...' : (mode === 'login' ? 'Log in' : 'Continue')}</span>
              {!loading && <ArrowRight className="w-5 h-5" />}
            </button>
          </form>

          {/* LOGIN VIEW: Compact Socials at bottom */}
          {mode === 'login' && (
            <>
              <div className="relative my-8">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-white/10"></div>
                </div>
                <div className="relative flex justify-center text-xs uppercase tracking-widest">
                  <span className="px-4 bg-transparent text-white/40">or log in with</span>
                </div>
              </div>
              <div className="flex justify-center gap-4">
                {/* Google Icon Only */}
                <button onClick={() => handleSocialLogin('Google')} className="p-3.5 bg-white/5 border border-white/10 rounded-2xl hover:bg-white/10 transition-colors group">
                  <svg className="w-5 h-5 group-hover:scale-110 transition-transform" viewBox="0 0 24 24">
                    <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4" />
                    <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853" />
                    <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05" />
                    <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335" />
                  </svg>
                </button>
                {/* Apple Icon Only */}
                <button onClick={() => handleSocialLogin('Apple')} className="p-3.5 bg-white/5 border border-white/10 rounded-2xl hover:bg-white/10 transition-colors group">
                  <svg className="w-5 h-5 text-white group-hover:scale-110 transition-transform" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M17.05 20.28c-.98.95-2.05.88-3.08.4-1.09-.5-2.08-.48-3.24 0-1.44.62-2.2.44-3.06-.4C2.79 15.25 3.51 7.59 9.05 7.31c1.35.07 2.29.74 3.08.74 1.18 0 2.21-1.23 3.6-1.14 1.35.08 2.35.66 3.03 1.63-2.57 1.57-2.12 6.03.49 7.04-.6 1.76-1.39 3.33-2.2 4.7zM12.03 7.25c-.15-2.23 1.66-4.07 3.74-4.25.29 2.58-2.34 4.5-3.74 4.25z" />
                  </svg>
                </button>
                {/* Microsoft Icon Only */}
                <button onClick={() => handleSocialLogin('Microsoft')} className="p-3.5 bg-white/5 border border-white/10 rounded-2xl hover:bg-white/10 transition-colors group">
                  <svg className="w-5 h-5 group-hover:scale-110 transition-transform" viewBox="0 0 23 23">
                    <path fill="#f35325" d="M1 1h10v10H1z" />
                    <path fill="#81bc06" d="M12 1h10v10H12z" />
                    <path fill="#05a6f0" d="M1 12h10v10H1z" />
                    <path fill="#ffba08" d="M12 12h10v10H12z" />
                  </svg>
                </button>
              </div>
            </>
          )}

          {/* Toggle Login/Signup */}
          {(mode === 'login' || (mode === 'signup' && signupStep === 1)) && (
            <div className="text-center mt-8">
              <p className="text-sm text-white/50">
                {mode === 'login' ? "Don't have an account? " : "Already have an account? "}
                <button
                  onClick={toggleMode}
                  className="font-medium text-blue-400 hover:text-blue-300 hover:underline transition-colors"
                >
                  {mode === 'login' ? 'Sign up' : 'Log in'}
                </button>
              </p>
            </div>
          )}

          <p className="text-center text-[10px] text-white/30 mt-8">
            By continuing, you agree to our <a href="#" className="underline hover:text-white/50">Terms</a> & <a href="#" className="underline hover:text-white/50">Privacy</a>.
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginModal;