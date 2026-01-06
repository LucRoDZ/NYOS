const API_BASE = 'http://localhost:8000';

export const api = {
  async getDashboard() {
    const res = await fetch(`${API_BASE}/data/dashboard`);
    return res.json();
  },

  async getBatches(limit = 50) {
    const res = await fetch(`${API_BASE}/data/batches?limit=${limit}`);
    return res.json();
  },

  async getTrends(parameter = 'hardness', days = 30) {
    const res = await fetch(`${API_BASE}/data/trends/${parameter}?days=${days}`);
    return res.json();
  },

  async getComplaints(status = null) {
    const url = status ? `${API_BASE}/data/complaints?status=${status}` : `${API_BASE}/data/complaints`;
    const res = await fetch(url);
    return res.json();
  },

  async getCapas(status = null) {
    const url = status ? `${API_BASE}/data/capas?status=${status}` : `${API_BASE}/data/capas`;
    const res = await fetch(url);
    return res.json();
  },

  async getConversations() {
    const res = await fetch(`${API_BASE}/chat/conversations`);
    return res.json();
  },

  async createConversation() {
    const res = await fetch(`${API_BASE}/chat/conversations`, { method: 'POST' });
    return res.json();
  },

  async deleteConversation(convId) {
    const res = await fetch(`${API_BASE}/chat/conversations/${convId}`, { method: 'DELETE' });
    return res.json();
  },

  async chat(convId, message) {
    const res = await fetch(`${API_BASE}/chat/${convId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message })
    });
    return res.json();
  },

  streamSummary(onChunk, onDone, onError) {
    const eventSource = new EventSource(`${API_BASE}/chat/summary/stream`);
    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.done) {
        eventSource.close();
        onDone?.();
      } else if (data.error) {
        eventSource.close();
        onError?.(data.error);
      } else if (data.text) {
        onChunk(data.text);
      }
    };
    eventSource.onerror = () => {
      eventSource.close();
      onError?.('Connection error');
    };
    return eventSource;
  },

  async getReport() {
    const res = await fetch(`${API_BASE}/chat/report`);
    return res.json();
  },

  async getChatHistory(convId) {
    const res = await fetch(`${API_BASE}/chat/${convId}/history`);
    return res.json();
  },

  async uploadFile(file, dataType) {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_BASE}/data/upload?data_type=${dataType}`, {
      method: 'POST',
      body: formData
    });
    return res.json();
  },

  async getUploads() {
    const res = await fetch(`${API_BASE}/data/uploads`);
    return res.json();
  }
};
