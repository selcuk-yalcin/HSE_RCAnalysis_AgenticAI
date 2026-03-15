import React from 'react';
import { Globe, Menu, Settings, Sun, Moon } from 'lucide-react';
import LanguageSelector from './LanguageSelector';
import './Header.css';

const Header = ({ selectedLanguage, onLanguageChange, isDarkMode, onToggleDarkMode }) => {
  return (
    <header className="header">
      <div className="header-left">
        {/* Logo kaldırıldı - daha minimal header */}
      </div>

      <div className="header-right">
        <LanguageSelector 
          selectedLanguage={selectedLanguage}
          onLanguageChange={onLanguageChange}
        />
        
        <button 
          className="icon-btn dark-mode-toggle" 
          title={isDarkMode ? 'Açık Mod' : 'Karanlık Mod'}
          onClick={() => onToggleDarkMode(!isDarkMode)}
        >
          {isDarkMode ? <Sun size={20} /> : <Moon size={20} />}
        </button>

        <button className="icon-btn" title="Ayarlar">
          <Settings size={20} />
        </button>
      </div>
    </header>
  );
};

export default Header;
