import { useState, useEffect, useRef, useCallback } from 'react';

// Extend Window for Web Speech API
interface IWindow extends Window {
    webkitSpeechRecognition: any;
    SpeechRecognition: any;
}

type AgentState = 'IDLE' | 'WAKE_WORD_DETECTED' | 'LISTENING_COMMAND' | 'PROCESSING' | 'SPEAKING' | 'STOPPED';

interface UseVoiceAgentProps {
    onCommand: (text: string) => void;
    userName: string;
    hasGreeted: boolean;
    setHasGreeted: (value: boolean) => void;
}

export const useVoiceAgent = ({ onCommand, userName, hasGreeted, setHasGreeted }: UseVoiceAgentProps) => {
    const [state, setState] = useState<AgentState>('STOPPED');
    const [transcript, setTranscript] = useState('');
    const [feedback, setFeedback] = useState('');

    // Refs to keep track of state inside callbacks
    const stateRef = useRef<AgentState>('STOPPED');
    const recognitionRef = useRef<any>(null);
    const silenceTimerRef = useRef<any>(null);
    const ignoreNextEnd = useRef(false);

    const isExplicitlyStopped = useRef(false);
    const [error, setError] = useState<string | null>(null);

    // Wake Lock Ref
    const wakeLockRef = useRef<any>(null);

    const requestWakeLock = async () => {
        try {
            if ('wakeLock' in navigator) {
                wakeLockRef.current = await (navigator as any).wakeLock.request('screen');
                console.log('Wake Lock active.');
                wakeLockRef.current.addEventListener('release', () => {
                    console.log('Wake Lock released.');
                });
            }
        } catch (err) {
            console.error(`${err} - Wake Lock failed`);
        }
    };

    // Update ref whenever state changes
    useEffect(() => {
        stateRef.current = state;
    }, [state]);

    // TTS Helper
    const speak = useCallback((text: string, onEnd?: () => void) => {
        if ('speechSynthesis' in window) {
            window.speechSynthesis.cancel();

            const utterance = new SpeechSynthesisUtterance(text);
            utterance.rate = 1.0;
            utterance.pitch = 1.0;
            utterance.volume = 1.0;

            const voices = window.speechSynthesis.getVoices();
            // PRIORITY: Female Voices (Zira, Google US English, Generic Female)
            const preferredVoice = voices.find(v =>
                v.name.includes('Zira') ||
                v.name.includes('Google US English') ||
                v.name.toLowerCase().includes('female')
            ) || voices[0];

            if (preferredVoice) utterance.voice = preferredVoice;

            utterance.onstart = () => setState('SPEAKING');

            // Safety timeout
            const safetyTimeout = setTimeout(() => {
                console.warn("TTS timed out, forcing callback");
                if (onEnd) onEnd();
            }, 4000);

            utterance.onend = () => {
                clearTimeout(safetyTimeout);
                if (onEnd) onEnd();
            };

            window.speechSynthesis.speak(utterance);
        } else {
            console.warn("TTS not supported");
            if (onEnd) onEnd();
        }
    }, []);

    const processTranscript = useCallback((text: string) => {
        const lowerText = text.toLowerCase().trim();
        const currentState = stateRef.current;

        console.log(`[VoiceAgent] State: ${currentState}, Heard: "${lowerText}"`);

        // WAKE WORDS
        const wakeWords = ['hey atom', 'hay atom', 'hi atom', 'atom', 'hay', 'hey'];
        const isWakeWord = wakeWords.some(w => lowerText.includes(w));

        // --- STRICT ECHO CANCELLATION GATE ---
        // If speaking, IGNORE ALL input unless it is a Wake Word (Interrupt)
        if (currentState === 'SPEAKING') {
            if (isWakeWord) {
                console.log("Interrupting Speech!");
                window.speechSynthesis.cancel();

                // CRITICAL FIX: If we are interrupted, GO DIRECTLY TO LISTENING.
                // Do NOT speak again (avoids "Hay Hay Hay" loop).
                setState('LISTENING_COMMAND');
                setTranscript('');
                return;
            } else {
                console.log("Ignored input while speaking (Echo Guard).");
                return;
            }
        }

        // --- 1. IDLE: Listen for Wake Word ---
        if (currentState === 'IDLE' || currentState === 'STOPPED' || currentState === 'PROCESSING') {

            // IGNORE SELF-HEARING
            if (lowerText.includes("how can i help") || lowerText.includes("i'm here") || lowerText.includes("listening")) {
                return;
            }

            if (isWakeWord) {
                console.log("Wake Word Detected!");

                setState('WAKE_WORD_DETECTED');
                setFeedback("I'm listening...");

                const proceed = () => {
                    setState('LISTENING_COMMAND');
                    setTranscript('');
                };

                // Friendly Greeting (User Request)
                if (!hasGreeted) {
                    setHasGreeted(true);
                    speak("Hey! I'm here.", proceed);
                } else {
                    // Short friendly acknowledgement
                    speak("Hey.", proceed);
                }
            }
        }

        // --- 2. COMMAND LISTENING ---
        else if (currentState === 'LISTENING_COMMAND') {
            if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current);
            silenceTimerRef.current = setTimeout(() => {
                finalizeCommand(lowerText);
            }, 3000);
        }

    }, [speak, hasGreeted, setHasGreeted, userName]);

    const finalizeCommand = (cmdText: string) => {
        if (!cmdText.trim()) return;

        console.log(`[VoiceAgent] Finalizing Command: "${cmdText}"`);
        setState('PROCESSING');

        // Speak confirmation (User Request: Female Voice)
        speak(`Okay.`, () => {
            if (stateRef.current === 'PROCESSING') {
                setState('IDLE');
                setTranscript('');
            }
        });

        onCommand(cmdText);
    };

    // Initialize Recognition
    useEffect(() => {
        const { webkitSpeechRecognition, SpeechRecognition } = window as unknown as IWindow;
        const SpeechRecognitionApi = SpeechRecognition || webkitSpeechRecognition;

        if (SpeechRecognitionApi) {
            const recognition = new SpeechRecognitionApi();
            recognition.continuous = true;
            recognition.interimResults = true;
            recognition.lang = 'en-US';

            recognition.onresult = (event: any) => {
                const resultIndex = event.resultIndex;
                const result = event.results[resultIndex];
                const text = result[0].transcript;

                setTranscript(text);
                processTranscript(text);
            };

            recognition.onerror = (event: any) => {
                console.error("Speech Error:", event.error);
                if (event.error === 'not-allowed') {
                    setFeedback("Microphone access denied");
                    stopAgent();
                } else if (event.error === 'no-speech') {
                    // console.log("No speech detected");
                }
            };

            recognition.onend = () => {
                console.log("Recognition Ended. Checking restart...");
                if (ignoreNextEnd.current) {
                    ignoreNextEnd.current = false;
                    return;
                }

                if (!isExplicitlyStopped.current) {
                    recognition.start();
                    requestWakeLock();
                }
            };

            recognitionRef.current = recognition;
        }
    }, [processTranscript]);

    const startAgent = (skipWakeWord: boolean = false) => {
        isExplicitlyStopped.current = false;
        setError(null);
        requestWakeLock();

        if (recognitionRef.current) {
            try {
                recognitionRef.current.start();
                if (skipWakeWord) {
                    setState('LISTENING_COMMAND');
                    setFeedback("Listening for command...");
                } else {
                    setState('IDLE');
                    setFeedback("Listening for 'Hay Atom'...");
                }
            } catch (e) {
                console.error("Start failed:", e);
                setError("Could not start microphone.");
            }
        } else {
            setError("Speech API not supported in this browser.");
        }
    };

    const stopAgent = () => {
        isExplicitlyStopped.current = true;
        setState('STOPPED');
        setFeedback("Agent Stopped");
        if (recognitionRef.current) recognitionRef.current.stop();
        if (wakeLockRef.current) {
            wakeLockRef.current.release();
            wakeLockRef.current = null;
        }
    };

    return { state, feedback, error, transcript, startAgent, stopAgent };
};
