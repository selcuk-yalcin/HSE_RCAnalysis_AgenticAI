import React, { useState, useEffect } from 'react';
import { Sun, Moon, ChevronDown, ChevronUp, Plus, Trash2 } from 'lucide-react';
import './SmartQuestionnaire_V2.css';

/**
 * SMART QUESTIONNAIRE V2
 * ========================
 * - Genel Sorular (15 temel soru - tüm olaylar)
 * - Detaylı Analiz sekmesi (koşullu, açılı-kapanabilir)
 * - Light/Dark Mode seçeneği
 * - Taxonomy otomatik bağlama
 */

const SmartQuestionnaire_V2 = ({ incidentData, onComplete }) => {
  // ========================================================================
  // STATE
  // ========================================================================
  const [activeTab, setActiveTab] = useState('general'); // 'general' | 'detailed'
  const [darkMode, setDarkMode] = useState(false);
  const [answers, setAnswers] = useState({});
  const [detectedCodes, setDetectedCodes] = useState(new Set());
  const [expandedSections, setExpandedSections] = useState({});
  const [questionsAnswered, setQuestionsAnswered] = useState(0);

  // ========================================================================
  // GENEL SORULAR (15 SORU - TÜM OLAYLAR)
  // ========================================================================
  const generalQuestions = [
    {
      id: 'g1',
      question: 'Olayın Özeti Nedir?',
      type: 'textarea',
      category: 'Temel',
      description: 'Ne oldu, nerede, ne zaman, kim etkilendi?',
      placeholder: 'Kısaca olayı özetleyin...'
    },
    {
      id: 'g2',
      question: 'Olay Ne Zaman Gerçekleşti?',
      type: 'datetime',
      category: 'Temel',
      description: 'Tarih ve saat?'
    },
    {
      id: 'g3',
      question: 'Olay Nerede Gerçekleşti?',
      type: 'text',
      category: 'Konum',
      description: 'Tesis, bölüm, spesifik yer',
      placeholder: 'Üretim hattı A, Depo 3, vb.'
    },
    {
      id: 'g4',
      question: 'Etkilenen Personel Bilgileri',
      type: 'text',
      category: 'Personel',
      description: 'Ad, ünvan, deneyim',
      placeholder: 'Ahmet Çelik - Operatör - 2 yıl'
    },
    {
      id: 'g5',
      question: 'Olayın Türü Nedir?',
      type: 'select',
      category: 'Sınıflandırma',
      options: [
        'İş Kazası',
        'Ramak Kala (Near Miss)',
        'Çevre Olayı',
        'Mülkiyet Hasarı',
        'Diğer'
      ]
    },
    {
      id: 'g6',
      question: 'Yaralanma/Hasar Şiddeti',
      type: 'select',
      category: 'Şiddet',
      options: [
        'İlk Yardım (Hafif)',
        'Tedavi Gerektiren (Orta)',
        'Hastaneye Yatış',
        'Kalıcı Hasar',
        'Ölümlü',
        'Hasar Yok'
      ]
    },
    {
      id: 'g7',
      question: 'Prosedür/İş Talimatı Var Mıydı?',
      type: 'select',
      category: 'Sistem',
      options: [
        'Hayır, yoktu',
        'Vardı ama bilinmiyordu',
        'Vardı ve biliniyordu',
        'Vardı ama uygulanmıyordu'
      ],
      taxonomy: ['D9.1', 'D9.3', 'D9.5']
    },
    {
      id: 'g8',
      question: 'Eğitim Verilmiş Miydi?',
      type: 'select',
      category: 'Personel',
      options: [
        'Hayır',
        'Genel eğitim var ama spesifik yoktu',
        'Evet, spesifik eğitim vardı'
      ],
      taxonomy: ['D3.1', 'D3.2']
    },
    {
      id: 'g9',
      question: 'Risk Değerlendirmesi Yapılmış Mıydı?',
      type: 'select',
      category: 'Yönetim',
      options: [
        'Hayır',
        'Yapıldı ama kontroller uygulanmadı',
        'Yapıldı ve kontroller takip edildi'
      ],
      taxonomy: ['D4.1', 'D4.2']
    },
    {
      id: 'g10',
      question: 'Denetim/Gözetim Var Mıydı?',
      type: 'select',
      category: 'Yönetim',
      options: [
        'Hayır',
        'Kısmen',
        'Evet, tam denetim vardı'
      ],
      taxonomy: ['D1.2']
    },
    {
      id: 'g11',
      question: 'KKD (Kişisel Koruyucu Donanım) Yeterli Miydi?',
      type: 'select',
      category: 'Koruma',
      options: [
        'Gerekli değildi',
        'Gerekli ama sağlanmadı',
        'Sağlandı ama kullanılmadı',
        'Sağlandı ve kullanıldı'
      ],
      taxonomy: ['A3.1', 'A3.2', 'A3.4']
    },
    {
      id: 'g12',
      question: 'İletişim Sorun Var Mıydı?',
      type: 'select',
      category: 'İletişim',
      options: [
        'Evet, önemli iletişim kopukluğu',
        'Kısmen, talimatlar açık değildi',
        'Hayır, iletişim açıktı'
      ],
      taxonomy: ['D2.1', 'D2.2']
    },
    {
      id: 'g13',
      question: 'Benzer Olay Daha Önce Yaşandı Mı?',
      type: 'select',
      category: 'Sistem',
      options: [
        'Evet, benzer olaylar yaşandı',
        'Ramak kala (near miss) var',
        'Hayır, bu ilk'
      ],
      taxonomy: ['D1.3']
    },
    {
      id: 'g14',
      question: 'Acil Müdahale/Ilk Yardım Yeterli Miydi?',
      type: 'select',
      category: 'Müdahale',
      options: [
        'Hayır, yetersizdi',
        'Kısmen yapıldı',
        'Evet, profesyonel müdahale yapıldı'
      ]
    },
    {
      id: 'g15',
      question: 'Ek Açıklamalar',
      type: 'textarea',
      category: 'Diğer',
      description: 'Önemli detaylar, tanık ifadeleri, vb.',
      placeholder: 'Başka dikkat çeken noktalar...'
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
          <h1>🎯 Akıllı Soruşturma Sistemi</h1>
          <p>Olay hakkında sistemli bilgi toplayarak kök nedene ulaşın</p>
        </div>

        <div className="header-right">
          {/* Theme Toggle */}
          <button
            className="theme-toggle"
            onClick={() => setDarkMode(!darkMode)}
            title={darkMode ? 'Aydınlık Mod' : 'Karanlık Mod'}
          >
            {darkMode ? <Sun size={20} /> : <Moon size={20} />}
          </button>

          {/* Progress */}
          <div className="progress-indicator">
            <span className="progress-text">
              {questionsAnswered} / {generalQuestions.length} Soru
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
          <span className="tab-label">Genel Sorular</span>
          <span className="tab-badge">{generalQuestions.length}</span>
        </button>

        <button
          className={`tab-button ${activeTab === 'detailed' ? 'active' : ''}`}
          onClick={() => setActiveTab('detailed')}
        >
          <span className="tab-icon">🔍</span>
          <span className="tab-label">Detaylı Analiz</span>
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
                      <option value="">-- Seçiniz --</option>
                      {question.options.map((option) => (
                        <option key={option} value={option}>
                          {option}
                        </option>
                      ))}
                    </select>
                  )}

                  {question.taxonomy && answers[question.id] && (
                    <div className="taxonomy-hint">
                      🏷️ <strong>Kodlar:</strong> {question.taxonomy.join(', ')}
                    </div>
                  )}
                </div>
              ))}
            </div>

            {/* Detected Codes Summary */}
            {detectedCodes.size > 0 && (
              <div className="detected-codes-panel">
                <h4>📌 Otomatik Tespit Edilen Kodlar</h4>
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
                <p>📋 Henüz detaylı analiz bölümü yok.</p>
                <p>Genel sorularda daha fazla bilgi girerek detaylı seçenekler görün.</p>
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
          🔄 Sıfırla
        </button>
        <button className="btn-primary" onClick={handleComplete}>
          ✅ Soruşturmayı Tamamla
        </button>
      </div>
    </div>
  );
};

export default SmartQuestionnaire_V2;
