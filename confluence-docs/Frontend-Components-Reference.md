# Frontend Components Reference - IED Explorer

**Space**: VPAC
**Category**: Technical Reference
**Last Updated**: 2025-01-09

---

## Component Hierarchy

```
IEDExplorerPage (Page Component)
├─ IEDMasterPanel (Feature Component)
│  └─ IED List Rendering
├─ IEDDetailPanel (Feature Component)
│  └─ ExpandableTree (Shared Component)
│     └─ Recursive TreeNode Rendering
```

---

## 1. IEDExplorerPage

**Location**: `frontend/src/pages/IEDExplorerPage.tsx`

**Purpose**: Container component that manages shared state and coordinates between master and detail panels.

### Props

None. Gets `file_id` from URL query parameter via `useSearchParams()`.

### State

```typescript
interface IED {
  uri: string;
  name: string;
  type: string;
  manufacturer: string;
  description?: string;
}

// Grouping method
const [groupBy, setGroupBy] = useState<'type' | 'bay'>('type');

// Search filter
const [searchQuery, setSearchQuery] = useState('');

// Currently selected IED
const [selectedIED, setSelectedIED] = useState<IED | null>(null);
```

### Callbacks

```typescript
const handleSelectIED = (ied: IED) => {
  setSelectedIED(ied);
};
```

**Purpose**: Update selected IED when user clicks in master panel.

### Layout Structure

```tsx
<div className="ied-explorer-page">
  {/* Header */}
  <div className="page-header">
    <h1>IED Explorer</h1>
    <p className="subtitle">Navigate IEC 61850 Intelligent Electronic Devices</p>
  </div>

  {/* Controls */}
  <div className="explorer-controls">
    {/* Radio buttons for groupBy */}
    {/* Search input */}
  </div>

  {/* Main Content */}
  <div className="explorer-container">
    <div className="master-panel-container">
      <IEDMasterPanel
        fileId={parseInt(fileId)}
        groupBy={groupBy}
        searchQuery={searchQuery}
        selectedIED={selectedIED?.uri || null}
        onSelectIED={handleSelectIED}
      />
    </div>

    <div className="detail-panel-container">
      <IEDDetailPanel
        fileId={parseInt(fileId)}
        selectedIED={selectedIED}
      />
    </div>
  </div>
</div>
```

### Data Flow

1. User changes `groupBy` → triggers `setGroupBy()`
2. User types in search → triggers `setSearchQuery()`
3. `groupBy` and `searchQuery` passed to `IEDMasterPanel`
4. User clicks IED in master panel → `onSelectIED()` called
5. `setSelectedIED()` updates state
6. `selectedIED` passed to both panels to keep them in sync

### Error Handling

```typescript
if (!fileId) {
  return (
    <div className="ied-explorer-page error">
      <h1>IED Explorer</h1>
      <p>Error: No file ID provided</p>
    </div>
  );
}
```

### Styling

Uses CSS classes defined in `IEDExplorerPage.css`:
- `.ied-explorer-page` - Main container
- `.page-header` - Title section
- `.explorer-controls` - Controls bar with radio buttons and search
- `.explorer-container` - Flex container for master/detail panels
- `.master-panel-container` - Left panel wrapper
- `.detail-panel-container` - Right panel wrapper

---

## 2. IEDMasterPanel

**Location**: `frontend/src/components/ied-explorer/IEDMasterPanel.tsx`

**Purpose**: Displays list of IEDs grouped by type or bay, with search filtering.

### Props

```typescript
interface IEDMasterPanelProps {
  fileId: number;              // SCL file ID to query
  groupBy: 'type' | 'bay';     // Grouping method
  searchQuery: string;          // Search filter
  selectedIED: string | null;   // URI of currently selected IED
  onSelectIED: (ied: IED) => void;  // Callback when IED is clicked
}
```

### State

```typescript
interface GroupedIEDs {
  [key: string]: IED[];  // e.g., { "BCU": [ied1, ied2], "SCU": [ied3] }
}

const [groups, setGroups] = useState<GroupedIEDs>({});
const [loading, setLoading] = useState(true);
const [error, setError] = useState<string | null>(null);
```

### Effects

```typescript
useEffect(() => {
  fetchIEDs();
}, [fileId, groupBy, searchQuery]);
```

**Purpose**: Re-fetch IEDs whenever file, grouping, or search changes.

### API Integration

```typescript
const fetchIEDs = async () => {
  setLoading(true);
  setError(null);

  try {
    const params = new URLSearchParams({
      file_id: fileId.toString(),
      group_by: groupBy,
      search: searchQuery
    });

    const response = await fetch(
      `${import.meta.env.VITE_API_URL}/api/ieds?${params}`,
      {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      }
    );

    if (!response.ok) {
      throw new Error('Failed to fetch IEDs');
    }

    const data = await response.json();
    setGroups(data.groups);
  } catch (err) {
    setError(err instanceof Error ? err.message : 'Unknown error');
  } finally {
    setLoading(false);
  }
};
```

### Rendering Logic

```typescript
// Loading state
if (loading) return <div>Loading IEDs...</div>;

// Error state
if (error) return <div>Error: {error}</div>;

// Empty state
if (Object.keys(groups).length === 0) {
  return <div>No IEDs found</div>;
}

// Render groups
{Object.entries(groups).map(([groupName, ieds]) => (
  <div key={groupName} className="ied-group">
    <h3 className="group-header">{groupName}</h3>
    {ieds.map(ied => (
      <div
        key={ied.uri}
        className={`ied-item ${selectedIED === ied.uri ? 'selected' : ''}`}
        onClick={() => onSelectIED(ied)}
      >
        <div className="ied-name">{ied.name}</div>
        <div className="ied-manufacturer">{ied.manufacturer}</div>
      </div>
    ))}
  </div>
))}
```

### User Interactions

1. **Click on IED**: Calls `onSelectIED(ied)` to notify parent
2. **Selected IED**: Highlighted with `.selected` class
3. **Hover**: CSS hover effects for better UX

### Styling

Uses CSS classes defined in `IEDMasterPanel.css`:
- `.ied-master-panel` - Main container
- `.ied-group` - Group container (e.g., all BCUs)
- `.group-header` - Group title (e.g., "BCU")
- `.ied-item` - Individual IED row
- `.ied-item.selected` - Highlighted selected IED
- `.ied-name` - IED name display
- `.ied-manufacturer` - Manufacturer display

---

## 3. IEDDetailPanel

**Location**: `frontend/src/components/ied-explorer/IEDDetailPanel.tsx`

**Purpose**: Displays detailed hierarchical structure of selected IED using expandable tree.

### Props

```typescript
interface IEDDetailPanelProps {
  fileId: number;           // SCL file ID to query
  selectedIED: IED | null;  // Currently selected IED (full object)
}
```

### State

```typescript
const [treeRoot, setTreeRoot] = useState<TreeNode | null>(null);
const [loading, setLoading] = useState(false);
const [error, setError] = useState<string | null>(null);
```

### Effects

```typescript
useEffect(() => {
  if (selectedIED) {
    loadIEDTree();
  } else {
    setTreeRoot(null);
  }
}, [selectedIED]);
```

**Purpose**: Create new tree root whenever selected IED changes.

### Tree Initialization

```typescript
const loadIEDTree = () => {
  if (!selectedIED) return;

  // Create root node
  const root: TreeNode = {
    uri: selectedIED.uri,
    name: selectedIED.name,
    type: 'IED',
    hasChildren: true,
    isExpanded: false,
    children: null,  // null = not loaded yet
    manufacturer: selectedIED.manufacturer,
    iedType: selectedIED.type
  };

  setTreeRoot(root);
};
```

**Key Insight**: `children: null` means "not loaded yet". After loading, it becomes `[]` (empty) or `[...]` (has children).

### Lazy Loading Logic

```typescript
const handleExpand = async (node: TreeNode) => {
  // If already loaded, just toggle
  if (node.children !== null) {
    node.isExpanded = !node.isExpanded;
    // IMPORTANT: Create new reference to trigger React re-render
    setTreeRoot(treeRoot ? { ...treeRoot } : null);
    return;
  }

  // Fetch children from API
  setLoading(true);
  setError(null);

  try {
    const params = new URLSearchParams({
      file_id: fileId.toString(),
      parent_uri: encodeURIComponent(node.uri),  // IMPORTANT: URL encode
      parent_type: node.type
    });

    const response = await fetch(
      `${import.meta.env.VITE_API_URL}/api/ieds/tree?${params}`,
      {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      }
    );

    if (!response.ok) {
      throw new Error('Failed to fetch tree children');
    }

    const data = await response.json();

    // Convert API response to TreeNode format
    const children = data.children.map((child: any) => ({
      uri: child.uri,
      name: child.name,
      type: child.type,
      hasChildren: child.hasChildren,
      isExpanded: false,
      children: null,  // Children not loaded yet
      ...child  // Include all metadata (lnClass, inst, etc.)
    }));

    // Update node
    node.children = children;
    node.isExpanded = true;

    // Force re-render with a fresh copy
    // IMPORTANT: Shallow copy creates new reference
    setTreeRoot({ ...treeRoot! });

  } catch (err) {
    setError(err instanceof Error ? err.message : 'Unknown error');
    console.error('Error fetching tree children:', err);
  } finally {
    setLoading(false);
  }
};
```

**Key Techniques**:
1. Check `children !== null` to avoid re-fetching
2. URL encode `parent_uri` (contains special characters)
3. Set `children: null` initially so lazy loading works for grandchildren
4. Use shallow copy `{ ...treeRoot! }` to trigger React re-render

### Empty State

```typescript
if (!selectedIED) {
  return (
    <div className="ied-detail-panel empty">
      <div className="empty-state">
        <h3>No IED Selected</h3>
        <p>Select an IED from the left panel to view its details</p>
      </div>
    </div>
  );
}
```

### Rendering Structure

```tsx
<div className="ied-detail-panel">
  {/* Header with IED metadata */}
  <div className="ied-header">
    <h2>{selectedIED.name}</h2>
    <div className="ied-metadata">
      <div className="metadata-item">
        <span className="label">Type:</span>
        <span className="value">{selectedIED.type}</span>
      </div>
      <div className="metadata-item">
        <span className="label">Manufacturer:</span>
        <span className="value">{selectedIED.manufacturer}</span>
      </div>
      {selectedIED.description && (
        <div className="metadata-item">
          <span className="label">Description:</span>
          <span className="value">{selectedIED.description}</span>
        </div>
      )}
    </div>
  </div>

  {/* Expandable tree */}
  <div className="ied-tree-container">
    <h3>IED Hierarchy</h3>
    {error && (
      <div className="error-message">
        <p>Error: {error}</p>
      </div>
    )}
    <ExpandableTree
      rootNode={treeRoot}
      onExpand={handleExpand}
      loading={loading}
    />
  </div>
</div>
```

### Styling

Uses CSS classes defined in `IEDDetailPanel.css`:
- `.ied-detail-panel` - Main container
- `.ied-header` - Metadata header section
- `.ied-metadata` - Metadata grid
- `.metadata-item` - Single metadata row
- `.ied-tree-container` - Tree section
- `.empty-state` - No IED selected message
- `.error-message` - Error display

---

## 4. ExpandableTree

**Location**: `frontend/src/components/common/ExpandableTree.tsx`

**Purpose**: Reusable recursive tree component for displaying hierarchical data with lazy loading.

### Props

```typescript
interface ExpandableTreeProps {
  rootNode: TreeNode | null;          // Root of tree to display
  onExpand: (node: TreeNode) => void; // Callback when node is expanded
  loading?: boolean;                   // Show loading indicator
}
```

### TreeNode Interface

```typescript
export interface TreeNode {
  uri: string;              // Unique identifier (RDF URI)
  name: string;             // Display name
  type: string;             // Node type (IED, AccessPoint, Server, etc.)
  hasChildren: boolean;     // Can this node be expanded?
  isExpanded?: boolean;     // Is it currently expanded?
  children?: TreeNode[] | null;  // null = not loaded, [] = loaded but empty, [...] = has children
  [key: string]: any;       // Additional metadata (lnClass, inst, manufacturer, etc.)
}
```

**Important State Values**:

| `children` | `isExpanded` | Meaning |
|-----------|-------------|---------|
| `null` | `false` | Not loaded yet, shows ▶ |
| `[]` | `true` | Loaded but empty, shows ▼ |
| `[...]` | `false` | Loaded and has children, collapsed, shows ▶ |
| `[...]` | `true` | Loaded and has children, expanded, shows ▼ |

### Rendering Logic

```typescript
const renderNode = (node: TreeNode, depth: number = 0): JSX.Element => {
  const hasExpandableChildren = node.hasChildren;
  const isExpanded = node.isExpanded ?? false;
  const children = node.children;

  return (
    <div key={node.uri} className="tree-node-container">
      <div
        className={`tree-node ${hasExpandableChildren ? 'expandable' : 'leaf'} ${isExpanded ? 'expanded' : ''}`}
        style={{ paddingLeft: `${depth * 20}px` }}
        onClick={() => hasExpandableChildren && onExpand(node)}
      >
        {/* Expand/collapse icon */}
        {hasExpandableChildren && (
          <span className="expand-icon">
            {isExpanded ? '▼' : '▶'}
          </span>
        )}

        {/* Node name */}
        <span className="node-name">{node.name}</span>

        {/* Node type badge */}
        <span className="node-type">[{node.type}]</span>
      </div>

      {/* Recursively render children if expanded */}
      {isExpanded && children && children.length > 0 && (
        <div className="tree-children">
          {children.map(child => renderNode(child, depth + 1))}
        </div>
      )}

      {/* Show message if expanded but no children */}
      {isExpanded && children && children.length === 0 && (
        <div
          className="tree-node leaf"
          style={{ paddingLeft: `${(depth + 1) * 20}px` }}
        >
          <span className="node-name empty">No children</span>
        </div>
      )}
    </div>
  );
};
```

**Key Features**:
1. **Indentation**: `paddingLeft: ${depth * 20}px` creates visual hierarchy
2. **Conditional Icons**: Only show ▶/▼ if `hasChildren` is true
3. **Click Handler**: Only trigger `onExpand()` if node is expandable
4. **Recursion**: Each child calls `renderNode()` with incremented depth
5. **Empty State**: Show "No children" if expanded but empty

### Root Rendering

```typescript
if (!rootNode) {
  return (
    <div className="expandable-tree empty">
      <p>No data to display</p>
    </div>
  );
}

return (
  <div className="expandable-tree">
    {loading && (
      <div className="loading-overlay">
        <span className="loading-spinner">⏳</span>
        <span>Loading...</span>
      </div>
    )}
    {renderNode(rootNode, 0)}
  </div>
);
```

### Styling

Uses CSS classes defined in `ExpandableTree.css`:
- `.expandable-tree` - Main container
- `.tree-node-container` - Single node wrapper
- `.tree-node` - Node content row
- `.tree-node.expandable` - Expandable node (cursor: pointer)
- `.tree-node.leaf` - Leaf node (no cursor change)
- `.tree-node.expanded` - Expanded node (different styling)
- `.expand-icon` - ▶/▼ icon
- `.node-name` - Node display name
- `.node-type` - Node type badge [IED]
- `.tree-children` - Children container
- `.loading-overlay` - Loading indicator

### CSS Example

```css
.tree-node {
  display: flex;
  align-items: center;
  padding: 0.5rem;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.tree-node.expandable {
  cursor: pointer;
}

.tree-node.expandable:hover {
  background-color: #f5f5f5;
}

.expand-icon {
  width: 20px;
  text-align: center;
  margin-right: 0.5rem;
  color: #666;
}

.node-name {
  flex: 1;
  font-weight: 500;
}

.node-type {
  font-size: 0.75rem;
  color: #666;
  background-color: #e0e0e0;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
}
```

---

## Data Flow Summary

### Initial Load Flow

```
1. User opens /ied-explorer?file_id=1
   ↓
2. IEDExplorerPage renders with default state
   ↓
3. IEDMasterPanel mounts → useEffect triggers
   ↓
4. fetchIEDs() → GET /api/ieds?file_id=1&group_by=type
   ↓
5. Backend queries Fuseki with SPARQL
   ↓
6. Returns grouped IEDs: { "BCU": [...], "SCU": [...] }
   ↓
7. IEDMasterPanel renders groups
   ↓
8. IEDDetailPanel shows "No IED Selected"
```

### Selection Flow

```
1. User clicks IED in master panel
   ↓
2. IEDMasterPanel calls onSelectIED(ied)
   ↓
3. IEDExplorerPage calls setSelectedIED(ied)
   ↓
4. selectedIED state updated
   ↓
5. IEDDetailPanel receives new selectedIED prop
   ↓
6. useEffect triggers → loadIEDTree()
   ↓
7. Creates TreeNode root with children: null
   ↓
8. ExpandableTree renders root (collapsed)
```

### Expansion Flow

```
1. User clicks ▶ on tree node
   ↓
2. ExpandableTree calls onExpand(node)
   ↓
3. IEDDetailPanel.handleExpand() executes
   ↓
4. Check if node.children === null (not loaded)
   ↓
5. If null → fetch from API:
   GET /api/ieds/tree?parent_uri=X&parent_type=Y
   ↓
6. Backend builds SPARQL query based on parent_type
   ↓
7. Query Fuseki → return children
   ↓
8. Convert API response to TreeNode[]
   ↓
9. Update node.children = [...], node.isExpanded = true
   ↓
10. setTreeRoot({ ...treeRoot }) to trigger re-render
   ↓
11. ExpandableTree re-renders with expanded node
   ↓
12. Recursively renders children at depth + 1
```

---

## Component Communication Patterns

### 1. State Lifting

Shared state lives in parent (`IEDExplorerPage`), passed down via props:

```typescript
// Parent
const [selectedIED, setSelectedIED] = useState<IED | null>(null);

// Child 1 (Master)
<IEDMasterPanel
  selectedIED={selectedIED?.uri}
  onSelectIED={setSelectedIED}
/>

// Child 2 (Detail)
<IEDDetailPanel
  selectedIED={selectedIED}
/>
```

**Benefits**:
- Single source of truth
- Synchronized views
- Easy to debug (state in one place)

### 2. Callback Props

Children notify parents via callback functions:

```typescript
// Parent defines callback
const handleSelectIED = (ied: IED) => {
  setSelectedIED(ied);
};

// Parent passes to child
<IEDMasterPanel onSelectIED={handleSelectIED} />

// Child calls callback
<div onClick={() => onSelectIED(ied)}>
```

**Benefits**:
- Unidirectional data flow
- Clear contract between components
- Testable (can mock callbacks)

### 3. Recursive Rendering

ExpandableTree calls itself recursively:

```typescript
const renderNode = (node: TreeNode, depth: number) => {
  return (
    <div>
      {/* Node content */}
      {node.isExpanded && node.children?.map(child =>
        renderNode(child, depth + 1)  // Recursive call
      )}
    </div>
  );
};
```

**Benefits**:
- Handles arbitrary depth
- Simple code for complex structures
- Each level is self-contained

### 4. Controlled vs Uncontrolled

Our tree is **controlled**: parent manages `treeRoot` state, child just renders it.

```typescript
// Parent (IEDDetailPanel) controls state
const [treeRoot, setTreeRoot] = useState<TreeNode | null>(null);
const handleExpand = (node) => {
  // Mutate node, then trigger re-render
  node.children = [...];
  setTreeRoot({ ...treeRoot });
};

// Child (ExpandableTree) is stateless
<ExpandableTree rootNode={treeRoot} onExpand={handleExpand} />
```

**Alternative (Uncontrolled)**: ExpandableTree would manage its own state internally.

**Why Controlled?**:
- Parent can inspect/modify tree structure
- Easier to persist tree state (e.g., save to localStorage)
- Parent can reset tree when IED changes

---

## TypeScript Type Definitions

### Shared Types (`frontend/src/types/index.ts`)

```typescript
// IED entity
export interface IED {
  uri: string;
  name: string;
  type: string;
  manufacturer: string;
  description?: string;
}

// Tree node for expandable tree
export interface TreeNode {
  uri: string;
  name: string;
  type: string;
  hasChildren: boolean;
  isExpanded?: boolean;
  children?: TreeNode[] | null;
  [key: string]: any;  // Allow additional metadata
}

// API response for /api/ieds
export interface IEDListResponse {
  group_by: string;
  search: string;
  groups: {
    [key: string]: IED[];
  };
  total_ieds: number;
}

// API response for /api/ieds/tree
export interface IEDTreeResponse {
  parent_uri: string;
  parent_type: string;
  children: TreeNode[];
  count: number;
}
```

---

## Testing Considerations

### Unit Tests

```typescript
// IEDMasterPanel.test.tsx
describe('IEDMasterPanel', () => {
  it('should render groups of IEDs', () => {
    const mockGroups = {
      "BCU": [{ uri: "1", name: "BCU1", type: "BCU", manufacturer: "Siemens" }],
      "SCU": [{ uri: "2", name: "SCU1", type: "SCU", manufacturer: "ABB" }]
    };
    // ... mock fetch to return mockGroups
    // ... assert groups are rendered
  });

  it('should call onSelectIED when IED is clicked', () => {
    const mockCallback = jest.fn();
    // ... render with onSelectIED={mockCallback}
    // ... click IED
    // ... expect(mockCallback).toHaveBeenCalledWith(ied)
  });
});
```

### Integration Tests

```typescript
// IEDExplorerPage.test.tsx
describe('IEDExplorerPage', () => {
  it('should sync master and detail panels', async () => {
    // ... render IEDExplorerPage
    // ... wait for IEDs to load
    // ... click IED in master panel
    // ... assert detail panel shows IED name
    // ... assert master panel highlights selected IED
  });
});
```

### E2E Tests (Cypress)

```typescript
describe('IED Explorer', () => {
  it('should navigate IED hierarchy', () => {
    cy.visit('/ied-explorer?file_id=1');
    cy.contains('POSTE4BUIS1BCU1').click();
    cy.contains('PROCESS_AP').parent().find('.expand-icon').click();
    cy.contains('Server');
    cy.contains('[LDevice]');
  });
});
```

---

## Performance Optimizations

### 1. Lazy Loading

Only fetch children when node is expanded:

```typescript
if (node.children !== null) {
  // Already loaded, skip fetch
  return;
}
```

**Impact**: Reduces initial load time from minutes to milliseconds.

### 2. Shallow Copy for Re-render

```typescript
setTreeRoot({ ...treeRoot! });  // Shallow copy
```

vs

```typescript
setTreeRoot(JSON.parse(JSON.stringify(treeRoot)));  // Deep copy
```

**Why Shallow?**: Deep copy is expensive for large trees. Shallow copy is sufficient because we create new node objects in `handleExpand()`.

### 3. useEffect Dependencies

```typescript
useEffect(() => {
  fetchIEDs();
}, [fileId, groupBy, searchQuery]);  // Only re-run when these change
```

**Without Dependencies**: Would re-run on every render, causing infinite loop.

### 4. Memoization (Future)

```typescript
const memoizedTree = useMemo(() => {
  return renderNode(rootNode, 0);
}, [rootNode]);
```

**Use Case**: If tree rendering becomes slow (1000+ nodes visible).

---

## Accessibility (a11y)

### Keyboard Navigation

```typescript
<div
  className="tree-node"
  onClick={handleClick}
  onKeyDown={(e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      handleClick();
    }
  }}
  tabIndex={0}
  role="button"
  aria-expanded={isExpanded}
>
```

### Screen Readers

```typescript
<div
  role="tree"
  aria-label="IED Hierarchy"
>
  <div
    role="treeitem"
    aria-level={depth + 1}
    aria-expanded={isExpanded}
    aria-label={`${node.name}, ${node.type}`}
  >
```

### Focus Management

```typescript
const nodeRef = useRef<HTMLDivElement>(null);

useEffect(() => {
  if (isExpanded) {
    // Focus first child when expanded
    nodeRef.current?.querySelector('.tree-node')?.focus();
  }
}, [isExpanded]);
```

---

## Related Documentation

- [IED Explorer Overview](./IED-Explorer-Overview.md)
- [API Endpoints Reference](./API-Endpoints-Reference.md)
- [Styling Guide](./Styling-Guide.md)
- [Testing Guide](./Testing-Guide.md)

---

**End of Component Reference**
