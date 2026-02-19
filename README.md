# HSE Root Cause Analysis - AI Agent System

Multi-agent root cause investigation system based on HSG245 framework.

##  Project Structure

```
HSE_AgenticAI/
├── agents/              # AI Agents (Overview, Investigation, etc.)
├── api/                 # FastAPI Backend
├── shared/              # Shared configuration and utilities
├── admin/              # Admin Panel (Submodule - Separate repo)
├── examples/            # Test files
└── requirements.txt     # Python dependencies
```

##  Repository Structure

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

##  Installation

### Prerequisites

- Python 3.11+
- Node.js 18+ (for admin panel)
- OpenAI API Key ([Get one here](https://platform.openai.com/api-keys))

### Backend Setup

```bash
# Clone repository (with submodules)
git clone --recurse-submodules https://github.com/selcuk-yalcin/HSE_RCAnalysis_AgenticAI.git
cd HSE_AgenticAI

# Install Python dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
nano .env

# Test installation
python examples/test_pdf_agent.py

# Start the API server
python -m uvicorn api.main:app --reload
# API will be available at http://localhost:8000
```

### Admin Panel Setup

```bash
# Navigate to admin panel folder
cd admin

# Install Node.js dependencies
npm install

# Start admin panel
npm run dev
# Admin panel will be available at http://localhost:3000
```

### Environment Variables

See [Environment Setup Guide](docs/ENVIRONMENT_SETUP.md) for detailed configuration.

**Required:**
- `OPENAI_API_KEY` - Your OpenAI API key

**Optional:**
- `OPENAI_MODEL` - Model to use (default: gpt-4o-mini)
- `OPENAI_TEMPERATURE` - Creativity (default: 0.7)
- `PORT` - API port (default: 8000)

##  Git Workflow

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

## API Endpoints

- `GET /` - API status
- `POST /api/v1/incidents` - Create new incident
- `GET /api/v1/health` - Health check

##  Technologies

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
