import axios from "axios";
import { clearTokens, getStoredTokens, storeTokens } from "./authStorage";

const baseURL = import.meta.env.VITE_API_BASE_URL || "/api/v1";

const client = axios.create({
  baseURL,
  timeout: 30000,
});

let isRefreshing = false;
let pendingQueue = [];

function flushQueue(error, token = null) {
  pendingQueue.forEach(({ resolve, reject }) => {
    if (error) {
      reject(error);
    } else {
      resolve(token);
    }
  });
  pendingQueue = [];
}

client.interceptors.request.use((config) => {
  const { access } = getStoredTokens();
  if (access) {
    config.headers.Authorization = `Bearer ${access}`;
  }
  return config;
});

client.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (!error.response || error.response.status !== 401 || originalRequest._retry) {
      return Promise.reject(error);
    }

    const { refresh } = getStoredTokens();
    if (!refresh) {
      clearTokens();
      window.location.href = "/login";
      return Promise.reject(error);
    }

    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        pendingQueue.push({ resolve, reject });
      }).then((token) => {
        originalRequest.headers.Authorization = `Bearer ${token}`;
        return client(originalRequest);
      });
    }

    originalRequest._retry = true;
    isRefreshing = true;

    try {
      const response = await axios.post(`${baseURL}/auth/refresh/`, { refresh });
      storeTokens({
        access: response.data.access,
        refresh: response.data.refresh || refresh,
      });
      flushQueue(null, response.data.access);
      originalRequest.headers.Authorization = `Bearer ${response.data.access}`;
      return client(originalRequest);
    } catch (refreshError) {
      flushQueue(refreshError, null);
      clearTokens();
      window.location.href = "/login";
      return Promise.reject(refreshError);
    } finally {
      isRefreshing = false;
    }
  },
);

export default client;
