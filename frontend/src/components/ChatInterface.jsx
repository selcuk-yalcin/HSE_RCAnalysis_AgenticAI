import React, { useState, useRef, useEffect } from 'react';
import { Send, Paperclip, RotateCcw, Download, AlertCircle } from 'lucide-react';
import Message from './Message';
import QuestionFlow from './QuestionFlow';
import { getTranslation } from '../utils/translations';
import { sendMessage, analyzeIncident } from '../utils/api';
import './ChatInterface.css';

const ChatInterface = ({ language }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentFlow, setCurrentFlow] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const messagesEndRef = useRef(null);

  const t = (key) => getTranslation(language, key);

  useEffect(() => {
    // Initialize with welcome message
    setMessages([{
      id: '1',
      type: 'assistant',
      content: t('welcome_message'),
      timestamp: new Date(),
    }]);
    setSessionId(Date.now().toString());
  }, [language]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: input,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // Interactive Q&A mode
      const response = await sendMessage({
        message: input,
        sessionId,
        language,
      });

      const assistantMessage = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: response.message,
        suggestions: response.suggestions,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, assistantMessage]);
      
      // Check if we need to start question flow
      if (response.startFlow) {
        setCurrentFlow(response.flowType);
      }
    } catch (error) {
      const errorMessage = {
        id: (Date.now() + 1).toString(),
        type: 'error',
        content: t('error_occurred') + ': ' + error.message,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleReset = () => {
    setMessages([{
      id: Date.now().toString(),
      type: 'assistant',
      content: t('welcome_message'),
      timestamp: new Date(),
    }]);
    setCurrentFlow(null);
    setSessionId(Date.now().toString());
  };

  const handleQuestionAnswer = (answer) => {
    const userMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: answer,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, userMessage]);
  };

  return (
    <div className="chat-interface">
      {/* Sidebar - Analysis Steps (optional) */}
      <div className="chat-sidebar">
        <div className="sidebar-header">
          <h3>{t('analysis_steps')}</h3>
        </div>
        <div className="sidebar-content">
          <div className="step-item completed">
            <div className="step-icon">✓</div>
            <div className="step-text">
              <h4>{t('step_1')}</h4>
              <p>{t('step_1_desc')}</p>
            </div>
          </div>
          <div className="step-item active">
            <div className="step-icon">2</div>
            <div className="step-text">
              <h4>{t('step_2')}</h4>
              <p>{t('step_2_desc')}</p>
            </div>
          </div>
          <div className="step-item">
            <div className="step-icon">3</div>
            <div className="step-text">
              <h4>{t('step_3')}</h4>
              <p>{t('step_3_desc')}</p>
            </div>
          </div>
          <div className="step-item">
            <div className="step-icon">4</div>
            <div className="step-text">
              <h4>{t('step_4')}</h4>
              <p>{t('step_4_desc')}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="chat-main">
        <div className="chat-messages">
          {messages.map((message) => (
            <Message 
              key={message.id}
              message={message}
              language={language}
            />
          ))}

          {/* Question Flow */}
          {currentFlow && (
            <QuestionFlow
              flowType={currentFlow}
              language={language}
              onAnswer={handleQuestionAnswer}
              onComplete={() => setCurrentFlow(null)}
            />
          )}

          {isLoading && (
            <div className="message-loading">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="chat-input-container">
          <div className="chat-actions">
            <button className="action-btn" onClick={handleReset} title={t('reset')}>
              <RotateCcw size={18} />
              <span>{t('reset')}</span>
            </button>
            <button className="action-btn" title={t('export')}>
              <Download size={18} />
              <span>{t('export')}</span>
            </button>
          </div>

          <div className="chat-input-wrapper">
            <button className="attach-btn" title={t('attach_file')}>
              <Paperclip size={20} />
            </button>

            <textarea
              className="chat-input"
              placeholder={t('input_placeholder')}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              rows={1}
              disabled={isLoading}
            />

            <button 
              className="send-btn"
              onClick={handleSend}
              disabled={!input.trim() || isLoading}
            >
              <Send size={20} />
            </button>
          </div>

          <div className="input-hint">
            <AlertCircle size={14} />
            <span>{t('input_hint')}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;
