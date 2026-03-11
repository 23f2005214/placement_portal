import axios from 'axios'
import store from '../store'
import router from '../router'

const API_URL = 'http://localhost:5000/api'

const api = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' }
})

// Add token to requests
api.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`, token ? '(with token)' : '(no token)')
  return config
})

// Handle errors
api.interceptors.response.use(
  response => response,
  error => {
    console.error('[API Error]', error.response?.status, error.config?.url)
    
    // Logout on 401 (except for auth endpoints)
    if (error.response?.status === 401 && !error.config?.url?.includes('/auth/')) {
      store.commit('CLEAR_AUTH')
      router.push('/login')
    }
    
    return Promise.reject(error)
  }
)

// Admin API
export const adminAPI = {
  getDashboard: () => api.get('/admin/dashboard').then(r => r.data),
  getCompanies: (params) => api.get('/admin/companies', { params }).then(r => r.data),
  getCompany: (id) => api.get(`/admin/companies/${id}`).then(r => r.data),
  approveCompany: (id) => api.post(`/admin/companies/${id}/approve`).then(r => r.data),
  rejectCompany: (id, reason) => api.post(`/admin/companies/${id}/reject`, { reason }).then(r => r.data),
  toggleCompanyBlacklist: (id) => api.post(`/admin/companies/${id}/blacklist`).then(r => r.data),
  toggleCompanyStatus: (id) => api.post(`/admin/companies/${id}/deactivate`).then(r => r.data),
  getStudents: (params) => api.get('/admin/students', { params }).then(r => r.data),
  getStudent: (id) => api.get(`/admin/students/${id}`).then(r => r.data),
  toggleStudentBlacklist: (id) => api.post(`/admin/students/${id}/blacklist`).then(r => r.data),
  getDrives: (params) => api.get('/admin/drives', { params }).then(r => r.data),
  approveDrive: (id) => api.post(`/admin/drives/${id}/approve`).then(r => r.data),
  rejectDrive: (id, remarks) => api.post(`/admin/drives/${id}/reject`, { remarks }).then(r => r.data),
  getMonthlyReport: (params) => api.get('/admin/reports/monthly', { params }).then(r => r.data),
  getBranchStats: () => api.get('/admin/stats/branches').then(r => r.data)
}

// Company API
export const companyAPI = {
  getDashboard: () => api.get('/company/dashboard').then(r => r.data),
  getProfile: () => api.get('/company/profile').then(r => r.data),
  getDrive: (id) => api.get(`/company/drives/${id}`).then(r => r.data),
  createDrive: (data) => api.post('/company/drives', data).then(r => r.data),
  closeDrive: (id) => api.post(`/company/drives/${id}/close`).then(r => r.data),
  getDriveApplications: (id, params) => api.get(`/company/drives/${id}/applications`, { params }).then(r => r.data),
  updateApplicationStatus: (id, data) => api.put(`/company/applications/${id}/status`, data).then(r => r.data),
  scheduleInterview: (id, data) => api.post(`/company/applications/${id}/schedule-interview`, data).then(r => r.data)
}

// Student API
export const studentAPI = {
  getDashboard: () => api.get('/student/dashboard').then(r => r.data),
  getProfile: () => api.get('/student/profile').then(r => r.data),
  getDrive: (id) => api.get(`/student/drives/${id}`).then(r => r.data),
  getDrives: (params) => api.get('/student/drives', { params }).then(r => r.data),
  applyToDrive: (id, letter) => api.post(`/student/drives/${id}/apply`, { cover_letter: letter }).then(r => r.data),
  getApplications: (params) => api.get('/student/applications', { params }).then(r => r.data),
  withdrawApplication: (id) => api.post(`/student/applications/${id}/withdraw`).then(r => r.data),
  respondToOffer: (id, status) => api.post(`/student/applications/${id}/offer-response`, { status }).then(r => r.data),
  getPlacementHistory: () => api.get('/student/placement-history').then(r => r.data),
  exportApplications: () => api.post('/student/applications/export').then(r => r.data),
  checkExportStatus: (taskId) => api.get(`/student/export/${taskId}/status`).then(r => r.data),
  updateProfile: (data) => api.put('/student/profile', data).then(r => r.data)
}

export default api