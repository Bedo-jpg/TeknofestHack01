// frontend/src/services/api.js
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

export const checkHealth = () => axios.get(`${API_BASE_URL}/health`);

export const analyzeHatay = () => axios.post(`${API_BASE_URL}/api/analyze/hatay`);

export const getHatayResults = (taskId) => 
  axios.get(`${API_BASE_URL}/api/results/hatay/${taskId}`);

export const getImageURL = (imageId) => {
  // Bu fonksiyonu backend'deki gerçek endpoint'e göre güncelle
  return `${API_BASE_URL}/imagery/${imageId}`;
};

// Mevcut fonksiyonları da güncelle
export const analyzeAOI = (geojson) => 
  axios.post(`${API_BASE_URL}/aoi/analyze`, geojson);

export const getJobStatus = (jobId) => 
  axios.get(`${API_BASE_URL}/jobs/${jobId}/status`);

export const getJobResults = (jobId) => 
  axios.get(`${API_BASE_URL}/jobs/${jobId}/results`);