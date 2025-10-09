import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './contexts/AuthContext'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import NodesPage from './pages/NodesPage'
import SCLFilesPage from './pages/SCLFilesPage'
import RDFSchemaPage from './pages/RDFSchemaPage'
import IEDExplorerPage from './pages/IEDExplorerPage'
import Layout from './components/Layout'

function App() {
  const { isAuthenticated } = useAuth()

  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />

      <Route
        path="/"
        element={
          isAuthenticated ? <Layout /> : <Navigate to="/login" replace />
        }
      >
        <Route index element={<DashboardPage />} />
        <Route path="nodes" element={<NodesPage />} />
        <Route path="scl-files" element={<SCLFilesPage />} />
        <Route path="scl-files/:fileId/rdf-schema" element={<RDFSchemaPage />} />
        <Route path="ied-explorer" element={<IEDExplorerPage />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App
