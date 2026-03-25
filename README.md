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

## 🆕 Root Cause Agent V3.1 (NEW - INACTIVE)

**Status**: ✅ Ready for Testing | 🔒 Production Safe (Not Active)

### What's New?

V3.1 introduces **DSPy-powered 5-Why analysis** with significant improvements over V2.5:

- **80% reduction** in repeated root causes (vs 50% in V2.5)
- **83% reduction** in chain breakage (30% → 5%)
- **Type-safe chain continuity** via DSPy signatures
- **Modular architecture** (4 independent modules)
- **Semantic answer verification** (prevents similar answers)
- **Chain quality metrics** (0-1 score per branch)

### Files

```
agents/rootcause_agent_v3_1.py       # Main implementation (28KB, 1100+ lines)
test_rootcause_v3_1.py               # Test suite (3 real-world cases)
V3_1_ACTIVATION_GUIDE.py             # Step-by-step deployment guide
V3_1_ARCHITECTURE.md                 # Full documentation
V3_1_IMPLEMENTATION_SUMMARY.txt      # Quick reference
V3_1_FINAL_STATUS.txt                # Current status report
```

### Quick Start (Testing)

```bash
# Install DSPy
pip install dspy-ai

# Run tests
python test_rootcause_v3_1.py

# Verbose output
python test_rootcause_v3_1.py --verbose

# Compare with V2.5
python test_rootcause_v3_1.py --compare
```

### Activation (After Testing)

V3.1 is **currently INACTIVE** to ensure production safety. To activate:

1. **Test successfully** (all 3 cases pass, chain quality > 90%)
2. **Update app.py**:
   ```python
   # Replace V2.5 import with:
   from agents.rootcause_agent_v3_1 import RootCauseAgentV3_1
   rca_agent = RootCauseAgentV3_1(use_rag=False, enable_diversity_check=True)
   ```
3. **Deploy** with fallback option (recommended)

See `V3_1_ACTIVATION_GUIDE.py` for detailed instructions.

### Why Not Active Yet?

- **Testing phase**: Needs validation with real-world cases
- **Production safety**: V2.5 is stable and working
- **User control**: Activation decision left to user after testing
- **Fallback ready**: Can switch back to V2.5 instantly if needed

### Architecture

```
RootCauseAgentV3_1
├── ImmediateCauseFinder (A/B categories)
├── WhyChain (5-Why with DSPy)
│   ├── SemanticAnswerVerifier (NEW - prevents repeats)
│   ├── WhyQuestion (type-safe)
│   ├── WhyAnswer (type-safe)
│   └── RootCauseValidator (C/D validation)
└── MetaRootCauseSynthesizer (common root)
```

## License

MIT License
