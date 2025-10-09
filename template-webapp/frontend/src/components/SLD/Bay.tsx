/**
 * Bay Component - Represents a vertical column of equipment (travée)
 *
 * Layout:
 * - Busbar connection point at top (y=0)
 * - Equipment stacked vertically below
 * - Vertical line connecting equipment to busbar
 * - Bay label at bottom
 *
 * Data Flow:
 * - Receives equipment list via props (read-only)
 * - Emits equipment click events to parent
 * - Does NOT manage selection state (parent does)
 */

import React from 'react';
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
  // Calculate bay height based on number of equipment
  const bayHeight = equipments.length * (equipmentHeight + verticalSpacing);

  // Bay label styling (at bottom, not top)
  const labelColor = isCoupling ? '#D32F2F' : '#000';
  const labelWeight = isCoupling ? 'bold' : 'normal';
  const labelPrefix = isCoupling ? '⚡ ' : '';
  const labelY = busbarY + 50 + bayHeight + 30; // Below all equipment

  return (
    <g className="sld-bay" transform={`translate(${x}, 0)`}>
      {/* Single clean vertical line from busbar to bottom */}
      <line
        x1={0}
        y1={busbarY}
        x2={0}
        y2={busbarY + 50 + bayHeight}
        stroke="#000"
        strokeWidth={2}
      />

      {/* Equipment stack (sorted by order) - NO LABELS */}
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
