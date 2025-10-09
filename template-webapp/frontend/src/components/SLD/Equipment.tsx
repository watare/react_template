/**
 * Equipment Component - Represents a single electrical equipment in the SLD
 *
 * Equipment types:
 * - CBR: Circuit Breaker (Disjoncteur)
 * - DIS: Disconnector (Sectionneur) - with subtypes SA, SL, ST, SS
 * - CTR: Current Transformer
 * - VTR: Voltage Transformer
 * - PTR: Power Transformer
 * - CAP: Capacitor
 * - REA: Reactor
 * - GEN: Generator
 * - BAT: Battery
 * - MOT: Motor
 */

import React from 'react';

interface EquipmentProps {
  name: string;
  type: string;
  subtype?: string;
  x: number;
  y: number;
  onClick?: () => void;
  onHover?: () => void;
  selected?: boolean;
  highlighted?: boolean;
  width?: number;
  height?: number;
}

// Equipment colors matching backend configuration
const EQUIPMENT_COLORS: Record<string, string> = {
  'CBR': '#FF6B6B',  // Circuit Breaker - Red
  'DIS': '#4ECDC4',  // Disconnector - Cyan
  'CTR': '#FFD93D',  // Current Transformer - Yellow
  'VTR': '#95E1D3',  // Voltage Transformer - Mint
  'PTR': '#AA96DA',  // Power Transformer - Purple
  'CAP': '#FCBAD3',  // Capacitor - Pink
  'REA': '#A8D8EA',  // Reactor - Light Blue
  'GEN': '#F38181',  // Generator - Salmon
  'BAT': '#FCE38A',  // Battery - Light Yellow
  'DEFAULT': '#E0E0E0'  // Unknown - Gray
};

export const Equipment: React.FC<EquipmentProps> = ({
  name,
  type,
  subtype,
  x,
  y,
  onClick,
  onHover,
  selected = false,
  highlighted = false,
  width = 40,
  height = 30
}) => {
  const color = EQUIPMENT_COLORS[type] || EQUIPMENT_COLORS['DEFAULT'];
  const strokeColor = selected ? '#1976d2' : '#000';
  const strokeWidth = selected ? 3 : 2;

  // Render different symbols based on equipment type
  const renderSymbol = () => {
    switch (type) {
      case 'CBR': // Circuit Breaker - Rectangle with diagonal line
        return (
          <g>
            <rect x={-width/2} y={-height/2} width={width} height={height} fill="none" stroke={strokeColor} strokeWidth={strokeWidth} />
            <line x1={-width/2} y1={-height/2} x2={width/2} y2={height/2} stroke={strokeColor} strokeWidth={strokeWidth} />
          </g>
        );

      case 'DIS': // Disconnector - Two parallel lines with gap
        return (
          <g>
            <line x1={-width/2} y1={0} x2={-5} y2={0} stroke={strokeColor} strokeWidth={strokeWidth} />
            <line x1={5} y1={0} x2={width/2} y2={0} stroke={strokeColor} strokeWidth={strokeWidth} />
            <circle cx={0} cy={0} r={3} fill={color} stroke={strokeColor} strokeWidth={1} />
          </g>
        );

      case 'CTR': // Current Transformer - Circle
        return (
          <circle cx={0} cy={0} r={width/2} fill="none" stroke={strokeColor} strokeWidth={strokeWidth} />
        );

      case 'VTR': // Voltage Transformer - Circle with cross
        return (
          <g>
            <circle cx={0} cy={0} r={width/2} fill="none" stroke={strokeColor} strokeWidth={strokeWidth} />
            <line x1={-width/3} y1={0} x2={width/3} y2={0} stroke={strokeColor} strokeWidth={1} />
            <line x1={0} y1={-width/3} x2={0} y2={width/3} stroke={strokeColor} strokeWidth={1} />
          </g>
        );

      case 'PTR': // Power Transformer - Two circles
        return (
          <g>
            <circle cx={-width/4} cy={0} r={width/3} fill="none" stroke={strokeColor} strokeWidth={strokeWidth} />
            <circle cx={width/4} cy={0} r={width/3} fill="none" stroke={strokeColor} strokeWidth={strokeWidth} />
          </g>
        );

      default: // Generic - Small rectangle
        return (
          <rect x={-width/3} y={-height/3} width={width*2/3} height={height*2/3} fill={color} stroke={strokeColor} strokeWidth={strokeWidth} />
        );
    }
  };

  return (
    <g
      transform={`translate(${x}, ${y})`}
      onClick={onClick}
      onMouseEnter={onHover}
      style={{ cursor: onClick ? 'pointer' : 'default' }}
      className="sld-equipment"
    >
      {/* Selection highlight circle */}
      {(selected || highlighted) && (
        <circle
          cx={0}
          cy={0}
          r={width}
          fill="none"
          stroke={selected ? '#1976d2' : '#666'}
          strokeWidth={2}
          opacity={0.3}
        />
      )}

      {/* Equipment symbol */}
      {renderSymbol()}

      {/* Tooltip */}
      <title>{`${type}${subtype ? `-${subtype}` : ''}: ${name}`}</title>
    </g>
  );
};
