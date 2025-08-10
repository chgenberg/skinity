import axios from 'axios';

export const api = axios.create({
  baseURL: '/backend'
});

export const fetcher = (url: string) => api.get(url).then((r) => r.data); 