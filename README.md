# HSE Root Cause Analysis - AI Agent System

Multi-agent root cause investigation system based on HSG245 framework.

## 📂 Project Structure

```
HSE_AgenticAI/
├── agents/              # AI Agents (Overview, Investigation, etc.)
├── api/                 # FastAPI Backend
├── shared/              # Shared configuration and utilities
├── admin/              # Admin Panel (Submodule - Separate repo)
├── examples/            # Test files
└── requirements.txt     # Python dependencies
```

## 🔗 Repository Structure

This project uses **two separate repositories**:

### 1. Backend/Agents (This Repo)
- **Repository**: `HSE_RCAnalysis_AgenticAI`
- **Content**: AI agents, FastAPI backend, shared utilities
- **Deployment**: Vercel (API)

### 2. Admin Panel (Submodule)
- **Repository**: `admin_pan`
- **Content**: Next.js/React admin interface
- **Deployment**: Vercel (Frontend)
- **URL**: https://inferaworld-admin.vercel.app

## 🚀 Installation

### Backend Setup

```bash
# Clone repository (with submodules)
git clone --recurse-submodules https://github.com/selcuk-yalcin/HSE_RCAnalysis_AgenticAI.git
cd HSE_AgenticAI

# Install Python dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Add your OPENAI_API_KEY

# Start the API
cd api
python main.py
```

### Admin Panel Setup

```bash
# Navigate to admin panel folder
cd admin

# Install Node.js dependencies
npm install

# Start admin panel
npm run dev
```

## 🔄 Git Workflow

### Backend Changes

```bash
# Commit backend files
git add agents/ api/ shared/
git commit -m "feat: Update agents"
git push origin main
```

### Admin Panel Changes

```bash
# Navigate to admin panel folder
cd admin

# Commit changes to admin_pan repo
git add .
git commit -m "feat: Update admin UI"
git push origin main

# Return to main repo
cd ..

# Update submodule reference
git add admin
git commit -m "chore: Update admin panel submodule"
git push origin main
```

## 📡 API Endpoints

- `GET /` - API status
- `POST /api/v1/incidents` - Create new incident
- `GET /api/v1/health` - Health check

## 🛠️ Technologies

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

## 📝 License

MIT License
