import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
})

function firstErrorMessage(value) {
  if (typeof value === 'string') {
    return value
  }

  if (Array.isArray(value)) {
    return value.map(firstErrorMessage).find(Boolean)
  }

  if (value && typeof value === 'object') {
    return Object.values(value).map(firstErrorMessage).find(Boolean)
  }

  return ''
}

export function getApiErrorMessage(error, fallback) {
  const data = error.response?.data

  return (
    firstErrorMessage(data?.detail)
    || firstErrorMessage(data?.message)
    || firstErrorMessage(data)
    || fallback
  )
}

export function uploadFiles(files) {
  const formData = new FormData()

  files.forEach((file) => {
    formData.append('files', file)
  })

  return api.post('upload/', formData)
}

export function searchEvents(payload) {
  return api.post('search/', payload)
}
