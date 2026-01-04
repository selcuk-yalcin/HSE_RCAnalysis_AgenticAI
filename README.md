# HSE Root Cause Analysis - AI Agent System

HSG245 tabanlı çok-ajanlı kök neden analizi sistemi.

## 📂 Proje Yapısı

```
HSE_AgenticAI/
├── agents/              # AI Agents (Overview, Investigation, etc.)
├── api/                 # FastAPI Backend
├── shared/              # Ortak konfigürasyon ve yardımcılar
├── admin/              # Admin Panel (Submodule - Ayrı repo)
├── examples/            # Test dosyaları
└── requirements.txt     # Python bağımlılıkları
```

## 🔗 Repository Yapısı

Bu proje **iki ayrı repository** kullanır:

### 1. Backend/Agents (Bu Repo)
- **Repository**: `HSE_RCAnalysis_AgenticAI`
- **İçerik**: AI agents, FastAPI backend, shared utilities
- **Deployment**: Vercel (API)

### 2. Admin Panel (Submodule)
- **Repository**: `admin_pan`
- **İçerik**: Next.js/React admin interface
- **Deployment**: Vercel (Frontend)
- **URL**: https://inferaworld-admin.vercel.app

## 🚀 Kurulum

### Backend Setup

```bash
# Repository'yi klonlayın (submodule ile birlikte)
git clone --recurse-submodules https://github.com/selcuk-yalcin/HSE_RCAnalysis_AgenticAI.git
cd HSE_AgenticAI

# Python bağımlılıklarını yükleyin
pip install -r requirements.txt

# .env dosyası oluşturun
cp .env.example .env
# OPENAI_API_KEY'inizi ekleyin

# API'yi başlatın
cd api
python main.py
```

### Admin Panel Setup

```bash
# Admin panel klasörüne gidin
cd admin

# Node.js bağımlılıklarını yükleyin
npm install

# Admin panel'i başlatın
npm run dev
```

## 🔄 Git Workflow

### Backend Değişiklikleri

```bash
# Backend dosyalarını commit edin
git add agents/ api/ shared/
git commit -m "feat: Update agents"
git push origin main
```

### Admin Panel Değişiklikleri

```bash
# Admin panel klasörüne gidin
cd admin

# Değişiklikleri admin_pan repo'suna commit edin
git add .
git commit -m "feat: Update admin UI"
git push origin main

# Ana repo'ya geri dönün
cd ..

# Submodule referansını güncelleyin
git add admin
git commit -m "chore: Update admin panel submodule"
git push origin main
```

## 📡 API Endpoints

- `GET /` - API status
- `POST /api/v1/incidents` - Yeni olay oluştur
- `GET /api/v1/health` - Health check

## 🛠️ Teknolojiler

### Backend
- Python 3.11+
- FastAPI
- OpenAI GPT-4o-mini
- PDFPlumber

### Admin Panel (Submodule)
- Next.js
- React
- TypeScript
- Tailwind CSS

## 📝 Lisans

MIT License
