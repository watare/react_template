/**
 * Busbar Component - Horizontal line representing a busbar (jeu de barres)
 *
 * Layout:
 * - Horizontal line at specified y position
 * - VoltageLevel label on the left
 * - Extends across all bays
 *
 * Data Flow:
 * - Receives position and label via props (read-only)
 * - Pure presentational component (no events)
 */

import React from 'react';

interface BusbarProps {
  name: string;
  voltage?: string;
  y: number;
  xStart: number;
  xEnd: number;
  onClick?: () => void;
  selected?: boolean;
}

export const Busbar: React.FC<BusbarProps> = ({
  name,
  voltage,
  y,
  xStart,
  xEnd,
  onClick,
  selected = false
}) => {
  // Format voltage display - simpler
  const voltageDisplay = voltage ? `${name} - ${voltage}V` : name;

  const strokeColor = selected ? '#1976d2' : '#000';
  const strokeWidth = selected ? 8 : 6; // Thicker busbar

  return (
    <g
      className="sld-busbar"
      onClick={onClick}
      style={{ cursor: onClick ? 'pointer' : 'default' }}
    >
      {/* Thick horizontal busbar line */}
      <line
        x1={xStart}
        y1={y}
        x2={xEnd}
        y2={y}
        stroke={strokeColor}
        strokeWidth={strokeWidth}
      />

      {/* Selection glow effect */}
      {selected && (
        <line
          x1={xStart}
          y1={y}
          x2={xEnd}
          y2={y}
          stroke="#1976d2"
          strokeWidth={12}
          opacity={0.3}
        />
      )}

      {/* VoltageLevel label - cleaner, above busbar */}
      <text
        x={xStart + 10}
        y={y - 15}
        fontSize="13"
        fontWeight="bold"
        fill="#000"
        pointerEvents="none"
      >
        {voltageDisplay}
      </text>

      {/* Hover tooltip */}
      {onClick && (
        <title>{voltageDisplay}</title>
      )}
    </g>
  );
};
