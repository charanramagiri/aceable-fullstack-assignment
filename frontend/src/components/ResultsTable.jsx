function ResultsTable({ searchResults }) {
  const hasSearched = searchResults !== null
  const results = searchResults?.results ?? []

  return (
    <section className="card results-card" aria-labelledby="results-title">
      <div className="card-heading">
        <div>
          <p className="card-kicker">Step 3</p>
          <h2 id="results-title">Search results</h2>
        </div>
        <span className="result-count">
          {hasSearched ? `${searchResults.count} events` : 'No search yet'}
        </span>
      </div>

      {!hasSearched ? (
        <p className="empty-state">No search performed.</p>
      ) : (
        <>
          <div className="results-summary">
            <p>
              Total Matches <strong>{searchResults.count}</strong>
            </p>
            <p>
              Search Time <strong>{searchResults.search_time}s</strong>
            </p>
          </div>

      <div className="table-wrapper">
        <table>
          <thead>
            <tr>
              <th scope="col">File Name</th>
              <th scope="col">Source IP</th>
              <th scope="col">Destination IP</th>
              <th scope="col">Action</th>
              <th scope="col">Status</th>
            </tr>
          </thead>
          <tbody>
            {results.length === 0 ? (
              <tr>
                <td colSpan="5" className="empty-state">
                  No matching events found.
                </td>
              </tr>
            ) : (
              results.map((event, index) => (
                <tr key={`${event.file_name}-${event.serialno}-${index}`}>
                  <td>{event.file_name}</td>
                  <td>{event.srcaddr}</td>
                  <td>{event.dstaddr}</td>
                  <td>{event.action}</td>
                  <td>{event.log_status}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
        </>
      )}
    </section>
  )
}

export default ResultsTable
