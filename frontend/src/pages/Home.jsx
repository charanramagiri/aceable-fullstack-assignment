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
    <main className="page-shell">
      <Header />
      <div className="workspace">
        <UploadCard />
        <SearchCard onSearch={handleSearch} />
        <ResultsTable searchResults={searchResults} />
      </div>
    </main>
  )
}

export default Home
