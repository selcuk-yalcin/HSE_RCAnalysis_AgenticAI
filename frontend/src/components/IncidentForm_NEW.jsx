import React, { useState, useEffect, useRef } from 'react';
import { 
  User, AlertTriangle, FileText, Shield, Users, Cloud, 
  Briefcase, Heart, Search, Clock, CheckSquare, AlertCircle, Plus, Trash2
} from 'lucide-react';
import { getTranslation } from '../utils/translations';
import './IncidentForm.css';

const IncidentForm = ({ language = 'tr', onSubmit }) => {
  const [formData, setFormData] = useState({
    // Temel Bilgiler
    reporter: '',
    reportDate: '',
    reportTime: '',
    
    // Olay Detayları
    incidentDate: '',
    incidentTime: '',
    location: '',
    department: '',
    eventCategory: 'Kaza',
    severity: '',
    
    // OLAY AKIŞI (Timeline) - YENİ!
    timeline: [
      { time: '', action: '', responsible: '', evidence: '' }
    ],
    
    // ÖNLEME KONTROL LİSTESİ - YENİ!
    preventionChecklist: {
      riskAssessment: { exists: null, details: '', lastUpdate: '' },
      ptw: { exists: null, number: '', approver: '' },
      toolboxTalk: { exists: null, date: '', participants: '' },
      ppe: { provided: null, used: null, type: '' },
      training: { completed: null, date: '', type: '' },
      inspection: { done: null, date: '', findings: '' },
      procedures: { available: null, followed: null, name: '' }
    },
    
    // 5W1H
    what: '',
    where: '',
    when: '',
    who: '',
    why: '',
    how: '',
    emergencyActions: '',
    
    // Güvenlik Ekipmanları
    ppeDetails: '',
    
    // Tanıklar
    witnesses: '',
    
    // Çevresel Koşullar
    weather: '',
    lighting: '',
    temperature: '',
    
    // Çalışma Koşulları
    workType: '',
    experience: '',
    
    // Yaralanma/Hasar
    injuryType: '',
    injurySeverity: '',
    bodyPart: '',
    
    // KÖK NEDEN + ÖNLEME ÖNERİLERİ
    rootCauses: [
      { category: '', description: '', preventionAction: '', responsible: '', deadline: '' }
    ],
    
    // Ek Notlar
    additionalNotes: ''
  });

  const [activeSection, setActiveSection] = useState(0);
  const sectionRefs = useRef([]);

  const t = (key) => getTranslation(language, key);

  // Section başlıkları
  const sections = [
    { id: 0, title: 'Bildirim Yapan', icon: User },
    { id: 1, title: 'Kaza Detayları', icon: AlertTriangle },
    { id: 2, title: 'Olay Akışı', icon: Clock },
    { id: 3, title: 'Kontrol Listesi', icon: CheckSquare },
    { id: 4, title: 'Olay Açıklaması', icon: FileText },
    { id: 5, title: 'Tanıklar', icon: Users },
    { id: 6, title: 'Çevre Koşulları', icon: Cloud },
    { id: 7, title: 'Çalışma Koşulları', icon: Briefcase },
    { id: 8, title: 'Yaralanma/Hasar', icon: Heart },
    { id: 9, title: 'Kök Neden & Önlemler', icon: AlertCircle }
  ];

  // Scroll spy
  useEffect(() => {
    const handleScroll = () => {
      const scrollPosition = window.scrollY + 150;
      
      for (let i = sections.length - 1; i >= 0; i--) {
        const section = sectionRefs.current[i];
        if (section && section.offsetTop <= scrollPosition) {
          setActiveSection(i);
          break;
        }
      }
    };

    window.addEventListener('scroll', handleScroll);
    handleScroll();
    
    return () => window.removeEventListener('scroll', handleScroll);
  }, [sections.length]);

  const scrollToSection = (sectionId) => {
    const section = sectionRefs.current[sectionId];
    if (section) {
      const yOffset = -100;
      const y = section.getBoundingClientRect().top + window.pageYOffset + yOffset;
      window.scrollTo({ top: y, behavior: 'smooth' });
    }
  };

  // Timeline item ekleme/silme
  const addTimelineItem = () => {
    setFormData({
      ...formData,
      timeline: [...formData.timeline, { time: '', action: '', responsible: '', evidence: '' }]
    });
  };

  const removeTimelineItem = (index) => {
    const newTimeline = formData.timeline.filter((_, i) => i !== index);
    setFormData({ ...formData, timeline: newTimeline });
  };

  // Kök neden ekleme/silme
  const addRootCause = () => {
    setFormData({
      ...formData,
      rootCauses: [...formData.rootCauses, { 
        category: '', description: '', preventionAction: '', responsible: '', deadline: '' 
      }]
    });
  };

  const removeRootCause = (index) => {
    const newCauses = formData.rootCauses.filter((_, i) => i !== index);
    setFormData({ ...formData, rootCauses: newCauses });
  };

  // Prevention checklist güncelleme
  const updateChecklist = (key, field, value) => {
    setFormData({
      ...formData,
      preventionChecklist: {
        ...formData.preventionChecklist,
        [key]: {
          ...formData.preventionChecklist[key],
          [field]: value
        }
      }
    });
  };

  // Test senaryosu yükleme
  const loadTestScenario = async (scenarioName) => {
    // Test senaryoları için placeholder
    console.log('Test senaryosu yüklenecek:', scenarioName);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit && onSubmit(formData);
  };

  return (
    <div className="incident-form-wrapper">
      {/* Sol Navigation Panel */}
      <div className="form-nav-panel">
        <div className="form-nav-header">
          <h3>İŞ KAZASI RAPORU</h3>
        </div>

        {/* Test Senaryoları */}
        <div className="form-nav-tests">
          <div className="test-scenario-label">Hızlı Test</div>
          <div className="test-scenario-buttons">
            <button onClick={() => loadTestScenario('fall')} className="test-scenario-btn">
              Düşme
            </button>
            <button onClick={() => loadTestScenario('electric')} className="test-scenario-btn">
              Elektrik
            </button>
            <button onClick={() => loadTestScenario('machine')} className="test-scenario-btn">
              Makine
            </button>
            <button onClick={() => loadTestScenario('excavation')} className="test-scenario-btn">
              Kazı
            </button>
          </div>
        </div>

        {/* Section Navigation */}
        <div className="form-nav-sections">
          {sections.map((section) => {
            const Icon = section.icon;
            return (
              <div
                key={section.id}
                className={`form-nav-item ${activeSection === section.id ? 'active' : ''}`}
                onClick={() => scrollToSection(section.id)}
              >
                <Icon className="nav-icon" size={18} />
                <span className="nav-text">{section.title}</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Ana Form İçeriği */}
      <div className="form-main-content">
        <div className="incident-form-container">
          <form className="incident-form" onSubmit={handleSubmit}>
            
            {/* SECTION 0: Bildirim Yapan Kişi */}
            <div ref={el => sectionRefs.current[0] = el} className="form-section">
              <div className="section-header">
                <User size={24} />
                <h2>Bildirim Yapan Kişi</h2>
              </div>
              <div className="form-row">
                <div className="form-field">
                  <label>Bildiren <span className="required">*</span></label>
                  <input 
                    type="text" 
                    value={formData.reporter}
                    onChange={(e) => setFormData({...formData, reporter: e.target.value})}
                    placeholder="İsim Soyisim" 
                  />
                </div>
                <div className="form-field">
                  <label>Bildirim Tarihi <span className="required">*</span></label>
                  <input 
                    type="date" 
                    value={formData.reportDate}
                    onChange={(e) => setFormData({...formData, reportDate: e.target.value})}
                  />
                </div>
                <div className="form-field">
                  <label>Bildirim Saati</label>
                  <input 
                    type="time" 
                    value={formData.reportTime}
                    onChange={(e) => setFormData({...formData, reportTime: e.target.value})}
                  />
                </div>
              </div>
            </div>

            {/* SECTION 1: Kaza Detayları */}
            <div ref={el => sectionRefs.current[1] = el} className="form-section">
              <div className="section-header">
                <AlertTriangle size={24} />
                <h2>Kaza Detayları</h2>
              </div>
              <div className="form-row">
                <div className="form-field">
                  <label>Kaza Tarihi <span className="required">*</span></label>
                  <input 
                    type="date" 
                    value={formData.incidentDate}
                    onChange={(e) => setFormData({...formData, incidentDate: e.target.value})}
                  />
                </div>
                <div className="form-field">
                  <label>Kaza Saati <span className="required">*</span></label>
                  <input 
                    type="time" 
                    value={formData.incidentTime}
                    onChange={(e) => setFormData({...formData, incidentTime: e.target.value})}
                  />
                </div>
              </div>
              <div className="form-row">
                <div className="form-field">
                  <label>Konum <span className="required">*</span></label>
                  <input 
                    type="text" 
                    value={formData.location}
                    onChange={(e) => setFormData({...formData, location: e.target.value})}
                    placeholder="İşyeri, bölüm, alan" 
                  />
                </div>
                <div className="form-field">
                  <label>Departman</label>
                  <input 
                    type="text" 
                    value={formData.department}
                    onChange={(e) => setFormData({...formData, department: e.target.value})}
                    placeholder="Üretim, bakım, vb." 
                  />
                </div>
              </div>
              <div className="form-row">
                <div className="form-field">
                  <label>Olay Kategorisi <span className="required">*</span></label>
                  <select 
                    value={formData.eventCategory}
                    onChange={(e) => setFormData({...formData, eventCategory: e.target.value})}
                  >
                    <option value="Kaza">İş Kazası</option>
                    <option value="Ramak Kala">Ramak Kala</option>
                    <option value="Tehlikeli Durum">Tehlikeli Durum</option>
                  </select>
                </div>
                <div className="form-field">
                  <label>Şiddet Derecesi</label>
                  <select 
                    value={formData.severity}
                    onChange={(e) => setFormData({...formData, severity: e.target.value})}
                  >
                    <option value="">Seçiniz</option>
                    <option value="Hafif">Hafif (İlkyardım)</option>
                    <option value="Orta">Orta (Tedavi gerekti)</option>
                    <option value="Ağır">Ağır (Hastaneye yatış)</option>
                    <option value="Ölümlü">Ölümlü</option>
                  </select>
                </div>
              </div>
            </div>

            {/* SECTION 2: OLAY AKIŞI (Timeline) */}
            <div ref={el => sectionRefs.current[2] = el} className="form-section timeline-section">
              <div className="section-header">
                <Clock size={24} />
                <h2>Olay Akışı (Timeline)</h2>
              </div>
              
              <div className="info-box">
                <AlertCircle size={16} />
                <p>Olayın başlangıcından sonuna kadar zaman sırasına göre adımları ekleyin.</p>
              </div>

              {formData.timeline.map((item, index) => (
                <div key={index} className="timeline-item">
                  <div className="timeline-item-header">
                    <div className="timeline-number">#{index + 1}</div>
                    {formData.timeline.length > 1 && (
                      <button 
                        type="button"
                        className="remove-btn"
                        onClick={() => removeTimelineItem(index)}
                        title="Sil"
                      >
                        <Trash2 size={16} />
                      </button>
                    )}
                  </div>
                  <div className="form-row">
                    <div className="form-field" style={{flex: '0 0 150px'}}>
                      <label>Saat</label>
                      <input 
                        type="time" 
                        value={item.time}
                        onChange={(e) => {
                          const newTimeline = [...formData.timeline];
                          newTimeline[index].time = e.target.value;
                          setFormData({...formData, timeline: newTimeline});
                        }}
                      />
                    </div>
                    <div className="form-field" style={{flex: '1'}}>
                      <label>Ne oldu? / Ne yapıldı?</label>
                      <input 
                        type="text" 
                        value={item.action}
                        onChange={(e) => {
                          const newTimeline = [...formData.timeline];
                          newTimeline[index].action = e.target.value;
                          setFormData({...formData, timeline: newTimeline});
                        }}
                        placeholder="Örn: Çalışan iskeleye çıktı"
                      />
                    </div>
                  </div>
                  <div className="form-row">
                    <div className="form-field">
                      <label>Sorumlu Kişi/Ekip</label>
                      <input 
                        type="text" 
                        value={item.responsible}
                        onChange={(e) => {
                          const newTimeline = [...formData.timeline];
                          newTimeline[index].responsible = e.target.value;
                          setFormData({...formData, timeline: newTimeline});
                        }}
                        placeholder="Kim yaptı?"
                      />
                    </div>
                    <div className="form-field">
                      <label>Kanıt/Belge</label>
                      <input 
                        type="text" 
                        value={item.evidence}
                        onChange={(e) => {
                          const newTimeline = [...formData.timeline];
                          newTimeline[index].evidence = e.target.value;
                          setFormData({...formData, timeline: newTimeline});
                        }}
                        placeholder="Fotoğraf, tanık, doküman"
                      />
                    </div>
                  </div>
                </div>
              ))}
              
              <button 
                type="button" 
                className="add-item-btn"
                onClick={addTimelineItem}
              >
                <Plus size={18} />
                Yeni Adım Ekle
              </button>
            </div>

            {/* SECTION 3: ÖNLEME KONTROL LİSTESİ */}
            <div ref={el => sectionRefs.current[3] = el} className="form-section checklist-section">
              <div className="section-header">
                <CheckSquare size={24} />
                <h2>Önleme Kontrol Listesi</h2>
              </div>
              
              <div className="info-box">
                <AlertCircle size={16} />
                <p>Bu bilgiler önleyici aksiyonlar belirlemek için kritik önem taşıyor!</p>
              </div>

              {/* Risk Değerlendirmesi */}
              <div className="checklist-item">
                <h4>🎯 Risk Değerlendirmesi (Risk Assessment)</h4>
                <div className="form-row">
                  <div className="form-field">
                    <label>Mevcut mu?</label>
                    <select 
                      value={formData.preventionChecklist.riskAssessment.exists === null ? '' : formData.preventionChecklist.riskAssessment.exists}
                      onChange={(e) => updateChecklist('riskAssessment', 'exists', e.target.value === '' ? null : e.target.value === 'true')}
                    >
                      <option value="">Seçiniz</option>
                      <option value="true">✅ Evet</option>
                      <option value="false">❌ Hayır</option>
                    </select>
                  </div>
                  <div className="form-field">
                    <label>Son Güncelleme</label>
                    <input 
                      type="date" 
                      value={formData.preventionChecklist.riskAssessment.lastUpdate}
                      onChange={(e) => updateChecklist('riskAssessment', 'lastUpdate', e.target.value)}
                    />
                  </div>
                </div>
                <div className="form-field">
                  <label>Detaylar / Risk No</label>
                  <textarea 
                    value={formData.preventionChecklist.riskAssessment.details}
                    onChange={(e) => updateChecklist('riskAssessment', 'details', e.target.value)}
                    placeholder="Risk matrisi, değerlendirme sonuçları..."
                    rows="2"
                  />
                </div>
              </div>

              {/* PTW */}
              <div className="checklist-item">
                <h4>📋 Çalışma İzni (PTW - Permit to Work)</h4>
                <div className="form-row">
                  <div className="form-field">
                    <label>Mevcut mu?</label>
                    <select 
                      value={formData.preventionChecklist.ptw.exists === null ? '' : formData.preventionChecklist.ptw.exists}
                      onChange={(e) => updateChecklist('ptw', 'exists', e.target.value === '' ? null : e.target.value === 'true')}
                    >
                      <option value="">Seçiniz</option>
                      <option value="true">✅ Evet</option>
                      <option value="false">❌ Hayır</option>
                    </select>
                  </div>
                  <div className="form-field">
                    <label>PTW Numarası</label>
                    <input 
                      type="text" 
                      value={formData.preventionChecklist.ptw.number}
                      onChange={(e) => updateChecklist('ptw', 'number', e.target.value)}
                      placeholder="PTW-2026-001"
                    />
                  </div>
                  <div className="form-field">
                    <label>Onaylayan</label>
                    <input 
                      type="text" 
                      value={formData.preventionChecklist.ptw.approver}
                      onChange={(e) => updateChecklist('ptw', 'approver', e.target.value)}
                      placeholder="İSG Uzmanı / Amir"
                    />
                  </div>
                </div>
              </div>

              {/* Toolbox Talk */}
              <div className="checklist-item">
                <h4>👥 Toolbox Talk / İş Başı Eğitimi</h4>
                <div className="form-row">
                  <div className="form-field">
                    <label>Yapıldı mı?</label>
                    <select 
                      value={formData.preventionChecklist.toolboxTalk.exists === null ? '' : formData.preventionChecklist.toolboxTalk.exists}
                      onChange={(e) => updateChecklist('toolboxTalk', 'exists', e.target.value === '' ? null : e.target.value === 'true')}
                    >
                      <option value="">Seçiniz</option>
                      <option value="true">✅ Evet</option>
                      <option value="false">❌ Hayır</option>
                    </select>
                  </div>
                  <div className="form-field">
                    <label>Tarih</label>
                    <input 
                      type="date" 
                      value={formData.preventionChecklist.toolboxTalk.date}
                      onChange={(e) => updateChecklist('toolboxTalk', 'date', e.target.value)}
                    />
                  </div>
                  <div className="form-field">
                    <label>Katılımcı Sayısı</label>
                    <input 
                      type="text" 
                      value={formData.preventionChecklist.toolboxTalk.participants}
                      onChange={(e) => updateChecklist('toolboxTalk', 'participants', e.target.value)}
                      placeholder="Örn: 8 kişi"
                    />
                  </div>
                </div>
              </div>

              {/* KKD/PPE */}
              <div className="checklist-item">
                <h4>🦺 Kişisel Koruyucu Donanım (KKD)</h4>
                <div className="form-row">
                  <div className="form-field">
                    <label>Sağlandı mı?</label>
                    <select 
                      value={formData.preventionChecklist.ppe.provided === null ? '' : formData.preventionChecklist.ppe.provided}
                      onChange={(e) => updateChecklist('ppe', 'provided', e.target.value === '' ? null : e.target.value === 'true')}
                    >
                      <option value="">Seçiniz</option>
                      <option value="true">✅ Evet</option>
                      <option value="false">❌ Hayır</option>
                    </select>
                  </div>
                  <div className="form-field">
                    <label>Kullanıldı mı?</label>
                    <select 
                      value={formData.preventionChecklist.ppe.used === null ? '' : formData.preventionChecklist.ppe.used}
                      onChange={(e) => updateChecklist('ppe', 'used', e.target.value === '' ? null : e.target.value === 'true')}
                    >
                      <option value="">Seçiniz</option>
                      <option value="true">✅ Evet</option>
                      <option value="false">❌ Hayır</option>
                    </select>
                  </div>
                  <div className="form-field">
                    <label>KKD Türü</label>
                    <input 
                      type="text" 
                      value={formData.preventionChecklist.ppe.type}
                      onChange={(e) => updateChecklist('ppe', 'type', e.target.value)}
                      placeholder="Baret, emniyet kemeri, eldiven..."
                    />
                  </div>
                </div>
              </div>

              {/* Eğitim */}
              <div className="checklist-item">
                <h4>🎓 Eğitim (Training)</h4>
                <div className="form-row">
                  <div className="form-field">
                    <label>Tamamlandı mı?</label>
                    <select 
                      value={formData.preventionChecklist.training.completed === null ? '' : formData.preventionChecklist.training.completed}
                      onChange={(e) => updateChecklist('training', 'completed', e.target.value === '' ? null : e.target.value === 'true')}
                    >
                      <option value="">Seçiniz</option>
                      <option value="true">✅ Evet</option>
                      <option value="false">❌ Hayır</option>
                    </select>
                  </div>
                  <div className="form-field">
                    <label>Eğitim Tarihi</label>
                    <input 
                      type="date" 
                      value={formData.preventionChecklist.training.date}
                      onChange={(e) => updateChecklist('training', 'date', e.target.value)}
                    />
                  </div>
                  <div className="form-field">
                    <label>Eğitim Konusu</label>
                    <input 
                      type="text" 
                      value={formData.preventionChecklist.training.type}
                      onChange={(e) => updateChecklist('training', 'type', e.target.value)}
                      placeholder="Yüksekte çalışma, LOTO..."
                    />
                  </div>
                </div>
              </div>

              {/* Denetim */}
              <div className="checklist-item">
                <h4>🔍 Denetim/İnspeksiyon</h4>
                <div className="form-row">
                  <div className="form-field">
                    <label>Yapıldı mı?</label>
                    <select 
                      value={formData.preventionChecklist.inspection.done === null ? '' : formData.preventionChecklist.inspection.done}
                      onChange={(e) => updateChecklist('inspection', 'done', e.target.value === '' ? null : e.target.value === 'true')}
                    >
                      <option value="">Seçiniz</option>
                      <option value="true">✅ Evet</option>
                      <option value="false">❌ Hayır</option>
                    </select>
                  </div>
                  <div className="form-field">
                    <label>Son Denetim</label>
                    <input 
                      type="date" 
                      value={formData.preventionChecklist.inspection.date}
                      onChange={(e) => updateChecklist('inspection', 'date', e.target.value)}
                    />
                  </div>
                </div>
                <div className="form-field">
                  <label>Bulgular</label>
                  <textarea 
                    value={formData.preventionChecklist.inspection.findings}
                    onChange={(e) => updateChecklist('inspection', 'findings', e.target.value)}
                    placeholder="Denetimde tespit edilen eksiklikler..."
                    rows="2"
                  />
                </div>
              </div>

              {/* Prosedür */}
              <div className="checklist-item">
                <h4>📖 İş Prosedürleri</h4>
                <div className="form-row">
                  <div className="form-field">
                    <label>Mevcut mu?</label>
                    <select 
                      value={formData.preventionChecklist.procedures.available === null ? '' : formData.preventionChecklist.procedures.available}
                      onChange={(e) => updateChecklist('procedures', 'available', e.target.value === '' ? null : e.target.value === 'true')}
                    >
                      <option value="">Seçiniz</option>
                      <option value="true">✅ Evet</option>
                      <option value="false">❌ Hayır</option>
                    </select>
                  </div>
                  <div className="form-field">
                    <label>Uyuldu mu?</label>
                    <select 
                      value={formData.preventionChecklist.procedures.followed === null ? '' : formData.preventionChecklist.procedures.followed}
                      onChange={(e) => updateChecklist('procedures', 'followed', e.target.value === '' ? null : e.target.value === 'true')}
                    >
                      <option value="">Seçiniz</option>
                      <option value="true">✅ Evet</option>
                      <option value="false">❌ Hayır</option>
                    </select>
                  </div>
                  <div className="form-field">
                    <label>Prosedür No/Adı</label>
                    <input 
                      type="text" 
                      value={formData.preventionChecklist.procedures.name}
                      onChange={(e) => updateChecklist('procedures', 'name', e.target.value)}
                      placeholder="SOP-XX, İş Talimatı YY"
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* SECTION 4: Olay Açıklaması (5W1H) */}
            <div ref={el => sectionRefs.current[4] = el} className="form-section">
              <div className="section-header">
                <FileText size={24} />
                <h2>Olay Açıklaması (5W1H)</h2>
              </div>
              
              <div className="form-field">
                <label>Ne Oldu? (What)</label>
                <textarea 
                  value={formData.what}
                  onChange={(e) => setFormData({...formData, what: e.target.value})}
                  placeholder="Olayı kısaca özetleyin..."
                  rows="3"
                />
              </div>

              <div className="form-row">
                <div className="form-field">
                  <label>Nerede? (Where)</label>
                  <input 
                    type="text" 
                    value={formData.where}
                    onChange={(e) => setFormData({...formData, where: e.target.value})}
                    placeholder="Spesifik konum"
                  />
                </div>
                <div className="form-field">
                  <label>Ne Zaman? (When)</label>
                  <input 
                    type="text" 
                    value={formData.when}
                    onChange={(e) => setFormData({...formData, when: e.target.value})}
                    placeholder="Tarih, saat, vardiya"
                  />
                </div>
              </div>

              <div className="form-row">
                <div className="form-field">
                  <label>Kim? (Who)</label>
                  <input 
                    type="text" 
                    value={formData.who}
                    onChange={(e) => setFormData({...formData, who: e.target.value})}
                    placeholder="İlgili kişiler"
                  />
                </div>
                <div className="form-field">
                  <label>Neden? (Why)</label>
                  <input 
                    type="text" 
                    value={formData.why}
                    onChange={(e) => setFormData({...formData, why: e.target.value})}
                    placeholder="İlk değerlendirme"
                  />
                </div>
              </div>

              <div className="form-field">
                <label>Nasıl Oldu? (How)</label>
                <textarea 
                  value={formData.how}
                  onChange={(e) => setFormData({...formData, how: e.target.value})}
                  placeholder="Olay süreci detaylı..."
                  rows="4"
                />
              </div>

              <div className="form-field">
                <label>Acil Müdahale / Alınan Önlemler</label>
                <textarea 
                  value={formData.emergencyActions}
                  onChange={(e) => setFormData({...formData, emergencyActions: e.target.value})}
                  placeholder="Olay sonrası hemen yapılanlar..."
                  rows="3"
                />
              </div>
            </div>

            {/* SECTION 5: Tanıklar */}
            <div ref={el => sectionRefs.current[5] = el} className="form-section">
              <div className="section-header">
                <Users size={24} />
                <h2>Tanıklar</h2>
              </div>
              
              <div className="form-field">
                <label>Tanık Bilgileri</label>
                <textarea 
                  value={formData.witnesses}
                  onChange={(e) => setFormData({...formData, witnesses: e.target.value})}
                  placeholder="Tanık isimleri, ifadeleri..."
                  rows="4"
                />
              </div>
            </div>

            {/* SECTION 6: Çevresel Koşullar */}
            <div ref={el => sectionRefs.current[6] = el} className="form-section">
              <div className="section-header">
                <Cloud size={24} />
                <h2>Çevresel Koşullar</h2>
              </div>
              
              <div className="form-row">
                <div className="form-field">
                  <label>Hava Durumu</label>
                  <input 
                    type="text" 
                    value={formData.weather}
                    onChange={(e) => setFormData({...formData, weather: e.target.value})}
                    placeholder="Güneşli, yağmurlu, karlı..."
                  />
                </div>
                <div className="form-field">
                  <label>Aydınlatma</label>
                  <input 
                    type="text" 
                    value={formData.lighting}
                    onChange={(e) => setFormData({...formData, lighting: e.target.value})}
                    placeholder="İyi, yetersiz, karanlık..."
                  />
                </div>
                <div className="form-field">
                  <label>Sıcaklık</label>
                  <input 
                    type="text" 
                    value={formData.temperature}
                    onChange={(e) => setFormData({...formData, temperature: e.target.value})}
                    placeholder="°C veya tanım"
                  />
                </div>
              </div>
            </div>

            {/* SECTION 7: Çalışma Koşulları */}
            <div ref={el => sectionRefs.current[7] = el} className="form-section">
              <div className="section-header">
                <Briefcase size={24} />
                <h2>Çalışma Koşulları</h2>
              </div>
              
              <div className="form-row">
                <div className="form-field">
                  <label>İş Türü</label>
                  <input 
                    type="text" 
                    value={formData.workType}
                    onChange={(e) => setFormData({...formData, workType: e.target.value})}
                    placeholder="Bakım, montaj, temizlik..."
                  />
                </div>
                <div className="form-field">
                  <label>Deneyim Süresi</label>
                  <input 
                    type="text" 
                    value={formData.experience}
                    onChange={(e) => setFormData({...formData, experience: e.target.value})}
                    placeholder="Örn: 2 yıl"
                  />
                </div>
              </div>
            </div>

            {/* SECTION 8: Yaralanma/Hasar */}
            <div ref={el => sectionRefs.current[8] = el} className="form-section">
              <div className="section-header">
                <Heart size={24} />
                <h2>Yaralanma / Hasar Bilgileri</h2>
              </div>
              
              <div className="form-row">
                <div className="form-field">
                  <label>Yaralanma Türü</label>
                  <input 
                    type="text" 
                    value={formData.injuryType}
                    onChange={(e) => setFormData({...formData, injuryType: e.target.value})}
                    placeholder="Kırık, burkulma, kesik..."
                  />
                </div>
                <div className="form-field">
                  <label>Şiddet</label>
                  <select 
                    value={formData.injurySeverity}
                    onChange={(e) => setFormData({...formData, injurySeverity: e.target.value})}
                  >
                    <option value="">Seçiniz</option>
                    <option value="İlkyardım">İlkyardım</option>
                    <option value="Ayakta Tedavi">Ayakta Tedavi</option>
                    <option value="Hastaneye Yatış">Hastaneye Yatış</option>
                    <option value="Kalıcı Hasar">Kalıcı Hasar</option>
                    <option value="Ölüm">Ölüm</option>
                  </select>
                </div>
                <div className="form-field">
                  <label>Vücut Bölgesi</label>
                  <input 
                    type="text" 
                    value={formData.bodyPart}
                    onChange={(e) => setFormData({...formData, bodyPart: e.target.value})}
                    placeholder="Kol, bacak, baş..."
                  />
                </div>
              </div>
            </div>

            {/* SECTION 9: KÖK NEDEN VE ÖNLEMLER */}
            <div ref={el => sectionRefs.current[9] = el} className="form-section root-cause-section">
              <div className="section-header">
                <AlertCircle size={24} />
                <h2>Kök Neden ve Önleme Aksiyonları</h2>
              </div>
              
              <div className="info-box">
                <AlertCircle size={16} />
                <p><strong>ÖNEMLİ:</strong> Her kök neden için spesifik önleme aksiyonu, sorumlu ve termin belirleyin!</p>
              </div>

              {formData.rootCauses.map((cause, index) => (
                <div key={index} className="root-cause-item">
                  <div className="root-cause-header">
                    <h4>Kök Neden #{index + 1}</h4>
                    {formData.rootCauses.length > 1 && (
                      <button 
                        type="button"
                        className="remove-btn"
                        onClick={() => removeRootCause(index)}
                        title="Sil"
                      >
                        <Trash2 size={16} />
                      </button>
                    )}
                  </div>
                  
                  <div className="form-field">
                    <label>Kategori (6M)</label>
                    <select 
                      value={cause.category}
                      onChange={(e) => {
                        const newCauses = [...formData.rootCauses];
                        newCauses[index].category = e.target.value;
                        setFormData({...formData, rootCauses: newCauses});
                      }}
                    >
                      <option value="">Seçiniz</option>
                      <option value="Manpower">👤 İnsan (Manpower)</option>
                      <option value="Machine">⚙️ Makine/Ekipman (Machine)</option>
                      <option value="Material">📦 Malzeme (Material)</option>
                      <option value="Method">📋 Yöntem/Prosedür (Method)</option>
                      <option value="Measurement">📊 Ölçüm/İzleme (Measurement)</option>
                      <option value="Environment">🌍 Çevre (Environment)</option>
                    </select>
                  </div>

                  <div className="form-field">
                    <label>Kök Neden Açıklaması</label>
                    <textarea 
                      value={cause.description}
                      onChange={(e) => {
                        const newCauses = [...formData.rootCauses];
                        newCauses[index].description = e.target.value;
                        setFormData({...formData, rootCauses: newCauses});
                      }}
                      placeholder="Bu kök nedeni detaylı açıklayın (5 Why tekniği kullanabilirsiniz)..."
                      rows="3"
                    />
                  </div>

                  <div className="form-field">
                    <label>Önleme Aksiyonu (Corrective/Preventive Action)</label>
                    <textarea 
                      value={cause.preventionAction}
                      onChange={(e) => {
                        const newCauses = [...formData.rootCauses];
                        newCauses[index].preventionAction = e.target.value;
                        setFormData({...formData, rootCauses: newCauses});
                      }}
                      placeholder="Bu kök nedeni ortadan kaldırmak veya etkisini azaltmak için yapılacaklar..."
                      rows="3"
                    />
                  </div>

                  <div className="form-row">
                    <div className="form-field">
                      <label>Sorumlu Kişi/Departman</label>
                      <input 
                        type="text" 
                        value={cause.responsible}
                        onChange={(e) => {
                          const newCauses = [...formData.rootCauses];
                          newCauses[index].responsible = e.target.value;
                          setFormData({...formData, rootCauses: newCauses});
                        }}
                        placeholder="İSG Müdürü, Bakım Şefi..."
                      />
                    </div>
                    <div className="form-field">
                      <label>Termin Tarihi</label>
                      <input 
                        type="date" 
                        value={cause.deadline}
                        onChange={(e) => {
                          const newCauses = [...formData.rootCauses];
                          newCauses[index].deadline = e.target.value;
                          setFormData({...formData, rootCauses: newCauses});
                        }}
                      />
                    </div>
                  </div>
                </div>
              ))}
              
              <button 
                type="button" 
                className="add-item-btn"
                onClick={addRootCause}
              >
                <Plus size={18} />
                Yeni Kök Neden Ekle
              </button>
            </div>

            {/* Ek Notlar */}
            <div className="form-section">
              <div className="section-header">
                <FileText size={24} />
                <h2>Ek Notlar</h2>
              </div>
              
              <div className="form-field">
                <label>Diğer Bilgiler</label>
                <textarea 
                  value={formData.additionalNotes}
                  onChange={(e) => setFormData({...formData, additionalNotes: e.target.value})}
                  placeholder="Ek açıklamalar, belgeler, referanslar..."
                  rows="4"
                />
              </div>
            </div>

            {/* Form Butonları */}
            <div className="form-actions">
              <button type="button" className="btn-secondary">
                💾 Taslak Kaydet
              </button>
              <button type="submit" className="btn-primary">
                🚀 Analiz İçin Gönder
              </button>
            </div>

          </form>
        </div>
      </div>
    </div>
  );
};

export default IncidentForm;
