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
    emergencyMeasures: '',
    
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

  const eventCategories = React.useMemo(() => [
    { value: 'incident', label: t('incident') },
    { value: 'near_miss', label: t('near_miss') },
    { value: 'unsafe_condition', label: t('unsafe_condition') },
    { value: 'property_damage', label: t('property_damage') },
  ], [language]);

  const yesNoOptions = React.useMemo(() => [
    { value: 'yes', label: t('yes') },
    { value: 'no', label: t('no') },
    { value: 'unknown', label: t('unknown') },
  ], [language]);

  // Section configurations for left navigation - UPDATED WHEN LANGUAGE CHANGES
  const sections = React.useMemo(() => [
    { id: 'reporter', title: t('section_reporter'), icon: User },
    { id: 'incident', title: t('section_incident_details'), icon: AlertTriangle },
    { id: 'description', title: t('section_description'), icon: FileText },
    { id: 'safety', title: t('section_safety_equipment'), icon: Shield },
    { id: 'witnesses', title: t('section_witnesses'), icon: Users },
    { id: 'environment', title: t('section_environment'), icon: Cloud },
    { id: 'work', title: t('section_work_conditions'), icon: Briefcase },
    { id: 'injuries', title: t('section_injuries'), icon: Heart },
    { id: 'rootcause', title: t('section_root_cause'), icon: Search },
  ], [language]);

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
            <span>
              <strong>{t('report_content_hint_title')}</strong>{' '}
              {t('report_content_hint_body')}
            </span>
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
                <option value="sunny">{t('weather_sunny')}</option>
                <option value="cloudy">{t('weather_cloudy')}</option>
                <option value="rainy">{t('weather_rainy')}</option>
                <option value="snowy">{t('weather_snowy')}</option>
                <option value="windy">{t('weather_windy')}</option>
                <option value="foggy">{t('weather_foggy')}</option>
                <option value="stormy">{t('weather_stormy')}</option>
              </select>
            </div>
            
            <div className="form-field">
              <label>{t('lighting_conditions')}</label>
              <select
                value={formData.lightingConditions}
                onChange={(e) => handleChange('lightingConditions', e.target.value)}
              >
                <option value="">{t('select_option')}</option>
                <option value="excellent">{t('lighting_excellent')}</option>
                <option value="good">{t('lighting_good')}</option>
                <option value="adequate">{t('lighting_adequate')}</option>
                <option value="poor">{t('lighting_poor')}</option>
                <option value="very_poor">{t('lighting_very_poor')}</option>
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
                <option value="quiet">{t('noise_quiet')}</option>
                <option value="normal">{t('noise_normal')}</option>
                <option value="loud">{t('noise_loud')}</option>
                <option value="very_loud">{t('noise_very_loud')}</option>
              </select>
            </div>
            
            <div className="form-field">
              <label>{t('temperature')}</label>
              <select
                value={formData.temperature}
                onChange={(e) => handleChange('temperature', e.target.value)}
              >
                <option value="">{t('select_option')}</option>
                <option value="very_cold">{t('temp_very_cold')}</option>
                <option value="cold">{t('temp_cold')}</option>
                <option value="cool">{t('temp_cool')}</option>
                <option value="comfortable">{t('temp_comfortable')}</option>
                <option value="warm">{t('temp_warm')}</option>
                <option value="hot">{t('temp_hot')}</option>
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
                <option value="manual_labor">{t('work_manual_labor')}</option>
                <option value="machine_operation">{t('work_machine_operation')}</option>
                <option value="assembly">{t('work_assembly')}</option>
                <option value="construction">{t('work_construction')}</option>
                <option value="maintenance">{t('work_maintenance')}</option>
                <option value="cleaning">{t('work_cleaning')}</option>
                <option value="driving">{t('work_driving')}</option>
                <option value="admin_work">{t('work_admin')}</option>
                <option value="other">{t('work_other')}</option>
              </select>
            </div>
            
            <div className="form-field">
              <label>{t('work_height')}</label>
              <select
                value={formData.workHeight}
                onChange={(e) => handleChange('workHeight', e.target.value)}
              >
                <option value="">{t('select_option')}</option>
                <option value="ground_level">{t('height_ground_level')}</option>
                <option value="low_height">{t('height_low')}</option>
                <option value="medium_height">{t('height_medium')}</option>
                <option value="high">{t('height_high')}</option>
                <option value="very_high">{t('height_very_high')}</option>
                <option value="confined_space">{t('height_confined_space')}</option>
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
                <option value="new_employee">{t('exp_new_employee')}</option>
                <option value="trainee">{t('exp_trainee')}</option>
                <option value="junior">{t('exp_junior')}</option>
                <option value="experienced">{t('exp_experienced')}</option>
                <option value="senior">{t('exp_senior')}</option>
                <option value="expert">{t('exp_expert')}</option>
              </select>
            </div>
            
            <div className="form-field">
              <label>{t('shift_time')}</label>
              <select
                value={formData.shiftTime}
                onChange={(e) => handleChange('shiftTime', e.target.value)}
              >
                <option value="">{t('select_option')}</option>
                <option value="morning_shift">{t('shift_morning')}</option>
                <option value="afternoon_shift">{t('shift_afternoon')}</option>
                <option value="night_shift">{t('shift_night')}</option>
                <option value="early_morning">{t('shift_early_morning')}</option>
                <option value="late_evening">{t('shift_late_evening')}</option>
                <option value="overtime">{t('shift_overtime')}</option>
                <option value="not_applicable">{t('shift_not_applicable')}</option>
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
