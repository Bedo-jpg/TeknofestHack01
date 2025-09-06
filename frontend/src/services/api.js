import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// Health check
export const checkHealth = () => api.get('/health');

// Görüntü analizi için
export const analyzeImage = (formData) => api.post('/predict', formData, {
  headers: {
    'Content-Type': 'multipart/form-data'
  }
});

// AOI analizi için
export const analyzeAOI = (geojsonData) => api.post('/aoi/analyze', geojsonData);

// Sonuçları getir
export const getResults = (jobId) => api.get(`/results/${jobId}`);

// Görüntü sahnelerini getir
export const getScenes = () => api.get('/imagery/scenes');

export default api;
// Görüntü URL'sini al
// Örnek: getImageURL('2023-02-01') -> 'http://localhost:8000/imagery/2023-02-01'
export const getImageURL = (imageId) => {
  return `${API_BASE_URL}/imagery/${imageId}`;
};