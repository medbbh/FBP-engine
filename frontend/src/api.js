import axios from 'axios'

const http = axios.create({ baseURL: '/api' })

http.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

http.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export const login = (email, password) => {
  const form = new URLSearchParams()
  form.append('username', email)
  form.append('password', password)
  return http.post('/auth/token', form)
}

export const getFacilities = (skip = 0, limit = 100) =>
  http.get('/facilities/', { params: { skip, limit } })

export const getDeclaration = (id) => http.get(`/declarations/${id}`)

export const getIndicators = (limit = 100) =>
  http.get('/indicators/', { params: { limit } })

export const getChecklist = (limit = 100) =>
  http.get('/indicators/checklist', { params: { limit } })

export const createFacility = (data) => http.post('/facilities/', data)

export const createDeclaration = (data) => http.post('/declarations/', data)

export const submitQuantity = (id, items) =>
  http.post(`/declarations/${id}/quantity`, items)

export const submitQuality = (id, items) =>
  http.post(`/declarations/${id}/quality`, items)

export const verifyDeclaration = (id) =>
  http.post(`/declarations/${id}/verify`)

export const getPayment = (id) => http.get(`/declarations/${id}/payment`)

export const getAnomalies = (id) => http.get(`/declarations/${id}/anomalies`)

export const recordAudit = (id, data) =>
  http.post(`/declarations/${id}/audit`, data)

export const getFacilityReport = (facilityId) =>
  http.get(`/reports/facility/${facilityId}`)
