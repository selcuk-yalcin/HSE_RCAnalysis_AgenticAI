import React, { useState, useEffect } from 'react';
import { Sun, Moon, ChevronDown, ChevronUp, Plus, Trash2 } from 'lucide-react';
import { getTranslation } from '../utils/translations';
import './SmartQuestionnaire_V2.css';

/**
 * SMART QUESTIONNAIRE V2
 * ========================
 * - Genel Sorular (15 temel soru - tüm olaylar)
 * - Detaylı Analiz sekmesi (koşullu, açılı-kapanabilir)
 * - Light/Dark Mode seçeneği
 * - Taxonomy otomatik bağlama
 * - Multi-language support
 */

const SmartQuestionnaire_V2 = ({ language = 'tr', incidentData, onComplete }) => {
  // ========================================================================
  // STATE
  // ========================================================================
  const [activeTab, setActiveTab] = useState('general'); // 'general' | 'detailed'
  const [darkMode, setDarkMode] = useState(false);
  const [answers, setAnswers] = useState({});
  const [detectedCodes, setDetectedCodes] = useState(new Set());
  const [expandedSections, setExpandedSections] = useState({});
  const [questionsAnswered, setQuestionsAnswered] = useState(0);

  const t = (key) => getTranslation(language, key);

  // ========================================================================
  // GENEL SORULAR (15 SORU - TÜM OLAYLAR)
  // ========================================================================
  const generalQuestions = [
    {
      id: 'g1',
      question: t('incident_summary'),
      type: 'textarea',
      category: t('category_basic'),
      description: t('incident_summary_desc'),
      placeholder: t('incident_summary_placeholder')
    },
    {
      id: 'g2',
      question: t('incident_when'),
      type: 'datetime',
      category: t('category_basic'),
      description: t('incident_when_desc')
    },
    {
      id: 'g3',
      question: t('incident_where'),
      type: 'text',
      category: t('category_location'),
      description: t('incident_where_desc'),
      placeholder: t('incident_where_placeholder')
    },
    {
      id: 'g4',
      question: t('affected_personnel'),
      type: 'text',
      category: t('category_personnel'),
      description: t('affected_personnel_desc'),
      placeholder: t('affected_personnel_placeholder')
    },
    {
      id: 'g5',
      question: t('incident_type'),
      type: 'select',
      category: t('category_classification'),
      options: [
        t('incident_type_work_accident'),
        t('incident_type_near_miss'),
        t('incident_type_environmental'),
        t('incident_type_property'),
        t('incident_type_other')
      ]
    },
    {
      id: 'g6',
      question: t('injury_severity_level'),
      type: 'select',
      category: t('category_severity'),
      options: [
        t('injury_first_aid'),
        t('injury_medical'),
        t('injury_lost_time'),
        t('injury_permanent'),
        t('injury_fatal'),
        t('no') + ' ' + t('injury_type')
      ]
    },
    {
      id: 'g7',
      question: t('procedure_available'),
      type: 'select',
      category: t('category_system'),
      options: [
        t('procedure_no'),
        t('procedure_unknown'),
        t('procedure_known'),
        t('procedure_not_followed')
      ],
      taxonomy: ['D9.1', 'D9.3', 'D9.5']
    },
    {
      id: 'g8',
      question: t('training_provided'),
      type: 'select',
      category: t('category_personnel'),
      options: [
        t('training_no'),
        t('training_general'),
        t('training_specific')
      ],
      taxonomy: ['D3.1', 'D3.2']
    },
    {
      id: 'g9',
      question: t('risk_assessment'),
      type: 'select',
      category: t('category_management'),
      options: [
        t('risk_no'),
        t('risk_not_applied'),
        t('risk_applied')
      ],
      taxonomy: ['D4.1', 'D4.2']
    },
    {
      id: 'g10',
      question: t('supervision'),
      type: 'select',
      category: t('category_management'),
      options: [
        t('supervision_no'),
        t('supervision_partial'),
        t('supervision_full')
      ],
      taxonomy: ['D1.2']
    },
    {
      id: 'g11',
      question: t('ppe_adequate'),
      type: 'select',
      category: t('category_protection'),
      options: [
        t('ppe_not_needed'),
        t('ppe_not_provided'),
        t('ppe_not_used'),
        t('ppe_used')
      ],
      taxonomy: ['A3.1', 'A3.2', 'A3.4']
    },
    {
      id: 'g12',
      question: t('communication_issue'),
      type: 'select',
      category: t('category_communication'),
      options: [
        t('communication_major'),
        t('communication_unclear'),
        t('communication_clear')
      ],
      taxonomy: ['D2.1', 'D2.2']
    },
    {
      id: 'g13',
      question: t('similar_incident'),
      type: 'select',
      category: t('category_system'),
      options: [
        t('similar_yes'),
        t('similar_near_miss'),
        t('similar_first')
      ],
      taxonomy: ['D1.3']
    },
    {
      id: 'g14',
      question: t('emergency_response'),
      type: 'select',
      category: t('category_response'),
      options: [
        t('emergency_inadequate'),
        t('emergency_partial'),
        t('emergency_professional')
      ]
    },
    {
      id: 'g15',
      question: t('additional_comments'),
      type: 'textarea',
      category: t('category_other'),
      description: t('additional_comments_desc'),
      placeholder: t('additional_comments_placeholder')
    }
  ];

  // ========================================================================
  // DETAYLI ANALIZ SEKTÖRLERİ (Koşullu, açılı-kapanabilir)
  // ========================================================================
  const detailedAnalysisSections = [
    {
      id: 'confined-space',
      title: '🔒 Kapalı Alan (Confined Space)',
      condition: (answers) => answers.g3?.toLowerCase().includes('kapalı') || answers.g3?.toLowerCase().includes('tank'),
      questions: [
        { id: 'cs1', q: 'Permit sistemi uygulandı mı?', type: 'select', options: ['Hayır', 'Kısmen', 'Evet'] },
        { id: 'cs2', q: 'Atmosfer testi yapıldı mı?', type: 'select', options: ['Hayır', 'Kısmen', 'Evet'] },
        { id: 'cs3', q: 'Gözcü personel var mıydı?', type: 'select', options: ['Hayır', 'Kısmen', 'Evet'] },
        { id: 'cs4', q: 'Kurtarma ekipmanı hazırlanmış mıydı?', type: 'select', options: ['Hayır', 'Vardı ama erişilmez', 'Evet'] }
      ]
    },
    {
      id: 'loto',
      title: '🔌 Lockout-Tagout (LOTO)',
      condition: (answers) => answers.g3?.toLowerCase().includes('makine') || answers.g3?.toLowerCase().includes('ekipman'),
      questions: [
        { id: 'loto1', q: 'LOTO prosedürü uygulandı mı?', type: 'select', options: ['Hayır', 'Kısmen', 'Evet'] },
        { id: 'loto2', q: 'Tüm enerji kaynakları bloke edildi mi?', type: 'select', options: ['Hayır', 'Kısmen', 'Evet'] },
        { id: 'loto3', q: 'Lock açma yetkisi kime aitti?', type: 'text', placeholder: 'İSG Uzmanı, Şef, vb.' },
        { id: 'loto4', q: 'Güvenlik kontrolü yapıldı mı?', type: 'select', options: ['Hayır', 'Kısmen', 'Evet'] }
      ]
    },
    {
      id: 'height-work',
      title: '⬆️ Yüksekte Çalışma',
      condition: (answers) => answers.g3?.toLowerCase().includes('yüksek') || answers.g3?.toLowerCase().includes('iskele'),
      questions: [
        { id: 'hw1', q: 'Emniyet kemeri/Halat sistemi var mıydı?', type: 'select', options: ['Hayır', 'Vardı ama kullanılmadı', 'Evet, kullanıldı'] },
        { id: 'hw2', q: 'Çalışma yüksekliği ne kadardı?', type: 'text', placeholder: 'Metre cinsinden' },
        { id: 'hw3', q: 'Iskele/Platform durumu neydi?', type: 'select', options: ['Hasarlı', 'Normal', 'İyi'] },
        { id: 'hw4', q: 'Hava durumu nasıldı?', type: 'text', placeholder: 'Rüzgarlı, yağmurlu, vb.' }
      ]
    },
    {
      id: 'chemical',
      title: '⚗️ Kimyasal İşlem',
      condition: (answers) => answers.g3?.toLowerCase().includes('kimya') || answers.g3?.toLowerCase().includes('endüstri'),
      questions: [
        { id: 'ch1', q: 'Kimyasal madde MSDS (Güvenlik Bilgi Formu) mevcut miydi?', type: 'select', options: ['Hayır', 'Vardı ama personel bilmiyordu', 'Evet, personel biliyordu'] },
        { id: 'ch2', q: 'Havalandırma yeterli miydi?', type: 'select', options: ['Hayır', 'Kısmen', 'Evet'] },
        { id: 'ch3', q: 'Uygun KKD kullanıldı mı?', type: 'select', options: ['Hayır', 'Kısmen', 'Evet'] },
        { id: 'ch4', q: 'İlk yardım ekipmanı uygun muydu?', type: 'select', options: ['Hayır', 'Kısmen', 'Evet'] }
      ]
    },
    {
      id: 'ergonomics',
      title: '🏋️ Ergonomi / Tekrarlayan Hareket',
      condition: (answers) => answers.g3?.toLowerCase().includes('montaj') || answers.g3?.toLowerCase().includes('taşıma'),
      questions: [
        { id: 'erg1', q: 'İş istasyonu ergonomik miydi?', type: 'select', options: ['Hayır', 'Kısmen', 'Evet'] },
        { id: 'erg2', q: 'Çalışma süresi kaç saat?', type: 'text', placeholder: '8, 10 saat, vb.' },
        { id: 'erg3', q: 'Mola/Dinlenme süresi yeterli miydi?', type: 'select', options: ['Hayır', 'Kısmen', 'Evet'] },
        { id: 'erg4', q: 'Mekanik yardımcı araçlar var mıydı?', type: 'select', options: ['Hayır', 'Vardı ama kullanılmadı', 'Evet, kullanıldı'] }
      ]
    }
  ];

  // ========================================================================
  // HELPER FUNCTIONS
  // ========================================================================

  const handleGeneralAnswer = (questionId, value) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: value
    }));

    // Taxonomy otomatik bağlama
    const question = generalQuestions.find(q => q.id === questionId);
    if (question?.taxonomy && value !== '') {
      question.taxonomy.forEach(code => {
        setDetectedCodes(prev => new Set([...prev, code]));
      });
    }

    // Cevaplanan soru sayısını güncelle
    const answered = Object.keys(answers).length + 1;
    setQuestionsAnswered(answered);
  };

  const handleDetailedAnswer = (sectionId, questionId, value) => {
    setAnswers(prev => ({
      ...prev,
      [`${sectionId}-${questionId}`]: value
    }));
  };

  const toggleSection = (sectionId) => {
    setExpandedSections(prev => ({
      ...prev,
      [sectionId]: !prev[sectionId]
    }));
  };

  const getVisibleDetailedSections = () => {
    return detailedAnalysisSections.filter(section => section.condition(answers));
  };

  const handleComplete = () => {
    onComplete({
      answers,
      detectedCodes: Array.from(detectedCodes),
      totalQuestionsAnswered: questionsAnswered
    });
  };

  // ========================================================================
  // RENDER
  // ========================================================================

  return (
    <div className={`smart-questionnaire-v2`} data-theme={darkMode ? 'dark' : 'light'}>
      {/* Header */}
      <div className="questionnaire-header">
        <div className="header-left">
          <h1>🎯 {t('smart_investigation_system')}</h1>
          <p>{t('systematic_info_collection')}</p>
        </div>

        <div className="header-right">
          {/* Theme Toggle */}
          <button
            className="theme-toggle"
            onClick={() => setDarkMode(!darkMode)}
            title={darkMode ? t('light_mode') : t('dark_mode')}
          >
            {darkMode ? <Sun size={20} /> : <Moon size={20} />}
          </button>

          {/* Progress */}
          <div className="progress-indicator">
            <span className="progress-text">
              {questionsAnswered} / {generalQuestions.length} {t('questions_answered')}
            </span>
            <div className="progress-bar">
              <div
                className="progress-fill"
                style={{
                  width: `${(questionsAnswered / generalQuestions.length) * 100}%`
                }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="tab-navigation">
        <button
          className={`tab-button ${activeTab === 'general' ? 'active' : ''}`}
          onClick={() => setActiveTab('general')}
        >
          <span className="tab-icon">📋</span>
          <span className="tab-label">{t('general_questions')}</span>
          <span className="tab-badge">{generalQuestions.length}</span>
        </button>

        <button
          className={`tab-button ${activeTab === 'detailed' ? 'active' : ''}`}
          onClick={() => setActiveTab('detailed')}
        >
          <span className="tab-icon">🔍</span>
          <span className="tab-label">{t('detailed_analysis')}</span>
          <span className="tab-badge">{getVisibleDetailedSections().length}</span>
        </button>
      </div>

      {/* Content */}
      <div className="questionnaire-content">
        {/* TAB 1: GENEL SORULAR */}
        {activeTab === 'general' && (
          <div className="tab-content general-questions">
            <div className="questions-grid">
              {generalQuestions.map((question, idx) => (
                <div key={question.id} className="question-card">
                  <div className="question-header">
                    <h3 className="question-title">
                      <span className="question-number">{idx + 1}</span>
                      {question.question}
                    </h3>
                    <span className="category-badge">{question.category}</span>
                  </div>

                  {question.description && (
                    <p className="question-description">{question.description}</p>
                  )}

                  {/* Input Types */}
                  {question.type === 'text' && (
                    <input
                      type="text"
                      className="form-input"
                      placeholder={question.placeholder || ''}
                      value={answers[question.id] || ''}
                      onChange={(e) => handleGeneralAnswer(question.id, e.target.value)}
                    />
                  )}

                  {question.type === 'textarea' && (
                    <textarea
                      className="form-textarea"
                      placeholder={question.placeholder || ''}
                      value={answers[question.id] || ''}
                      onChange={(e) => handleGeneralAnswer(question.id, e.target.value)}
                      rows="3"
                    />
                  )}

                  {question.type === 'datetime' && (
                    <div className="datetime-inputs">
                      <input
                        type="date"
                        className="form-input"
                        value={answers[`${question.id}-date`] || ''}
                        onChange={(e) => handleGeneralAnswer(`${question.id}-date`, e.target.value)}
                      />
                      <input
                        type="time"
                        className="form-input"
                        value={answers[`${question.id}-time`] || ''}
                        onChange={(e) => handleGeneralAnswer(`${question.id}-time`, e.target.value)}
                      />
                    </div>
                  )}

                  {question.type === 'select' && (
                    <select
                      className="form-select"
                      value={answers[question.id] || ''}
                      onChange={(e) => handleGeneralAnswer(question.id, e.target.value)}
                    >
                      <option value="">{t('select_placeholder')}</option>
                      {question.options.map((option) => (
                        <option key={option} value={option}>
                          {option}
                        </option>
                      ))}
                    </select>
                  )}

                  {question.taxonomy && answers[question.id] && (
                    <div className="taxonomy-hint">
                      🏷️ <strong>{t('auto_detected_codes').split(' ')[2]}:</strong> {question.taxonomy.join(', ')}
                    </div>
                  )}
                </div>
              ))}
            </div>

            {/* Detected Codes Summary */}
            {detectedCodes.size > 0 && (
              <div className="detected-codes-panel">
                <h4>📌 {t('auto_detected_codes')}</h4>
                <div className="codes-list">
                  {Array.from(detectedCodes)
                    .sort()
                    .map((code) => (
                      <span key={code} className="code-tag">
                        {code}
                      </span>
                    ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* TAB 2: DETAYLI ANALIZ */}
        {activeTab === 'detailed' && (
          <div className="tab-content detailed-analysis">
            {getVisibleDetailedSections().length === 0 ? (
              <div className="no-sections">
                <p>📋 {t('no_detailed_sections')}</p>
                <p>{t('enter_more_info')}</p>
              </div>
            ) : (
              getVisibleDetailedSections().map((section) => (
                <div key={section.id} className="detail-section">
                  {/* Section Header */}
                  <button
                    className="section-header-button"
                    onClick={() => toggleSection(section.id)}
                  >
                    <span className="section-title">{section.title}</span>
                    <span className="section-toggle">
                      {expandedSections[section.id] ? (
                        <ChevronUp size={20} />
                      ) : (
                        <ChevronDown size={20} />
                      )}
                    </span>
                  </button>

                  {/* Section Questions */}
                  {expandedSections[section.id] && (
                    <div className="section-questions">
                      {section.questions.map((q) => (
                        <div key={q.id} className="detail-question">
                          <label className="detail-question-label">{q.q}</label>

                          {q.type === 'select' && (
                            <select
                              className="form-select detail"
                              value={answers[`${section.id}-${q.id}`] || ''}
                              onChange={(e) =>
                                handleDetailedAnswer(section.id, q.id, e.target.value)
                              }
                            >
                              <option value="">-- Seçiniz --</option>
                              {q.options.map((opt) => (
                                <option key={opt} value={opt}>
                                  {opt}
                                </option>
                              ))}
                            </select>
                          )}

                          {q.type === 'text' && (
                            <input
                              type="text"
                              className="form-input detail"
                              placeholder={q.placeholder || ''}
                              value={answers[`${section.id}-${q.id}`] || ''}
                              onChange={(e) =>
                                handleDetailedAnswer(section.id, q.id, e.target.value)
                              }
                            />
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="questionnaire-footer">
        <button
          className="btn-secondary"
          onClick={() => {
            setAnswers({});
            setDetectedCodes(new Set());
            setQuestionsAnswered(0);
          }}
        >
          🔄 {t('reset_form')}
        </button>
        <button className="btn-primary" onClick={handleComplete}>
          ✅ {t('complete_investigation')}
        </button>
      </div>
    </div>
  );
};

export default SmartQuestionnaire_V2;
