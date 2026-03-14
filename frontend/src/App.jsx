import React, { useState } from 'react';
import ChatInterface from './components/ChatInterface';
import IncidentForm from './components/IncidentForm';
import LanguageSelector from './components/LanguageSelector';
import Header from './components/Header';
import './App.css';

function App() {
  const [selectedLanguage, setSelectedLanguage] = useState('tr');
  const [activeTab, setActiveTab] = useState('chat'); // 'chat' | 'form'

  const handleFormSubmit = (formData) => {
    console.log('Form submitted:', formData);
    // Here you would send formData to the backend for analysis
    // Switch to chat tab to show analysis progress
    setActiveTab('chat');
  };

  return (
    <div className="app">
      {/* Header */}
      <Header 
        selectedLanguage={selectedLanguage}
        onLanguageChange={setSelectedLanguage}
      />

      {/* Tab Navigation */}
      <div className="tab-navigation">
        <button
          className={`tab-btn ${activeTab === 'form' ? 'active' : ''}`}
          onClick={() => setActiveTab('form')}
        >
          <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <span>{selectedLanguage === 'tr' ? 'Manuel Form' : 'Manual Form'}</span>
        </button>
        <button
          className={`tab-btn ${activeTab === 'chat' ? 'active' : ''}`}
          onClick={() => setActiveTab('chat')}
        >
          <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
          <span>{selectedLanguage === 'tr' ? 'Etkileşimli Analiz' : 'Interactive Analysis'}</span>
        </button>
      </div>

      {/* Info Banner */}
      <div className="info-banner">
        <div className="info-banner-icon">RCA</div>
        <div className="info-banner-content">
          <h2>Root Cause Analysis</h2>
          <p>HSG245 v2.0 - İş Kazası Kök Neden Analiz Sistemi</p>
        </div>
      </div>

      {/* Main Content */}
      <main className="main-content">
        {activeTab === 'form' ? (
          <IncidentForm 
            language={selectedLanguage}
            onSubmit={handleFormSubmit}
          />
        ) : (
          <ChatInterface 
            language={selectedLanguage}
          />
        )}
      </main>
    </div>
  );
}

export default App;
