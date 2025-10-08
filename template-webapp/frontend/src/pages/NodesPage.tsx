import { useState } from 'react'
import { useNodes, useCreateNode, useDeleteNode } from '../hooks/useNodes'

export default function NodesPage() {
  const { data: nodes, isLoading } = useNodes()
  const createNode = useCreateNode()
  const deleteNode = useDeleteNode()

  const [showCreateForm, setShowCreateForm] = useState(false)
  const [newNode, setNewNode] = useState({
    id: '',
    type: '',
    label: '',
  })

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()

    try {
      await createNode.mutateAsync(newNode)
      setShowCreateForm(false)
      setNewNode({ id: '', type: '', label: '' })
    } catch (err) {
      console.error('Failed to create node:', err)
    }
  }

  const handleDelete = async (nodeId: string) => {
    if (!confirm('Are you sure you want to delete this node?')) return

    try {
      await deleteNode.mutateAsync(nodeId)
    } catch (err) {
      console.error('Failed to delete node:', err)
    }
  }

  return (
    <div className="nodes-page">
      <div className="page-header">
        <h1>RDF Nodes</h1>
        <button
          onClick={() => setShowCreateForm(!showCreateForm)}
          className="btn-primary"
        >
          {showCreateForm ? 'Cancel' : 'Create Node'}
        </button>
      </div>

      {showCreateForm && (
        <div className="create-form-card">
          <h3>Create New Node</h3>
          <form onSubmit={handleCreate}>
            <div className="form-group">
              <label>Node ID</label>
              <input
                type="text"
                value={newNode.id}
                onChange={(e) => setNewNode({ ...newNode, id: e.target.value })}
                placeholder="e.g., node1"
                required
              />
            </div>

            <div className="form-group">
              <label>Type</label>
              <input
                type="text"
                value={newNode.type}
                onChange={(e) => setNewNode({ ...newNode, type: e.target.value })}
                placeholder="e.g., Device"
                required
              />
            </div>

            <div className="form-group">
              <label>Label</label>
              <input
                type="text"
                value={newNode.label}
                onChange={(e) => setNewNode({ ...newNode, label: e.target.value })}
                placeholder="e.g., My Device"
                required
              />
            </div>

            <button type="submit" disabled={createNode.isPending} className="btn-primary">
              {createNode.isPending ? 'Creating...' : 'Create Node'}
            </button>
          </form>
        </div>
      )}

      <div className="nodes-list">
        {isLoading ? (
          <p>Loading nodes...</p>
        ) : nodes && nodes.length > 0 ? (
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Type</th>
                <th>Label</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {nodes.map((node: any) => (
                <tr key={node.id}>
                  <td><code>{node.id.split('#').pop()}</code></td>
                  <td>{node.type.split('#').pop()}</td>
                  <td>{node.label || '-'}</td>
                  <td>
                    <button
                      onClick={() => handleDelete(node.id.split('#').pop())}
                      className="btn-danger btn-small"
                      disabled={deleteNode.isPending}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div className="empty-state">
            <p>No nodes found in the RDF graph.</p>
            <p>Create your first node to get started!</p>
          </div>
        )}
      </div>
    </div>
  )
}
