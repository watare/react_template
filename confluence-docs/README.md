# IED Explorer Documentation - Confluence Upload Guide

**Target Space**: VPAC
**Date**: 2025-01-09

---

## Documentation Structure

This directory contains comprehensive documentation for the IED Explorer feature, structured for Confluence pages in the VPAC space.

### Documentation Files

| File | Target Page Title | Category | Audience |
|------|------------------|----------|----------|
| `IED-Explorer-Overview.md` | IED Explorer - Complete Documentation | Main | All (Beginner → Implementer) |
| `API-Endpoints-Reference.md` | API Endpoints Reference - IED Explorer | Technical | Developers/Integrators |
| `Frontend-Components-Reference.md` | Frontend Components Reference - IED Explorer | Technical | Frontend Developers |
| `SPARQL-Query-Guide.md` | SPARQL Query Guide - IED Explorer | Technical | Backend Developers/Data Engineers |

---

## Confluence Page Hierarchy

```
VPAC Space
└── IED Explorer (Parent Page)
    ├── IED Explorer - Complete Documentation (Overview)
    │   ├── For Beginners: Understanding the Concepts
    │   ├── For Developers: Architecture
    │   ├── For Implementers: Code Reference
    │   └── Troubleshooting
    ├── API Endpoints Reference
    │   ├── GET /api/ieds
    │   └── GET /api/ieds/tree
    ├── Frontend Components Reference
    │   ├── Component Hierarchy
    │   ├── IEDExplorerPage
    │   ├── IEDMasterPanel
    │   ├── IEDDetailPanel
    │   └── ExpandableTree
    └── SPARQL Query Guide
        ├── SPARQL Basics
        ├── IED List Queries
        ├── IED Hierarchy Queries
        └── Query Optimization
```

---

## How to Upload to Confluence

### Option 1: Manual Copy-Paste (Recommended)

1. **Log into Confluence**: Navigate to your Confluence instance and the VPAC space

2. **Create Parent Page**:
   - Click "Create" button
   - Title: "IED Explorer"
   - Add description: "Documentation for the IED Explorer feature - RDF-based navigation of IEC 61850 SCL files"

3. **Create Child Pages** (one for each markdown file):

   **For IED-Explorer-Overview.md**:
   - Create child page under "IED Explorer"
   - Title: "IED Explorer - Complete Documentation"
   - Copy markdown content
   - Use Confluence markdown import or paste into editor
   - Format as needed (Confluence will convert most markdown automatically)

   **For API-Endpoints-Reference.md**:
   - Create child page under "IED Explorer"
   - Title: "API Endpoints Reference - IED Explorer"
   - Copy markdown content
   - Paste into Confluence editor

   **For Frontend-Components-Reference.md**:
   - Create child page under "IED Explorer"
   - Title: "Frontend Components Reference - IED Explorer"
   - Copy markdown content
   - Paste into Confluence editor

   **For SPARQL-Query-Guide.md**:
   - Create child page under "IED Explorer"
   - Title: "SPARQL Query Guide - IED Explorer"
   - Copy markdown content
   - Paste into Confluence editor

4. **Format Code Blocks**:
   - Confluence supports code blocks with syntax highlighting
   - Select code, click "Code block" button
   - Choose language (JavaScript, Python, SPARQL, Bash)

5. **Add Labels**:
   - Add labels to each page: `ied-explorer`, `rdf`, `documentation`, `iec61850`

6. **Link Pages**:
   - Update "Related Pages" sections with actual Confluence links
   - Use `[Page Title]` to auto-link

---

### Option 2: Using Confluence Markdown Importer

Some Confluence instances have markdown import plugins:

1. Install "Markdown Macro" or similar plugin (if available)
2. Create page
3. Click "Insert" → "Other macros" → "Markdown"
4. Paste markdown content
5. Save

---

### Option 3: Using Confluence CLI (Advanced)

If you have Confluence CLI installed:

```bash
confluence-cli \
  --action addPage \
  --space VPAC \
  --title "IED Explorer - Complete Documentation" \
  --parent "IED Explorer" \
  --file IED-Explorer-Overview.md \
  --labels "ied-explorer,rdf,documentation"
```

Repeat for each file.

---

## Documentation Content Summary

### 1. IED Explorer - Complete Documentation (Overview)

**Purpose**: Main entry point for all users

**Content**:
- Overview of IED Explorer features
- **For Beginners**: RDF basics, SPARQL basics, IEC 61850 hierarchy, lazy loading concept
- **For Developers**: System architecture, component hierarchy, data flow, state management patterns
- **For Implementers**: Backend implementation (ieds.py), frontend implementation (all components), API integration
- Troubleshooting common issues
- References and related pages

**Target Audience**:
- ✅ Beginners learning web development
- ✅ Developers understanding architecture
- ✅ Implementers needing code reference

**Key Sections**:
- What is RDF? (Beginner)
- What is SPARQL? (Beginner)
- What is IEC 61850? (Beginner)
- Why Lazy Loading? (Beginner)
- System Architecture (Developer)
- Component Hierarchy (Developer)
- Data Flow (Developer)
- Backend Code Reference (Implementer)
- Frontend Code Reference (Implementer)

---

### 2. API Endpoints Reference

**Purpose**: Technical reference for API integration

**Content**:
- Base URL and authentication
- Detailed documentation for each endpoint:
  - GET /api/ieds (list with grouping and search)
  - GET /api/ieds/tree (lazy loading hierarchy)
- Request parameters with types and descriptions
- Response formats with field descriptions
- Error responses with status codes
- SPARQL queries used by each endpoint
- Display name formatting logic
- hasChildren logic
- Best practices for API usage

**Target Audience**:
- ✅ Backend developers
- ✅ API integrators
- ✅ Frontend developers calling the API

**Key Sections**:
- GET /api/ieds (with examples)
- GET /api/ieds/tree (with examples)
- Authentication (JWT)
- Error handling
- Best practices

---

### 3. Frontend Components Reference

**Purpose**: Technical reference for frontend components

**Content**:
- Component hierarchy diagram
- Detailed documentation for each component:
  - IEDExplorerPage (container with state management)
  - IEDMasterPanel (IED list with grouping)
  - IEDDetailPanel (tree with lazy loading)
  - ExpandableTree (reusable recursive component)
- Props, state, effects for each component
- Data flow between components
- API integration code
- Rendering logic
- User interaction handlers
- TypeScript type definitions
- Testing considerations
- Performance optimizations
- Accessibility features

**Target Audience**:
- ✅ Frontend developers
- ✅ React/TypeScript developers
- ✅ Component architects

**Key Sections**:
- Component Hierarchy
- Each component (props, state, logic, rendering)
- Data Flow Summary
- Component Communication Patterns
- TypeScript Types
- Testing
- Performance
- Accessibility

---

### 4. SPARQL Query Guide

**Purpose**: Technical reference for SPARQL queries

**Content**:
- SPARQL basics (for beginners)
- Complete query documentation for:
  - IED list queries (by type, by bay)
  - IED hierarchy queries (all 10 parent-child relationships)
- Query explanations with line-by-line breakdowns
- Display name formatting for each node type
- Query optimization techniques
- Testing queries in Fuseki
- Common issues and solutions
- Best practices

**Target Audience**:
- ✅ Backend developers
- ✅ Data engineers
- ✅ SPARQL beginners
- ✅ Anyone debugging queries

**Key Sections**:
- SPARQL Basics (Beginner)
- IED List Queries (2 queries)
- IED Hierarchy Queries (10 queries for each parent-child relationship)
- Query Optimization (6 techniques)
- Testing in Fuseki
- Troubleshooting

---

## Documentation Features

### ✅ Structured from Beginner to Implementer

Each page is organized by expertise level:

1. **Beginner Level**: Concepts, explanations, "what" and "why"
   - What is RDF?
   - What is SPARQL?
   - Why lazy loading?

2. **Developer Level**: Architecture, design patterns, "how"
   - System architecture
   - Component hierarchy
   - Data flow

3. **Implementer Level**: Code, APIs, technical details
   - Function signatures
   - API endpoints
   - SPARQL queries
   - Code examples

### ✅ All Components Documented

Every created component is fully documented:

- **Backend**:
  - `backend/app/api/ieds.py` (functions, endpoints, SPARQL queries)
  - Integration with `backend/app/main.py`

- **Frontend**:
  - `IEDExplorerPage.tsx` (state management, layout)
  - `IEDMasterPanel.tsx` (IED list, grouping, search)
  - `IEDDetailPanel.tsx` (tree root, lazy loading)
  - `ExpandableTree.tsx` (recursive rendering)
  - Integration with `App.tsx` and `DashboardPage.tsx`

### ✅ All Rules and Logic Documented

Every decision and rule is explained:

- hasChildren logic (which node types are expandable)
- Display name formatting (different for each parent type)
- React re-rendering (shallow copy pattern)
- State management (state lifting pattern)
- SPARQL query structure (for each hierarchy level)
- Error handling
- API parameters (required vs optional)

### ✅ Examples Throughout

Every concept includes examples:

- Code examples (TypeScript, Python, SPARQL)
- API request/response examples
- SPARQL query examples with explanations
- Display name formatting examples
- Data flow diagrams
- Component hierarchy diagrams

---

## Automatic Documentation

### FastAPI OpenAPI Documentation

FastAPI automatically generates API documentation:

**Access URLs**:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

**Features**:
- Interactive API testing ("Try it out")
- Request/response schemas
- Authentication support
- Automatically stays in sync with code

**To Use**:
1. Start backend: `docker-compose up backend`
2. Navigate to http://localhost:8000/docs
3. Click "Authorize" and enter JWT token
4. Explore and test endpoints

**Confluence Integration**:
Add a page with:
- Title: "Live API Documentation"
- Content: Link to http://localhost:8000/docs (or production URL)
- Description: "Interactive API documentation automatically generated from code"

---

## Complementary Tools

### TypeDoc (Future Enhancement)

For automatic TypeScript component documentation:

```bash
npm install --save-dev typedoc
npx typedoc --out docs/typescript src/
```

Then upload `docs/typescript/index.html` to Confluence as attachment.

### Sphinx (Future Enhancement)

For Python backend documentation:

```bash
pip install sphinx sphinx-autodoc-typehints
sphinx-quickstart docs/
sphinx-build -b html docs/ docs/_build/
```

Then upload to Confluence.

---

## Maintenance

### Keeping Documentation Up to Date

**When to Update**:
- ✅ New endpoints added → Update API Endpoints Reference
- ✅ New components created → Update Frontend Components Reference
- ✅ New SPARQL queries → Update SPARQL Query Guide
- ✅ Architecture changes → Update Overview
- ✅ Bug fixes → Update Troubleshooting section

**How to Update**:
1. Edit markdown files in this directory
2. Test changes locally (preview markdown)
3. Copy to Confluence
4. Update "Last Updated" date
5. Add version note at top (optional)

---

## JIRA Integration

### Updating JIRA Tickets

After uploading documentation to Confluence, update related JIRA tickets in VPAC space:

**Example**:

**Ticket**: VPAC-123 - Implement IED Explorer

**Comment**:
```
✅ Feature implemented and documented

Documentation available in Confluence:
- Main: [[IED Explorer - Complete Documentation]]
- API: [[API Endpoints Reference - IED Explorer]]
- Frontend: [[Frontend Components Reference - IED Explorer]]
- Queries: [[SPARQL Query Guide - IED Explorer]]

Key changes:
- Added /api/ieds endpoint for listing IEDs
- Added /api/ieds/tree endpoint for lazy loading
- Created 4 new frontend components
- Implemented 10 SPARQL queries for hierarchy navigation
```

**Steps**:
1. Find related JIRA tickets (search for "IED" or "Explorer")
2. Add comment with links to Confluence pages
3. Move ticket to "Done" status
4. Link Confluence pages in ticket (if Confluence/JIRA integration is enabled)

---

## Next Steps

1. ✅ Review all 4 markdown files for accuracy
2. ✅ Create parent page "IED Explorer" in Confluence VPAC space
3. ✅ Upload each markdown file as child page
4. ✅ Format code blocks with syntax highlighting
5. ✅ Add labels: `ied-explorer`, `rdf`, `documentation`, `iec61850`
6. ✅ Link pages together (update "Related Pages" sections)
7. ✅ Add link to live API docs (http://localhost:8000/docs)
8. ✅ Update JIRA tickets with Confluence links
9. ✅ Share page link with team

---

## Contact

For questions or updates to this documentation:
- **JIRA**: Create ticket in VPAC space with label `documentation`
- **Confluence**: Comment on relevant page
- **Development Team**: Tag @dev-team in Confluence

---

**End of Upload Guide**
