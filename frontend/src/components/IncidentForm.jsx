import React, { useState, useEffect, useRef } from 'react';
import { Calendar, Clock, MapPin, User, AlertTriangle, FileText, Users, Shield, Cloud, Briefcase, Heart, Search } from 'lucide-react';
import { getTranslation } from '../utils/translations';
import { getTestScenarioList, loadTestScenario } from '../utils/testScenarios';
import './IncidentForm.css';

const IncidentForm = ({ language, onSubmit }) => {
  const testScenarios = getTestScenarioList(language);
  const [activeSection, setActiveSection] = useState(0);
  const sectionRefs = useRef([]);
  
  const [formData, setFormData] = useState({
    // Reporter Info
    reportedBy: '',
    reportDate: '',
    reportTime: '',
    
    // Incident Details
    incidentDate: '',
    incidentTime: '',
    location: '',
    department: '',
    eventCategory: 'incident',
    
    // Incident Description
    incidentDescription: '',
    
    // Safety Equipment
    fallProtection: '',
    safetyHarness: '',
    safetyTraining: '',
    ppeUsed: '',
    
    // Witnesses
    witnessesPresent: '',
    witnessNames: '',
    witnessStatements: '',
    
    // Environmental Conditions
    weatherConditions: '',
    lightingConditions: '',
    noiseLevel: '',
    temperature: '',
    
    // Work Conditions
    workType: '',
    workHeight: '',
    experienceLevel: '',
    shiftTime: '',
    workDuration: '',
    
    // Equipment/Machinery
    equipmentInvolved: '',
    equipmentCondition: '',
    lastMaintenance: '',
    
    // Injuries/Damages
    injuryType: '',
    injurySeverity: '',
    bodyPart: '',
    medicalTreatment: '',
    propertyDamage: '',
    
    // Additional Info
    previousIncidents: '',
    rootCauseInitial: '',
    correctiveActions: '',
    additionalNotes: '',
  });

  const t = (key) => getTranslation(language, key);

  const handleChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleLoadTestScenario = (scenarioId) => {
    const scenarioData = loadTestScenario(scenarioId);
    if (scenarioData) {
      setFormData(scenarioData);
    }
  };

  const handleClearForm = () => {
    setFormData({
      reportedBy: '',
      reportDate: '',
      reportTime: '',
      incidentDate: '',
      incidentTime: '',
      location: '',
      department: '',
      eventCategory: 'incident',
      incidentDescription: '',
      emergencyMeasures: '',
      fallProtection: '',
      safetyHarness: '',
      safetyTraining: '',
      ppeUsed: '',
      witnessesPresent: '',
      witnessNames: '',
      witnessStatements: '',
      weatherConditions: '',
      lightingConditions: '',
      noiseLevel: '',
      temperature: '',
      workType: '',
      workHeight: '',
      experienceLevel: '',
      shiftTime: '',
      workDuration: '',
      injuryType: '',
      injurySeverity: '',
      bodyPart: '',
      medicalTreatment: '',
      propertyDamage: '',
      rootCauseInitial: '',
      correctiveActions: '',
      additionalNotes: '',
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  const eventCategories = [
    { value: 'incident', label: t('incident') },
    { value: 'near_miss', label: t('near_miss') },
    { value: 'unsafe_condition', label: t('unsafe_condition') },
    { value: 'property_damage', label: t('property_damage') },
  ];

  const yesNoOptions = [
    { value: 'yes', label: t('yes') },
    { value: 'no', label: t('no') },
    { value: 'unknown', label: t('unknown') },
  ];

  // Section configurations for left navigation
  const sections = [
    { id: 'reporter', title: t('section_reporter'), icon: User },
    { id: 'incident', title: t('section_incident_details'), icon: AlertTriangle },
    { id: 'description', title: t('section_description'), icon: FileText },
    { id: 'safety', title: t('section_safety_equipment'), icon: Shield },
    { id: 'witnesses', title: t('section_witnesses'), icon: Users },
    { id: 'environment', title: t('section_environment'), icon: Cloud },
    { id: 'work', title: t('section_work_conditions'), icon: Briefcase },
    { id: 'injuries', title: t('section_injuries'), icon: Heart },
    { id: 'rootcause', title: t('section_root_cause'), icon: Search },
  ];

  // Scroll spy effect
  useEffect(() => {
    const handleScroll = () => {
      const scrollPosition = window.scrollY + 200; // Increased for info banner
      
      for (let i = sections.length - 1; i >= 0; i--) {
        const section = sectionRefs.current[i];
        if (section && section.offsetTop <= scrollPosition) {
          setActiveSection(i);
          break;
        }
      }
    };

    window.addEventListener('scroll', handleScroll);
    handleScroll(); // Initial call
    return () => window.removeEventListener('scroll', handleScroll);
  }, [sections.length]);

  const scrollToSection = (index) => {
    const section = sectionRefs.current[index];
    if (section) {
      const offsetTop = section.offsetTop - 20; // Minimal offset, let scroll-margin handle it
      window.scrollTo({ top: offsetTop, behavior: 'smooth' });
    }
  };

  return (
    <div className="incident-form-wrapper">
      {/* Left Navigation Panel */}
      <div className="form-nav-panel">
        <div className="form-nav-header">
          <h3>{t('incident_report_form')}</h3>
        </div>

        {/* Test Scenario Loader - AT TOP */}
        <div className="form-nav-tests">
          <span className="test-scenario-label">{t('load_test_scenario')}</span>
          <div className="test-scenario-buttons">
            {testScenarios.map(scenario => (
              <button
                key={scenario.id}
                type="button"
                onClick={() => handleLoadTestScenario(scenario.id)}
                className="test-scenario-btn"
              >
                {scenario.name}
              </button>
            ))}
          </div>
        </div>

        <div className="form-nav-sections">
          {sections.map((section, index) => {
            const Icon = section.icon;
            return (
              <div
                key={section.id}
                className={`form-nav-item ${activeSection === index ? 'active' : ''}`}
                onClick={() => scrollToSection(index)}
              >
                <Icon className="nav-icon" size={18} />
                <span className="nav-text">{section.title}</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Main Form Content */}
      <div className="form-main-content">
        <form onSubmit={handleSubmit} className="incident-form">
        
        {/* SECTION 1: REPORTER INFORMATION */}
        <div className="form-section" ref={(el) => (sectionRefs.current[0] = el)}>
          <div className="section-header">
            <User size={20} />
            <h2>{t('section_reporter')}</h2>
          </div>
          
          <div className="form-row">
            <div className="form-field">
              <label>{t('reported_by')} *</label>
              <input
                type="text"
                value={formData.reportedBy}
                onChange={(e) => handleChange('reportedBy', e.target.value)}
                placeholder={t('enter_name')}
                required
              />
            </div>
            
            <div className="form-field">
              <label>{t('report_date')} *</label>
              <input
                type="date"
                value={formData.reportDate}
                onChange={(e) => handleChange('reportDate', e.target.value)}
                required
              />
            </div>
            
            <div className="form-field">
              <label>{t('report_time')} *</label>
              <input
                type="time"
                value={formData.reportTime}
                onChange={(e) => handleChange('reportTime', e.target.value)}
                required
              />
            </div>
          </div>
        </div>

        {/* SECTION 2: INCIDENT DETAILS */}
        <div className="form-section" ref={(el) => (sectionRefs.current[1] = el)}>
          <div className="section-header">
            <AlertTriangle size={20} />
            <h2>{t('section_incident_details')}</h2>
          </div>
          
          <div className="form-row">
            <div className="form-field">
              <label>{t('incident_date')} *</label>
              <input
                type="date"
                value={formData.incidentDate}
                onChange={(e) => handleChange('incidentDate', e.target.value)}
                required
              />
            </div>
            
            <div className="form-field">
              <label>{t('incident_time')} *</label>
              <input
                type="time"
                value={formData.incidentTime}
                onChange={(e) => handleChange('incidentTime', e.target.value)}
                required
              />
            </div>
          </div>
          
          <div className="form-row">
            <div className="form-field full-width">
              <label>{t('location')} *</label>
              <input
                type="text"
                value={formData.location}
                onChange={(e) => handleChange('location', e.target.value)}
                placeholder={t('enter_location')}
                required
              />
            </div>
          </div>
          
          <div className="form-row">
            <div className="form-field">
              <label>{t('department')}</label>
              <input
                type="text"
                value={formData.department}
                onChange={(e) => handleChange('department', e.target.value)}
                placeholder={t('enter_department')}
              />
            </div>
            
            <div className="form-field">
              <label>{t('event_category')} *</label>
              <select
                value={formData.eventCategory}
                onChange={(e) => handleChange('eventCategory', e.target.value)}
                required
              >
                {eventCategories.map(cat => (
                  <option key={cat.value} value={cat.value}>{cat.label}</option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* SECTION 3: INCIDENT DESCRIPTION (5W1H) */}
        <div className="form-section" ref={(el) => (sectionRefs.current[2] = el)}>
          <div className="section-header">
            <FileText size={20} />
            <h2>{t('section_description')}</h2>
          </div>
          
          <div className="form-field full-width">
            <label>{t('incident_description')} * ({t('what_where_when_who')})</label>
            <textarea
              value={formData.incidentDescription}
              onChange={(e) => handleChange('incidentDescription', e.target.value)}
              placeholder={t('describe_incident_detail')}
              rows={8}
              required
            />
          </div>
          
          <div className="info-box">
            <AlertTriangle size={16} />
            <span><strong>Lütfen belirtin:</strong> Ne oldu? Nerede oldu? Ne zaman oldu? Kim katılı?</span>
          </div>
          
          <div className="form-field full-width">
            <label>{t('emergency_measures')}</label>
            <textarea
              value={formData.emergencyMeasures}
              onChange={(e) => handleChange('emergencyMeasures', e.target.value)}
              placeholder={t('emergency_placeholder')}
              rows={3}
            />
          </div>
        </div>

        {/* SECTION 4: SAFETY EQUIPMENT */}
        <div className="form-section" ref={(el) => (sectionRefs.current[3] = el)}>
          <div className="section-header">
            <h2>{t('section_safety_equipment')}</h2>
          </div>
          
          <div className="form-row">
            <div className="form-field">
              <label>{t('fall_protection_present')}</label>
              <select
                value={formData.fallProtection}
                onChange={(e) => handleChange('fallProtection', e.target.value)}
              >
                <option value="">{t('select_option')}</option>
                {yesNoOptions.map(opt => (
                  <option key={opt.value} value={opt.value}>{opt.label}</option>
                ))}
              </select>
            </div>
            
            <div className="form-field">
              <label>{t('safety_harness_worn')}</label>
              <select
                value={formData.safetyHarness}
                onChange={(e) => handleChange('safetyHarness', e.target.value)}
              >
                <option value="">{t('select_option')}</option>
                {yesNoOptions.map(opt => (
                  <option key={opt.value} value={opt.value}>{opt.label}</option>
                ))}
              </select>
            </div>
          </div>
          
          <div className="form-row">
            <div className="form-field">
              <label>{t('safety_training_received')}</label>
              <select
                value={formData.safetyTraining}
                onChange={(e) => handleChange('safetyTraining', e.target.value)}
              >
                <option value="">{t('select_option')}</option>
                {yesNoOptions.map(opt => (
                  <option key={opt.value} value={opt.value}>{opt.label}</option>
                ))}
                <option value="partial">{t('partial')}</option>
              </select>
            </div>
            
            <div className="form-field">
              <label>{t('ppe_used')}</label>
              <input
                type="text"
                value={formData.ppeUsed}
                onChange={(e) => handleChange('ppeUsed', e.target.value)}
                placeholder={t('ppe_placeholder')}
              />
            </div>
          </div>
        </div>

        {/* SECTION 5: WITNESSES */}
        <div className="form-section" ref={(el) => (sectionRefs.current[4] = el)}>
          <div className="section-header">
            <Users size={20} />
            <h2>{t('section_witnesses')}</h2>
          </div>
          
          <div className="form-field">
            <label>{t('witnesses_present')}</label>
            <select
              value={formData.witnessesPresent}
              onChange={(e) => handleChange('witnessesPresent', e.target.value)}
            >
              <option value="">{t('select_option')}</option>
              {yesNoOptions.map(opt => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
          </div>
          
          {formData.witnessesPresent === 'yes' && (
            <>
              <div className="form-field full-width">
                <label>{t('witness_names')}</label>
                <textarea
                  value={formData.witnessNames}
                  onChange={(e) => handleChange('witnessNames', e.target.value)}
                  placeholder={t('witness_names_placeholder')}
                  rows={2}
                />
              </div>
              
              <div className="form-field full-width">
                <label>{t('witness_statements')}</label>
                <textarea
                  value={formData.witnessStatements}
                  onChange={(e) => handleChange('witnessStatements', e.target.value)}
                  placeholder={t('witness_statements_placeholder')}
                  rows={4}
                />
              </div>
            </>
          )}
        </div>

        {/* SECTION 6: ENVIRONMENTAL CONDITIONS */}
        <div className="form-section" ref={(el) => (sectionRefs.current[5] = el)}>
          <div className="section-header">
            <Cloud size={20} />
            <h2>{t('section_environment')}</h2>
          </div>
          
          <div className="form-row">
            <div className="form-field">
              <label>{t('weather_conditions')}</label>
              <select
                value={formData.weatherConditions}
                onChange={(e) => handleChange('weatherConditions', e.target.value)}
              >
                <option value="">{t('select_option')}</option>
                <option value="sunny">☀️ Güneşli</option>
                <option value="cloudy">☁️ Bulutlu</option>
                <option value="rainy">🌧️ Yağmurlu</option>
                <option value="snowy">❄️ Karlı</option>
                <option value="windy">💨 Rüzgarlı</option>
                <option value="foggy">🌫️ Sisli</option>
                <option value="stormy">⛈️ Fırtınalı</option>
              </select>
            </div>
            
            <div className="form-field">
              <label>{t('lighting_conditions')}</label>
              <select
                value={formData.lightingConditions}
                onChange={(e) => handleChange('lightingConditions', e.target.value)}
              >
                <option value="">{t('select_option')}</option>
                <option value="excellent">⭐⭐⭐⭐⭐ Mükemmel</option>
                <option value="good">⭐⭐⭐⭐ İyi</option>
                <option value="adequate">⭐⭐⭐ Yeterli</option>
                <option value="poor">⭐⭐ Zayıf</option>
                <option value="very_poor">⭐ Çok Zayıf</option>
              </select>
            </div>
          </div>
          
          <div className="form-row">
            <div className="form-field">
              <label>{t('noise_level')}</label>
              <select
                value={formData.noiseLevel}
                onChange={(e) => handleChange('noiseLevel', e.target.value)}
              >
                <option value="">{t('select_option')}</option>
                <option value="quiet">🔇 Sessiz (&lt; 50 dB)</option>
                <option value="normal">🔉 Normal (50-70 dB)</option>
                <option value="loud">🔊 Yüksek (70-85 dB)</option>
                <option value="very_loud">🔊🔊 Çok Yüksek (&gt; 85 dB)</option>
              </select>
            </div>
            
            <div className="form-field">
              <label>{t('temperature')}</label>
              <select
                value={formData.temperature}
                onChange={(e) => handleChange('temperature', e.target.value)}
              >
                <option value="">{t('select_option')}</option>
                <option value="very_cold">❄️ Çok Soğuk (&lt; 0°C)</option>
                <option value="cold">🧊 Soğuk (0-10°C)</option>
                <option value="cool">🌤️ Serin (10-15°C)</option>
                <option value="comfortable">😊 Rahat (15-25°C)</option>
                <option value="warm">☀️ Sıcak (25-35°C)</option>
                <option value="hot">🔥 Çok Sıcak (&gt; 35°C)</option>
              </select>
            </div>
          </div>
        </div>

        {/* SECTION 7: WORK CONDITIONS */}
        <div className="form-section" ref={(el) => (sectionRefs.current[6] = el)}>
          <div className="section-header">
            <Briefcase size={20} />
            <h2>{t('section_work_conditions')}</h2>
          </div>
          
          <div className="form-row">
            <div className="form-field">
              <label>{t('work_type')}</label>
              <select
                value={formData.workType}
                onChange={(e) => handleChange('workType', e.target.value)}
              >
                <option value="">{t('select_option')}</option>
                <option value="manual_labor">👷 Elle İşçilik</option>
                <option value="machine_operation">⚙️ Makine Operasyon</option>
                <option value="assembly">🔧 Montaj</option>
                <option value="construction">🏗️ İnşaat</option>
                <option value="maintenance">🛠️ Bakım/Onarım</option>
                <option value="cleaning">🧹 Temizlik</option>
                <option value="driving">🚗 Araç Kullanma</option>
                <option value="admin_work">📝 İdari İş</option>
                <option value="other">📌 Diğer</option>
              </select>
            </div>
            
            <div className="form-field">
              <label>{t('work_height')}</label>
              <select
                value={formData.workHeight}
                onChange={(e) => handleChange('workHeight', e.target.value)}
              >
                <option value="">{t('select_option')}</option>
                <option value="ground_level">🟢 Yer Seviyesi (0 m)</option>
                <option value="low_height">🟡 Düşük Yükseklik (1-2 m)</option>
                <option value="medium_height">🟠 Orta Yükseklik (2-5 m)</option>
                <option value="high">🔴 Yüksek (5-10 m)</option>
                <option value="very_high">⭕ Çok Yüksek (&gt; 10 m)</option>
                <option value="confined_space">⬛ Kapalı Alan</option>
              </select>
            </div>
          </div>
          
          <div className="form-row">
            <div className="form-field">
              <label>{t('experience_level')}</label>
              <select
                value={formData.experienceLevel}
                onChange={(e) => handleChange('experienceLevel', e.target.value)}
              >
                <option value="">{t('select_option')}</option>
                <option value="new_employee">👶 Yeni Çalışan (&lt; 1 ay)</option>
                <option value="trainee">📚 Stajyer/Eğitimdeki (1-3 ay)</option>
                <option value="junior">🟢 Acemi (3-6 ay)</option>
                <option value="experienced">🟡 Tecrübeli (6-12 ay)</option>
                <option value="senior">🟠 Kıdemli (1-5 yıl)</option>
                <option value="expert">⭐ Uzman (&gt; 5 yıl)</option>
              </select>
            </div>
            
            <div className="form-field">
              <label>{t('shift_time')}</label>
              <select
                value={formData.shiftTime}
                onChange={(e) => handleChange('shiftTime', e.target.value)}
              >
                <option value="">{t('select_option')}</option>
                <option value="morning_shift">🌅 Sabah Vardiyası (06:00-14:00)</option>
                <option value="afternoon_shift">☀️ Öğle Vardiyası (14:00-22:00)</option>
                <option value="night_shift">🌙 Gece Vardiyası (22:00-06:00)</option>
                <option value="early_morning">🌄 Erken Sabah (04:00-12:00)</option>
                <option value="late_evening">🌆 Geç Akşam (20:00-04:00)</option>
                <option value="overtime">⏰ Fazla Mesai</option>
                <option value="not_applicable">N/A Uygulanmaz</option>
              </select>
            </div>
          </div>
        </div>

        {/* SECTION 8: INJURIES/DAMAGES */}
        <div className="form-section" ref={(el) => (sectionRefs.current[7] = el)}>
          <div className="section-header">
            <h2>{t('section_injuries')}</h2>
          </div>
          
          <div className="form-row">
            <div className="form-field">
              <label>{t('injury_type')}</label>
              <input
                type="text"
                value={formData.injuryType}
                onChange={(e) => handleChange('injuryType', e.target.value)}
                placeholder={t('injury_type_placeholder')}
              />
            </div>
            
            <div className="form-field">
              <label>{t('injury_severity')}</label>
              <select
                value={formData.injurySeverity}
                onChange={(e) => handleChange('injurySeverity', e.target.value)}
              >
                <option value="">{t('select_option')}</option>
                <option value="minor">{t('minor')}</option>
                <option value="moderate">{t('moderate')}</option>
                <option value="severe">{t('severe')}</option>
                <option value="fatal">{t('fatal')}</option>
              </select>
            </div>
          </div>
          
          <div className="form-row">
            <div className="form-field">
              <label>{t('body_part')}</label>
              <input
                type="text"
                value={formData.bodyPart}
                onChange={(e) => handleChange('bodyPart', e.target.value)}
                placeholder={t('body_part_placeholder')}
              />
            </div>
            
            <div className="form-field">
              <label>{t('medical_treatment')}</label>
              <input
                type="text"
                value={formData.medicalTreatment}
                onChange={(e) => handleChange('medicalTreatment', e.target.value)}
                placeholder={t('medical_placeholder')}
              />
            </div>
          </div>
        </div>

        {/* SECTION 9: ROOT CAUSE & CORRECTIVE ACTIONS */}
        <div className="form-section" ref={(el) => (sectionRefs.current[8] = el)}>
          <div className="section-header">
            <h2>{t('section_root_cause')}</h2>
          </div>
          
          <div className="form-field full-width">
            <label>{t('root_cause_initial')}</label>
            <textarea
              value={formData.rootCauseInitial}
              onChange={(e) => handleChange('rootCauseInitial', e.target.value)}
              placeholder={t('root_cause_placeholder')}
              rows={4}
            />
          </div>
          
          <div className="form-field full-width">
            <label>{t('corrective_actions')}</label>
            <textarea
              value={formData.correctiveActions}
              onChange={(e) => handleChange('correctiveActions', e.target.value)}
              placeholder={t('corrective_placeholder')}
              rows={4}
            />
          </div>
          
          <div className="form-field full-width">
            <label>{t('additional_notes')}</label>
            <textarea
              value={formData.additionalNotes}
              onChange={(e) => handleChange('additionalNotes', e.target.value)}
              placeholder={t('notes_placeholder')}
              rows={3}
            />
          </div>
        </div>

        {/* SUBMIT BUTTON */}
        <div className="form-actions">
          <button type="button" className="btn-secondary" onClick={() => console.log('Draft saved')}>
            {t('save_draft')}
          </button>
          <button type="submit" className="btn-primary">
            {t('submit_for_analysis')}
          </button>
        </div>
      </form>
      </div>
    </div>
  );
};

export default IncidentForm;
