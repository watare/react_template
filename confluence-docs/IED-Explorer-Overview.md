# IED Explorer - Complete Documentation

**Space**: VPAC
**Last Updated**: 2025-01-09
**Author**: Development Team

---

## Table of Contents

1. [Overview](#overview)
2. [For Beginners: Understanding the Concepts](#for-beginners)
3. [For Developers: Architecture](#for-developers)
4. [For Implementers: Code Reference](#for-implementers)
5. [API Documentation](#api-documentation)
6. [Troubleshooting](#troubleshooting)

---

## Overview

The **IED Explorer** is a web-based visualization tool for navigating IEC 61850 Substation Configuration Description (SCL/SCD) files that have been converted to RDF format. It provides an interactive, hierarchical view of Intelligent Electronic Devices (IEDs) and their internal structure.

### Key Features

- **Master-Detail Interface**: List of IEDs on the left, detailed hierarchy on the right
- **Lazy Loading**: Only fetches data as you expand nodes, handling files with millions of triples
- **Grouping Options**: Group IEDs by type (BCU, SCU, etc.) or by bay location
- **Search**: Filter IEDs by name
- **Full Hierarchy Navigation**: IED → AccessPoint → Server → LDevice → LN0/LN → DataSets/Controls/DOI

---

## For Beginners: Understanding the Concepts

### What is RDF?

**RDF (Resource Description Framework)** is a way to store data as interconnected resources using triples:

```
Subject → Predicate → Object
```

Example:
```
<IED_BCU1> rdf:type iec:IED
<IED_BCU1> iec:name "POSTE4BUIS1SCU1"
<IED_BCU1> iec:hasAccessPoint <AP_PROCESS>
```

### What is SPARQL?

**SPARQL** is a query language for RDF data, similar to SQL for relational databases.

Example query to get all IEDs:
```sparql
PREFIX iec: <http://iec61850.com/SCL#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?ied ?name ?type
WHERE {
  ?ied rdf:type iec:IED .
  OPTIONAL { ?ied iec:name ?name }
  OPTIONAL { ?ied iec:type ?type }
}
```

### What is IEC 61850?

**IEC 61850** is an international standard for communication in electrical substations. An **IED (Intelligent Electronic Device)** is a smart device like a protection relay or controller.

The standard defines a hierarchy:
```
Substation
  └─ VoltageLevel
      └─ Bay
          └─ IED (our focus)
              └─ AccessPoint
                  └─ Server
                      └─ LDevice (Logical Device)
                          └─ LN0/LN (Logical Nodes)
                              └─ DataSets, Controls, Data Objects
```

### Why Lazy Loading?

SCL files can contain **millions of RDF triples**. Loading everything at once would:
- Crash the browser (too much memory)
- Take minutes to render
- Be impossible to navigate

**Lazy loading** means: "Only fetch the children of a node when the user clicks to expand it."

This is done by:
1. User clicks expand arrow (▶)
2. Frontend sends SPARQL query: "Give me children of this specific node"
3. Backend queries Fuseki RDF triplestore
4. Frontend displays only those children

---

## For Developers: Architecture

### System Architecture

```
┌─────────────────┐
│  React Frontend │
│  (TypeScript)   │
└────────┬────────┘
         │ HTTP/REST
         ↓
┌─────────────────┐
│  FastAPI Backend│
│  (Python)       │
└────────┬────────┘
         │ SPARQL
         ↓
┌─────────────────┐
│ Apache Fuseki   │
│ (RDF Triplestore)│
└─────────────────┘
```

### Component Hierarchy

```
IEDExplorerPage (Container)
├─ State Management
│  ├─ groupBy: 'type' | 'bay'
│  ├─ searchQuery: string
│  └─ selectedIED: IED | null
│
├─ IEDMasterPanel (Left Panel)
│  ├─ Fetches IED list from /api/ieds
│  ├─ Groups IEDs by type or bay
│  └─ Callbacks: onSelectIED()
│
└─ IEDDetailPanel (Right Panel)
   ├─ Shows selected IED metadata
   └─ ExpandableTree (Recursive)
      ├─ Fetches children from /api/ieds/tree
      ├─ Lazy expansion with handleExpand()
      └─ TreeNode interface
```

### Data Flow

```
1. User Action: Click IED in left panel
   ↓
2. IEDMasterPanel → onSelectIED(ied)
   ↓
3. IEDExplorerPage → setSelectedIED(ied)
   ↓
4. IEDDetailPanel receives selectedIED prop
   ↓
5. Creates root TreeNode
   ↓
6. User Action: Click expand on node
   ↓
7. handleExpand() → fetch(/api/ieds/tree?parent_uri=X&parent_type=Y)
   ↓
8. Backend builds SPARQL query based on parent_type
   ↓
9. Query Fuseki triplestore
   ↓
10. Format results as TreeNode[]
   ↓
11. Update node.children and trigger re-render
```

### State Management Pattern

We use **state lifting**: shared state lives in the parent component (`IEDExplorerPage`) and is passed down via props:

```typescript
// Parent
const [selectedIED, setSelectedIED] = useState<IED | null>(null);

// Pass to children
<IEDMasterPanel onSelectIED={setSelectedIED} />
<IEDDetailPanel selectedIED={selectedIED} />
```

This ensures both panels stay synchronized.

---

## For Implementers: Code Reference

### Backend Implementation

#### File: `backend/app/api/ieds.py`

**Purpose**: Provides REST API endpoints for IED navigation

**Key Endpoints**:

1. **GET /api/ieds** - List IEDs with grouping
2. **GET /api/ieds/tree** - Get children of a node

**Key Functions**:

```python
def build_ied_list_query(group_by: str, search: str = "") -> str
    """
    Builds SPARQL query to get all IEDs with optional search filter
    Returns: SPARQL query string
    """

def build_ied_by_bay_query(search: str = "") -> str
    """
    Builds SPARQL query to get IEDs grouped by Bay
    Uses LNode references to find Bay associations
    Returns: SPARQL query string
    """

def build_ied_children_query(parent_uri: str, parent_type: str) -> str
    """
    Builds SPARQL query for children based on parent type

    Parent Types:
    - IED → hasAccessPoint → AccessPoint
    - AccessPoint → hasServer → Server
    - Server → hasLDevice → LDevice
    - LDevice → hasLN0/hasLN → LN0/LN
    - LN0/LN → hasDataSet, hasGSEControl, hasDOI, etc.
    - DataSet → hasFCDA → FCDA
    - Inputs → hasExtRef → ExtRef

    Returns: SPARQL query string
    """

def extract_binding_value(binding: Dict) -> str
    """
    Extracts value from SPARQL JSON binding

    SPARQL returns: {"type": "uri", "value": "http://..."}
    This extracts: "http://..."
    """

def group_ieds_by_field(results: List[Dict], field: str) -> Dict[str, List[Dict]]
    """
    Groups IED results by a field (type or bayName)
    Returns: {"BCU": [ied1, ied2], "SCU": [ied3]}
    """
```

**Endpoint Details**:

##### GET /api/ieds

**Parameters**:
- `file_id` (int): SCL file ID
- `group_by` (str): "type" or "bay"
- `search` (str): Optional search filter

**Response**:
```json
{
  "group_by": "type",
  "search": "",
  "groups": {
    "BCU": [
      {
        "uri": "http://example.com/IED1",
        "name": "POSTE4BUIS1BCU1",
        "type": "BCU",
        "manufacturer": "Siemens",
        "description": "Bay Control Unit"
      }
    ],
    "SCU": [...]
  },
  "total_ieds": 12
}
```

##### GET /api/ieds/tree

**Parameters**:
- `file_id` (int): SCL file ID
- `parent_uri` (str): URI of parent node (URL encoded)
- `parent_type` (str): Type of parent (IED, AccessPoint, Server, LDevice, LN0, LN, DataSet, Inputs)

**Response**:
```json
{
  "parent_uri": "http://example.com/IED1",
  "parent_type": "IED",
  "children": [
    {
      "uri": "http://example.com/AP1",
      "name": "PROCESS_AP",
      "type": "AccessPoint",
      "hasChildren": true
    }
  ],
  "count": 1
}
```

**hasChildren Logic**:

Only these node types have expandable children:
- AccessPoint
- Server
- LDevice
- LN0
- LN
- DataSet
- Inputs

Leaf nodes (no children):
- DOI (Data Object Instance)
- FCDA (Functional Constraint Data Attribute)
- ExtRef (External Reference)
- GSEControl, ReportControl, SampledValueControl

**Display Name Logic**:

Different node types format their display names differently:

| Parent Type | Display Name Format | Example |
|------------|---------------------|---------|
| Server | `{inst} ({ldName})` | `LDAGSA1 (AgentServerLD)` |
| LDevice | `{prefix}{lnClass}{inst}` | `I01ATCTR11` or `LPHD0` |
| DataSet | `{ldInst}.{prefix}{lnClass}{lnInst}.{doName}.{daName} [{fc}]` | `LDAGSA1.LPHD0.PhyHealth.stVal [ST]` |
| Inputs | `{iedName}/{ldInst}/{prefix}{lnClass}{lnInst}/{doName}/{daName}` | `POSTE4/LDAGSA1/LPHD0/PhyHealth/stVal` |
| Other | `{name}` or `{inst}` | `PROCESS_AP` |

---

### Frontend Implementation

#### File: `frontend/src/pages/IEDExplorerPage.tsx`

**Purpose**: Container component managing shared state

**State**:
```typescript
interface IED {
  uri: string;
  name: string;
  type: string;
  manufacturer: string;
  description?: string;
}

const [groupBy, setGroupBy] = useState<'type' | 'bay'>('type');
const [searchQuery, setSearchQuery] = useState('');
const [selectedIED, setSelectedIED] = useState<IED | null>(null);
```

**Layout**:
- Page header with title and subtitle
- Controls section (radio buttons for groupBy, search input)
- Explorer container with master and detail panels side-by-side

---

#### File: `frontend/src/components/ied-explorer/IEDMasterPanel.tsx`

**Purpose**: Left panel showing grouped IED list

**Props**:
```typescript
interface IEDMasterPanelProps {
  fileId: number;
  groupBy: 'type' | 'bay';
  searchQuery: string;
  selectedIED: string | null;  // URI of selected IED
  onSelectIED: (ied: IED) => void;
}
```

**Behavior**:
- Fetches IEDs on mount and whenever `fileId`, `groupBy`, or `searchQuery` changes
- Groups IEDs by the specified field
- Highlights selected IED
- Calls `onSelectIED()` when user clicks an IED

**API Call**:
```typescript
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
```

---

#### File: `frontend/src/components/ied-explorer/IEDDetailPanel.tsx`

**Purpose**: Right panel showing expandable tree for selected IED

**Props**:
```typescript
interface IEDDetailPanelProps {
  fileId: number;
  selectedIED: IED | null;
}
```

**Key Function**:

```typescript
const handleExpand = async (node: TreeNode) => {
  // If already loaded, just toggle
  if (node.children !== null) {
    node.isExpanded = !node.isExpanded;
    setTreeRoot(treeRoot ? { ...treeRoot } : null);
    return;
  }

  // Fetch children from API
  const params = new URLSearchParams({
    file_id: fileId.toString(),
    parent_uri: encodeURIComponent(node.uri),
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

  const data = await response.json();

  // Convert API response to TreeNode format
  const children = data.children.map((child: any) => ({
    uri: child.uri,
    name: child.name,
    type: child.type,
    hasChildren: child.hasChildren,
    isExpanded: false,
    children: null,
    ...child  // Include all metadata
  }));

  // Update node
  node.children = children;
  node.isExpanded = true;

  // Force re-render with a fresh copy
  setTreeRoot({ ...treeRoot! });
};
```

**Important Note**: We use shallow copy (`{ ...treeRoot }`) to trigger React re-render. React doesn't detect nested object mutations, so we must create a new object reference.

---

#### File: `frontend/src/components/common/ExpandableTree.tsx`

**Purpose**: Reusable recursive tree component

**Interface**:
```typescript
export interface TreeNode {
  uri: string;              // Unique identifier (RDF URI)
  name: string;             // Display name
  type: string;             // Node type (IED, AccessPoint, etc.)
  hasChildren: boolean;     // Can this node be expanded?
  isExpanded?: boolean;     // Is it currently expanded?
  children?: TreeNode[] | null;  // null = not loaded, [] = loaded but empty
  [key: string]: any;       // Additional metadata
}
```

**Props**:
```typescript
interface ExpandableTreeProps {
  rootNode: TreeNode | null;
  onExpand: (node: TreeNode) => void;
  loading?: boolean;
}
```

**Rendering Logic**:

```typescript
const renderNode = (node: TreeNode, depth: number = 0) => {
  const hasExpandableChildren = node.hasChildren;
  const isExpanded = node.isExpanded;
  const children = node.children;

  return (
    <div key={node.uri} style={{ marginLeft: `${depth * 20}px` }}>
      {/* Node header */}
      <div className="tree-node" onClick={() => hasExpandableChildren && onExpand(node)}>
        {hasExpandableChildren && (
          <span className="expand-icon">
            {isExpanded ? '▼' : '▶'}
          </span>
        )}
        <span className="node-name">{node.name}</span>
        <span className="node-type">[{node.type}]</span>
      </div>

      {/* Children (if expanded) */}
      {isExpanded && children && children.map(child =>
        renderNode(child, depth + 1)
      )}
    </div>
  );
};
```

---

### Integration with Dashboard

**File**: `frontend/src/pages/DashboardPage.tsx`

Added "Explore IEDs" button for files with status `validated`:

```typescript
{file.status === 'validated' && (
  <button
    className="explore-button"
    onClick={(e) => {
      e.stopPropagation();
      navigate(`/ied-explorer?file_id=${file.id}`);
    }}
  >
    🔍 Explore IEDs
  </button>
)}
```

**File**: `frontend/src/App.tsx`

Added route:

```typescript
import IEDExplorerPage from './pages/IEDExplorerPage';

<Route path="ied-explorer" element={<IEDExplorerPage />} />
```

**File**: `backend/app/main.py`

Registered IED router:

```python
from app.api import auth, nodes, scl_files, ieds

app.include_router(ieds.router, prefix=settings.API_PREFIX)
```

---

## API Documentation

### Automatic OpenAPI Documentation

FastAPI automatically generates interactive API documentation at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These provide:
- List of all endpoints
- Request/response schemas
- "Try it out" functionality
- Authentication support

### Using the API Documentation

1. Navigate to http://localhost:8000/docs
2. Click "Authorize" and enter your JWT token
3. Expand any endpoint (e.g., `GET /api/ieds`)
4. Click "Try it out"
5. Fill in parameters
6. Click "Execute"
7. View response

---

## Troubleshooting

### Tree Expansion Shows No Children

**Symptom**: Click expand arrow, see loading, but no children appear

**Possible Causes**:

1. **Data not fully expanded**: You must expand each level individually
   - Expand IED → then AccessPoint → then Server → then LDevice
   - Don't expect to see LDevices directly under IED

2. **Node doesn't have children**: Check console logs for query results
   - Open browser DevTools (F12)
   - Check Network tab for API responses
   - Check Console tab for logged data

3. **SPARQL query returns empty results**: The node genuinely has no children
   - Verify in Fuseki UI: http://localhost:3030

### Display Names Show "0" or "Unknown"

**Symptom**: LN nodes show "0" instead of "LPHD0"

**Cause**: Display name logic not handling all field combinations

**Fix Applied**: Build name from parts list:
```python
name_parts = []
if prefix: name_parts.append(prefix)
if lnClass: name_parts.append(lnClass)
if inst: name_parts.append(inst)
node["name"] = "".join(name_parts) if name_parts else "Unknown LN"
```

### Multiple Server Nodes Appear

**Symptom**: Expanding Server shows 10 Server nodes instead of LDevices

**Cause**: React not detecting nested object mutations

**Fix Applied**: Use shallow copy to trigger re-render:
```typescript
setTreeRoot({ ...treeRoot! });
```

### "Failed to fetch tree children" on Leaf Nodes

**Symptom**: Clicking DOI or FCDA shows error message

**Cause**: `hasChildren` flag incorrectly set to true

**Fix Applied**: Check child node type instead of parent type:
```python
child_type = extract_binding_value(binding.get("type"))
node["hasChildren"] = child_type in ["AccessPoint", "Server", "LDevice", "LN0", "LN", "DataSet", "Inputs"]
```

---

## References

- **IEC 61850 Standard**: https://en.wikipedia.org/wiki/IEC_61850
- **RDF Primer**: https://www.w3.org/TR/rdf11-primer/
- **SPARQL Tutorial**: https://www.w3.org/TR/sparql11-query/
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **React TypeScript**: https://react-typescript-cheatsheet.netlify.app/

---

## Related Pages

- [SCL to RDF Conversion Process](./SCL-to-RDF-Conversion.md)
- [Apache Fuseki Setup Guide](./Fuseki-Setup.md)
- [Frontend Component Library](./Frontend-Components.md)
- [API Reference](http://localhost:8000/docs)

---

**End of Documentation**
