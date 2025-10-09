/**
 * BusbarNode - Custom ReactFlow node for busbar (jeu de barres)
 *
 * Displays as a thick horizontal line
 * Shows voltage level name and voltage
 * Multiple connection handles along the line
 */

import React from 'react';
import { Handle, Position, NodeProps } from '@xyflow/react';

interface BusbarNodeData {
  label: string;
  voltage?: string;
  voltageLevelName?: string;
}

export const BusbarNode: React.FC<NodeProps<BusbarNodeData>> = ({ data, selected }) => {
  const busbarWidth = 500;
  const busbarHeight = 20;

  return (
    <div
      style={{
        position: 'relative',
        width: `${busbarWidth}px`,
        height: `${busbarHeight + 40}px`,
      }}
    >
      {/* Voltage level label (above busbar) */}
      <div
        style={{
          position: 'absolute',
          top: '-25px',
          left: '0',
          fontSize: '14px',
          fontWeight: 'bold',
          color: '#000',
        }}
      >
        {data.label}
        {data.voltage && (
          <span style={{ marginLeft: '8px', fontSize: '12px', color: '#666' }}>
            {data.voltage}
          </span>
        )}
      </div>

      {/* Busbar (thick horizontal line) */}
      <div
        style={{
          width: `${busbarWidth}px`,
          height: `${busbarHeight}px`,
          background: selected ? '#1976d2' : '#333',
          borderRadius: '2px',
          boxShadow: selected ? '0 2px 8px rgba(25, 118, 210, 0.5)' : 'none',
          transition: 'all 0.2s',
        }}
      />

      {/* Connection handles along the busbar */}
      {/* Left */}
      <Handle
        type="source"
        position={Position.Bottom}
        id="left"
        style={{
          left: '10%',
          background: '#555',
          width: '10px',
          height: '10px',
        }}
      />

      {/* Center-left */}
      <Handle
        type="source"
        position={Position.Bottom}
        id="center-left"
        style={{
          left: '30%',
          background: '#555',
          width: '10px',
          height: '10px',
        }}
      />

      {/* Center */}
      <Handle
        type="source"
        position={Position.Bottom}
        id="center"
        style={{
          left: '50%',
          background: '#555',
          width: '10px',
          height: '10px',
        }}
      />

      {/* Center-right */}
      <Handle
        type="source"
        position={Position.Bottom}
        id="center-right"
        style={{
          left: '70%',
          background: '#555',
          width: '10px',
          height: '10px',
        }}
      />

      {/* Right */}
      <Handle
        type="source"
        position={Position.Bottom}
        id="right"
        style={{
          left: '90%',
          background: '#555',
          width: '10px',
          height: '10px',
        }}
      />
    </div>
  );
};
