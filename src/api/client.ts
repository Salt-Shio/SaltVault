import axios from 'axios';
import router from '@/router';
import { useAuthStore } from '@/stores/auth';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// 請求攔截器：自動帶上 JWT Token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

// 回應攔截器：後端回 401 (token 失效/過期) 時自動登出並導回登入頁，
// 避免使用者卡在「畫面顯示已登入、但所有 API 都失敗」的狀態
api.interceptors.response.use((response) => response, (error) => {
  if (error.response?.status === 401) {
    const authStore = useAuthStore();
    if (authStore.isLoggedIn) {
      authStore.logout();
      router.push('/login');
    }
  }
  return Promise.reject(error);
});

export default api;
