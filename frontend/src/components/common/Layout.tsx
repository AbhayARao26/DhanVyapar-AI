
import React, { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { useTranslation } from 'react-i18next';
import { useSelector, useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { RootState } from '../../store';
import { logout } from '../../store/slices/authSlice';
import { LogOut, Menu, User, MessageCircle, X } from 'lucide-react';
import { ThemeToggle } from './ThemeToggle';
import LanguageSelector from './LanguageSelector';
import ChatBot from './ChatBot';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { t } = useTranslation();
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { user } = useSelector((state: RootState) => state.auth);
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isChatOpen, setIsChatOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsMenuOpen(false);
      }
    };

    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setIsMenuOpen(false);
      }
    };

    if (isMenuOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      document.addEventListener('keydown', handleEscape);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleEscape);
    };
  }, [isMenuOpen]);

  const handleLogout = () => {
    dispatch(logout());
    navigate('/login');
    setIsMenuOpen(false);
  };

  const handleProfileClick = () => {
    navigate('/profile');
    setIsMenuOpen(false);
  };

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
  };

  const toggleChat = () => {
    setIsChatOpen(!isChatOpen);
    setIsMenuOpen(false);
  };

  return (
    <div className="min-h-screen bg-background">
      <header className="bg-card/50 backdrop-blur-sm shadow-sm border-b border-border/50 relative z-[10002]">
        <div className="w-full px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Left side - Menu dropdown */}
            <div className="relative" ref={menuRef}>
              <button
                onClick={toggleMenu}
                className="p-2 text-muted-foreground hover:text-foreground transition-colors rounded-lg bg-white/5 backdrop-blur-sm border border-white/10 hover:bg-white/10"
                title="Menu"
              >
                {isMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
              </button>

              {/* Dropdown menu */}
              {isMenuOpen && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  className="absolute left-0 top-full mt-2 w-64 bg-white/95 dark:bg-gray-800/95 backdrop-blur-md border border-gray-200/50 dark:border-gray-700/50 rounded-lg shadow-xl z-[10003]"
                >
                  <div className="p-2 space-y-1">
                    {/* Language Selector */}
                    <div className="px-3 py-2 border-b border-border/30">
                      <p className="text-xs font-medium text-muted-foreground mb-2">{t('common.language')}</p>
                      <LanguageSelector />
                    </div>
                    
                    {/* Theme Toggle */}
                    <div className="px-3 py-2 border-b border-border/30">
                      <p className="text-xs font-medium text-muted-foreground mb-2">{t('common.theme')}</p>
                      <ThemeToggle />
                    </div>
                    
                    {/* AI Chatbot */}
                    <button
                      onClick={toggleChat}
                      className="w-full flex items-center space-x-3 px-3 py-2 text-left hover:bg-white/5 rounded-lg transition-colors"
                    >
                      <MessageCircle className="w-4 h-4 text-sapBlue-600" />
                      <span className="text-sm font-medium">{t('common.aiChatbot')}</span>
                    </button>
                    
                    {user && (
                      <>
                        {/* Profile */}
                        <button
                          onClick={handleProfileClick}
                          className="w-full flex items-center space-x-3 px-3 py-2 text-left hover:bg-white/5 rounded-lg transition-colors"
                        >
                          <User className="w-4 h-4 text-muted-foreground" />
                          <div className="flex-1">
                            <p className="text-sm font-medium">{t('common.profile')}</p>
                            <p className="text-xs text-muted-foreground">{user.name}</p>
                          </div>
                        </button>
                        
                        {/* Logout */}
                        <button
                          onClick={handleLogout}
                          className="w-full flex items-center space-x-3 px-3 py-2 text-left hover:bg-red-50 hover:text-red-600 rounded-lg transition-colors border-t border-border/30 mt-1 pt-3"
                        >
                          <LogOut className="w-4 h-4" />
                          <span className="text-sm font-medium">{t('auth.logout')}</span>
                        </button>
                      </>
                    )}
                  </div>
                </motion.div>
              )}
            </div>
            
            {/* Right side - Logo and Name */}
            <div className="flex items-center">
              <img src="/Logo.png" alt="GramSetu Logo" className="w-8 h-8 mr-3" />
              <h1 className="text-2xl font-bold text-sapBlue-600">GramSetu</h1>
            </div>
          </div>
        </div>
      </header>

      <main className="w-full px-4 sm:px-6 lg:px-8 py-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          {children}
        </motion.div>
      </main>
      
      {/* ChatBot Component */}
      <ChatBot open={isChatOpen} onClose={() => setIsChatOpen(false)} />
    </div>
  );
};

export default Layout;
