function SearchCard() {
  return (
    <section className="card" aria-labelledby="search-title">
      <div className="card-heading">
        <div>
          <p className="card-kicker">Step 2</p>
          <h2 id="search-title">Search events</h2>
        </div>
        <span className="status-chip">Coming soon</span>
      </div>

      <p className="card-description">
        Filter parsed events by address, account, action, and time range.
      </p>

      <div className="search-fields">
        <label>
          Search term
          <input type="search" placeholder="e.g. account ID or IP address" disabled />
        </label>
        <label>
          Earliest time
          <input type="number" placeholder="Unix timestamp" disabled />
        </label>
        <label>
          Latest time
          <input type="number" placeholder="Unix timestamp" disabled />
        </label>
      </div>

      <button className="primary-button" type="button" disabled>
        Search events
      </button>
    </section>
  )
}

export default SearchCard
