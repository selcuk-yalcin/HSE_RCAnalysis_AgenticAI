import React, { useState } from 'react';
import { Sun, Moon, ChevronDown, Plus, Trash2 } from 'lucide-react';
import './SmartQuestionnaire_V2.css';

/**
 * SMART QUESTIONNAIRE V2 - UPDATED
 * ===================================
 * 24 Düzeltilmiş Genel Soru + Detaylı Analiz
 * Gramer ve Anlam İyileştirilmiş
 * HSG245 Knowledge Base Uyumlu
 */

const SmartQuestionnaire_V2 = ({ onComplete, isDarkMode: parentDarkMode }) => {
  // ===== STATE =====
  const isDarkMode = parentDarkMode || false;
  const [activeTab, setActiveTab] = useState('general');
  const [answers, setAnswers] = useState({});
  const [expandedSections, setExpandedSections] = useState({});

  // ===== 24 DÜZELTILMIŞ GENEL SORULAR =====
  const generalQuestions = [
    // BÖLÜM 1: NEREDE, NE ZAMAN, KİM
    {
      id: 'q1',
      order: 1,
      category: 'Temel Bilgiler',
      question: 'Olay nerede ve ne zaman gerçekleşti?',
      type: 'textarea',
      placeholder: 'Yer, tarih ve saat bilgisini giriniz...',
      description: 'Tesis, bölüm, spesifik yer ve tam tarih-saat'
    },
    {
      id: 'q2',
      order: 2,
      category: 'Temel Bilgiler',
      question: 'Olayda kim yaralandı, hastalandı veya etkilendi?',
      type: 'textarea',
      placeholder: 'Kişi sayısı, adları, görevleri giriniz...',
      description: 'Ad, ünvan, deneyim, yaş grubu, sayı'
    },
    // BÖLÜM 2: AYRINTI - NEYİ VE NASIL
    {
      id: 'q3',
      order: 3,
      category: 'Olay Detayları',
      question: 'Olay nasıl gerçekleşti? Dahil olan ekipmanları belirtiniz.',
      type: 'textarea',
      placeholder: 'Olay süreci ve kullanılan ekipmanları açıklayınız...',
      description: 'Olay sırasını adım adım, ilgili ekipmanları listeleyin'
    },
    {
      id: 'q4',
      order: 4,
      category: 'Olay Detayları',
      question: 'O sırada hangi faaliyetler/işler gerçekleştiriliyordu?',
      type: 'textarea',
      placeholder: 'Yapılan işlerin adımlarını açıklayınız...',
      description: 'Yapılan işlem, prosedür, kullanılan yöntem'
    },
    {
      id: 'q5',
      order: 5,
      category: 'Olay Detayları',
      question: 'Çalışma koşullarında olağandışı veya farklı bir durum var mıydı?',
      type: 'select',
      options: ['Evet', 'Hayır', 'Bilinmiyor'],
      description: 'Sıcaklık, nem, gürültü, aydınlatma, temizlik vb.'
    },
    {
      id: 'q6',
      order: 6,
      category: 'Prosedür ve Kontrol',
      question: 'Güvenli çalışma prosedürleri (GÇP) yeterli miydi ve uygulanıyor muydu?',
      type: 'select',
      options: [
        'Prosedür yok',
        'Prosedür var ama yetersiz',
        'Prosedür yeterli ama uygulanmıyor',
        'Prosedür var ve uygulanıyor'
      ],
      description: 'Yazılı prosedür varlığı ve uygulanması'
    },
    {
      id: 'q7',
      order: 7,
      category: 'Yaralanma',
      question: 'Olay ne tür yaralanma veya sağlık sorunlarına neden oldu?',
      type: 'textarea',
      placeholder: 'Yaralanma türü, ciddiyet ve sağlık etkileri...',
      description: 'Kesik, çürük, kırık, yanık, zehirlenme vb.'
    },
    {
      id: 'q8',
      order: 8,
      category: 'Yaralanma',
      question: 'Yaralanma mekanizması neydi ve buna ne sebep oldu?',
      type: 'textarea',
      placeholder: 'Yaralanma süreci ve temel sebebini açıklayınız...',
      description: 'Enerji transferi, etki alanı, ısı transferi vb.'
    },
    {
      id: 'q9',
      order: 9,
      category: 'Risk Bilinci',
      question: 'Risk önceden biliniyordu mu? Eğer öyleyse, neden kontrol edilmedi?',
      type: 'select',
      options: [
        'Risk bilinmiyor',
        'Risk biliniyordu ama göz ardı edildi',
        'Risk biliniyordu ama kontrol edilmedi (bütçe/kaynak)',
        'Risk biliniyordu ve kontrol edildi'
      ],
      description: 'Risk tanımlanması ve yönetimi durumu'
    },
    // BÖLÜM 3: ORGANİZASYON VE ÇEVRE
    {
      id: 'q10',
      order: 10,
      category: 'Organizasyon',
      question: 'Organizasyon ve çalışmanın yapılandırılması olayı etkiledi mi?',
      type: 'select',
      options: ['Evet', 'Hayır', 'Kısmen', 'Bilinmiyor'],
      description: 'Yönetim yapısı, sorumluluklar açık mı?'
    },
    {
      id: 'q11',
      order: 11,
      category: 'Bakım ve Temizlik',
      question: 'Bakım ve temizlik yeterli miydi? Değilse, neden?',
      type: 'select',
      options: [
        'Bakım ve temizlik yeterli',
        'Bakım yetmez / Prosedür yok',
        'Temizlik yetmez / Prosedür yok',
        'Her ikisi de yetmez'
      ],
      description: 'Bakım ve temizlik standartları'
    },
    {
      id: 'q12',
      order: 12,
      category: 'Personel',
      question: 'Dahil olan kişiler yetkin ve uygun muydu?',
      type: 'select',
      options: [
        'Evet, yetkin ve eğitimli',
        'Kısmen eğitimli',
        'Eğitimsiz',
        'Bilinmiyor'
      ],
      description: 'Personel eğitim ve yetkinlik seviyeleri'
    },
    {
      id: 'q13',
      order: 13,
      category: 'İşyeri',
      question: 'İşyeri düzeni olayı etkiledi mi?',
      type: 'textarea',
      placeholder: 'Çalışma alanı organize mı? Tehlikeli mı?',
      description: 'Geçit yolları, korkuluklar, bariyerler, aydınlatma vb.'
    },
    {
      id: 'q14',
      order: 14,
      category: 'Malzeme',
      question: 'Malzemelerin niteliği veya durumu olayı etkiledi mi?',
      type: 'textarea',
      placeholder: 'Kusurlu/bozuk malzeme var mıydı?',
      description: 'Kimyasal özellikleri, sıcaklığı, keskinliği, ağırlığı vb.'
    },
    {
      id: 'q15',
      order: 15,
      category: 'Ekipman',
      question: 'Tesis ve ekipmanı kullanmada yaşanan zorluklar olayı etkiledi mi?',
      type: 'textarea',
      placeholder: 'Ekipman arızası, kullanım güçlüğü vb...',
      description: 'Tasarım sorunları, HMI, ergonomi vb.'
    },
    {
      id: 'q16',
      order: 16,
      category: 'KKD',
      question: 'Kişisel koruyucu donanım (KKD) yeterli miydi?',
      type: 'select',
      options: [
        'KKD yeterli ve uygun',
        'KKD yeterli ama uygun değil',
        'KKD yetersiz',
        'KKD kullanılmadı'
      ],
      description: 'Koruyucu donanım durumu'
    },
    {
      id: 'q17',
      order: 17,
      category: 'Diğer Faktörler',
      question: 'Diğer hangi koşullar olayı etkiledi?',
      type: 'textarea',
      placeholder: 'Hava durumu, zaman baskısı, stres, yorgunluk vb...',
      description: 'İnsan faktörleri, çevresel koşullar vb.'
    },
    // BÖLÜM 4: KÖK NEDEN VE KONTROL
    {
      id: 'q18',
      order: 18,
      category: 'Kök Neden',
      question: 'Doğrudan, altta yatan ve kök nedenler nelerdi?',
      type: 'textarea',
      placeholder: 'Doğrudan sebep → Sistem eksikliği → Kök neden zinciri...',
      description: '5 Neden, HAZOP veya HSG245 taxonomy kullanın'
    },
    {
      id: 'q19',
      order: 19,
      category: 'Kontrol Önlemleri',
      question: 'Hangi risk kontrol önlemleri gereklidir?',
      type: 'textarea',
      placeholder: 'Acil, kısa vadeli ve uzun vadeli önlemler...',
      description: 'Hiyerarşik kontrol: Eleme > Değiştirme > Mühendislik > Yönetim > KKD'
    },
    {
      id: 'q20',
      order: 20,
      category: 'Benzer Riskler',
      question: 'Başka yerlerde benzer riskler var mı? Varsa nerede?',
      type: 'textarea',
      placeholder: 'Diğer departmanlar, benzer görevler vb...',
      description: 'Diğer tesisler, vardiyalar, benzeri operasyonlar'
    },
    {
      id: 'q21',
      order: 21,
      category: 'Geçmiş Olaylar',
      question: 'Daha önce benzer olaylar yaşandı mı? Detayları nelerdir?',
      type: 'textarea',
      placeholder: 'Tarih, ne oldu, hangi önlemler alındı...',
      description: 'Geçmiş ramak kala, kazalar, eğilimler'
    },
    {
      id: 'q22',
      order: 22,
      category: 'Eylem Planı',
      question: 'Kısa ve uzun vadede hangi kontrol önlemleri uygulanmalıdır?',
      type: 'textarea',
      placeholder: 'Acil (24s), kısa vadeli (1ay), uzun vadeli (3-6ay)...',
      description: 'Kimlerin sorumlu, bütçe, tarih, izleme'
    },
    {
      id: 'q23',
      order: 23,
      category: 'Gözden Geçirme',
      question: 'Hangi risk değerlendirmeleri ve prosedürler gözden geçirilmeli?',
      type: 'textarea',
      placeholder: 'Risk değerlendirmesi, GÇP, KKD prosedürleri vb...',
      description: 'Güncellenecek belgeler ve yeni eğitimler'
    },
    {
      id: 'q24',
      order: 24,
      category: 'Belgeleme',
      question: 'Araştırma bulguları kaydedildi mi? Benzer/ortak nedenler var mı?',
      type: 'textarea',
      placeholder: 'Hangi belgeler hazırlandı? Trend analizi yapıldı mı?',
      description: 'Belgeleme durumu ve müteakip araştırma gereksinimleri'
    }
  ];

  // ===== HANDLERS =====
  const handleAnswer = (questionId, value) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: value
    }));
  };

  const handleComplete = () => {
    const questionsAnswered = Object.keys(answers).length;
    if (onComplete) {
      onComplete({
        answers,
        totalQuestionsAnswered: questionsAnswered,
        completionPercentage: (questionsAnswered / generalQuestions.length) * 100
      });
    }
  };

  const progress = (Object.keys(answers).length / generalQuestions.length) * 100;
  const currentQuestion = generalQuestions.filter(q => !answers[q.id])[0] || generalQuestions[0];

  // ===== RENDER =====
  return (
    <div className={`questionnaire-v2 ${isDarkMode ? 'dark' : 'light'}`}>
      {/* Header */}
      <div className="questionnaire-header">
        <div className="header-content">
          <h1>🎯 Genel Soruşturma Formu</h1>
          <p className="header-subtitle">HSG245 Standartlarına Uygun - Düzeltilmiş Soru Seti</p>
        </div>

        {/* Progress */}
        <div className="progress-section">
          <div className="progress-bar">
            <div className="progress-fill" style={{ width: `${progress}%` }}></div>
          </div>
          <p className="progress-text">{Object.keys(answers).length} / {generalQuestions.length} Soru</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="tab-navigation">
        <button
          className={`tab-btn ${activeTab === 'general' ? 'active' : ''}`}
          onClick={() => setActiveTab('general')}
        >
          📋 Genel Sorular (24)
        </button>
        <button
          className={`tab-btn ${activeTab === 'detailed' ? 'active' : ''}`}
          onClick={() => setActiveTab('detailed')}
        >
          📊 Detaylı Analiz
        </button>
      </div>

      {/* Content */}
      <div className="questionnaire-content">
        {activeTab === 'general' && (
          <div className="questions-section">
            <div className="questions-grid">
              {generalQuestions.map((question) => (
                <div key={question.id} className="question-card">
                  <div className="question-meta">
                    <span className="category-badge">{question.category}</span>
                    <span className="question-number">S{question.order}</span>
                  </div>

                  <h3 className="question-title">{question.question}</h3>
                  <p className="question-description">💡 {question.description}</p>

                  {/* Answer Area */}
                  <div className="answer-area">
                    {question.type === 'textarea' && (
                      <textarea
                        className="text-input"
                        placeholder={question.placeholder}
                        value={answers[question.id] || ''}
                        onChange={(e) => handleAnswer(question.id, e.target.value)}
                        rows={3}
                      />
                    )}

                    {question.type === 'select' && (
                      <div className="select-options">
                        {question.options.map((option, idx) => (
                          <button
                            key={idx}
                            className={`option-btn ${answers[question.id] === option ? 'selected' : ''}`}
                            onClick={() => handleAnswer(question.id, option)}
                          >
                            {option}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>

            {/* Action Buttons */}
            <div className="action-buttons">
              <button className="btn-reset" onClick={() => setAnswers({})}>
                🔄 Sıfırla
              </button>
              <button
                className="btn-complete"
                onClick={handleComplete}
                disabled={Object.keys(answers).length === 0}
              >
                ✅ Tamamla
              </button>
            </div>
          </div>
        )}

        {activeTab === 'detailed' && (
          <div className="detailed-section">
            <div className="info-box">
              <h2>📊 Detaylı Analiz Sekmesi</h2>
              <p>
                Genel soruları tamamladıktan sonra, burada detaylı kök neden analizi
                (Fishbone, 5 Neden, Barrier Analysis vb.) yapabilirsiniz.
              </p>
              <div className="placeholder">
                🔧 Geliştirilmekte - Kısa zamanda hazır olacak
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Sidebar Stats */}
      <div className="sidebar-stats">
        <h4>📈 İstatistikler</h4>
        <div className="stat-item">
          <span>Yanıtlanan:</span>
          <strong>{Object.keys(answers).length} / {generalQuestions.length}</strong>
        </div>
        <div className="stat-item">
          <span>Tamamlanma:</span>
          <strong>{Math.round(progress)}%</strong>
        </div>
        <div className="stat-item">
          <span>Kalan:</span>
          <strong>{generalQuestions.length - Object.keys(answers).length}</strong>
        </div>
      </div>
    </div>
  );
};

export default SmartQuestionnaire_V2;
