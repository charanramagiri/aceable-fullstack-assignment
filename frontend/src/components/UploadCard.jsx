function UploadCard() {
  return (
    <section className="card" aria-labelledby="upload-title">
      <div className="card-heading">
        <div>
          <p className="card-kicker">Step 1</p>
          <h2 id="upload-title">Upload event files</h2>
        </div>
        <span className="status-chip">Coming soon</span>
      </div>

      <p className="card-description">
        Choose one or more event log files to make them available for search.
      </p>

      <label className="file-dropzone" htmlFor="event-files">
        <span className="file-dropzone-title">Select log files</span>
        <span className="file-dropzone-help">File uploads will be enabled in a future update.</span>
      </label>
      <input id="event-files" type="file" multiple disabled />
    </section>
  )
}

export default UploadCard
