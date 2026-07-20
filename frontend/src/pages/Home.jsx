import { useState } from 'react'
import Header from '../components/Header'
import ResultsTable from '../components/ResultsTable'
import SearchCard from '../components/SearchCard'
import UploadCard from '../components/UploadCard'

function Home() {
  const [searchResults, setSearchResults] = useState(null)

  function handleSearch(response) {
    setSearchResults(response.data)
  }

  return (
    <div className="page-shell">
      <main>
        <Header />
        <div className="workspace">
          <UploadCard />
          <SearchCard onSearch={handleSearch} />
          <ResultsTable searchResults={searchResults} />
        </div>
      </main>
      <footer className="site-footer">
        Aceable Full Stack Assignment <span aria-hidden="true">•</span> React + Django REST Framework
      </footer>
    </div>
  )
}

export default Home
