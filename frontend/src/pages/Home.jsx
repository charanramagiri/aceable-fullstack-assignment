import { useState } from 'react'
import { searchEvents } from '../api/api'
import Header from '../components/Header'
import ResultsTable from '../components/ResultsTable'
import SearchCard from '../components/SearchCard'
import UploadCard from '../components/UploadCard'

function Home() {
  const [searchResults, setSearchResults] = useState(null)
  const [searchPayload, setSearchPayload] = useState(null)
  const [pageLoading, setPageLoading] = useState(false)
  const [paginationError, setPaginationError] = useState('')

  function handleSearch(response, payload) {
    setSearchResults(response.data)
    setSearchPayload(payload)
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
      const backendMessage = error.response?.data?.detail || error.response?.data?.message
      setPaginationError(backendMessage || 'Unable to load this page. Please try again.')
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
          <SearchCard onSearch={handleSearch} />
          <ResultsTable
            searchResults={searchResults}
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
