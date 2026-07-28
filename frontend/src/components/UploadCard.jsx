import { useRef, useState } from 'react'
import { getApiErrorMessage, uploadFiles } from '../api/api'

function formatFileSize(bytes) {
  if (bytes < 1024) {
    return `${bytes} ${bytes === 1 ? 'byte' : 'bytes'}`
  }

  if (bytes < 1024 * 1024) {
    return `${(bytes / 1024).toFixed(1)} KB`
  }

  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function pluralize(count, singular, plural) {
  return count === 1 ? singular : plural
}

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

    const submittedArchiveCount = selectedFiles.length
    setUploading(true)
    setSuccessMessage('')
    setErrorMessage('')

    try {
      const response = await uploadFiles(selectedFiles)
      const importedMemberCount = response.data.files.length

      setSuccessMessage(
        `Imported ${importedMemberCount} ${pluralize(importedMemberCount, 'archive member', 'archive members')} from ${submittedArchiveCount} submitted ${pluralize(submittedArchiveCount, 'archive', 'archives')}.`,
      )
      setSelectedFiles([])
      fileInputRef.current.value = ''
    } catch (error) {
      setErrorMessage(
        getApiErrorMessage(error, 'Unable to upload archives. Please try again.'),
      )
    } finally {
      setUploading(false)
    }
  }

  return (
    <section
      className="card upload-card"
      aria-labelledby="upload-title"
      aria-busy={uploading}
    >
      <div className="card-heading">
        <h2 id="upload-title">Upload archives</h2>
      </div>

      <p className="card-description">
        Choose one or more .tgz or .tar.gz archives. Each regular event member will be
        imported and made searchable.
      </p>

      <label className="file-dropzone" htmlFor="event-files">
        <span className="file-dropzone-title">Select archives</span>
        <span id="archive-file-help" className="file-dropzone-help">
          Choose one or more .tgz or .tar.gz files.
        </span>
      </label>
      <input
        ref={fileInputRef}
        id="event-files"
        type="file"
        accept=".tgz,.tar.gz"
        multiple
        disabled={uploading}
        aria-describedby="archive-file-help"
        onChange={handleFileChange}
      />

      {selectedFiles.length > 0 && (
        <div className="selected-files">
          <p>Selected archives ({selectedFiles.length})</p>
          <ul>
            {selectedFiles.map((file, index) => (
              <li key={`${file.name}-${file.size}-${file.lastModified}-${index}`}>
                <span className="selected-file-name">{file.name}</span>
                <span className="selected-file-size">{formatFileSize(file.size)}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      <button
        className={`primary-button ${uploading ? 'is-loading' : ''}`}
        type="button"
        disabled={selectedFiles.length === 0 || uploading}
        onClick={handleUpload}
        aria-busy={uploading}
      >
        {uploading ? 'Uploading and importing…' : 'Upload archives'}
      </button>

      {uploading && (
        <p
          className="upload-feedback upload-progress"
          role="status"
          aria-live="polite"
        >
          Uploading and importing archives. Large imports may take 30 seconds or longer.
        </p>
      )}

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
