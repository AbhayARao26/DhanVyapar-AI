import React from 'react';
import { Moon, Sun } from 'lucide-react';
import { useTheme } from './ThemeProvider';

export const ThemeToggle: React.FC = () => {
  const { theme, toggleTheme } = useTheme();
  const isDark = theme === 'dark';

  return (
    <button
      onClick={toggleTheme}
      className="relative flex items-center w-16 h-8 bg-white/10 backdrop-blur-sm border border-white/20 rounded-full transition-all duration-300 hover:bg-white/20 focus:outline-none focus:ring-2 focus:ring-sapBlue-500 focus:ring-offset-2 focus:ring-offset-background"
      title={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
      aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
    >
      {/* Background track */}
      <div
        className={`absolute inset-0 rounded-full transition-colors duration-300 ${
          isDark 
            ? 'bg-gradient-to-r from-blue-600 to-purple-600' 
            : 'bg-gradient-to-r from-yellow-400 to-orange-500'
        }`}
      />
      
      {/* Icons */}
      <div className="relative z-10 flex items-center justify-between w-full px-1">
        <Sun 
          className={`w-4 h-4 transition-all duration-300 ${
            isDark ? 'text-white/40' : 'text-white'
          }`} 
        />
        <Moon 
          className={`w-4 h-4 transition-all duration-300 ${
            isDark ? 'text-white' : 'text-white/40'
          }`} 
        />
      </div>
      
      {/* Sliding toggle */}
      <div
        className={`absolute top-1 w-6 h-6 bg-white rounded-full shadow-lg transition-all duration-300 ease-in-out transform ${
          isDark ? 'translate-x-8' : 'translate-x-1'
        }`}
      >
        <div className="flex items-center justify-center w-full h-full">
          {isDark ? (
            <Moon className="w-3 h-3 text-blue-600" />
          ) : (
            <Sun className="w-3 h-3 text-orange-500" />
          )}
        </div>
      </div>
    </button>
  );
};
