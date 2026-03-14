# HSE Root Cause Analysis AI - Frontend

Modern React-based chatbot interface for interactive workplace incident analysis with Human-in-the-Loop (HITL) capability.

## 🎯 Features

- **Interactive Chatbot**: Real-time conversation for incident data collection
- **Multi-Language Support**: TR, EN, DE, FR, ES, AR
- **Dual Modes**:
  - 🤖 **Interactive Chat**: Progressive Q&A flow with HITL
  - 📊 **Batch Analysis**: Submit full incident description for async processing
- **Dark Theme UI**: Modern, professional interface matching HSE standards
- **Real-time Updates**: WebSocket integration for live analysis progress
- **Question Flow System**: Guided incident data collection based on safety standards
- **Responsive Design**: Works on desktop, tablet, and mobile

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Header.jsx              # Top navigation with mode/language selector
│   │   ├── Header.css
│   │   ├── LanguageSelector.jsx    # Multi-language dropdown
│   │   ├── LanguageSelector.css
│   │   ├── ChatInterface.jsx       # Main chat area with sidebar
│   │   ├── ChatInterface.css
│   │   ├── Message.jsx             # Chat message bubbles
│   │   ├── Message.css
│   │   ├── QuestionFlow.jsx        # HITL question cards
│   │   └── QuestionFlow.css
│   ├── utils/
│   │   ├── translations.js         # Multi-language strings (6 languages)
│   │   └── api.js                  # Backend API integration
│   ├── App.jsx                     # Main application component
│   ├── App.css
│   ├── main.jsx                    # React entry point
│   └── index.css                   # Global styles & theme
├── package.json                    # Dependencies
├── vite.config.js                  # Vite configuration with proxy
└── index.html                      # HTML entry point
```

## 🚀 Quick Start

### Prerequisites

- Node.js 16+ and npm
- Backend API running on `http://localhost:8000`

### Installation

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install
```

### Development

```bash
# Start development server (runs on http://localhost:3000)
npm run dev
```

The development server includes:
- Hot Module Replacement (HMR)
- Auto-reload on file changes
- API proxy to backend (`/api` → `http://localhost:8000`)
- WebSocket proxy (`/ws` → `http://localhost:8000`)

### Build for Production

```bash
# Create optimized production build
npm run build

# Preview production build
npm run preview
```

## 🔧 Configuration

### API Proxy (vite.config.js)

```javascript
export default defineConfig({
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true,
      },
    },
  },
});
```

### Environment Variables

Create `.env` file in `frontend/` directory:

```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

## 🎨 Theme Customization

Edit `src/index.css` to customize colors:

```css
:root {
  --primary: #667eea;           /* Primary brand color */
  --secondary: #764ba2;         /* Secondary/gradient color */
  --background: #0f1419;        /* Main background */
  --surface: #1a1f2e;          /* Card/surface background */
  --border: #2d3748;           /* Border color */
  --text-primary: #f7fafc;     /* Primary text */
  --text-secondary: #a0aec0;   /* Secondary text */
}
```

## 🌍 Adding New Languages

Edit `src/utils/translations.js`:

```javascript
const translations = {
  // Add new language
  it: {
    welcome_message: 'Ciao! ...',
    input_placeholder: 'Scrivi il tuo messaggio...',
    // ... other translations
  },
};
```

Update `LanguageSelector.jsx`:

```javascript
const LANGUAGES = [
  // Add new language
  { code: 'it', name: 'Italiano', flag: '🇮🇹' },
];
```

## 📡 API Integration

### Interactive Mode (Chat)

```javascript
// Send message
const response = await sendMessage({
  message: "Worker fell from scaffold",
  sessionId: "12345",
  language: "tr"
});

// Response format
{
  message: "İşkelede düşme koruması var mıydı?",
  suggestions: ["Evet", "Hayır", "Bilinmiyor"],
  startFlow: true,
  flowType: "safety_equipment"
}
```

### Batch Mode (Analysis)

```javascript
// Start analysis
const response = await analyzeIncident({
  description: "Worker fell from 3m height scaffold...",
  language: "en"
});

// Response format
{
  jobId: "job_67890",
  status: "processing",
  message: "Analysis started"
}

// Check status
const status = await getAnalysisStatus("job_67890");

// Get result
const result = await getAnalysisResult("job_67890");
```

### WebSocket Updates

```javascript
const ws = createWebSocket(
  "job_67890",
  (data) => {
    console.log("Progress:", data.progress);
    console.log("Step:", data.step);
  },
  (error) => console.error(error)
);
```

## 🧪 Testing

### Test Interactive Mode

1. Start dev server: `npm run dev`
2. Select "Interactive Chat" mode
3. Type incident description in Turkish:
   ```
   İşçi 3 metre yükseklikteki iskeleden düştü. 
   Emniyet kemeri takmıyordu.
   ```
4. System should ask progressive questions

### Test Batch Mode

1. Select "Batch Analysis" mode
2. Paste full incident description
3. Click send
4. Should receive job ID and status updates

### Test Language Switching

1. Click language selector (top right)
2. Select different language (e.g., English)
3. All UI text should update
4. Welcome message should change

## 📝 Component Usage

### ChatInterface

```jsx
<ChatInterface 
  language="tr"      // Language code
  mode="interactive" // 'interactive' or 'batch'
/>
```

**Features:**
- Message history with auto-scroll
- Loading indicators
- Question flow integration
- File attachment (future)
- Export functionality

### Message

```jsx
<Message 
  message={{
    id: "123",
    type: "assistant",         // 'user', 'assistant', 'error', 'success'
    content: "Message text",
    timestamp: new Date(),
    suggestions: ["A", "B", "C"], // Optional
    analysisId: "job_123"      // Optional
  }}
  language="tr"
/>
```

### QuestionFlow

```jsx
<QuestionFlow 
  flowType="safety_equipment"  // Flow type
  language="tr"
  onAnswer={(answer) => console.log(answer)}
  onComplete={(answers) => console.log(answers)}
/>
```

**Flow Types:**
- `safety_equipment`: Fall protection, harness, training
- `incident_details`: Location, time, witnesses

## 🔌 Backend Integration Requirements

The frontend expects these API endpoints:

### POST `/api/chat/message`
```json
// Request
{
  "message": "Worker fell from scaffold",
  "session_id": "12345",
  "language": "tr"
}

// Response
{
  "message": "İşkelede düşme koruması var mıydı?",
  "suggestions": ["Evet", "Hayır", "Bilinmiyor"],
  "startFlow": true,
  "flowType": "safety_equipment"
}
```

### POST `/api/analyze`
```json
// Request
{
  "incident_description": "...",
  "language": "en",
  "mode": "batch"
}

// Response
{
  "jobId": "job_67890",
  "status": "processing"
}
```

### GET `/api/analysis/{jobId}/status`
```json
{
  "jobId": "job_67890",
  "status": "processing",
  "progress": 45,
  "currentStep": "Root Cause Analysis"
}
```

### GET `/api/analysis/{jobId}/result`
```json
{
  "jobId": "job_67890",
  "status": "completed",
  "result": {
    "rootCauses": [...],
    "analysis": {...},
    "htmlReport": "..."
  }
}
```

### WebSocket `/ws/analysis/{jobId}`
```json
// Progress updates
{
  "type": "progress",
  "progress": 65,
  "step": "Generating Report",
  "message": "Compiling analysis results..."
}

// Completion
{
  "type": "complete",
  "jobId": "job_67890",
  "message": "Analysis complete"
}
```

## 🐛 Troubleshooting

### API Connection Issues

**Problem:** `Network Error` or `CORS` errors

**Solution:**
1. Ensure backend is running on port 8000
2. Check `vite.config.js` proxy configuration
3. Verify CORS settings in FastAPI backend

### WebSocket Connection Fails

**Problem:** WebSocket disconnects immediately

**Solution:**
1. Check WebSocket endpoint in backend
2. Verify proxy configuration in `vite.config.js`
3. Use `ws://` for development (not `wss://`)

### Translations Not Working

**Problem:** Keys showing instead of translated text

**Solution:**
1. Check language code matches in `translations.js`
2. Verify `getTranslation()` fallback logic
3. Add missing translation keys

## 📚 Dependencies

### Production
- `react` (18.2.0) - UI framework
- `react-dom` (18.2.0) - DOM rendering
- `axios` (1.6.0) - HTTP client
- `react-markdown` (9.0.0) - Markdown rendering
- `framer-motion` (10.0.0) - Animations
- `lucide-react` (0.294.0) - Icons

### Development
- `vite` (5.0.0) - Build tool
- `@vitejs/plugin-react` (4.2.0) - React plugin

## 🚢 Deployment

### Vercel/Netlify (Recommended)

```bash
# Build
npm run build

# Deploy dist/ folder
# Configure API_URL environment variable
```

### Docker

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "run", "preview"]
```

## 📄 License

Part of HSE RCAnalysis AgenticAI project.

## 🤝 Contributing

1. Follow component structure in `src/components/`
2. Add translations for new UI text
3. Update this README for new features
4. Test in multiple languages before committing

## 📞 Support

For backend integration issues, refer to:
- `agents/v3_vector_search/async_orchestrator_v3.py`
- `docs/FRONTEND_INTEGRATION_DESIGN.md`
- `docs/HITL_SYSTEM_GUIDE.md`
