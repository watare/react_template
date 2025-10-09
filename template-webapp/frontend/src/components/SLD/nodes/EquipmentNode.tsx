/**
 * EquipmentNode - Custom ReactFlow node for electrical equipment
 *
 * Displays QElectroTech symbols loaded from backend API
 * Shows equipment name, type, and handles for connections
 */

import React, { useEffect, useState } from 'react';
import { Handle, Position, NodeProps } from '@xyflow/react';

interface EquipmentNodeData {
  label: string;
  equipmentType: string;
  equipmentSubtype?: string;
  bayName?: string;
  voltageLevelName?: string;
  substationName?: string;
  order?: number;
}

// Equipment colors (matching old implementation)
const EQUIPMENT_COLORS: Record<string, string> = {
  CBR: '#FF6B6B', // Circuit Breaker - Red
  DIS: '#4ECDC4', // Disconnector - Cyan
  CTR: '#FFD93D', // Current Transformer - Yellow
  VTR: '#95E1D3', // Voltage Transformer - Mint
  PTR: '#AA96DA', // Power Transformer - Purple
  CAP: '#FCBAD3', // Capacitor - Pink
  REA: '#A8D8EA', // Reactor - Light Blue
  GEN: '#F38181', // Generator - Salmon
  BAT: '#FCE38A', // Battery - Light Yellow
  DEFAULT: '#E0E0E0', // Unknown - Gray
};

export const EquipmentNode: React.FC<NodeProps<EquipmentNodeData>> = ({ data, selected }) => {
  const [symbolSvg, setSymbolSvg] = useState<string | null>(null);
  const [symbolError, setSymbolError] = useState<boolean>(false);

  const equipmentType = data.equipmentType || 'DEFAULT';
  const color = EQUIPMENT_COLORS[equipmentType] || EQUIPMENT_COLORS['DEFAULT'];

  // Load QElectroTech symbol from backend
  useEffect(() => {
    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    const symbolUrl = `${apiUrl}/api/sld/symbols/${equipmentType}`;

    fetch(symbolUrl, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error(`Symbol ${equipmentType} not found`);
        }
        return response.text();
      })
      .then((svgText) => {
        // Remove outer <svg> tag to get inner content
        const innerContent = svgText
          .replace(/<svg[^>]*>/, '')
          .replace(/<\/svg>/, '');

        setSymbolSvg(innerContent);
        setSymbolError(false);
      })
      .catch((err) => {
        console.warn(`Failed to load symbol ${equipmentType}:`, err);
        setSymbolError(true);
      });
  }, [equipmentType]);

  // Fallback symbol rendering
  const renderFallbackSymbol = () => {
    return (
      <div
        style={{
          width: '60px',
          height: '60px',
          borderRadius: '8px',
          border: `2px solid ${selected ? '#1976d2' : '#666'}`,
          background: color,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '12px',
          fontWeight: 'bold',
          color: '#333',
        }}
      >
        {equipmentType}
      </div>
    );
  };

  return (
    <div
      style={{
        padding: '10px',
        borderRadius: '8px',
        border: `2px solid ${selected ? '#1976d2' : '#ddd'}`,
        background: 'white',
        minWidth: '80px',
        boxShadow: selected ? '0 4px 8px rgba(0,0,0,0.2)' : '0 2px 4px rgba(0,0,0,0.1)',
        transition: 'all 0.2s',
      }}
    >
      {/* Top handle (north terminal) */}
      <Handle
        type="source"
        position={Position.Top}
        id="north"
        style={{
          background: '#555',
          width: '8px',
          height: '8px',
        }}
      />

      {/* Equipment symbol */}
      <div style={{ textAlign: 'center' }}>
        {symbolSvg && !symbolError ? (
          // QElectroTech symbol
          <svg
            width="60"
            height="60"
            viewBox="-30 -30 60 60"
            dangerouslySetInnerHTML={{ __html: symbolSvg }}
          />
        ) : (
          // Fallback
          renderFallbackSymbol()
        )}
      </div>

      {/* Equipment label */}
      <div
        style={{
          marginTop: '8px',
          fontSize: '10px',
          fontWeight: 'bold',
          textAlign: 'center',
          color: '#333',
          maxWidth: '80px',
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          whiteSpace: 'nowrap',
        }}
        title={data.label}
      >
        {data.label}
      </div>

      {/* Type badge */}
      {data.equipmentSubtype && (
        <div
          style={{
            marginTop: '4px',
            fontSize: '8px',
            textAlign: 'center',
            color: '#666',
            background: '#f0f0f0',
            borderRadius: '3px',
            padding: '2px 4px',
          }}
        >
          {data.equipmentSubtype}
        </div>
      )}

      {/* Bottom handle (south terminal) */}
      <Handle
        type="source"
        position={Position.Bottom}
        id="south"
        style={{
          background: '#555',
          width: '8px',
          height: '8px',
        }}
      />

      {/* Left handle (west terminal) */}
      <Handle
        type="source"
        position={Position.Left}
        id="west"
        style={{
          background: '#555',
          width: '8px',
          height: '8px',
        }}
      />

      {/* Right handle (east terminal) */}
      <Handle
        type="source"
        position={Position.Right}
        id="east"
        style={{
          background: '#555',
          width: '8px',
          height: '8px',
        }}
      />
    </div>
  );
};
