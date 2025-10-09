/**
 * VoltageLevel Component - Represents a voltage level with busbar and bays
 *
 * Layout:
 * - Busbar at top
 * - Bays arranged horizontally below busbar
 * - Each bay contains vertical stack of equipment
 *
 * Data Flow:
 * - Receives voltage level data via props (read-only)
 * - Passes events up to parent (SLDCanvas)
 * - Does NOT manage state
 */

import React from 'react';
import { Busbar } from './Busbar';
import { Bay } from './Bay';

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

interface VoltageLevelProps {
  name: string;
  voltage?: string;
  bays: BayData[];
  y: number;
  margin: number;
  bayWidth: number;
  horizontalSpacing: number;
  onEquipmentClick?: (equipmentName: string) => void;
  onEquipmentHover?: (equipmentName: string) => void;
  onBusbarClick?: (voltageLevelName: string) => void;
  selectedEquipment?: string | null;
  highlightedEquipment?: string | null;
  selectedBusbar?: string | null;
}

export const VoltageLevel: React.FC<VoltageLevelProps> = ({
  name,
  voltage,
  bays,
  y,
  margin,
  bayWidth,
  horizontalSpacing,
  onEquipmentClick,
  onEquipmentHover,
  onBusbarClick,
  selectedEquipment,
  highlightedEquipment,
  selectedBusbar
}) => {
  // Calculate busbar extent (spans all bays)
  const numBays = bays.length;
  const busbarXStart = margin;
  const busbarXEnd = margin + numBays * (bayWidth + horizontalSpacing);

  return (
    <g className="sld-voltage-level">
      {/* Busbar */}
      <Busbar
        name={name}
        voltage={voltage}
        y={y}
        xStart={busbarXStart}
        xEnd={busbarXEnd}
        onClick={onBusbarClick ? () => onBusbarClick(name) : undefined}
        selected={selectedBusbar === name}
      />

      {/* Bays */}
      {bays.map((bay, index) => {
        const bayX = margin + horizontalSpacing + index * (bayWidth + horizontalSpacing);

        return (
          <Bay
            key={`${name}-${bay.name}`}
            name={bay.name}
            equipments={bay.equipments}
            x={bayX}
            busbarY={y}
            isCoupling={bay.is_coupling}
            onEquipmentClick={onEquipmentClick}
            onEquipmentHover={onEquipmentHover}
            selectedEquipment={selectedEquipment}
            highlightedEquipment={highlightedEquipment}
          />
        );
      })}
    </g>
  );
};
