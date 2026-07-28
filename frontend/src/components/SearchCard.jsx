import { useState } from 'react'
import { getApiErrorMessage, searchEvents } from '../api/api'

const SEARCH_ERROR_ID = 'search-error'

function SearchCard({ onSearchStart, onSearch, onSearchError, onClear }) {
  const [search, setSearch] = useState('')
  const [earliestTime, setEarliestTime] = useState('')
  const [latestTime, setLatestTime] = useState('')
  const [searching, setSearching] = useState(false)
  const [errorMessage, setErrorMessage] = useState('')
  const [invalidFields, setInvalidFields] = useState([])

  function validateTimeRange() {
    const integerPattern = /^-?\d+$/
    const earliestValue = earliestTime.trim()
    const latestValue = latestTime.trim()

    if (earliestValue && !integerPattern.test(earliestValue)) {
      return {
        message: 'Earliest time must be a whole-number Unix timestamp.',
        fields: ['earliest-time'],
      }
    }

    if (latestValue && !integerPattern.test(latestValue)) {
      return {
        message: 'Latest time must be a whole-number Unix timestamp.',
        fields: ['latest-time'],
      }
    }

    if (earliestValue && latestValue && BigInt(earliestValue) > BigInt(latestValue)) {
      return {
        message: 'Earliest Unix timestamp cannot be later than latest Unix timestamp.',
        fields: ['earliest-time', 'latest-time'],
      }
    }

    return null
  }

  function clearError() {
    setErrorMessage('')
    setInvalidFields([])
  }

  function handleClear() {
    setSearch('')
    setEarliestTime('')
    setLatestTime('')
    clearError()
    onClear()
  }

  async function handleSubmit(event) {
    event.preventDefault()

    const validationError = validateTimeRange()

    if (validationError) {
      setErrorMessage(validationError.message)
      setInvalidFields(validationError.fields)
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
    clearError()
    onSearchStart()

    try {
      const response = await searchEvents(payload)
      onSearch(response, payload)
    } catch (error) {
      setErrorMessage(
        getApiErrorMessage(error, 'Unable to search events. Please try again.'),
      )
      setInvalidFields([])
      onSearchError()
    } finally {
      setSearching(false)
    }
  }

  return (
    <section className="card" aria-labelledby="search-title">
      <div className="card-heading">
        <h2 id="search-title">Search events</h2>
      </div>

      <p className="card-description">
        Search account IDs, instance IDs, source or destination IPs, actions, and log
        status. Leave filters blank to browse all events.
      </p>

      <form onSubmit={handleSubmit}>
        <div className="search-fields">
          <label htmlFor="event-search">
            Search term
            <input
              id="event-search"
              type="search"
              placeholder="Account, instance, IP, action, or log status"
              value={search}
              disabled={searching}
              onChange={(event) => {
                setSearch(event.target.value)
                clearError()
              }}
            />
          </label>
          <label htmlFor="earliest-time">
            Earliest start time (Unix seconds)
            <input
              id="earliest-time"
              type="text"
              inputMode="numeric"
              placeholder="Unix timestamp"
              value={earliestTime}
              disabled={searching}
              aria-invalid={invalidFields.includes('earliest-time')}
              aria-describedby={errorMessage ? SEARCH_ERROR_ID : undefined}
              onChange={(event) => {
                setEarliestTime(event.target.value)
                clearError()
              }}
            />
          </label>
          <label htmlFor="latest-time">
            Latest end time (Unix seconds)
            <input
              id="latest-time"
              type="text"
              inputMode="numeric"
              placeholder="Unix timestamp"
              value={latestTime}
              disabled={searching}
              aria-invalid={invalidFields.includes('latest-time')}
              aria-describedby={errorMessage ? SEARCH_ERROR_ID : undefined}
              onChange={(event) => {
                setLatestTime(event.target.value)
                clearError()
              }}
            />
          </label>
        </div>

        <div className="form-actions">
          <button
            className={`primary-button ${searching ? 'is-loading' : ''}`}
            type="submit"
            disabled={searching}
            aria-busy={searching}
          >
            {searching ? 'Searching…' : 'Search events'}
          </button>
          <button
            className="secondary-button"
            type="button"
            disabled={searching}
            onClick={handleClear}
          >
            Clear filters
          </button>
        </div>
      </form>

      {errorMessage && (
        <p id={SEARCH_ERROR_ID} className="search-feedback" role="alert">
          {errorMessage}
        </p>
      )}
    </section>
  )
}

export default SearchCard
