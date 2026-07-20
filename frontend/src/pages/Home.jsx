import Header from '../components/Header'
import ResultsTable from '../components/ResultsTable'
import SearchCard from '../components/SearchCard'
import UploadCard from '../components/UploadCard'

function Home() {
  return (
    <main className="page-shell">
      <Header />
      <div className="workspace">
        <UploadCard />
        <SearchCard />
        <ResultsTable />
      </div>
    </main>
  )
}

export default Home
