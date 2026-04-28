const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export async function apiRequest(endpoint: string, options: RequestInit = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const defaultOptions: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(url, defaultOptions);
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(error.detail || 'Request failed');
    }
    
    return await response.json();
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
}

export const sessionsApi = {
  create: (data: { event_name: string; event_date: string; location: string; client_name: string }) =>
    apiRequest('/api/v1/sessions', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  getAll: () => apiRequest('/api/v1/sessions'),
  getById: (id: string) => apiRequest(`/api/v1/sessions/${id}`),
  update: (id: string, data: any) =>
    apiRequest(`/api/v1/sessions/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),
  delete: (id: string) =>
    apiRequest(`/api/v1/sessions/${id}`, {
      method: 'DELETE',
    }),
};

export const uploadApi = {
  uploadFiles: (sessionId: string, files: File[]) => {
    const formData = new FormData();
    files.forEach(file => formData.append('files', file));
    
    return apiRequest(`/api/v1/upload/${sessionId}/files`, {
      method: 'POST',
      headers: {},
      body: formData,
    });
  },
};

export const workflowApi = {
  processSession: (sessionId: string) =>
    apiRequest(`/api/v1/workflow/process-session/${sessionId}`, {
      method: 'POST',
    }),
};

export const healthApi = {
  check: () => apiRequest('/health'),
};

export const assetsApi = {
  getBySession: (sessionId: string) =>
    apiRequest(`/api/v1/assets?session_id=${sessionId}`),
  getById: (id: string) => apiRequest(`/api/v1/assets/${id}`),
};

export const outputsApi = {
  getBySession: (sessionId: string) =>
    apiRequest(`/api/v1/outputs?session_id=${sessionId}`),
  getById: (id: string) => apiRequest(`/api/v1/outputs/${id}`),
};
