import { useState } from 'react'
import { getApiErrorMessage, searchEvents } from '../api/api'
import Header from '../components/Header'
import ResultsTable from '../components/ResultsTable'
import SearchCard from '../components/SearchCard'
import UploadCard from '../components/UploadCard'

function Home() {
  const [searchResults, setSearchResults] = useState(null)
  const [searchPayload, setSearchPayload] = useState(null)
  const [searchLoading, setSearchLoading] = useState(false)
  const [pageLoading, setPageLoading] = useState(false)
  const [paginationError, setPaginationError] = useState('')

  function handleSearchStart() {
    setSearchResults(null)
    setSearchPayload(null)
    setSearchLoading(true)
    setPageLoading(false)
    setPaginationError('')
  }

  function handleSearch(response, payload) {
    setSearchResults(response.data)
    setSearchPayload(payload)
    setSearchLoading(false)
    setPaginationError('')
  }

  function handleSearchError() {
    setSearchResults(null)
    setSearchPayload(null)
    setSearchLoading(false)
    setPageLoading(false)
    setPaginationError('')
  }

  function handleClearSearch() {
    setSearchResults(null)
    setSearchPayload(null)
    setSearchLoading(false)
    setPageLoading(false)
    setPaginationError('')
  }

  async function handlePageChange(page) {
    if (!searchPayload || pageLoading) {
      return
    }

    setPageLoading(true)
    setPaginationError('')

    try {
      const response = await searchEvents({
        ...searchPayload,
        page,
      })

      setSearchResults(response.data)
    } catch (error) {
      setPaginationError(
        getApiErrorMessage(error, 'Unable to load this page. Please try again.'),
      )
    } finally {
      setPageLoading(false)
    }
  }

  return (
    <div className="page-shell">
      <main>
        <Header />
        <div className="workspace">
          <UploadCard />
          <SearchCard
            onSearchStart={handleSearchStart}
            onSearch={handleSearch}
            onSearchError={handleSearchError}
            onClear={handleClearSearch}
          />
          <ResultsTable
            searchResults={searchResults}
            searchLoading={searchLoading}
            onPageChange={handlePageChange}
            pageLoading={pageLoading}
            paginationError={paginationError}
          />
        </div>
      </main>
      <footer className="site-footer">
        Aceable Full Stack Assignment <span aria-hidden="true">•</span> React + Django REST Framework
      </footer>
    </div>
  )
}

export default Home
