import axios from 'axios';
import type { DashboardResponse, ChatResponse } from '../types';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
});

export const getDashboard = async (role: string): Promise<DashboardResponse> => {
  const response = await api.get(`/dashboard/${role}`);
  return response.data;
};

export const sendChat = async (query: string, role: string, deepSearch: boolean, imageFile?: File): Promise<ChatResponse> => {
  const formData = new FormData();
  formData.append('query', query);
  formData.append('role', role);
  formData.append('deep_search', String(deepSearch));
  if (imageFile) {
    formData.append('image', imageFile);
  }
  const response = await api.post('/chat', formData);
  return response.data;
};

export const initializeDB = async () => {
  const response = await api.post('/initialize');
  return response.data;
};
