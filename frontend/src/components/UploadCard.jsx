import { useRef, useState } from 'react'
import { uploadFiles } from '../api/api'

function UploadCard() {
  const fileInputRef = useRef(null)
  const [selectedFiles, setSelectedFiles] = useState([])
  const [uploading, setUploading] = useState(false)
  const [successMessage, setSuccessMessage] = useState('')
  const [errorMessage, setErrorMessage] = useState('')

  function handleFileChange(event) {
    setSelectedFiles(Array.from(event.target.files))
    setSuccessMessage('')
    setErrorMessage('')
  }

  async function handleUpload() {
    if (selectedFiles.length === 0 || uploading) {
      return
    }

    setUploading(true)
    setSuccessMessage('')
    setErrorMessage('')

    try {
      const response = await uploadFiles(selectedFiles)

      setSuccessMessage(response.data.message)
      setSelectedFiles([])
      fileInputRef.current.value = ''
    } catch (error) {
      const backendMessage = error.response?.data?.message
      setErrorMessage(backendMessage || 'Unable to upload files. Please try again.')
    } finally {
      setUploading(false)
    }
  }

  return (
    <section className="card" aria-labelledby="upload-title">
      <div className="card-heading">
        <div>
          <p className="card-kicker">Step 1</p>
          <h2 id="upload-title">Upload event files</h2>
        </div>
        <span className="status-chip">Ready</span>
      </div>

      <p className="card-description">
        Choose one or more event log files to make them available for search.
      </p>

      <label className="file-dropzone" htmlFor="event-files">
        <span className="file-dropzone-title">Select log files</span>
        <span className="file-dropzone-help">Choose one or more event log files to upload.</span>
      </label>
      <input
        ref={fileInputRef}
        id="event-files"
        type="file"
        multiple
        disabled={uploading}
        onChange={handleFileChange}
      />

      {selectedFiles.length > 0 && (
        <div className="selected-files">
          <p>Selected files ({selectedFiles.length})</p>
          <ul>
            {selectedFiles.map((file) => (
              <li key={`${file.name}-${file.lastModified}`}>{file.name}</li>
            ))}
          </ul>
        </div>
      )}

      <button
        className="primary-button"
        type="button"
        disabled={selectedFiles.length === 0 || uploading}
        onClick={handleUpload}
      >
        {uploading ? 'Uploading...' : 'Upload files'}
      </button>

      {successMessage && (
        <p className="upload-feedback upload-success" role="status">
          {successMessage}
        </p>
      )}

      {errorMessage && (
        <p className="upload-feedback upload-error" role="alert">
          {errorMessage}
        </p>
      )}
    </section>
  )
}

export default UploadCard
