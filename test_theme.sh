#!/bin/bash

# TEMA TOGGLE TEST SCRIPT
# ======================
# SmartQuestionnaire V2 tema değişikliğini test et

echo "🌙 TEMA TOGGLE TEST BAŞLIYOR..."
echo "================================="
echo ""

# 1. CSS dosyasını kontrol et
echo "1️⃣ CSS dosyasını kontrol ediliyor..."
CSS_FILE="/Users/selcuk/Desktop/HSE_RCAnalysis_AgenticAI-main/frontend/src/components/SmartQuestionnaire_V2.css"

if grep -q 'data-theme="dark"' "$CSS_FILE"; then
  echo "✅ CSS: data-theme='dark' selector bulundu"
else
  echo "❌ CSS: data-theme='dark' selector BULUNAMADI"
fi

if grep -q 'data-theme="light"' "$CSS_FILE"; then
  echo "✅ CSS: data-theme='light' selector bulundu"
else
  echo "❌ CSS: data-theme='light' selector BULUNAMADI"
fi

echo ""

# 2. JSX dosyasını kontrol et
echo "2️⃣ JSX dosyasını kontrol ediliyor..."
JSX_FILE="/Users/selcuk/Desktop/HSE_RCAnalysis_AgenticAI-main/frontend/src/components/SmartQuestionnaire_V2.jsx"

if grep -q 'data-theme={darkMode' "$JSX_FILE"; then
  echo "✅ JSX: data-theme attribute bulundu"
else
  echo "❌ JSX: data-theme attribute BULUNAMADI"
fi

if grep -q 'setDarkMode' "$JSX_FILE"; then
  echo "✅ JSX: setDarkMode state bulundu"
else
  echo "❌ JSX: setDarkMode state BULUNAMADI"
fi

echo ""

# 3. CSS değişkenleri kontrol et
echo "3️⃣ CSS değişkenleri kontrol ediliyor..."

echo "Light Mode CSS Variables:"
grep -A 5 "Light Mode" "$CSS_FILE" | head -8

echo ""
echo "Dark Mode CSS Variables:"
grep -A 5 "Dark Mode" "$CSS_FILE" | head -8

echo ""
echo "================================="
echo "✅ TEST TAMAMLANDI"
echo ""
echo "TALİMATLAR:"
echo "1. Tarayıcıda http://localhost:3001 aç"
echo "2. 'Akıllı Form (V2)' sekmesine tıkla"
echo "3. Sağ üstteki Ay butonuna tıkla"
echo "4. Ekran rengi koyu renge dönmeli"
echo "5. Güneş butonuna tıkla → Açık renge dönmeli"
