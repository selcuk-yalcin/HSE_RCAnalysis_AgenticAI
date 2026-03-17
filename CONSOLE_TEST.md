#!/bin/bash

# TARAYICI CONSOLE TEST SCRIPT
# ============================
# Tarayıcı açık olduğunda çalıştırılacak

cat << 'EOF'
🧪 CONSOLE TEST SCRIPT
=======================

Tarayıcıda F12 basarak DevTools → Console açın ve
aşağıdaki kodu yapıştırın ve Enter'a basın:

────────────────────────────────────────────────────────────

// TEST 1: Dark Mode Aktifleştir
const form = document.querySelector('.smart-questionnaire-v2');
form.setAttribute('data-theme', 'dark');
console.log('✅ Dark Mode Aktif - Siyah arka plan olmalı');
console.log('data-theme:', form.getAttribute('data-theme'));

// TEST 2: Light Mode Aktifleştir  
setTimeout(() => {
  form.setAttribute('data-theme', 'light');
  console.log('✅ Light Mode Aktif - Beyaz arka plan olmalı');
  console.log('data-theme:', form.getAttribute('data-theme'));
}, 2000);

// TEST 3: CSS Değişkenlerini Kontrol Et
setTimeout(() => {
  const root = getComputedStyle(document.documentElement);
  console.log('Light BG:', root.getPropertyValue('--bg-secondary-light'));
  console.log('Dark BG:', root.getPropertyValue('--bg-secondary-dark'));
}, 4000);

────────────────────────────────────────────────────────────

VEYA aşağıdaki linkten tıkla:

ÖNEMLİ:
1. Tarayıcıda F5 ile refresh et
2. http://localhost:3001 aç
3. "Akıllı Form (V2)" sekmesine tıkla
4. Sağ üstte Ay/Güneş ikonu ara
5. Tıkla ve renk değişimini gözle

BEKLENEN:
- Ay butonu → Tıkla → Koyu arka plan (Dark Mode)
- Güneş butonu → Tıkla → Açık arka plan (Light Mode)
- Geçiş 0.3 saniyede smooth olmalı

EOF
