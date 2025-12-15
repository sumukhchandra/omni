import { useState, useEffect, useCallback } from 'react';

// Extend the Window interface to include webkitSpeechRecognition
interface IWindow extends Window {
    webkitSpeechRecognition: any;
    SpeechRecognition: any;
}

const useSpeechRecognition = () => {
    const [isListening, setIsListening] = useState(false);
    const [transcript, setTranscript] = useState('');
    const [error, setError] = useState<string | null>(null);
    const [recognition, setRecognition] = useState<any>(null);

    useEffect(() => {
        const { webkitSpeechRecognition, SpeechRecognition } = window as unknown as IWindow;
        const SpeechRecognitionApi = SpeechRecognition || webkitSpeechRecognition;

        if (SpeechRecognitionApi) {
            const recognitionInstance = new SpeechRecognitionApi();
            recognitionInstance.continuous = false;
            recognitionInstance.interimResults = false;
            recognitionInstance.lang = 'en-US';

            recognitionInstance.onstart = () => {
                setIsListening(true);
                setError(null);
            };

            recognitionInstance.onend = () => {
                setIsListening(false);
            };

            recognitionInstance.onresult = (event: any) => {
                const currentTranscript = event.results[0][0].transcript;
                setTranscript(currentTranscript);
            };

            recognitionInstance.onerror = (event: any) => {
                setError(event.error);
                setIsListening(false);
            };

            setRecognition(recognitionInstance);
        } else {
            setError('Speech recognition not supported in this browser.');
        }
    }, []);

    const startListening = useCallback(() => {
        if (recognition && !isListening) {
            try {
                recognition.start();
            } catch (e) {
                console.error("Error starting recognition:", e);
            }
        }
    }, [recognition, isListening]);

    const stopListening = useCallback(() => {
        if (recognition && isListening) {
            recognition.stop();
        }
    }, [recognition, isListening]);

    const resetTranscript = useCallback(() => {
        setTranscript('');
    }, []);

    return {
        isListening,
        transcript,
        error,
        startListening,
        stopListening,
        resetTranscript
    };
};

export default useSpeechRecognition;
