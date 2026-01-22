# 🚀 Railway'de API Key Kurulumu

## ❌ Mevcut Sorun
Admin panelde "Backend API error" hatası alıyorsunuz çünkü Railway'deki backend'de `OPENROUTER_API_KEY` eksik.

## ✅ Çözüm Adımları

### 1. Railway Dashboard'a Gidin
```
https://railway.app
```

### 2. Projenizi Seçin
- **HSE_AgenticAI** projesini bulun
- Backend service'inizi seçin (API/Backend)

### 3. Environment Variables Ekleyin
1. **"Variables"** sekmesine tıklayın
2. **"+ New Variable"** butonuna tıklayın
3. Şu bilgileri girin:

```
Variable Name:  OPENROUTER_API_KEY
Variable Value: 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
```

### 4. Deploy
- Railway otomatik olarak yeniden deploy edecek
- **2-3 dakika** bekleyin

### 5. Test Edin
Deploy tamamlandıktan sonra admin panelden tekrar deneyin:
- Incident oluşturun
- "Analyze with AI" butonuna tıklayın
- ✅ Artık çalışmalı!

## 🔍 Doğrulama

Railway logs'da şu mesajı görmelisiniz:
```
✅ Overview Agent initialized
✅ Assessment Agent initialized
✅ Root Cause Agent initialized
✅ Action Plan Agent initialized
```

## 📝 Not
- `.env` dosyası sadece **lokal development** için
- Production'da (Railway) environment variables **dashboard'dan** eklenmeli
- Vercel frontend'de API key **GEREKMEZ** (sadece backend Railway URL'si yeterli)

## 🎯 Railway Environment Variables Checklist
- ✅ `OPENROUTER_API_KEY` - AI agent'ları için **GEREKLİ**
- ⚠️ `DATABASE_URL` - Şu an kullanılmıyor (opsiyonel)
- ⚠️ `OPENAI_API_KEY` - OpenRouter kullanıyorsanız gerekmez

## 🆘 Hala Çalışmazsa
Railway logs'u kontrol edin:
1. Railway Dashboard → Service → Deployments
2. En son deployment'a tıklayın
3. "View Logs" butonuna tıklayın
4. Hata mesajlarını bakın

Beklenen log çıktısı:
```
🚀 Starting HSE Investigation API...
📊 OpenRouter API Key configured: True
✅ Overview Agent initialized
✅ Assessment Agent initialized
✅ Root Cause Agent initialized (DeepSeek V3 + Claude 3.5 Sonnet)
✅ Action Plan Agent initialized
```
