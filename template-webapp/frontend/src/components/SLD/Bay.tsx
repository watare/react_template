/**
 * Bay Component - Represents a vertical column of equipment (travée)
 *
 * Layout:
 * - Busbar connection point at top (y=0)
 * - Equipment stacked vertically below
 * - Connection lines between equipment terminals (using QElectroTech terminal metadata)
 * - Bay label at bottom
 *
 * Data Flow:
 * - Receives equipment list via props (read-only)
 * - Loads symbol terminal metadata from backend
 * - Draws intelligent connections between terminals
 * - Emits equipment click events to parent
 */

import React, { useState, useEffect } from 'react';
import { Equipment } from './Equipment';

interface EquipmentData {
  name: string;
  type: string;
  subtype?: string;
  order: number;
}

interface BayProps {
  name: string;
  equipments: EquipmentData[];
  x: number;
  busbarY: number;
  isCoupling?: boolean;
  onEquipmentClick?: (equipmentName: string) => void;
  onEquipmentHover?: (equipmentName: string) => void;
  selectedEquipment?: string | null;
  highlightedEquipment?: string | null;
  equipmentHeight?: number;
  equipmentWidth?: number;
  verticalSpacing?: number;
}

interface Terminal {
  x: number;
  y: number;
  orientation: 'n' | 's' | 'e' | 'w';
}

interface SymbolMetadata {
  name: string;
  file: string;
  width: number;
  height: number;
  terminals: Terminal[];
}

type SymbolLibrary = Record<string, SymbolMetadata>;

export const Bay: React.FC<BayProps> = ({
  name,
  equipments,
  x,
  busbarY,
  isCoupling = false,
  onEquipmentClick,
  onEquipmentHover,
  selectedEquipment,
  highlightedEquipment,
  equipmentHeight = 30,
  equipmentWidth = 40,
  verticalSpacing = 80
}) => {
  const [symbolLibrary, setSymbolLibrary] = useState<SymbolLibrary | null>(null);

  // Load symbol library metadata (terminals)
  useEffect(() => {
    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    const libraryUrl = `${apiUrl}/api/sld/symbols`;

    fetch(libraryUrl, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
      .then(response => {
        if (!response.ok) {
          throw new Error('Failed to load symbol library');
        }
        return response.json();
      })
      .then((library: SymbolLibrary) => {
        setSymbolLibrary(library);
      })
      .catch(err => {
        console.warn('Failed to load symbol library:', err);
      });
  }, []);

  // Get terminal positions for an equipment at given Y position
  // Terminals from QElectroTech are in local SVG coordinates (relative to symbol origin)
  const getTerminals = (equipmentType: string, equipmentX: number, equipmentY: number): Terminal[] => {
    if (!symbolLibrary || !symbolLibrary[equipmentType]) {
      // Fallback: assume 2 terminals (top and bottom center)
      return [
        { x: equipmentX, y: equipmentY - equipmentHeight / 2, orientation: 'n' },
        { x: equipmentX, y: equipmentY + equipmentHeight / 2, orientation: 's' }
      ];
    }

    const metadata = symbolLibrary[equipmentType];
    // Transform terminal coordinates from SVG local space to global canvas space
    // The SVG is centered at (equipmentX, equipmentY) in the canvas
    return metadata.terminals.map(terminal => ({
      x: equipmentX + terminal.x,  // Add equipment X offset
      y: equipmentY + terminal.y,  // Add equipment Y offset
      orientation: terminal.orientation
    }));
  };

  // Find the northmost (top) terminal of an equipment
  const getTopTerminal = (equipmentType: string, equipmentX: number, equipmentY: number): { x: number; y: number } => {
    const terminals = getTerminals(equipmentType, equipmentX, equipmentY);
    const northTerminals = terminals.filter(t => t.orientation === 'n');

    if (northTerminals.length > 0) {
      // Return the first north terminal (usually center or left)
      return { x: northTerminals[0].x, y: northTerminals[0].y };
    }

    // Fallback: top of equipment
    return { x: equipmentX, y: equipmentY - equipmentHeight / 2 };
  };

  // Find the southmost (bottom) terminal of an equipment
  const getBottomTerminal = (equipmentType: string, equipmentX: number, equipmentY: number): { x: number; y: number } => {
    const terminals = getTerminals(equipmentType, equipmentX, equipmentY);
    const southTerminals = terminals.filter(t => t.orientation === 's');

    if (southTerminals.length > 0) {
      // Return the first south terminal
      return { x: southTerminals[0].x, y: southTerminals[0].y };
    }

    // Fallback: bottom of equipment
    return { x: equipmentX, y: equipmentY + equipmentHeight / 2 };
  };

  // Calculate bay height
  const bayHeight = equipments.length * (equipmentHeight + verticalSpacing);

  // Bay label styling
  const labelColor = isCoupling ? '#D32F2F' : '#000';
  const labelWeight = isCoupling ? 'bold' : 'normal';
  const labelPrefix = isCoupling ? '⚡ ' : '';
  const labelY = busbarY + 50 + bayHeight + 30;

  // Generate connection lines between equipment
  const connectionLines: JSX.Element[] = [];

  if (equipments.length > 0) {
    const equipmentX = 0;  // Equipment centered on X=0 in bay coordinate system

    // 1. Busbar to first equipment
    const firstEquipmentY = busbarY + 50;
    const firstTerminal = getTopTerminal(equipments[0].type, equipmentX, firstEquipmentY);

    connectionLines.push(
      <line
        key="busbar-to-first"
        x1={0}
        y1={busbarY}
        x2={firstTerminal.x}
        y2={firstTerminal.y}
        stroke="#000"
        strokeWidth={2}
      />
    );

    // 2. Equipment to equipment connections
    for (let i = 0; i < equipments.length - 1; i++) {
      const currentEquipmentY = busbarY + 50 + i * (equipmentHeight + verticalSpacing);
      const nextEquipmentY = busbarY + 50 + (i + 1) * (equipmentHeight + verticalSpacing);

      const currentBottomTerminal = getBottomTerminal(equipments[i].type, equipmentX, currentEquipmentY);
      const nextTopTerminal = getTopTerminal(equipments[i + 1].type, equipmentX, nextEquipmentY);

      connectionLines.push(
        <line
          key={`connection-${i}-${i + 1}`}
          x1={currentBottomTerminal.x}
          y1={currentBottomTerminal.y}
          x2={nextTopTerminal.x}
          y2={nextTopTerminal.y}
          stroke="#000"
          strokeWidth={2}
        />
      );
    }

    // 3. Last equipment to end point (feeder output)
    const lastIndex = equipments.length - 1;
    const lastEquipmentY = busbarY + 50 + lastIndex * (equipmentHeight + verticalSpacing);
    const lastBottomTerminal = getBottomTerminal(equipments[lastIndex].type, equipmentX, lastEquipmentY);
    const endY = busbarY + 50 + bayHeight;

    connectionLines.push(
      <line
        key="last-to-end"
        x1={lastBottomTerminal.x}
        y1={lastBottomTerminal.y}
        x2={0}
        y2={endY}
        stroke="#000"
        strokeWidth={2}
      />
    );
  }

  return (
    <g className="sld-bay" transform={`translate(${x}, 0)`}>
      {/* Connection lines between equipment (using terminal positions) */}
      {connectionLines}

      {/* Equipment stack (sorted by order) */}
      {equipments.map((equipment, index) => {
        const equipmentY = busbarY + 50 + index * (equipmentHeight + verticalSpacing);

        return (
          <Equipment
            key={`${name}-${equipment.name}`}
            name={equipment.name}
            type={equipment.type}
            subtype={equipment.subtype}
            x={0}
            y={equipmentY}
            width={equipmentWidth}
            height={equipmentHeight}
            onClick={onEquipmentClick ? () => onEquipmentClick(equipment.name) : undefined}
            onHover={onEquipmentHover ? () => onEquipmentHover(equipment.name) : undefined}
            selected={selectedEquipment === equipment.name}
            highlighted={highlightedEquipment === equipment.name}
          />
        );
      })}

      {/* Bay label at BOTTOM (feeder name) */}
      <text
        x={0}
        y={labelY}
        textAnchor="middle"
        fontSize="11"
        fill={labelColor}
        fontWeight={labelWeight}
        pointerEvents="none"
      >
        {labelPrefix}{name}
      </text>
    </g>
  );
};
