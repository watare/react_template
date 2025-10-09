# Architecture UI/UX - Single Line Diagram

## Vue d'ensemble

Ce document décrit l'architecture UI/UX pour l'intégration des schémas unifilaires dans l'application.

## Structure des pages

```
App
├─ Dashboard (/)
│  ├─ Upload SCL file
│  ├─ 📋 Explore IEDs → /ied-explorer
│  └─ 📊 Single Line Diagram → /sld-viewer
│
├─ IED Explorer (/ied-explorer)
│  ├─ Master Panel (liste des IEDs)
│  ├─ Detail Panel (détails IED + tree)
│  └─ [Button] View in SLD → /sld-viewer?highlight={iedUri}
│
└─ SLD Viewer (/sld-viewer)
   ├─ Full screen SVG diagram
   ├─ Toolbar (zoom, pan, export)
   ├─ Sidebar (liste des équipements)
   └─ Details panel (équipement sélectionné)
```

## Flux de navigation

### Scénario 1 : Depuis le Dashboard

```
User @ Dashboard
   │
   │ Click "Single Line Diagram"
   ▼
User @ SLD Viewer
   │
   │ Displays full substation diagram
   │ Can click on equipment → show details
   │ Can navigate to IED Explorer from equipment
```

### Scénario 2 : Depuis IED Explorer

```
User @ IED Explorer
   │
   │ Select IED (ex: POSTE4CBO1BCU1)
   ▼
IED Details shown in right panel
   │
   │ Click "View in SLD"
   ▼
User @ SLD Viewer
   │
   │ Diagram displayed
   │ Selected IED highlighted
   │ Can zoom to IED location
```

### Scénario 3 : Depuis SLD vers IED Explorer

```
User @ SLD Viewer
   │
   │ Click on equipment (ex: Breaker)
   ▼
Equipment details shown in sidebar
   │
   │ If equipment has associated IED
   │ [Button] "View IED Details"
   ▼
User @ IED Explorer
   │
   │ IED pre-selected
   │ Tree expanded to equipment
```

## State Management (Zustand)

### Global Store

**Fichier** : `frontend/src/stores/useAppStore.ts`

```typescript
interface AppState {
  // File selection
  selectedFile: SCLFile | null;
  setSelectedFile: (file: SCLFile | null) => void;

  // IED selection (shared between pages)
  selectedIED: IED | null;
  setSelectedIED: (ied: IED | null) => void;

  // SLD Cache (1 hour TTL)
  sldCache: Record<number, { svg: string; timestamp: Date }>;
  setSLDCache: (fileId: number, svg: string) => void;
  getSLDCache: (fileId: number) => string | null;
  clearSLDCache: () => void;
}
```

### Local State

#### IED Explorer

```typescript
// frontend/src/pages/IEDExplorerPage.tsx
const IEDExplorerPage = () => {
  // Global state
  const { selectedFile, selectedIED, setSelectedIED } = useAppStore();

  // Local state
  const [groupBy, setGroupBy] = useState<'type' | 'bay'>('type');
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedGroups, setExpandedGroups] = useState<Set<string>>(new Set());

  // selectedIED vient du global store, pas besoin de le dupliquer
};
```

#### SLD Viewer

```typescript
// frontend/src/pages/SLDViewerPage.tsx
const SLDViewerPage = () => {
  // Global state
  const { selectedFile, selectedIED, getSLDCache, setSLDCache } = useAppStore();

  // Local state
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [highlightedEquipment, setHighlightedEquipment] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // SVG from cache or API
  const [svg, setSvg] = useState<string>('');
};
```

## Composants

### 1. SLD Viewer Page

**Fichier** : `frontend/src/pages/SLDViewerPage.tsx`

```typescript
import React, { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { useAppStore } from '../stores/useAppStore';
import { SLDToolbar } from '../components/sld/SLDToolbar';
import { SLDCanvas } from '../components/sld/SLDCanvas';
import { SLDSidebar } from '../components/sld/SLDSidebar';

export const SLDViewerPage: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  // Global state
  const { selectedFile, selectedIED, getSLDCache, setSLDCache } = useAppStore();

  // Local state
  const [svg, setSvg] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });

  // Load SLD (from cache or generate)
  useEffect(() => {
    if (!selectedFile) {
      navigate('/');
      return;
    }

    loadSLD();
  }, [selectedFile]);

  const loadSLD = async () => {
    // Try cache first
    const cached = getSLDCache(selectedFile.id);
    if (cached) {
      setSvg(cached);
      return;
    }

    // Generate new SLD
    setIsLoading(true);
    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/api/sld/generate`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          },
          body: JSON.stringify({ file_id: selectedFile.id })
        }
      );

      if (!response.ok) throw new Error('Failed to generate SLD');

      const data = await response.json();
      setSvg(data.svg);
      setSLDCache(selectedFile.id, data.svg);
    } catch (error) {
      console.error('Error loading SLD:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle equipment click in SVG
  const handleEquipmentClick = (equipmentId: string) => {
    // Find associated IED
    // Show details in sidebar
    // Option to navigate to IED Explorer
  };

  return (
    <div className="sld-viewer-page">
      <header>
        <h1>Single Line Diagram - {selectedFile?.name}</h1>
      </header>

      <SLDToolbar
        zoom={zoom}
        onZoomIn={() => setZoom(z => Math.min(z + 0.1, 3))}
        onZoomOut={() => setZoom(z => Math.max(z - 0.1, 0.5))}
        onZoomFit={() => { setZoom(1); setPan({ x: 0, y: 0 }); }}
        onExport={() => exportSVG(svg)}
        onRefresh={() => loadSLD()}
      />

      <div className="sld-content">
        <SLDCanvas
          svg={svg}
          isLoading={isLoading}
          zoom={zoom}
          pan={pan}
          onPanChange={setPan}
          onEquipmentClick={handleEquipmentClick}
          highlightedIED={selectedIED?.uri}
        />

        <SLDSidebar
          selectedFile={selectedFile}
          selectedIED={selectedIED}
          onNavigateToIEDExplorer={() => navigate('/ied-explorer')}
        />
      </div>
    </div>
  );
};
```

### 2. SLD Canvas Component

**Fichier** : `frontend/src/components/sld/SLDCanvas.tsx`

```typescript
import React, { useRef, useEffect } from 'react';
import { TransformWrapper, TransformComponent } from 'react-zoom-pan-pinch';

interface SLDCanvasProps {
  svg: string;
  isLoading: boolean;
  zoom: number;
  pan: { x: number; y: number };
  onPanChange: (pan: { x: number; y: number }) => void;
  onEquipmentClick: (equipmentId: string) => void;
  highlightedIED?: string;
}

export const SLDCanvas: React.FC<SLDCanvasProps> = ({
  svg,
  isLoading,
  zoom,
  pan,
  onPanChange,
  onEquipmentClick,
  highlightedIED
}) => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current || !svg) return;

    // Add click listeners to equipment in SVG
    const svgElement = containerRef.current.querySelector('svg');
    if (!svgElement) return;

    // Find all equipment elements (depends on PowSyBl SVG structure)
    const equipments = svgElement.querySelectorAll('[data-equipment-id]');
    equipments.forEach(eq => {
      eq.addEventListener('click', (e) => {
        e.stopPropagation();
        const equipmentId = eq.getAttribute('data-equipment-id');
        if (equipmentId) onEquipmentClick(equipmentId);
      });

      // Hover effect
      eq.addEventListener('mouseenter', () => {
        eq.classList.add('hover');
      });
      eq.addEventListener('mouseleave', () => {
        eq.classList.remove('hover');
      });
    });

    // Highlight selected IED
    if (highlightedIED) {
      const iedElement = svgElement.querySelector(`[data-ied-id="${highlightedIED}"]`);
      if (iedElement) {
        iedElement.classList.add('highlighted');
        // Scroll to element
        iedElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }
  }, [svg, highlightedIED]);

  if (isLoading) {
    return (
      <div className="sld-canvas loading">
        <p>Generating single line diagram...</p>
        <div className="spinner"></div>
      </div>
    );
  }

  if (!svg) {
    return (
      <div className="sld-canvas empty">
        <p>No diagram available</p>
      </div>
    );
  }

  return (
    <TransformWrapper
      initialScale={zoom}
      initialPositionX={pan.x}
      initialPositionY={pan.y}
      onTransformed={(_, state) => {
        onPanChange({ x: state.positionX, y: state.positionY });
      }}
    >
      <TransformComponent>
        <div
          ref={containerRef}
          className="sld-canvas"
          dangerouslySetInnerHTML={{ __html: svg }}
        />
      </TransformComponent>
    </TransformWrapper>
  );
};
```

### 3. Toolbar Component

**Fichier** : `frontend/src/components/sld/SLDToolbar.tsx`

```typescript
import React from 'react';

interface SLDToolbarProps {
  zoom: number;
  onZoomIn: () => void;
  onZoomOut: () => void;
  onZoomFit: () => void;
  onExport: () => void;
  onRefresh: () => void;
}

export const SLDToolbar: React.FC<SLDToolbarProps> = ({
  zoom,
  onZoomIn,
  onZoomOut,
  onZoomFit,
  onExport,
  onRefresh
}) => {
  return (
    <div className="sld-toolbar">
      <div className="toolbar-group">
        <button onClick={onZoomIn} title="Zoom In">
          🔍+
        </button>
        <span className="zoom-level">{Math.round(zoom * 100)}%</span>
        <button onClick={onZoomOut} title="Zoom Out">
          🔍−
        </button>
        <button onClick={onZoomFit} title="Fit to Screen">
          ⤢
        </button>
      </div>

      <div className="toolbar-group">
        <button onClick={onRefresh} title="Refresh Diagram">
          🔄
        </button>
        <button onClick={onExport} title="Export as PNG">
          💾 Export
        </button>
      </div>
    </div>
  );
};
```

## Flux de données

```
┌─────────────────────────────────────────────┐
│         Zustand Global Store                │
│                                             │
│  selectedFile: SCLFile | null               │
│  selectedIED: IED | null                    │
│  sldCache: { [fileId]: { svg, timestamp } }│
└─────┬──────────────────────┬────────────────┘
      │                      │
      │                      │
┌─────▼─────────┐    ┌───────▼──────────┐
│ IED Explorer  │    │   SLD Viewer     │
│               │    │                  │
│ Reads:        │    │ Reads:           │
│ - selectedFile│    │ - selectedFile   │
│ - selectedIED │    │ - selectedIED    │
│               │    │ - sldCache       │
│ Writes:       │    │                  │
│ - selectedIED │    │ Writes:          │
│               │    │ - sldCache       │
└───────────────┘    └──────────────────┘
```

## Résumé des décisions

### ✅ Architecture choisie : Hybride

- **Dashboard** : Point d'entrée avec 2 options (IED Explorer / SLD Viewer)
- **IED Explorer** : Vue master/detail actuelle + bouton "View in SLD"
- **SLD Viewer** : Page dédiée full screen pour le schéma

### ✅ State Management : Zustand

- **Global** : `selectedFile`, `selectedIED`, `sldCache`
- **Local** : UI state (zoom, pan, expandedGroups, etc.)
- **Persisté** : Seul `selectedFile` (dans localStorage)

### ✅ Cache Strategy

- SLD généré mis en cache (1 heure TTL)
- Évite de régénérer le SVG à chaque navigation
- Bouton "Refresh" pour forcer la régénération

### ✅ Interactions

- Click sur IED → highlight dans SLD
- Click sur équipement dans SLD → show details + lien vers IED Explorer
- Zoom/Pan avec `react-zoom-pan-pinch`
- Export SVG/PNG

## Prochaines étapes

1. ✅ Installer Zustand : `npm install zustand`
2. ⏳ Créer les composants SLD (SLDCanvas, SLDToolbar, SLDSidebar)
3. ⏳ Créer la page SLDViewerPage
4. ⏳ Ajouter le lien dans Dashboard
5. ⏳ Ajouter le bouton "View in SLD" dans IED Explorer
6. ⏳ Tester le flux de navigation complet
