# 🔧 OpenRouter API Key Sorunu - TEK ÇÖZÜM

## ❌ Sorun
```
{"error":{"message":"User not found.","code":401}}
```
Mevcut OpenRouter API key **geçersiz** veya **expired**.

## ✅ TEK ÇÖZÜM: YENİ API KEY ALIN (2 Dakika)

### Adım 1: Yeni OpenRouter API Key Alın
```
1. https://openrouter.ai/ adresine git
2. Sağ üst köşeden "Sign In" / "Sign Up" tıkla
3. Google veya GitHub ile giriş yap
4. Sol menüden "Keys" sekmesine tıkla
5. "Create Key" butonuna tıkla
6. Key'i KOPYALA (sk-or-v1-... ile başlar)
```

**ÖNEMLİ:** Yeni account açarsanız **ücretsiz $5 credit** alırsınız!

### Adım 2: .env Dosyasını Güncelle
```bash
cd /Users/selcuk/Desktop/HSE_AgenticAI
nano .env

# Bu satırı bul (satır 10):
OPENROUTER_API_KEY=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

# YENİ KEY ile DEĞİŞTİR:
OPENROUTER_API_KEY=YENİ_KEY_BURAYA_YAPIŞTIR

# Kaydet: Ctrl+O, Enter, Ctrl+X
```

### Adım 3: Test Et (Local)
```bash
# Yeni key'i test et
curl -X POST "https://openrouter.ai/api/v1/chat/completions" \
  -H "Authorization: Bearer YENİ_KEY_BURAYA" \
  -H "Content-Type: application/json" \
  -H "HTTP-Referer: https://github.com/selcuk-yalcin" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "test"}]
  }'
```

✅ **Başarılı ise** JSON response göreceksin (içinde "choices" olacak)
❌ **Hata alırsan** key'i tekrar kontrol et

### Adım 4: Railway'e Ekle
```
1. https://railway.app/dashboard
2. HSE_AgenticAI project'ini aç
3. "backend" service'i seç
4. "Variables" tab
5. OPENROUTER_API_KEY değişkenini bul
6. "Edit" butonuna tıkla
7. YENİ KEY'İ yapıştır (aynı key)
8. "Save" 
9. Railway otomatik redeploy yapacak (2-3 dakika bekle)
```

### Adım 5: Commit & Push
```bash
git add .env
git commit -m "Update OpenRouter API key"
git push origin main
```

---

## 🎯 Neden OpenRouter?

✅ **Ucuz:** GPT-3.5-turbo sadece $0.50/1M token
✅ **Hızlı:** 1-2 saniye yanıt süresi  
✅ **Çok modelli:** Bir API key ile 200+ model
✅ **Ücretsiz credit:** Yeni hesaplara $5 ücretsiz
✅ **Ödeme yok:** Credit bitene kadar kredi kartı gerekmez

---

## 📊 Maliyetler (OpenRouter + GPT-3.5-turbo)

| İşlem | Token | Maliyet |
|-------|-------|---------|
| 1 incident analizi | ~5,000 | $0.0025 |
| 10 analiz | ~50,000 | $0.025 |
| 100 analiz | ~500,000 | $0.25 |
| 1000 analiz | ~5M | $2.50 |

**$5 ücretsiz credit ile ~2000 analiz yapabilirsiniz!**

---

## ⚡ Alternatif: Tamamen Ücretsiz Model

Eğer hiç para harcamak istemezseniz:
```bash
# agents/*.py dosyalarında model değiştir:
model="meta-llama/llama-3.2-3b-instruct:free"
```

Ama GPT-3.5-turbo çok daha iyi ve zaten çok ucuz ($0.0025/analiz)

---

## 🆘 Hala Çalışmazsa?

1. **API key doğru kopyalandı mı?** Boşluk veya satır sonu olmamalı
2. **Railway environment variable doğru mu?** Tam olarak aynı key olmalı
3. **Railway deploy tamamlandı mı?** "Deployments" sekmesinden kontrol et
4. **Logs'u kontrol et:** Railway'de "Logs" sekmesine bak, hata mesajı var mı?

Bana hata mesajını göster, birlikte çözelim!
