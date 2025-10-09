/**
 * SLDCanvas Component - Main SVG canvas for Single Line Diagram
 *
 * Responsibilities:
 * - Renders all substations, voltage levels, bays, equipment
 * - Manages pan/zoom state
 * - Handles mouse interactions (drag, wheel)
 * - Manages selection/highlight state
 * - Grid background
 *
 * Data Flow:
 * - Receives topology data from parent (SLDViewerPage)
 * - Manages local UI state (pan, zoom, selected, highlighted)
 * - Emits equipment selection events to parent
 */

import React, { useState } from 'react';
import { VoltageLevel } from './VoltageLevel';
import './SLDCanvas.css';

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

interface SLDCanvasProps {
  substations: SubstationData[];
  onEquipmentSelect?: (equipmentName: string) => void;
  width?: number;
  height?: number;
}

// Layout constants (cleaner professional spacing)
const MARGIN = 80;
const BAY_WIDTH = 100;
const HORIZONTAL_SPACING = 80;
const VERTICAL_SPACING = 500; // Much more space between voltage levels

export const SLDCanvas: React.FC<SLDCanvasProps> = ({
  substations,
  onEquipmentSelect,
  width: initialWidth = 1200,
  height: initialHeight = 800
}) => {
  // Pan/Zoom state
  const [scale, setScale] = useState<number>(1);
  const [panX, setPanX] = useState<number>(0);
  const [panY, setPanY] = useState<number>(0);
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });

  // Selection state
  const [selectedEquipment, setSelectedEquipment] = useState<string | null>(null);
  const [highlightedEquipment, setHighlightedEquipment] = useState<string | null>(null);
  const [selectedBusbar, setSelectedBusbar] = useState<string | null>(null);

  // Calculate canvas dimensions based on data
  const maxBays = Math.max(
    ...substations.flatMap(sub =>
      sub.voltage_levels.map(vl => vl.bays.length)
    ),
    0
  );
  const totalVoltageLevels = substations.reduce(
    (sum, sub) => sum + sub.voltage_levels.length,
    0
  );

  const canvasWidth = Math.max(initialWidth, MARGIN * 2 + maxBays * (BAY_WIDTH + HORIZONTAL_SPACING));
  const canvasHeight = Math.max(initialHeight, MARGIN * 2 + totalVoltageLevels * VERTICAL_SPACING);

  // Mouse handlers for pan/zoom
  const handleMouseDown = (e: React.MouseEvent) => {
    if (e.button === 0) {
      setIsDragging(true);
      setDragStart({
        x: e.clientX - panX,
        y: e.clientY - panY
      });
    }
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (isDragging) {
      setPanX(e.clientX - dragStart.x);
      setPanY(e.clientY - dragStart.y);
    }
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  const handleWheel = (e: React.WheelEvent) => {
    e.preventDefault();
    const delta = e.deltaY > 0 ? -0.1 : 0.1;
    setScale(prev => Math.max(0.2, Math.min(5, prev + delta)));
  };

  // Equipment interaction handlers
  const handleEquipmentClick = (equipmentName: string) => {
    setSelectedEquipment(equipmentName);
    if (onEquipmentSelect) {
      onEquipmentSelect(equipmentName);
    }
  };

  const handleEquipmentHover = (equipmentName: string) => {
    setHighlightedEquipment(equipmentName);
  };

  const handleBusbarClick = (voltageLevelName: string) => {
    setSelectedBusbar(voltageLevelName);
    setSelectedEquipment(null); // Deselect equipment when selecting busbar
  };

  // Render voltage levels for all substations
  let currentY = MARGIN + 30; // Start position

  return (
    <div
      className="sld-canvas-container"
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp}
      onWheel={handleWheel}
      style={{ cursor: isDragging ? 'grabbing' : 'grab' }}
    >
      <svg
        width="100%"
        height="100%"
        viewBox={`0 0 ${canvasWidth} ${canvasHeight}`}
        style={{
          transform: `translate(${panX}px, ${panY}px) scale(${scale})`,
          transformOrigin: '0 0',
          transition: isDragging ? 'none' : 'transform 0.1s ease-out'
        }}
      >
        {/* Background */}
        <rect width={canvasWidth} height={canvasHeight} fill="#f5f5f5" />

        {/* Render all substations */}
        {substations.map(substation => (
          <g key={substation.name}>
            {/* Substation title */}
            <text
              x={MARGIN}
              y={currentY}
              fontSize="18"
              fontWeight="bold"
              fill="#000"
            >
              {substation.name}
            </text>

            {/* Render voltage levels */}
            {substation.voltage_levels.map(voltageLevel => {
              const voltageLevelY = currentY;
              currentY += VERTICAL_SPACING; // Move down for next voltage level

              return (
                <VoltageLevel
                  key={`${substation.name}-${voltageLevel.name}`}
                  name={voltageLevel.name}
                  voltage={voltageLevel.voltage}
                  bays={voltageLevel.bays}
                  y={voltageLevelY}
                  margin={MARGIN}
                  bayWidth={BAY_WIDTH}
                  horizontalSpacing={HORIZONTAL_SPACING}
                  onEquipmentClick={handleEquipmentClick}
                  onEquipmentHover={handleEquipmentHover}
                  onBusbarClick={handleBusbarClick}
                  selectedEquipment={selectedEquipment}
                  highlightedEquipment={highlightedEquipment}
                  selectedBusbar={selectedBusbar}
                />
              );
            })}
          </g>
        ))}

        {/* No legend - cleaner look */}
      </svg>
    </div>
  );
};
