/**
 * HIZLI TEMA TOGGLE TEST
 * =====================
 * Tarayıcı Console'da çalıştırarak tema toggle'ı test et
 */

// Test 1: Dark Mode'a Geç
console.log('🌙 Dark Mode Test Başlıyor...');
const form = document.querySelector('.smart-questionnaire-v2');
if (form) {
  form.setAttribute('data-theme', 'dark');
  console.log('✅ Dark Mode Aktif');
  console.log('Arka Plan Rengi:', window.getComputedStyle(form).backgroundColor);
  console.log('Text Rengi:', window.getComputedStyle(form).color);
} else {
  console.error('❌ Form element bulunamadı!');
}

// Test 2: Light Mode'a Geç
setTimeout(() => {
  console.log('\n☀️ Light Mode Test Başlıyor...');
  const form = document.querySelector('.smart-questionnaire-v2');
  if (form) {
    form.setAttribute('data-theme', 'light');
    console.log('✅ Light Mode Aktif');
    console.log('Arka Plan Rengi:', window.getComputedStyle(form).backgroundColor);
    console.log('Text Rengi:', window.getComputedStyle(form).color);
  }
}, 2000);

// Test 3: CSS Variables Kontrol
setTimeout(() => {
  console.log('\n🎨 CSS Variables Test...');
  const root = getComputedStyle(document.documentElement);
  console.log('--bg-secondary-light:', root.getPropertyValue('--bg-secondary-light'));
  console.log('--bg-secondary-dark-mode:', root.getPropertyValue('--bg-secondary-dark-mode'));
}, 4000);

// Test 4: Toggle Butonu Var mı?
setTimeout(() => {
  console.log('\n🔘 Toggle Button Test...');
  const toggleBtn = document.querySelector('.theme-toggle');
  if (toggleBtn) {
    console.log('✅ Toggle Button Bulundu');
    console.log('Button HTML:', toggleBtn.outerHTML.substring(0, 100) + '...');
  } else {
    console.error('❌ Toggle Button Bulunamadı!');
  }
}, 6000);
