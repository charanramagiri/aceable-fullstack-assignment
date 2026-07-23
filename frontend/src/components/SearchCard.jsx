import { useState } from 'react'
import { searchEvents } from '../api/api'

function SearchCard({ onSearch }) {
  const [search, setSearch] = useState('')
  const [earliestTime, setEarliestTime] = useState('')
  const [latestTime, setLatestTime] = useState('')
  const [searching, setSearching] = useState(false)
  const [errorMessage, setErrorMessage] = useState('')

  function validateTimeRange() {
    const integerPattern = /^-?\d+$/
    const earliestValue = earliestTime.trim()
    const latestValue = latestTime.trim()

    if (earliestValue && !integerPattern.test(earliestValue)) {
      return 'Earliest time must be a whole number.'
    }

    if (latestValue && !integerPattern.test(latestValue)) {
      return 'Latest time must be a whole number.'
    }

    if (earliestValue && latestValue && BigInt(earliestValue) > BigInt(latestValue)) {
      return 'Earliest time cannot be later than latest time.'
    }

    return ''
  }

  async function handleSubmit(event) {
    event.preventDefault()

    const validationError = validateTimeRange()

    if (validationError) {
      setErrorMessage(validationError)
      return
    }

    const payload = {
      page: 1,
      page_size: 20,
    }
    const searchValue = search.trim()
    const earliestValue = earliestTime.trim()
    const latestValue = latestTime.trim()

    if (searchValue) {
      payload.search = searchValue
    }

    if (earliestValue) {
      payload.earliest_time = earliestValue
    }

    if (latestValue) {
      payload.latest_time = latestValue
    }

    setSearching(true)
    setErrorMessage('')

    try {
      const response = await searchEvents(payload)
      onSearch(response, payload)
    } catch (error) {
      const backendMessage = error.response?.data?.message || error.response?.data?.detail
      setErrorMessage(backendMessage || 'Unable to search events. Please try again.')
    } finally {
      setSearching(false)
    }
  }

  return (
    <section className="card" aria-labelledby="search-title">
      <div className="card-heading">
        <div>
          <p className="card-kicker"></p>
          <h2 id="search-title">Search events</h2>
        </div>
        <span className="status-chip"></span>
      </div>

      <p className="card-description">
        Filter parsed events by address, account, action, and time range.
      </p>

      <form onSubmit={handleSubmit}>
        <div className="search-fields">
        <label>
          Search term
          <input
            type="search"
            placeholder="e.g. account ID or IP address"
            value={search}
            disabled={searching}
            onChange={(event) => setSearch(event.target.value)}
          />
        </label>
        <label>
          Earliest time
          <input
            type="text"
            inputMode="numeric"
            placeholder="Unix timestamp"
            value={earliestTime}
            disabled={searching}
            onChange={(event) => setEarliestTime(event.target.value)}
          />
        </label>
        <label>
          Latest time
          <input
            type="text"
            inputMode="numeric"
            placeholder="Unix timestamp"
            value={latestTime}
            disabled={searching}
            onChange={(event) => setLatestTime(event.target.value)}
          />
        </label>
        </div>

        <button
          className={`primary-button ${searching ? 'is-loading' : ''}`}
          type="submit"
          disabled={searching}
          aria-busy={searching}
        >
          {searching ? 'Searching...' : 'Search events'}
        </button>
      </form>

      {errorMessage && (
        <p className="search-feedback" role="alert">
          {errorMessage}
        </p>
      )}
    </section>
  )
}

export default SearchCard
