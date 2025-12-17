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
    const restartTimerRef = useRef<any>(null);
    const ignoreNextEnd = useRef(false);

    const isExplicitlyStopped = useRef(false);
    const [error, setError] = useState<string | null>(null);
    // Removed internal hasGreetedRef in favor of prop

    // Update ref whenever state changes
    useEffect(() => {
        stateRef.current = state;
    }, [state]);

    // TTS Helper
    const speak = useCallback((text: string, onEnd?: () => void) => {
        if ('speechSynthesis' in window) {
            // Cancel current speech
            window.speechSynthesis.cancel();

            const utterance = new SpeechSynthesisUtterance(text);
            utterance.rate = 1.0;
            utterance.pitch = 1.0;
            utterance.volume = 1.0;

            // Try to find a good voice
            const voices = window.speechSynthesis.getVoices();
            const preferredVoice = voices.find(v => v.name.includes('Google US English') || v.name.includes('David')) || voices[0];
            if (preferredVoice) utterance.voice = preferredVoice;

            utterance.onstart = () => setState('SPEAKING');
            // Safety timeout: If TTS hangs or doesn't fire onend, force it after 4 seconds
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
        const lowerText = text.toLowerCase();
        const currentState = stateRef.current;

        console.log(`[VoiceAgent] State: ${currentState}, Heard: "${lowerText}"`);

        // --- 1. IDLE: Listen for Wake Word ---
        if (currentState === 'IDLE' || currentState === 'SPEAKING' || currentState === 'STOPPED') {
            // Also allow wake from STOPPED if we want (but usually STOPPED means OFF). 
            // If user says "it is hearing", they are likely in IDLE.

            // IGNORE SELF-HEARING (Simple Echo Cancellation)
            if (lowerText.includes("how can i help") || lowerText.includes("i'm on it")) {
                console.log("Ignored self-voice echo");
                return;
            }

            if (lowerText.includes('hey atom') || lowerText.includes('hay atom') || lowerText.includes('hi atom') || lowerText.includes('hey adam')) {
                console.log("Wake Word Detected!");

                // Stop listening briefly while speaking
                ignoreNextEnd.current = true;
                if (recognitionRef.current) recognitionRef.current.stop();

                setState('WAKE_WORD_DETECTED');
                setFeedback("I'm listening...");

                const proceed = () => {
                    // diverse back to listening for command
                    setState('LISTENING_COMMAND');
                    setTranscript(''); // Clear buffer
                    try { recognitionRef.current?.start(); } catch (e) { }
                };

                // Speak response only ONCE
                if (!hasGreeted) {
                    setHasGreeted(true);
                    console.log(`Greeting user: ${userName}`);
                    speak(`Hey ${userName}, how can I help you?`, proceed);
                } else {
                    // Just a short confirmation sound or immediate listen
                    speak("Yes?", proceed);
                }
            }
        }

        // --- 2. COMMAND LISTENING ---
        else if (currentState === 'LISTENING_COMMAND') {
            // Reset silence timer on new input
            if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current);

            // Setup a silence timer: if no new speech for 2 seconds, assume command finished
            silenceTimerRef.current = setTimeout(() => {
                finalizeCommand(lowerText);
            }, 2000);
        }

    }, [speak]);

    const finalizeCommand = (cmdText: string) => {
        if (!cmdText.trim()) return;

        console.log(`[VoiceAgent] Finalizing Command: "${cmdText}"`);
        setState('PROCESSING');

        // Stop listening
        ignoreNextEnd.current = true;
        if (recognitionRef.current) recognitionRef.current.stop();

        // Speak "I will do it", and then RESTART listening
        speak(`Okay ${userName}, I'm on it.`, () => {
            // ACTION: Restart listening AFTER speaking
            setTimeout(() => {
                setState('IDLE');
                setTranscript('');
                if (!isExplicitlyStopped.current) {
                    try { recognitionRef.current?.start(); } catch (e) { }
                }
            }, 1000); // 1.0s Delay to prevent self-hearing echo
        });

        // Execute command parallel to speaking
        onCommand(cmdText);
    };

    // Initialize Recognition
    useEffect(() => {
        const { webkitSpeechRecognition, SpeechRecognition } = window as unknown as IWindow;
        const SpeechRecognitionApi = SpeechRecognition || webkitSpeechRecognition;

        if (SpeechRecognitionApi) {
            const recognition = new SpeechRecognitionApi();
            recognition.continuous = true; // Always listen
            recognition.interimResults = true; // Get Real-time results
            recognition.lang = 'en-US';

            recognition.onresult = (event: any) => {
                const resultIndex = event.resultIndex;
                const result = event.results[resultIndex];
                const text = result[0].transcript;

                setTranscript(text);

                // Process interim or final results
                processTranscript(text);
            };

            recognition.onerror = (event: any) => {
                console.error("Speech Error:", event.error);
                // Auto-restart on error if intended to be always-on
                if (event.error === 'not-allowed') {
                    setFeedback("Microphone access denied");
                }
            };

            recognition.onend = () => {
                // Check if we manually stopped it
                if (ignoreNextEnd.current) {
                    console.log("Ignored manual stop.");
                    ignoreNextEnd.current = false;
                    return;
                }

                // Auto-restart unless specifically stopped or speaking
                if (!isExplicitlyStopped.current && stateRef.current !== 'STOPPED') {
                    // Always try to restart if logic didn't explicitly stop it.
                    // We rely on 'isExplicitlyStopped' to know if user pressed Stop.
                    // Even if SPEAKING or PROCESSING, if 'onend' fired, it means mic is dead.
                    // But if we are SPEAKING, we might want to wait?
                    // No, reliance on the 'speak' callback in finalizeCommand handles the specific restart-after-action.
                    // This block is for "Accidental" stops (silence, errors).

                    // If we are PROCESSING/SPEAKING, 'onend' is EXPECTED (we called stop).
                    // So we should NOT restart here, because finalizeCommand loop will do it.
                    if (stateRef.current === 'SPEAKING' || stateRef.current === 'PROCESSING') {
                        return;
                    }

                    restartTimerRef.current = setTimeout(() => {
                        try {
                            const currentState = stateRef.current;
                            // Only restart if we are supposed to be listening (IDLE or LISTENING_COMMAND)
                            // If we are SPEAKING, PROCESSING, or WAKE_WORD_DETECTED, let the specific logic handle the restart.
                            if (currentState === 'IDLE' || currentState === 'LISTENING_COMMAND') {
                                console.log("Auto-restarting recognition (Loop Guard)...");
                                recognition.start();
                            } else {
                                console.log(`Skipping auto-restart, state is ${currentState}`);
                            }
                        } catch (e) { console.error("Restart failed", e); }
                    }, 500);
                }
            };

            recognitionRef.current = recognition;
        }
    }, [processTranscript]);

    const startAgent = (skipWakeWord: boolean = false) => {
        isExplicitlyStopped.current = false;
        setError(null);
        if (recognitionRef.current) {
            try {
                recognitionRef.current.start();
                if (skipWakeWord) {
                    setState('LISTENING_COMMAND');
                    setFeedback("Listening for command...");
                } else {
                    setState('IDLE');
                    setFeedback("Listening...");
                }
            } catch (e) {
                console.log("Already started or error", e);
                if (skipWakeWord) {
                    setState('LISTENING_COMMAND');
                    setFeedback("Listening for command...");
                }
            }
        }
    };

    const stopAgent = () => {
        isExplicitlyStopped.current = true;
        if (recognitionRef.current) {
            recognitionRef.current.stop();
            setState('STOPPED');
            setFeedback("");
        }
    };

    return {
        state,
        transcript,
        feedback,
        error,
        startAgent,
        stopAgent
    };
};
