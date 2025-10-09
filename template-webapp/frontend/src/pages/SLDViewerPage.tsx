/**
 * SLD Viewer Page
 *
 * Affiche le schéma unifilaire (Single Line Diagram) généré depuis les données IEC 61850
 */

import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { SLDCanvas } from '../components/SLD';
import './SLDViewerPage.css';

interface SLDStatistics {
  substations: number;
  voltage_levels: number;
  bays: number;
  equipments: number;
  triples_extracted: number;
  original_file_size?: number;
}

interface EquipmentData {
  name: string;
  type: string;
  subtype?: string;
  order: number;
}

interface BayData {
  name: string;
  is_coupling: boolean;
  equipments: EquipmentData[];
}

interface VoltageLevelData {
  name: string;
  voltage?: string;
  bays: BayData[];
}

interface SubstationData {
  name: string;
  voltage_levels: VoltageLevelData[];
}

interface SLDResponse {
  substations: SubstationData[];
  statistics: SLDStatistics;
  file_name: string;
  generator: string;
}

export const SLDViewerPage: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const fileId = searchParams.get('file_id');

  const [substations, setSubstations] = useState<SubstationData[]>([]);
  const [statistics, setStatistics] = useState<SLDStatistics | null>(null);
  const [fileName, setFileName] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedEquipment, setSelectedEquipment] = useState<string | null>(null);

  useEffect(() => {
    // Rediriger si aucun file_id
    if (!fileId) {
      navigate('/');
      return;
    }

    loadSLD();
  }, [fileId, navigate]);

  const loadSLD = async () => {
    if (!fileId) return;

    setIsLoading(true);
    setError(null);

    try {
      const token = localStorage.getItem('token');

      if (!token) {
        throw new Error('Not authenticated. Please login first.');
      }

      const apiUrl = `${import.meta.env.VITE_API_URL}/api/sld/generate-data`;
      const requestBody = { file_id: parseInt(fileId) };

      console.log('SLD API Request:', {
        url: apiUrl,
        body: requestBody,
        tokenLength: token?.length,
        tokenPreview: token?.substring(0, 20) + '...'
      });

      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(requestBody)
      });

      if (!response.ok) {
        console.error('SLD API Error Response:', {
          status: response.status,
          statusText: response.statusText,
          url: response.url
        });
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        console.error('Error data:', errorData);
        throw new Error(errorData.detail || `Failed to generate SLD (${response.status})`);
      }

      const data: SLDResponse = await response.json();
      setSubstations(data.substations);
      setStatistics(data.statistics);
      setFileName(data.file_name);
    } catch (err) {
      console.error('Error loading SLD:', err);
      setError(err instanceof Error ? err.message : 'Failed to load SLD');
    } finally {
      setIsLoading(false);
    }
  };

  const handleRefresh = () => {
    loadSLD();
  };

  const handleEquipmentSelect = (equipmentName: string) => {
    setSelectedEquipment(equipmentName);
    console.log('Equipment selected:', equipmentName);
    // TODO: Show equipment details panel
  };

  return (
    <div className="sld-viewer-page">
      {/* Header */}
      <div className="page-header">
        <div>
          <h1>Single Line Diagram</h1>
          {fileName && <p className="subtitle">{fileName}</p>}
        </div>
        <div className="sld-toolbar">
          <button
            className="btn-secondary btn-small"
            onClick={() => navigate('/')}
          >
            ← Back
          </button>
          <button
            className="btn-secondary btn-small"
            onClick={handleRefresh}
            disabled={isLoading}
          >
            ↻ Refresh
          </button>
          <button
            className="btn-secondary btn-small"
            onClick={() => navigate(`/ied-explorer?file_id=${fileId}`)}
          >
            IED Explorer
          </button>
          {selectedEquipment && (
            <span className="selected-equipment-indicator">
              Selected: <strong>{selectedEquipment}</strong>
            </span>
          )}
        </div>
      </div>

      {/* Statistics Panel - Compact */}
      {statistics && (
        <div className="sld-statistics">
          <span className="stat-compact">Substations: <strong>{statistics.substations}</strong></span>
          <span className="stat-compact">Voltage Levels: <strong>{statistics.voltage_levels}</strong></span>
          <span className="stat-compact">Bays: <strong>{statistics.bays}</strong></span>
          <span className="stat-compact">Equipment: <strong>{statistics.equipments}</strong></span>
        </div>
      )}

      {/* Main Content */}
      <div className="sld-content">
        {isLoading && (
          <div className="sld-loading">
            <div className="spinner"></div>
            <p>Generating single line diagram...</p>
            <p className="loading-hint">Extracting topology from RDF data</p>
          </div>
        )}

        {error && (
          <div className="sld-error">
            <h2>❌ Error</h2>
            <p>{error}</p>
            <button onClick={handleRefresh}>Try Again</button>
          </div>
        )}

        {!isLoading && !error && substations.length > 0 && (
          <div className="sld-canvas">
            <SLDCanvas
              substations={substations}
              onEquipmentSelect={handleEquipmentSelect}
            />
          </div>
        )}

        {!isLoading && !error && substations.length === 0 && (
          <div className="sld-empty">
            <p>No diagram data available</p>
            <button onClick={handleRefresh}>Generate Diagram</button>
          </div>
        )}
      </div>
    </div>
  );
};
