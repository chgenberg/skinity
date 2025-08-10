import axios from 'axios';

export const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL || 'https://skinity-backend-production.up.railway.app/api'
});

export const fetcher = (url: string) => api.get(url).then((r) => r.data); 