import axios from 'axios';

export const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api'
});

export const fetcher = (url: string) => api.get(url).then((r) => r.data); 