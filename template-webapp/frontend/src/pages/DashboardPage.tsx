import { useAuth } from '../contexts/AuthContext'
import { useNodeStats } from '../hooks/useNodes'
import { useSCLFiles } from '../hooks/useSCLFiles'
import { useNavigate } from 'react-router-dom'
import { useState, useRef } from 'react'

export default function DashboardPage() {
  const { user } = useAuth()
  const { data: stats, isLoading } = useNodeStats()
  const { files, uploadFile, refreshFiles } = useSCLFiles()
  const navigate = useNavigate()
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [uploading, setUploading] = useState(false)

  const isAdmin = user?.is_superuser || user?.roles?.some((r: any) => r.name === 'admin')
  const recentFiles = files.slice(0, 5) // Top 5 most recent

  const handleQuickUpload = async (selectedFiles: FileList | null) => {
    if (!selectedFiles || selectedFiles.length === 0) return

    const file = selectedFiles[0]

    // Validate file extension
    const validExtensions = ['.scd', '.icd', '.cid', '.SCD', '.ICD', '.CID']
    const hasValidExtension = validExtensions.some(ext => file.name.endsWith(ext))

    if (!hasValidExtension) {
      alert('Invalid file format. Only .scd, .icd, .cid files are supported.')
      return
    }

    // Validate file size (100MB max)
    const maxSize = 100 * 1024 * 1024
    if (file.size > maxSize) {
      alert(`File too large. Maximum size is ${maxSize / (1024 * 1024)}MB`)
      return
    }

    setUploading(true)
    try {
      await uploadFile(file)
      await refreshFiles()
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
      alert('File uploaded successfully! Processing in background...')
    } catch (err) {
      alert(`Upload failed: ${err}`)
    } finally {
      setUploading(false)
    }
  }

  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'uploaded': return 'bg-blue-100 text-blue-800'
      case 'converting': return 'bg-yellow-100 text-yellow-800'
      case 'converted': return 'bg-green-100 text-green-800'
      case 'validated': return 'bg-green-200 text-green-900'
      case 'failed': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`
  }

  return (
    <div className="dashboard-page">
      <h1>Dashboard</h1>

      <div className="welcome-section">
        <h2>Welcome back, {user?.full_name || user?.username}!</h2>
        <p>Here's an overview of your data.</p>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <h3>User Info</h3>
          <div>
            <p><strong>Email:</strong> {user?.email}</p>
            <p><strong>Username:</strong> {user?.username}</p>
            <p><strong>Role:</strong> {user?.is_superuser ? 'Admin' : 'User'}</p>
          </div>
        </div>

        <div className="stat-card">
          <h3>RDF Graph Statistics</h3>
          {isLoading ? (
            <p>Loading...</p>
          ) : (
            <div>
              {stats?.stats && stats.stats.length > 0 ? (
                <ul>
                  {stats.stats.map((stat: any) => (
                    <li key={stat.type}>
                      <strong>{stat.type.split('#').pop()}:</strong> {stat.count} nodes
                    </li>
                  ))}
                </ul>
              ) : (
                <p>No data in RDF graph yet.</p>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Admin-only: SCL File Upload Widget */}
      {isAdmin && (
        <div className="stat-card" style={{ marginTop: '2rem' }}>
          <h3>📤 Upload SCL File (Admin)</h3>
          <p style={{ fontSize: '0.9rem', color: '#666', marginBottom: '1rem' }}>
            Upload IEC 61850 files (.scd, .icd, .cid) for automatic RDF conversion
          </p>

          <input
            ref={fileInputRef}
            type="file"
            accept=".scd,.icd,.cid,.SCD,.ICD,.CID"
            onChange={(e) => handleQuickUpload(e.target.files)}
            style={{ display: 'none' }}
            id="dashboard-file-upload"
          />

          {uploading ? (
            <div style={{ padding: '1rem', backgroundColor: '#e3f2fd', borderRadius: '8px', textAlign: 'center' }}>
              <p style={{ margin: 0, color: '#1976d2' }}>⏳ Uploading...</p>
            </div>
          ) : (
            <div style={{ display: 'flex', gap: '1rem' }}>
              <label
                htmlFor="dashboard-file-upload"
                className="btn-secondary"
                style={{ cursor: 'pointer', flex: 1, textAlign: 'center' }}
              >
                Choose File
              </label>
              <button
                onClick={() => navigate('/scl-files')}
                className="btn-secondary"
                style={{ flex: 1 }}
              >
                View All Files
              </button>
            </div>
          )}
        </div>
      )}

      {/* Admin-only: Recent SCL Files */}
      {isAdmin && recentFiles.length > 0 && (
        <div className="stat-card" style={{ marginTop: '1rem' }}>
          <h3>📁 Recent SCL Files</h3>
          <div style={{ marginTop: '1rem' }}>
            {recentFiles.map((file) => (
              <div
                key={file.id}
                style={{
                  padding: '0.75rem',
                  borderBottom: '1px solid #eee',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  cursor: 'pointer'
                }}
                onClick={(e) => {
                  // Don't navigate if clicking the explore button
                  if ((e.target as HTMLElement).closest('.explore-button')) {
                    return;
                  }
                  if (file.status === 'validated') {
                    navigate(`/scl-files/${file.id}/rdf-schema`)
                  } else {
                    navigate('/scl-files')
                  }
                }}
              >
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 500, fontSize: '0.9rem', marginBottom: '0.25rem' }}>
                    {file.original_filename}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: '#666' }}>
                    {formatFileSize(file.file_size)} • {new Date(file.uploaded_at).toLocaleDateString()}
                    {file.triple_count && ` • ${file.triple_count.toLocaleString()} triples`}
                  </div>
                  {/* Progress indicator for converting files */}
                  {file.status === 'converting' && file.progress_percent !== null && (
                    <div style={{ marginTop: '0.5rem' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
                        <div style={{ flex: 1, height: '4px', backgroundColor: '#e0e0e0', borderRadius: '2px', overflow: 'hidden' }}>
                          <div
                            style={{
                              width: `${file.progress_percent}%`,
                              height: '100%',
                              backgroundColor: '#2196F3',
                              transition: 'width 0.3s ease'
                            }}
                          ></div>
                        </div>
                        <span style={{ fontSize: '0.7rem', color: '#666', minWidth: '35px' }}>
                          {file.progress_percent}%
                        </span>
                      </div>
                      {file.stage_message && (
                        <div style={{ fontSize: '0.7rem', color: '#888' }}>
                          {file.stage_message}
                        </div>
                      )}
                    </div>
                  )}
                </div>
                <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                  {file.status === 'validated' && (
                    <>
                      <button
                        className="explore-button"
                        onClick={(e) => {
                          e.stopPropagation();
                          navigate(`/ied-explorer?file_id=${file.id}`);
                        }}
                        style={{
                          padding: '0.4rem 0.8rem',
                          backgroundColor: '#2196F3',
                          color: 'white',
                          border: 'none',
                          borderRadius: '4px',
                          fontSize: '0.75rem',
                          cursor: 'pointer',
                          fontWeight: 500
                        }}
                      >
                        🔍 Explore IEDs
                      </button>
                      <button
                        className="sld-button"
                        onClick={(e) => {
                          e.stopPropagation();
                          navigate(`/sld-viewer?file_id=${file.id}`);
                        }}
                        style={{
                          padding: '0.4rem 0.8rem',
                          backgroundColor: '#4CAF50',
                          color: 'white',
                          border: 'none',
                          borderRadius: '4px',
                          fontSize: '0.75rem',
                          cursor: 'pointer',
                          fontWeight: 500
                        }}
                      >
                        📊 View SLD
                      </button>
                    </>
                  )}
                  <span
                    className={getStatusColor(file.status)}
                    style={{
                      padding: '0.25rem 0.5rem',
                      borderRadius: '9999px',
                      fontSize: '0.75rem',
                      fontWeight: 500
                    }}
                  >
                    {file.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
          <button
            onClick={() => navigate('/scl-files')}
            style={{
              marginTop: '1rem',
              width: '100%',
              padding: '0.5rem',
              backgroundColor: 'transparent',
              border: '1px solid #ddd',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '0.85rem'
            }}
          >
            View All Files →
          </button>
        </div>
      )}

      <div className="quick-actions">
        <h3>Quick Actions</h3>
        <div className="action-buttons">
          <a href="/nodes" className="btn-secondary">View Nodes</a>
          {isAdmin && (
            <a href="/scl-files" className="btn-secondary">SCL Files</a>
          )}
          <a href="http://localhost:3030" target="_blank" rel="noopener noreferrer" className="btn-secondary">
            Open Fuseki UI
          </a>
          <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer" className="btn-secondary">
            API Documentation
          </a>
        </div>
      </div>
    </div>
  )
}
