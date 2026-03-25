import React, { useState } from 'react';
import ChatInterface from './components/ChatInterface';
import IncidentForm from './components/IncidentForm';
import SmartQuestionnaire_V2 from './components/SmartQuestionnaire_V2';
import LanguageSelector from './components/LanguageSelector';
import Header from './components/Header';
import { getTranslation } from './utils/translations';
import './App.css';

function App() {
  const [selectedLanguage, setSelectedLanguage] = useState('en');
  const [activeTab, setActiveTab] = useState('chat'); // 'chat' | 'form' | 'smart'

  const t = (key) => getTranslation(selectedLanguage, key);

  const handleFormSubmit = (formData) => {
    console.log('Form submitted:', formData);
    // Here you would send formData to the backend for analysis
    // Switch to chat tab to show analysis progress
    setActiveTab('chat');
  };

  const handleSmartQuestionnaireComplete = (data) => {
    console.log('Smart Questionnaire completed:', data);
    // Here you would send data to the backend for analysis
    // You can access:
    // - data.answers (all answers)
    // - data.detectedCodes (auto-detected taxonomy codes)
    // - data.totalQuestionsAnswered (progress count)
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
          className={`tab-btn ${activeTab === 'smart' ? 'active' : ''}`}
          onClick={() => setActiveTab('smart')}
        >
          <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <span>{t('smart_form_v2')}</span>
        </button>
        <button
          className={`tab-btn ${activeTab === 'form' ? 'active' : ''}`}
          onClick={() => setActiveTab('form')}
        >
          <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <span>{t('manual_form')}</span>
        </button>
        <button
          className={`tab-btn ${activeTab === 'chat' ? 'active' : ''}`}
          onClick={() => setActiveTab('chat')}
        >
          <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
          <span>{t('interactive_analysis')}</span>
        </button>
      </div>

      {/* Info Banner */}
      <div className="info-banner">
        <div className="info-banner-icon">RCA</div>
        <div className="info-banner-content">
          <h2>{t('root_cause_analysis')}</h2>
          <p>{t('subtitle')}</p>
        </div>
      </div>

      {/* Main Content */}
      <main className="main-content">
        {activeTab === 'smart' ? (
          <SmartQuestionnaire_V2 
            language={selectedLanguage}
            onComplete={handleSmartQuestionnaireComplete}
          />
        ) : activeTab === 'form' ? (
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
