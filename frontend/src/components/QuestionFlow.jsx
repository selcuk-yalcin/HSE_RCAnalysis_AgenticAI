import React, { useState } from 'react';
import { CheckCircle, XCircle, HelpCircle } from 'lucide-react';
import { getTranslation } from '../utils/translations';
import './QuestionFlow.css';

const QuestionFlow = ({ flowType, language, onAnswer, onComplete }) => {
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState({});

  const t = (key) => getTranslation(language, key);

  // Question templates based on INCIDENT_DATA structure
  const questionFlows = {
    safety_equipment: [
      {
        id: 'fall_protection',
        question: t('q_fall_protection'),
        options: [
          { value: 'yes', label: t('yes'), icon: CheckCircle },
          { value: 'no', label: t('no'), icon: XCircle },
          { value: 'unknown', label: t('unknown'), icon: HelpCircle },
        ],
      },
      {
        id: 'safety_harness',
        question: t('q_safety_harness'),
        options: [
          { value: 'yes', label: t('yes'), icon: CheckCircle },
          { value: 'no', label: t('no'), icon: XCircle },
          { value: 'unknown', label: t('unknown'), icon: HelpCircle },
        ],
      },
      {
        id: 'safety_training',
        question: t('q_safety_training'),
        options: [
          { value: 'yes', label: t('yes'), icon: CheckCircle },
          { value: 'no', label: t('no'), icon: XCircle },
          { value: 'partial', label: t('partial'), icon: HelpCircle },
        ],
      },
    ],
    incident_details: [
      {
        id: 'location',
        question: t('q_location'),
        type: 'text',
      },
      {
        id: 'time',
        question: t('q_time'),
        type: 'text',
      },
      {
        id: 'witnesses',
        question: t('q_witnesses'),
        options: [
          { value: 'yes', label: t('yes'), icon: CheckCircle },
          { value: 'no', label: t('no'), icon: XCircle },
        ],
      },
    ],
  };

  const questions = questionFlows[flowType] || [];
  const currentQuestion = questions[currentQuestionIndex];

  const handleAnswer = (answer) => {
    const newAnswers = {
      ...answers,
      [currentQuestion.id]: answer,
    };
    setAnswers(newAnswers);
    onAnswer(answer);

    // Move to next question or complete
    if (currentQuestionIndex < questions.length - 1) {
      setTimeout(() => {
        setCurrentQuestionIndex(currentQuestionIndex + 1);
      }, 500);
    } else {
      setTimeout(() => {
        onComplete(newAnswers);
      }, 500);
    }
  };

  if (!currentQuestion) return null;

  return (
    <div className="question-flow">
      <div className="question-progress">
        <div className="progress-bar">
          <div 
            className="progress-fill"
            style={{ width: `${((currentQuestionIndex + 1) / questions.length) * 100}%` }}
          />
        </div>
        <span className="progress-text">
          {currentQuestionIndex + 1} / {questions.length}
        </span>
      </div>

      <div className="question-card">
        <h3 className="question-text">{currentQuestion.question}</h3>

        {currentQuestion.type === 'text' ? (
          <div className="text-answer">
            <input
              type="text"
              placeholder={t('type_answer')}
              onKeyPress={(e) => {
                if (e.key === 'Enter' && e.target.value.trim()) {
                  handleAnswer(e.target.value);
                  e.target.value = '';
                }
              }}
              autoFocus
            />
          </div>
        ) : (
          <div className="question-options">
            {currentQuestion.options.map((option) => {
              const Icon = option.icon;
              return (
                <button
                  key={option.value}
                  className="option-btn"
                  onClick={() => handleAnswer(option.value)}
                >
                  <Icon size={20} />
                  <span>{option.label}</span>
                </button>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default QuestionFlow;
