function ResultsTable({ searchResults, onPageChange, pageLoading, paginationError }) {
  const hasSearched = searchResults !== null
  const results = searchResults?.results ?? []

  return (
    <section className="card results-card" aria-labelledby="results-title">
      <div className="card-heading">
        <div>
          <p className="card-kicker"></p>
          <h2 id="results-title">Search results</h2>
        </div>
        <span className="result-count">
          {hasSearched ? `${searchResults.count} events` : 'No search yet'}
        </span>
      </div>

      {!hasSearched ? (
        <p className="empty-state">No search performed. Use the filters above to explore your event logs.</p>
      ) : (
        <>
          <div className="results-summary">
            <div className="summary-card">
              <span>Total Matches</span>
              <strong>{searchResults.count}</strong>
            </div>
            <div className="summary-card">
              <span>Search Time</span>
              <strong>{searchResults.search_time}s</strong>
            </div>
          </div>

          <div className="pagination-controls">
            <button
              type="button"
              disabled={!searchResults.has_previous || pageLoading}
              onClick={() => onPageChange(searchResults.page - 1)}
            >
              Previous
            </button>
            <span>
              Page {searchResults.page} of {searchResults.total_pages}
            </span>
            <button
              type="button"
              disabled={!searchResults.has_next || pageLoading}
              onClick={() => onPageChange(searchResults.page + 1)}
            >
              {pageLoading ? 'Loading...' : 'Next'}
            </button>
          </div>

          {paginationError && (
            <p className="pagination-error" role="alert">
              {paginationError}
            </p>
          )}

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
                      No matching events found. Try broadening your search filters.
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
