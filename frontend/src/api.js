import axios from 'axios';

// In development, use the Vite proxy (/api)
// In production or when VITE_API_URL is explicitly set, use the full URL
const isDev = import.meta.env.DEV;
const API_URL = import.meta.env.VITE_API_URL && !isDev
    ? import.meta.env.VITE_API_URL+'/api'
    : '/api';

const api = axios.create({
    baseURL: API_URL,
});

// Log the API URL for debugging (only in development)
if (isDev) {
    console.log('API Base URL:', API_URL);
    console.log('Environment:', import.meta.env.MODE);
}

// Add request interceptor for debugging
if (isDev) {
    api.interceptors.request.use(
        (config) => {
            console.log('API Request:', config.method?.toUpperCase(), config.url);
            return config;
        },
        (error) => {
            console.error('API Request Error:', error);
            return Promise.reject(error);
        }
    );

    api.interceptors.response.use(
        (response) => {
            console.log('API Response:', response.status, response.config.url);
            return response;
        },
        (error) => {
            console.error('API Response Error:', error.response?.status, error.config?.url, error.message);
            return Promise.reject(error);
        }
    );
}

// Projects
export const getProjects = () => api.get('/projects/');
export const createProject = (data) => api.post('/projects/', data);

// Agents
export const getAgents = () => api.get('/agents/');
export const createAgent = (data) => api.post('/agents/', data);

export const deleteAgent = (id, params = {}) => api.delete(`/agents/${id}`, { params });

// Jobs
export const getAllJobs = () => api.get('/jobs/');
export const getJobs = (projectId) => api.get(`/projects/${projectId}/jobs`);
export const createJob = (data) => api.post('/jobs/', data);
export const getJob = (jobId) => api.get(`/jobs/${jobId}`);

// Settings
export const getSettings = () => api.get('/settings/');
export const saveSetting = (data) => api.post('/settings/', data);

// Users & Teams
export const getUsers = () => api.get('/users/');
export const getTeams = () => api.get('/teams/');

export default api;
