# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added - Component-Based SLD Architecture (2025-10-09)

#### Backend
- **New endpoint**: `/api/sld/generate-data` - Returns structured JSON for component-based rendering
  - Hierarchical structure: Substations → Voltage Levels → Bays → Equipment
  - Filters empty bays and voltage levels
  - Uses SCD file order for equipment positioning
  - Returns statistics and metadata

#### Frontend - Component Architecture
- **New components** in `frontend/src/components/SLD/`:
  - `Equipment.tsx` - Individual equipment symbols (CBR, DIS, CTR, VTR, PTR)
    - Simplified electrical symbols (full IEC symbols via PowSyBl later)
    - Click to select, hover for tooltips
    - No text labels (cleaner display)
  - `Bay.tsx` - Vertical bay/feeder layout
    - Clean single vertical line
    - Bay label at BOTTOM (professional style)
    - CBO (coupling) bays highlighted with ⚡
  - `Busbar.tsx` - Horizontal busbar
    - Thick line (6px stroke)
    - Voltage level label above
  - `VoltageLevel.tsx` - Container for busbar + bays
  - `SLDCanvas.tsx` - Main SVG canvas
    - Pan/zoom with mouse (drag + wheel)
    - Selection state management
    - Grid background (draw.io style)
    - Clean layout (no legend/title in SVG)

#### Frontend - Page Updates
- **Refactored** `SLDViewerPage.tsx`:
  - Switched from monolithic SVG to component-based rendering
  - Fetches structured data from `/api/sld/generate-data`
  - Removed old pan/zoom (now in SLDCanvas)
  - Selected equipment shown in toolbar
  - Cleaner toolbar (removed zoom buttons - use mouse wheel)

#### Layout Improvements
- **Professional spacing**:
  - Equipment: 40x30px symbols (was 100x40px rectangles)
  - Vertical spacing: 80px between equipment (was 60px)
  - Voltage level spacing: 500px (was 300px)
  - Bay spacing: 80px horizontal (was 50px)
- **Bay labels**: Moved from top (near busbar) to bottom (feeder name position)
- **Busbar**: Thicker line (6px), black color
- **Removed clutter**: No equipment names, no legend in SVG, no title in SVG

#### Documentation
- **Added** `SLD_COMPONENT_ARCHITECTURE.md` - Complete architecture documentation
  - Data flow diagrams (database → backend → frontend → components)
  - Component hierarchy
  - Props flow (top-down) and events flow (bottom-up)
  - State management strategy
  - API contract
  - Future enhancements roadmap

#### Interactive Features
- ✅ Click equipment to select (shows in toolbar)
- ✅ Hover for tooltips (full equipment details)
- ✅ Pan with mouse drag
- ✅ Zoom with mouse wheel
- ✅ CBO bays highlighted

#### Future Ready
- Equipment details panel (sidebar)
- Editing mode (switch equipment status)
- BCU/SCU signal associations
- Real-time status updates via WebSocket
- Context menus

### Technical Details
- **Data flow**: PostgreSQL → Fuseki (SPARQL) → Backend API → React State → Components
- **State management**: Page-level useState (no Redux needed yet)
- **Immutability**: Components never mutate props
- **Type safety**: Full TypeScript interfaces
- **Performance**: Clean component separation for future memoization

### Migration Notes
- Old endpoint `/api/sld/generate-simple` still works (returns SVG)
- New endpoint `/api/sld/generate-data` returns JSON (component-based)
- Frontend now uses new endpoint by default
- No breaking changes to database or authentication

---

## Previous Changes
(Document previous changes here as needed)
