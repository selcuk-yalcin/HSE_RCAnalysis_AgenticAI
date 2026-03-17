// SmartQuestionnaire_V2.jsx - TEMA TOGGLE DEBUG

// Tarayıcı Console'da çalıştır:

// 1. Element kontrol
const form = document.querySelector('.smart-questionnaire-v2');
console.log('Form element:', form);
console.log('Current data-theme:', form?.getAttribute('data-theme'));
console.log('Current classes:', form?.className);

// 2. Button kontrol
const btn = document.querySelector('.theme-toggle');
console.log('Theme button:', btn);
console.log('Button classes:', btn?.className);
console.log('Button parent:', btn?.parentElement);

// 3. CSS kontrol
const styles = window.getComputedStyle(form);
console.log('Computed background:', styles.backgroundColor);
console.log('Computed color:', styles.color);

// 4. Manual test - Dark mode aktifleştir
form.setAttribute('data-theme', 'dark');
console.log('✅ Manually set data-theme=dark');
console.log('New background:', window.getComputedStyle(form).backgroundColor);

// 5. Manual test - Light mode geri dön
setTimeout(() => {
  form.setAttribute('data-theme', 'light');
  console.log('✅ Manually set data-theme=light');
  console.log('New background:', window.getComputedStyle(form).backgroundColor);
}, 2000);

// 6. React state check
console.log('🔍 Debugging sonlandırıldı');
