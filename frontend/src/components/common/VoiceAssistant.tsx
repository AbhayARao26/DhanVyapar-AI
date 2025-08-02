import React, { useState, useRef, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { Mic, MicOff, VolumeX, X } from 'lucide-react';
import { motion } from 'framer-motion';
import { geminiChatService } from '../../services/geminiService';

interface VoiceAssistantProps {
  open: boolean;
  onClose: () => void;
}

const VoiceAssistant: React.FC<VoiceAssistantProps> = ({ open, onClose }) => {
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [response, setResponse] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  
  const recognitionRef = useRef<any>(null);
  const synthRef = useRef<SpeechSynthesis | null>(null);

  const getStatusTitle = () => {
    if (isProcessing) return 'Processing...';
    if (isListening) return 'Listening...';
    if (isSpeaking) return 'Speaking...';
    return 'Hello! I am Vaanee';
  };

  const getStatusDescription = () => {
    if (isProcessing) return 'Generating AI response';
    if (isListening) return 'Press microphone button and speak';
    if (isSpeaking) return 'Playing voice response';
    return 'Press microphone and ask your question';
  };

  useEffect(() => {
    // Initialize speech recognition
    if ('webkitSpeechRecognition' in window) {
      const recognition = new (window as any).webkitSpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = true;
      recognition.lang = 'en-US'; // Set to English

      recognition.onstart = () => {
        setIsListening(true);
      };

      recognition.onresult = (event: any) => {
        let finalTranscript = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
          if (event.results[i].isFinal) {
            finalTranscript += event.results[i][0].transcript;
          }
        }
        if (finalTranscript) {
          setTranscript(finalTranscript);
          handleVoiceInput(finalTranscript);
        }
      };

      recognition.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
      };

      recognition.onend = () => {
        setIsListening(false);
      };

      recognitionRef.current = recognition;
    }

    // Initialize speech synthesis
    synthRef.current = window.speechSynthesis;

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      if (synthRef.current) {
        synthRef.current.cancel();
      }
    };
  }, []);

  const handleVoiceInput = async (input: string) => {
    setIsProcessing(true);
    try {
      const context = 'You are Vaanee, an English Voice Assistant for financial services. Provide clear, conversational responses optimized for audio delivery. Use simple language and short sentences. Focus on making financial services accessible through voice interaction in English.';
      const contextualMessage = `${context}\n\nUser Question: ${input}`;
      
      const aiResponse = await geminiChatService.sendMessage(contextualMessage);
      setResponse(aiResponse);
      speakResponse(aiResponse);
    } catch (error) {
      console.error('Error getting AI response:', error);
      const errorMsg = 'Sorry, I am unable to connect right now. Please try again.';
      setResponse(errorMsg);
      speakResponse(errorMsg);
    } finally {
      setIsProcessing(false);
    }
  };

  const speakResponse = (text: string) => {
    if (synthRef.current) {
      synthRef.current.cancel(); // Stop any ongoing speech
      
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = 'en-US';
      utterance.rate = 0.9;
      utterance.pitch = 1.1;
      
      utterance.onstart = () => setIsSpeaking(true);
      utterance.onend = () => setIsSpeaking(false);
      utterance.onerror = () => setIsSpeaking(false);
      
      synthRef.current.speak(utterance);
    }
  };

  const startListening = () => {
    if (recognitionRef.current && !isListening) {
      setTranscript('');
      setResponse('');
      recognitionRef.current.start();
    }
  };

  const stopListening = () => {
    if (recognitionRef.current && isListening) {
      recognitionRef.current.stop();
    }
  };

  const stopSpeaking = () => {
    if (synthRef.current) {
      synthRef.current.cancel();
      setIsSpeaking(false);
    }
  };

  if (!open) return null;

  const voiceWidget = (
    <div className="fixed inset-0 z-[9999] flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.9 }}
        className="relative w-full max-w-md h-[600px] flex flex-col rounded-3xl shadow-2xl border border-white/10 bg-gradient-to-br from-orange-500/20 via-background/90 to-orange-300/20 backdrop-blur-xl"
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 rounded-t-3xl border-b border-white/10 bg-gradient-to-r from-orange-500/80 to-orange-400/60 text-white shadow-sm">
          <span className="font-bold text-lg tracking-wide flex items-center gap-3">
            <div className="w-12 h-12 bg-orange-500 rounded-full flex items-center justify-center border-2 border-white/30">
              <span className="text-2xl">🎤</span>
            </div>
            Vaanee - Voice Assistant
          </span>
          <button
            onClick={onClose}
            className="text-2xl font-bold text-white/80 hover:text-white focus:outline-none focus:ring-2 focus:ring-orange-400 rounded-full px-2 transition-colors"
            aria-label="Close voice assistant"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Voice Interface */}
        <div className="flex-1 flex flex-col items-center justify-center p-8 space-y-6">
          {/* Status Text */}
          <div className="text-center">
            <h3 className="text-xl font-semibold text-foreground mb-2">
              {getStatusTitle()}
            </h3>
            <p className="text-sm text-muted-foreground">
              {getStatusDescription()}
            </p>
          </div>

          {/* Audio Visualization */}
          <div className="flex items-center justify-center space-x-1 h-12">
            {isListening && (
              <>
                {[...Array(5)].map((_, i) => (
                  <motion.div
                    key={`listening-${i}`}
                    className="w-1 bg-orange-500 rounded-full"
                    animate={{
                      height: [4, 20, 4],
                    }}
                    transition={{
                      duration: 0.8,
                      repeat: Infinity,
                      delay: i * 0.1,
                    }}
                  />
                ))}
              </>
            )}
            {isSpeaking && (
              <>
                {[...Array(7)].map((_, i) => (
                  <motion.div
                    key={`speaking-${i}`}
                    className="w-1 bg-blue-500 rounded-full"
                    animate={{
                      height: [4, 32, 4],
                    }}
                    transition={{
                      duration: 0.6,
                      repeat: Infinity,
                      delay: i * 0.08,
                    }}
                  />
                ))}
              </>
            )}
            {isProcessing && (
              <div className="flex space-x-1">
                {[...Array(3)].map((_, i) => (
                  <motion.div
                    key={`processing-${i}`}
                    className="w-2 h-2 bg-orange-500 rounded-full"
                    animate={{ opacity: [1, 0.3, 1] }}
                    transition={{
                      duration: 1,
                      repeat: Infinity,
                      delay: i * 0.2,
                    }}
                  />
                ))}
              </div>
            )}
          </div>

          {/* Main Microphone Button */}
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={isListening ? stopListening : startListening}
            disabled={isProcessing || isSpeaking}
            className={`w-24 h-24 rounded-full flex items-center justify-center text-white font-bold text-2xl shadow-lg transition-all duration-300 ${
              isListening 
                ? 'bg-red-500 hover:bg-red-600 animate-pulse' 
                : 'bg-orange-500 hover:bg-orange-600'
            } disabled:opacity-50 disabled:cursor-not-allowed`}
          >
            {isListening ? <MicOff className="w-8 h-8" /> : <Mic className="w-8 h-8" />}
          </motion.button>

          {/* Speaker Control */}
          {isSpeaking && (
            <motion.button
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              onClick={stopSpeaking}
              className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center space-x-2 transition-colors"
            >
              <VolumeX className="w-4 h-4" />
              <span>Stop Speaking</span>
            </motion.button>
          )}

          {/* Transcript Display */}
          {transcript && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-white/10 backdrop-blur-sm rounded-lg p-3 max-w-full"
            >
              <p className="text-sm text-foreground">
                <strong>You said:</strong> {transcript}
              </p>
            </motion.div>
          )}

          {/* Response Display */}
          {response && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-orange-500/10 backdrop-blur-sm rounded-lg p-3 max-w-full"
            >
              <p className="text-sm text-foreground">
                <strong>Vaanee:</strong> {response}
              </p>
            </motion.div>
          )}
        </div>

        {/* Footer Instructions */}
        <div className="p-4 border-t border-white/10 bg-white/5 rounded-b-3xl">
          <p className="text-xs text-center text-muted-foreground">
            🎤 Press microphone • 🗣️ Speak in English • 🔊 Listen to voice response
          </p>
        </div>
      </motion.div>
    </div>
  );

  return createPortal(voiceWidget, document.body);
};

export default VoiceAssistant;
