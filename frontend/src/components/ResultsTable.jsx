function ResultsTable({
  searchResults,
  searchLoading,
  onPageChange,
  pageLoading,
  paginationError,
}) {
  const hasSearched = searchResults !== null
  const results = searchResults?.results ?? []
  const resultCount = searchResults?.count ?? 0
  const isBusy = searchLoading || pageLoading

  const resultAnnouncement = searchLoading
    ? 'Searching events.'
    : hasSearched
      ? `${resultCount} ${resultCount === 1 ? 'event' : 'events'} found. Page ${searchResults.page} of ${searchResults.total_pages}.`
      : ''

  return (
    <section
      className="card results-card"
      aria-labelledby="results-title"
      aria-busy={isBusy}
    >
      <div className="card-heading">
        <h2 id="results-title">Search results</h2>
        {hasSearched && (
          <span className="result-count" aria-hidden="true">
            {resultCount} {resultCount === 1 ? 'event' : 'events'}
          </span>
        )}
      </div>

      <p className="sr-only" aria-live="polite" aria-atomic="true">
        {resultAnnouncement}
      </p>

      {searchLoading ? (
        <div className="empty-state" role="status">
          <strong>Searching events…</strong>
          <span>Results will appear here when the search completes.</span>
        </div>
      ) : !hasSearched ? (
        <div className="empty-state">
          <strong>No search yet</strong>
          <span>
            Choose one or more filters to search imported events, or search
            without filters to view all events.
          </span>
        </div>
      ) : (
        <>
          <div className="results-summary">
            <div className="summary-card">
              <span>Total matches</span>
              <strong>{resultCount}</strong>
            </div>
            <div className="summary-card">
              <span>Backend search time</span>
              <strong>{searchResults.search_time}s</strong>
            </div>
          </div>

          <nav className="pagination-controls" aria-label="Search results pagination">
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
              Next
            </button>
          </nav>

          {pageLoading && (
            <p className="page-loading" role="status" aria-live="polite">
              Loading page…
            </p>
          )}

          {paginationError && (
            <p className="pagination-error" role="alert">
              {paginationError}
            </p>
          )}

          <div
            className="table-wrapper"
            tabIndex="0"
            aria-label="Event search results. Scroll horizontally to see all columns."
          >
            <table>
              <caption className="sr-only">Paginated event search results.</caption>
              <thead>
                <tr>
                  <th scope="col">Archive member</th>
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
                      No matching events found. Adjust or clear the filters and try again.
                    </td>
                  </tr>
                ) : (
                  results.map((event, index) => (
                    <tr
                      key={[
                        event.file_name,
                        event.serialno,
                        event.starttime,
                        event.endtime,
                        event.srcaddr,
                        event.dstaddr,
                        index,
                      ].join('-')}
                    >
                      <td title={event.file_name}>{event.file_name}</td>
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
