#!/usr/bin/env python3
"""
Test app rendering ve console errors'ını kontrol etmek için basit script
"""

import requests
import time

# 1. Sunucuyu kontrol et
print("🔍 Sunucu kontrol ediliyor...")
try:
    response = requests.get('http://localhost:3003', timeout=5)
    if response.status_code == 200:
        print("✅ Sunucu çalışıyor!")
        print(f"   Status: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type')}")
    else:
        print(f"❌ Sunucu hatası: {response.status_code}")
except Exception as e:
    print(f"❌ Sunucuya bağlanılamıyor: {e}")

# 2. Index.html kontrol
print("\n📄 Index.html kontrol ediliyor...")
try:
    response = requests.get('http://localhost:3003/index.html', timeout=5)
    if response.status_code == 200:
        print("✅ Index.html bulundu!")
        # React root element kontrol
        if "root" in response.text or "app" in response.text:
            print("✅ React root element mevcut")
        else:
            print("⚠️  React root element bulunamadı")
    else:
        print(f"❌ Index.html hatası: {response.status_code}")
except Exception as e:
    print(f"❌ Index.html'ye erişilemiyor: {e}")

# 3. Main.jsx kontrol
print("\n📦 Vite bundle kontrol ediliyor...")
try:
    response = requests.get('http://localhost:3003/@vite/client', timeout=5)
    if response.status_code == 200:
        print("✅ Vite client yükleniyor")
    else:
        print(f"⚠️  Vite client status: {response.status_code}")
except Exception as e:
    print(f"⚠️  Vite kontrol hatası: {e}")

print("\n" + "="*50)
print("✅ Tarayıcıda şu adımları yap:")
print("1. Cmd+Shift+Delete (cache temizle)")
print("2. http://localhost:3003 yenile")
print("3. DevTools açılı (F12)")
print("4. Console tab'ını kontrol et")
print("5. 'Akıllı Form (V2)' tab'ını tıkla")
print("6. Theme toggle (🌙/☀️) button'ı tıkla")
print("="*50)
