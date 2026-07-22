import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
})

export function uploadFiles(files) {
  const formData = new FormData()

  files.forEach((file) => {
    formData.append('files', file)
  })

  return api.post('upload/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
}

export function searchEvents(payload) {
  return api.post('search/', payload)
}

export default api
