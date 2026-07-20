function ResultsTable() {
  return (
    <section className="card results-card" aria-labelledby="results-title">
      <div className="card-heading">
        <div>
          <p className="card-kicker">Step 3</p>
          <h2 id="results-title">Search results</h2>
        </div>
        <span className="result-count">0 events</span>
      </div>

      <div className="table-wrapper">
        <table>
          <thead>
            <tr>
              <th scope="col">Source</th>
              <th scope="col">Destination</th>
              <th scope="col">Action</th>
              <th scope="col">Time</th>
              <th scope="col">File</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td colSpan="5" className="empty-state">
                Upload files and run a search to see matching event logs here.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  )
}

export default ResultsTable
