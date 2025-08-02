import React, { useState, useRef, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { geminiChatService, ChatMessage } from '../../services/geminiService';

interface ChatBotProps {
  open: boolean;
  onClose: () => void;
  aiType?: string;
}

const ChatBot: React.FC<ChatBotProps> = ({ open, onClose, aiType }) => {
  const getAIContext = () => {
    switch (aiType) {
      case 'credwise':
        return 'You are CredWise, a Credit Metric Explainer Agent specialized in helping users understand credit terms, factors, and scores. Break down complex credit concepts into simple, easy-to-understand explanations. Focus on practical advice for improving credit health and financial literacy.';
      case 'loanpathshala':
        return 'You are LoanPathshala, an Educational Content Agent for loans and finance. Deliver clear explainers, tutorials, guides, and answer FAQs about loans and financial concepts. Make complex financial topics accessible to everyone, especially those new to formal banking.';
      case 'riskraahi':
        return 'You are RiskRaahi, a Loan Risk Advisor Agent that evaluates risk and gives advice on the best loan options. Guide users through the maze of loan risks, help them understand different loan products, and recommend the safest credit routes based on their financial situation.';
      case 'voiceagent':
        return 'You are Vaanee, an English Voice Assistant that communicates through speech, not text. You should provide responses that are optimized for audio delivery - clear, conversational, and easy to understand when spoken aloud. Use simple language and short sentences that work well with text-to-speech systems. Focus on making financial services accessible through voice interaction in English.';
      case 'risk-assessment':
        return 'You are a Risk Assessment Tool for lenders. Help assess borrower risk, analyze loan applications, evaluate creditworthiness, and provide insights for lending decisions.';
      case 'portfolio-optimizer':
        return 'You are a Portfolio Optimizer for lenders. Help optimize loan portfolios, analyze performance metrics, suggest diversification strategies, and improve overall lending portfolio health.';
      case 'market-analytics':
        return 'You are a Market Analytics expert for lenders. Provide insights on market trends, competitive analysis, interest rate movements, and market opportunities in the lending sector.';
      case 'fraud-detection':
        return 'You are a Fraud Detection specialist for lenders. Help identify suspicious patterns, red flags in applications, fraud prevention strategies, and security best practices in lending.';
      default:
        return '';
    }
  };

  const getInitialMessage = () => {
    switch (aiType) {
      case 'credwise':
        return 'Hello! I am CredWise, your credit companion. I help you understand credit scores, terms, and factors in simple language. Whether you are new to credit or want to improve your score, I am here to make it crystal clear. What would you like to know about credit?';
      case 'loanpathshala':
        return 'Welcome to LoanPathshala! I am your financial education buddy, here to teach you everything about loans and finance through easy tutorials and guides. Think of me as your personal finance teacher. What financial topic would you like to learn about today?';
      case 'riskraahi':
        return 'Hello! I am RiskRaahi, your loan risk advisor and guide. I help you navigate through different loan options, understand risks, and find the safest credit path for your needs. What kind of loan guidance are you looking for?';
      case 'voiceagent':
        return 'Hello! I am Vaanee - your voice assistant. I am a voice assistant that listens to your questions and responds with audio. Please note: This is currently a text preview of what I would say. For full voice interaction, please use the voice feature in your app. What would you like to know?';
      case 'risk-assessment':
        return 'Hello! I am your Risk Assessment Tool. I can help you evaluate borrower profiles, assess loan applications, and analyze creditworthiness. What would you like to assess?';
      case 'portfolio-optimizer':
        return 'Hi! I am your Portfolio Optimizer. I can help you analyze your loan portfolio, suggest optimization strategies, and improve overall performance. How can I assist with your portfolio?';
      case 'market-analytics':
        return 'Welcome! I am your Market Analytics expert. I can provide insights on lending market trends, competitive analysis, and opportunities. What market data would you like to explore?';
      case 'fraud-detection':
        return 'Hello! I am your Fraud Detection specialist. I can help identify suspicious patterns, analyze risk indicators, and suggest prevention strategies. What would you like me to analyze?';
      default:
        return 'Hello! How can I assist you today?';
    }
  };

  const getAITitle = () => {
    switch (aiType) {
      case 'credwise':
        return 'CredWise - Credit Expert';
      case 'loanpathshala':
        return 'LoanPathshala - Finance Teacher';
      case 'riskraahi':
        return 'RiskRaahi - Loan Guide';
      case 'voiceagent':
        return 'Vaanee - Voice Assistant (Audio Mode)';
      case 'risk-assessment':
        return 'Risk Assessment Tool';
      case 'portfolio-optimizer':
        return 'Portfolio Optimizer';
      case 'market-analytics':
        return 'Market Analytics';
      case 'fraud-detection':
        return 'Fraud Detection';
      default:
        return 'Chat with Vrishabh';
    }
  };

  const [messages, setMessages] = useState<ChatMessage[]>([
    { from: 'bot', text: getInitialMessage() }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const chatRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (open && chatRef.current) {
      chatRef.current.scrollTop = chatRef.current.scrollHeight;
    }
  }, [messages, open]);

  if (!open) return null;

  const chatWidget = (
    <div className="fixed inset-0 z-[9999] flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm transition-all">
      <div className="relative w-full max-w-2xl max-h-[85vh] h-[70vh] min-w-[400px] min-h-[500px] flex flex-col rounded-3xl shadow-2xl border border-white/10 bg-gradient-to-br from-white/30 via-background/80 to-muted/40 backdrop-blur-xl">
        {/* Header */}
        <div className="flex items-center justify-between p-4 rounded-t-3xl border-b border-white/10 bg-gradient-to-r from-primary/80 to-primary/60 text-primary-foreground shadow-sm">
          <span className="font-bold text-lg tracking-wide flex items-center gap-3">
            <img 
              src="/Chatbot.jpeg" 
              alt="Vrishabh" 
              className="w-12 h-12 rounded-full object-cover border-2 border-white/30"
            />{' '}
            {getAITitle()}
          </span>
          <button
            onClick={onClose}
            className="text-2xl font-bold text-white/80 hover:text-white focus:outline-none focus:ring-2 focus:ring-primary rounded-full px-2 transition-colors"
            aria-label="Close chat"
          >
            ×
          </button>
        </div>
        {/* Chat area */}
        <div
          ref={chatRef}
          className="flex-1 overflow-y-auto p-6 space-y-4 bg-background min-h-0"
        >
        {messages.map((msg, idx) => (
          <div key={`${msg.from}-${idx}`} className={`flex ${msg.from === 'bot' ? 'justify-start' : 'justify-end'}`}>
            {msg.from === 'bot' && (
              <div className="flex-shrink-0 mr-3 mt-1">
                <img 
                  src="/Chatbot.jpeg" 
                  alt="Vrishabh" 
                  className="w-12 h-12 rounded-full object-cover border-2 border-white/50"
                />
              </div>
            )}
            <div
              className={`px-5 py-3 max-w-[70%] rounded-2xl shadow-md transition-all text-base whitespace-pre-line ${
                msg.from === 'bot'
                  ? 'bg-white/95 text-gray-800 border border-gray-200 rounded-bl-2'
                  : 'bg-blue-600 text-white border border-blue-500 rounded-br-2'
              }`}
            >
              {msg.text}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="flex-shrink-0 mr-3 mt-1">
              <img 
                src="/Chatbot.jpeg" 
                alt="Vrishabh" 
                className="w-12 h-12 rounded-full object-cover border-2 border-white/50"
              />
            </div>
            <div className="px-5 py-3 max-w-[70%] rounded-2xl shadow-md bg-white/95 text-gray-800 border border-gray-200">
              <div className="flex items-center space-x-2">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-primary/60 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-primary/60 rounded-full animate-bounce [animation-delay:100ms]"></div>
                  <div className="w-2 h-2 bg-primary/60 rounded-full animate-bounce [animation-delay:200ms]"></div>
                </div>
                <span className="text-sm text-gray-600">AI is thinking...</span>
              </div>
            </div>
          </div>
        )}
        </div>
        {/* Input area */}
        <form
          className="flex items-center gap-3 p-4 border-t border-white/10 bg-white/60 rounded-b-3xl backdrop-blur-md"
          onSubmit={async (e) => {
            e.preventDefault();
            if (!input.trim() || isLoading) return;
            
            const userMessage = input.trim();
            setInput('');
            setIsLoading(true);
            
            // Add user message
            setMessages(prev => [...prev, { from: 'user', text: userMessage }]);
            
            try {
              // Add AI-specific context to the message
              let contextualMessage = userMessage;
              if (aiType) {
                const context = getAIContext();
                contextualMessage = `${context}\n\nUser Question: ${userMessage}`;
              }
              
              // Get AI response
              const botResponse = await geminiChatService.sendMessage(contextualMessage);
              setMessages(prev => [...prev, { from: 'bot', text: botResponse }]);
            } catch (error) {
              console.error('Error getting AI response:', error);
              setMessages(prev => [...prev, { 
                from: 'bot', 
                text: 'I apologize, but I\'m having trouble connecting right now. Please try again in a moment.' 
              }]);
            } finally {
              setIsLoading(false);
            }
          }}
        >
          <input
            className="flex-1 px-4 py-2 rounded-xl border border-white/30 focus:outline-none focus:ring-2 focus:ring-primary bg-white/90 text-gray-800 placeholder:text-gray-500 shadow-sm transition-all"
            placeholder={isLoading ? "AI is thinking..." : "Type your message..."}
            value={input}
            onChange={e => setInput(e.target.value)}
            disabled={isLoading}
            autoFocus
            aria-label="Type your message"
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="px-5 py-2 rounded-xl bg-primary text-primary-foreground font-semibold shadow-md hover:bg-primary/80 transition-colors focus:outline-none focus:ring-2 focus:ring-primary disabled:opacity-50 disabled:cursor-not-allowed"
            aria-label="Send message"
          >
            {isLoading ? 'Sending...' : 'Send'}
          </button>
        </form>
      </div>
    </div>
  );

  return createPortal(chatWidget, document.body);
};

export default ChatBot; 