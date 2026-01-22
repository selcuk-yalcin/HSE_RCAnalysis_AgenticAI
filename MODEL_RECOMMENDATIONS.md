# OpenRouter Model Önerileri

## Mevcut Durum
- **Sorun:** Llama 3.1 70B ile "User not found" hatası
- **Sebep:** OpenRouter API key geçersiz veya expired

## Çözüm Seçenekleri

### Seçenek 1: API Key'i Düzelt (Önerilen)
1. https://openrouter.ai/keys adresine git
2. Yeni API key oluştur
3. `.env` dosyasını güncelle:
   ```
   OPENROUTER_API_KEY=yeni-key-buraya
   ```
4. Railway'de environment variable'ı güncelle
5. Backend'i redeploy et

### Seçenek 2: Alternatif Modeller

#### En Uygun Fiyat/Performans:
```python
# agents/*.py dosyalarında
model="meta-llama/llama-3.1-8b-instruct"  # $0.055/1M tokens
```

#### En İyi Kalite:
```python
model="anthropic/claude-3.5-sonnet"  # $3.00/1M input, $15/1M output
```

#### Dengeli Seçim:
```python
model="google/gemini-pro-1.5"  # $1.25/1M input, $5/1M output
```

#### Ücretsiz Seçenek:
```python
model="meta-llama/llama-3.2-3b-instruct:free"  # FREE
```

## Hızlı Test Script

```bash
# API key'i test et
curl -X POST "https://openrouter.ai/api/v1/chat/completions" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "meta-llama/llama-3.1-8b-instruct",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

## Railway Deployment Sonrası Kontrol

```bash
# Railway logs'u kontrol et
railway logs --service backend

# Health check
curl https://your-backend.railway.app/api/v1/health
```
