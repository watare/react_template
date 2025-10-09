/**
 * SLD Viewer Page with ReactFlow
 *
 * New implementation using ReactFlow + Dagre for automatic layout
 * Replaces the old custom SVG-based rendering
 */

import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import type { Node, Edge } from '@xyflow/react';
import { SLDReactFlow } from '../components/SLD/SLDReactFlow';
import './SLDViewerPage.css';

interface ReactFlowResponse {
  nodes: Node[];
  edges: Edge[];
  constraints: {
    busbars?: any[];
    rteRules?: any;
  };
  statistics: {
    nodes: number;
    edges: number;
    equipments: number;
    busbars: number;
    connectivityNodes: number;
    triples_extracted: number;
  };
  file_name: string;
  generator: string;
}

export const SLDViewerPageReactFlow: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const fileId = searchParams.get('file_id');

  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);
  const [statistics, setStatistics] = useState<any>(null);
  const [fileName, setFileName] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Rediriger si aucun file_id
    if (!fileId) {
      navigate('/');
      return;
    }

    loadReactFlowLayout();
  }, [fileId, navigate]);

  const loadReactFlowLayout = async () => {
    if (!fileId) return;

    setIsLoading(true);
    setError(null);

    try {
      const token = localStorage.getItem('token');

      if (!token) {
        throw new Error('Not authenticated. Please login first.');
      }

      const apiUrl = `${import.meta.env.VITE_API_URL}/api/sld/reactflow-layout`;
      const requestBody = { file_id: parseInt(fileId) };

      console.log('ReactFlow Layout API Request:', {
        url: apiUrl,
        body: requestBody,
      });

      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        console.error('ReactFlow API Error Response:', {
          status: response.status,
          statusText: response.statusText,
        });
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        console.error('Error data:', errorData);
        throw new Error(errorData.detail || `Failed to generate layout (${response.status})`);
      }

      const data: ReactFlowResponse = await response.json();

      console.log('ReactFlow layout loaded:', data);
      console.log('Nodes have positions:', data.nodes.every((n: any) => n.position));

      setNodes(data.nodes);
      setEdges(data.edges);
      setStatistics(data.statistics);
      setFileName(data.file_name);
    } catch (err) {
      console.error('Error loading ReactFlow layout:', err);
      setError(err instanceof Error ? err.message : 'Failed to load layout');
    } finally {
      setIsLoading(false);
    }
  };

  const handleRefresh = () => {
    loadReactFlowLayout();
  };

  const handleNodeDragStop = (nodeId: string, position: { x: number; y: number }) => {
    console.log('Node drag stopped:', nodeId, position);
    // TODO: Save position to RDF DiagramLayout
  };

  return (
    <div className="sld-viewer-page">
      {/* Header */}
      <div className="page-header">
        <div>
          <h1>Single Line Diagram (ReactFlow)</h1>
          {fileName && <p className="subtitle">{fileName}</p>}
        </div>
        <div className="sld-toolbar">
          <button className="btn-secondary btn-small" onClick={() => navigate('/')}>
            ← Back
          </button>
          <button className="btn-secondary btn-small" onClick={handleRefresh} disabled={isLoading}>
            ↻ Refresh
          </button>
          <button
            className="btn-secondary btn-small"
            onClick={() => navigate(`/ied-explorer?file_id=${fileId}`)}
          >
            IED Explorer
          </button>
        </div>
      </div>

      {/* Statistics Panel - Compact */}
      {statistics && (
        <div className="sld-statistics">
          <span className="stat-compact">
            Nodes: <strong>{statistics.nodes}</strong>
          </span>
          <span className="stat-compact">
            Edges: <strong>{statistics.edges}</strong>
          </span>
          <span className="stat-compact">
            Equipment: <strong>{statistics.equipments}</strong>
          </span>
          <span className="stat-compact">
            Busbars: <strong>{statistics.busbars}</strong>
          </span>
          <span className="stat-compact">
            Connectivity Nodes: <strong>{statistics.connectivityNodes}</strong>
          </span>
        </div>
      )}

      {/* Main Content */}
      <div className="sld-content" style={{ height: 'calc(100vh - 200px)' }}>
        {isLoading && (
          <div className="sld-loading">
            <div className="spinner"></div>
            <p>Generating ReactFlow layout...</p>
            <p className="loading-hint">Extracting topology and calculating positions</p>
          </div>
        )}

        {error && (
          <div className="sld-error">
            <h2>❌ Error</h2>
            <p>{error}</p>
            <button onClick={handleRefresh}>Try Again</button>
          </div>
        )}

        {!isLoading && !error && nodes.length > 0 && (
          <SLDReactFlow
            nodes={nodes}
            edges={edges}
            onNodeDragStop={handleNodeDragStop}
          />
        )}

        {!isLoading && !error && nodes.length === 0 && (
          <div className="sld-empty">
            <p>No diagram data available</p>
            <button onClick={handleRefresh}>Generate Diagram</button>
          </div>
        )}
      </div>
    </div>
  );
};
