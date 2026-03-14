import React from 'react';
import { User, Bot, AlertTriangle, CheckCircle } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import './Message.css';

const Message = ({ message, language }) => {
  const { type, content, timestamp, suggestions, analysisId } = message;

  const formatTime = (date) => {
    return new Date(date).toLocaleTimeString(language === 'tr' ? 'tr-TR' : 'en-US', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getIcon = () => {
    switch (type) {
      case 'user':
        return <User size={20} />;
      case 'assistant':
        return <Bot size={20} />;
      case 'error':
        return <AlertTriangle size={20} />;
      case 'success':
        return <CheckCircle size={20} />;
      default:
        return <Bot size={20} />;
    }
  };

  return (
    <div className={`message message-${type}`}>
      <div className="message-icon">
        {getIcon()}
      </div>
      
      <div className="message-content">
        <div className="message-bubble">
          <ReactMarkdown>{content}</ReactMarkdown>
          
          {suggestions && suggestions.length > 0 && (
            <div className="message-suggestions">
              {suggestions.map((suggestion, idx) => (
                <button key={idx} className="suggestion-btn">
                  {suggestion}
                </button>
              ))}
            </div>
          )}

          {analysisId && (
            <div className="analysis-badge">
              <span>Job ID: {analysisId}</span>
            </div>
          )}
        </div>
        
        <div className="message-time">
          {formatTime(timestamp)}
        </div>
      </div>
    </div>
  );
};

export default Message;
