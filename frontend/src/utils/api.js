import axios from 'axios';

// API base URL (configured via Vite proxy)
const API_BASE_URL = '/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Send a chat message
export const sendMessage = async ({ message, sessionId, language }) => {
  try {
    const response = await api.post('/chat/message', {
      message,
      session_id: sessionId,
      language,
    });
    return response.data;
  } catch (error) {
    console.error('Error sending message:', error);
    throw error;
  }
};

// Start batch analysis
export const analyzeIncident = async ({ description, language }) => {
  try {
    const response = await api.post('/analyze', {
      incident_description: description,
      language,
      mode: 'batch',
    });
    return response.data;
  } catch (error) {
    console.error('Error analyzing incident:', error);
    throw error;
  }
};

// Get analysis status
export const getAnalysisStatus = async (jobId) => {
  try {
    const response = await api.get(`/analysis/${jobId}/status`);
    return response.data;
  } catch (error) {
    console.error('Error getting analysis status:', error);
    throw error;
  }
};

// Get analysis result
export const getAnalysisResult = async (jobId) => {
  try {
    const response = await api.get(`/analysis/${jobId}/result`);
    return response.data;
  } catch (error) {
    console.error('Error getting analysis result:', error);
    throw error;
  }
};

// Export report
export const exportReport = async (jobId, format = 'html') => {
  try {
    const response = await api.get(`/analysis/${jobId}/export`, {
      params: { format },
      responseType: 'blob',
    });
    return response.data;
  } catch (error) {
    console.error('Error exporting report:', error);
    throw error;
  }
};

// WebSocket connection for real-time updates
export const createWebSocket = (jobId, onMessage, onError) => {
  const wsUrl = `ws://localhost:8000/ws/analysis/${jobId}`;
  const ws = new WebSocket(wsUrl);

  ws.onopen = () => {
    console.log('WebSocket connected');
  };

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    onMessage(data);
  };

  ws.onerror = (error) => {
    console.error('WebSocket error:', error);
    onError(error);
  };

  ws.onclose = () => {
    console.log('WebSocket disconnected');
  };

  return ws;
};

export default api;
