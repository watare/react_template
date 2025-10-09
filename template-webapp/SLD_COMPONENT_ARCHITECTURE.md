# SLD Component-Based Architecture

## Overview

The Single Line Diagram (SLD) viewer has been refactored from a monolithic SVG generator to a component-based React architecture. This enables:

- **Interactive equipment**: Click, hover, select individual equipment
- **Future editing mode**: Switch equipment status (open/closed)
- **Signal associations**: Link BCU/SCU signals to equipment
- **Real-time updates**: Update equipment states dynamically
- **Better UX**: Tooltips, details panels, context menus

## Component Hierarchy

```
SLDViewerPage (Container - manages data fetching)
  └─ SLDCanvas (SVG Canvas - manages pan/zoom, selection state)
      └─ Substation (Title)
          └─ VoltageLevel (Busbar + Bays)
              ├─ Busbar (Horizontal line)
              └─ Bay[] (Vertical columns)
                  └─ Equipment[] (Individual equipment pieces)
```

## Data Flow Architecture

### 1. Source of Truth

```
DATABASE (PostgreSQL)
    ↓ (SCL file metadata)
FUSEKI (RDF Triplestore)
    ↓ (SPARQL Query - get_sld_complete_query)
BACKEND API (/api/sld/generate-data)
    ↓ (HTTP POST with file_id + Bearer token)
REACT STATE (SLDViewerPage - useState)
    ↓ (Props drilling - read-only)
COMPONENTS (Equipment, Bay, Busbar, VoltageLevel)
```

**Key Principle**: Backend is the single source of truth for topology data. Frontend only manages UI state (pan, zoom, selection).

### 2. State Management

#### Global State (None - not needed yet)
- No Redux/Zustand for now
- All state managed at page level

#### Page-Level State (SLDViewerPage.tsx)
```typescript
const [substations, setSubstations] = useState<SubstationData[]>([]);  // Topology data from backend
const [statistics, setStatistics] = useState<SLDStatistics | null>(null);  // Stats from backend
const [fileName, setFileName] = useState<string>('');  // File name from backend
const [isLoading, setIsLoading] = useState(false);  // Loading state
const [error, setError] = useState<string | null>(null);  // Error state
const [selectedEquipment, setSelectedEquipment] = useState<string | null>(null);  // UI state
```

#### Component-Level State (SLDCanvas.tsx)
```typescript
const [scale, setScale] = useState<number>(1);  // Zoom level
const [panX, setPanX] = useState<number>(0);  // Pan X
const [panY, setPanY] = useState<number>(0);  // Pan Y
const [isDragging, setIsDragging] = useState(false);  // Drag state
const [dragStart, setDragStart] = useState({ x: 0, y: 0 });  // Drag start position
const [selectedEquipment, setSelectedEquipment] = useState<string | null>(null);  // Selected equipment
const [highlightedEquipment, setHighlightedEquipment] = useState<string | null>(null);  // Hovered equipment
const [selectedBusbar, setSelectedBusbar] = useState<string | null>(null);  // Selected busbar
```

#### Presentational Components (No State)
- `Equipment.tsx`: Pure presentational, receives props
- `Bay.tsx`: Pure presentational, receives props
- `Busbar.tsx`: Pure presentational, receives props
- `VoltageLevel.tsx`: Pure presentational, receives props

### 3. Props Flow (Top-Down)

```typescript
SLDViewerPage
  ├─ substations: SubstationData[]  ──→  SLDCanvas
  └─ onEquipmentSelect: (name) => void  ──→  SLDCanvas
                                               ├─ substations: SubstationData[]  ──→  VoltageLevel
                                               ├─ onEquipmentClick: (name) => void  ──→  VoltageLevel
                                               ├─ onEquipmentHover: (name) => void  ──→  VoltageLevel
                                               ├─ selectedEquipment: string | null  ──→  VoltageLevel
                                               └─ highlightedEquipment: string | null  ──→  VoltageLevel
                                                                                            ├─ name: string  ──→  Busbar
                                                                                            ├─ voltage: string  ──→  Busbar
                                                                                            ├─ bays: BayData[]  ──→  Bay
                                                                                            ├─ onEquipmentClick  ──→  Bay
                                                                                            ├─ onEquipmentHover  ──→  Bay
                                                                                            ├─ selectedEquipment  ──→  Bay
                                                                                            └─ highlightedEquipment  ──→  Bay
                                                                                                                        ├─ equipments: EquipmentData[]  ──→  Equipment
                                                                                                                        ├─ onClick: () => void  ──→  Equipment
                                                                                                                        ├─ onHover: () => void  ──→  Equipment
                                                                                                                        ├─ selected: boolean  ──→  Equipment
                                                                                                                        └─ highlighted: boolean  ──→  Equipment
```

**Key Principle**: Data flows down (parent → child), never mutated by children.

### 4. Events Flow (Bottom-Up)

```typescript
Equipment (onClick fired)
    ↓ calls onEquipmentClick(equipmentName)
Bay (receives event)
    ↓ calls onEquipmentClick(equipmentName)
VoltageLevel (receives event)
    ↓ calls onEquipmentClick(equipmentName)
SLDCanvas (receives event)
    ↓ updates local selectedEquipment state
    ↓ calls onEquipmentSelect(equipmentName)
SLDViewerPage (receives event)
    ↓ updates selectedEquipment state
    ↓ displays in toolbar: "Selected: DJ1"
    ↓ (TODO: show details panel)
```

**Key Principle**: Events bubble up (child → parent), never handled by siblings.

### 5. API Communication

#### Endpoint: `/api/sld/generate-data`

**Request**:
```typescript
POST /api/sld/generate-data
Headers: {
  'Content-Type': 'application/json',
  'Authorization': 'Bearer <token>'
}
Body: {
  file_id: number
}
```

**Response**:
```typescript
{
  substations: [
    {
      name: string,
      voltage_levels: [
        {
          name: string,
          voltage: string,
          bays: [
            {
              name: string,
              is_coupling: boolean,
              equipments: [
                {
                  name: string,
                  type: "CBR" | "DIS" | "CTR" | "VTR" | "PTR" | ...,
                  subtype: "SA" | "SL" | "ST" | "SS" | undefined,
                  order: number
                }
              ]
            }
          ]
        }
      ]
    }
  ],
  statistics: {
    substations: number,
    voltage_levels: number,
    bays: number,
    equipments: number,
    triples_extracted: number
  },
  file_name: string,
  generator: "component-based"
}
```

**Key Principle**: Backend returns structured JSON (not SVG string). Frontend renders with React components.

## Equipment Types and Colors

| Type | Color | Description |
|------|-------|-------------|
| CBR | #FF6B6B | Circuit Breaker (Disjoncteur) |
| DIS | #4ECDC4 | Disconnector (Sectionneur) - SA, SL, ST, SS |
| CTR | #FFD93D | Current Transformer |
| VTR | #95E1D3 | Voltage Transformer |
| PTR | #AA96DA | Power Transformer |
| CAP | #FCBAD3 | Capacitor |
| REA | #A8D8EA | Reactor |
| GEN | #F38181 | Generator |
| BAT | #FCE38A | Battery |

## Interaction Modes

### Current: View Mode
- ✅ Pan/zoom with mouse
- ✅ Click equipment to select
- ✅ Hover for tooltips
- ✅ Selected equipment shown in toolbar

### Future: Edit Mode
- ⏳ Switch equipment status (open/closed)
- ⏳ Associate BCU/SCU signals
- ⏳ Real-time status updates
- ⏳ Equipment details panel
- ⏳ Context menu (right-click)
- ⏳ Multi-select

## File Structure

```
frontend/src/
├── components/
│   └── SLD/
│       ├── index.ts              # Exports all components
│       ├── SLDCanvas.tsx         # Main SVG canvas (pan/zoom, selection)
│       ├── SLDCanvas.css         # Canvas styles (grid background)
│       ├── VoltageLevel.tsx      # Voltage level (busbar + bays)
│       ├── Busbar.tsx            # Horizontal busbar line
│       ├── Bay.tsx               # Vertical bay (column of equipment)
│       └── Equipment.tsx         # Individual equipment piece
└── pages/
    ├── SLDViewerPage.tsx         # Page container (data fetching)
    └── SLDViewerPage.css         # Page styles
```

## Best Practices Applied

### 1. Separation of Concerns
- **Container components**: Data fetching, state management (SLDViewerPage)
- **Smart components**: UI state, event coordination (SLDCanvas)
- **Presentational components**: Pure rendering, no state (Equipment, Bay, Busbar, VoltageLevel)

### 2. Single Responsibility
- Each component has one job
- No component does data fetching AND rendering

### 3. Unidirectional Data Flow
- Data flows down (props)
- Events flow up (callbacks)
- No sibling communication

### 4. Immutability
- Components never mutate props
- State updates use setters only

### 5. Type Safety
- All props typed with TypeScript interfaces
- No `any` types

### 6. Performance Considerations
- React keys on all lists (prevents re-renders)
- CSS transitions for smooth interactions
- No inline object creation in render (breaks memoization)

## Future Enhancements

### Phase 2: Equipment Details Panel
```typescript
interface EquipmentDetailsPanel {
  equipment: EquipmentData | null;
  onClose: () => void;
}
// Shows: type, subtype, bay, voltage level, terminals, signals
```

### Phase 3: Editing Mode
```typescript
interface SLDCanvas {
  mode: 'view' | 'edit';  // NEW
  onEquipmentStatusChange: (name: string, status: 'open' | 'closed') => void;  // NEW
}
```

### Phase 4: Signal Associations
```typescript
interface Equipment {
  signals: Signal[];  // NEW - BCU/SCU signals
  onSignalClick: (signal: Signal) => void;  // NEW
}
```

### Phase 5: Real-Time Updates
```typescript
// WebSocket connection for live updates
const ws = new WebSocket(`${WS_URL}/sld/updates/${fileId}`);
ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  updateEquipmentStatus(update.equipmentName, update.status);
};
```

## Testing Strategy

### Unit Tests
- Test each component in isolation
- Mock props, verify rendering
- Test event handlers

### Integration Tests
- Test data flow from API to components
- Test selection state propagation
- Test pan/zoom interactions

### E2E Tests
- Load SLD page with real file_id
- Click equipment, verify selection
- Pan/zoom, verify transforms
- Navigate to IED Explorer from SLD

## Performance Metrics

- Initial load: < 2s (1250 triples query)
- Re-render: < 16ms (60 FPS target)
- Pan/zoom: < 16ms (smooth 60 FPS)
- Equipment click: < 100ms (instant feedback)

## Deployment

No changes to deployment. Backend serves JSON instead of SVG, but API contract is backward compatible.

---

**Author**: Claude Code
**Date**: 2025-10-09
**Version**: 1.0.0
