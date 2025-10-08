# SCL Files Management Feature

## Overview

This feature allows administrators to upload IEC 61850 SCL files (.scd, .icd, .cid), automatically convert them to RDF format, validate the conversion, and visualize the RDF schema.

## Architecture & Data Flow

### Data Storage Strategy

We use a **hybrid storage approach** optimized for different data types:

#### 1. **PostgreSQL** (Relational Database)
**What:** File metadata, user tracking, validation status
**Why:**
- Structured metadata (filename, size, upload timestamp, user)
- ACID transactions for file lifecycle management
- Easy querying and filtering for admin dashboard
- Referential integrity with user accounts

**Schema:**
```sql
scl_files (
  id, filename, file_size, status,
  scl_path, rdf_path, validated_scl_path,
  is_validated, validation_passed, validation_message,
  triple_count, fuseki_dataset,
  uploaded_by → users(id),
  uploaded_at, converted_at
)
```

#### 2. **Apache Jena Fuseki** (RDF Triplestore)
**What:** Converted RDF graph data
**Why:**
- Native storage for semantic data
- SPARQL query capabilities
- Graph traversal and ontology reasoning
- Scalable for large knowledge graphs

**Storage:** Each file gets its own dataset (e.g., `scl_file_123`)

#### 3. **Filesystem** (Docker Volume)
**What:** Original SCL files, generated RDF files, validated SCL files
**Why:**
- Binary file storage (XML, Turtle)
- Simple backup and archival
- Direct file serving if needed

**Mount:** `scl_uploads:/app/uploads` (persistent Docker volume)

#### 4. **React Component State**
**What:** UI state (uploading, drag-over, selected class, expanded samples)
**Why:**
- Ephemeral UI interactions
- No need for persistence
- Fast local updates

**Implementation:** useState hooks

#### 5. **React Query/Hooks State**
**What:** Server data cache (file list, RDF schema)
**Why:**
- Automatic refetching
- Loading/error states
- Optimistic updates
- No global state needed (admin-only feature)

**Implementation:** Custom `useSCLFiles()` hook with auto-refresh

### No Redux/Global State

**Decision:** Admin-only feature with simple data flow doesn't need Redux

**Rationale:**
- Only admins access this feature → No complex state sharing
- File list is fetched fresh on mount → No stale data issues
- Form state (upload) is component-local → No persistence needed
- RDF visualization is read-only → No mutations to sync

## Features

### 1. File Upload (Admin Only)

**Component:** `SCLFilesPage.tsx`

**Capabilities:**
- Drag-and-drop or click to select
- File validation:
  - Extension: .scd, .icd, .cid
  - Size: max 100MB
- Background processing with real-time status updates

**Access Control:**
- API: `verify_admin()` dependency (checks `is_superuser` or `admin` role)
- Frontend: Navigation link only shown to admins

### 2. Automatic Conversion Pipeline

**Backend:** `scl_files.py` → `process_scl_file()` (background task)

**Steps:**
1. **SCL → RDF**
   - Uses `scl_rdf_converter.py` (from iec61850-scl-rdf-converter repo)
   - Preserves all XML structure, attributes, private sections
   - Generates unique URIs for each element

2. **Store in Fuseki**
   - Creates dedicated dataset: `scl_file_{id}`
   - Uploads RDF triples
   - Indexes for SPARQL queries

3. **Round-Trip Validation** (RDF → SCL)
   - Regenerates SCL from RDF
   - Compares with original (byte-level and XML-semantic)
   - Records validation result

4. **Status Updates**
   - `uploaded` → `converting` → `converted` → `validated` (or `failed`)
   - Auto-refresh in frontend every 5s during processing

### 3. File Gallery

**Component:** `SCLFilesPage.tsx`

**Display:**
- File cards with:
  - Original filename & size
  - Status badge (color-coded)
  - Validation result (✓ or ✗)
  - Triple count
  - Upload metadata (user, timestamp)
  - Error messages if failed

**Actions:**
- View RDF Schema (if validated)
- Delete file (removes DB record, files, Fuseki dataset)

### 4. RDF Schema Visualization

**Component:** `RDFSchemaPage.tsx`

**Features:**
- **Classes Sidebar:**
  - All RDF types found in the file
  - Instance count for each class
  - Click to view details

- **Class Details:**
  - Full URI
  - Instance count
  - Sample triples (subject → predicate → object)
  - Expandable accordion

- **SPARQL Query Templates:**
  - Pre-filled queries for each class
  - Link to Fuseki web interface

- **Namespaces:**
  - All namespaces used in the graph

**Data Flow:**
- Fetches schema via `/api/scl-files/{id}/rdf-schema`
- API queries Fuseki for:
  - `SELECT ?type (COUNT(?s)) GROUP BY ?type` → Classes
  - `SELECT ?s ?p ?o WHERE { ?s a <type> }` → Samples
- Component state manages selected class and UI

## API Endpoints

### `POST /api/scl-files/upload`
- **Auth:** Admin only
- **Body:** multipart/form-data with `file`
- **Returns:** File metadata + background task started
- **Side Effects:**
  - Saves file to disk
  - Creates DB record (status: `uploaded`)
  - Starts background conversion task

### `GET /api/scl-files/`
- **Auth:** Admin only
- **Returns:** List of all uploaded files with full metadata

### `GET /api/scl-files/{file_id}`
- **Auth:** Admin only
- **Returns:** Detailed file metadata (including file paths)

### `GET /api/scl-files/{file_id}/rdf-schema`
- **Auth:** Admin only
- **Returns:** RDF schema analysis:
  - `classes[]` (type, count, samples)
  - `namespaces[]`
  - `triple_count`, `fuseki_dataset`

### `DELETE /api/scl-files/{file_id}`
- **Auth:** Admin only
- **Side Effects:**
  - Deletes files from disk
  - Deletes Fuseki dataset
  - Deletes DB record

## Database Migration

**File:** `backend/alembic/versions/002_add_scl_files_table.py`

**Run:**
```bash
# Automatic on container start via init_db.py
docker-compose up -d backend
```

## Frontend Routing

```
/scl-files                      → File gallery (admin only)
/scl-files/:fileId/rdf-schema   → RDF visualization
```

**Navigation:** Link appears in navbar only for admin users

## Dependencies Added

### Backend (`requirements.txt`)
```
rdflib==7.0.0    # RDF graph manipulation
lxml==5.1.0      # XML parsing
```

### Files Copied
- `backend/app/scl_converter.py` (from iec61850-scl-rdf-converter)

## Docker Configuration

**Volume:**
```yaml
volumes:
  scl_uploads:
    driver: local

services:
  backend:
    volumes:
      - scl_uploads:/app/uploads
```

**Persistence:** Files survive container restarts

## Security Considerations

### Access Control
- **Admin-only endpoints:** All SCL file routes require admin role
- **Frontend protection:** Navigation link hidden for non-admins (but backend enforces it)

### File Upload Safety
- **Extension whitelist:** Only .scd, .icd, .cid
- **Size limit:** 100MB max
- **Unique filenames:** Timestamp prefix prevents collisions
- **Sandboxed processing:** Background tasks isolated from request lifecycle

### Data Isolation
- **Per-file datasets:** Each file has its own Fuseki dataset → No cross-file queries
- **User tracking:** All uploads linked to user account for audit

## Performance Optimizations

### Background Processing
- File conversion runs in FastAPI BackgroundTasks
- Frontend polls for status updates
- Non-blocking user experience

### Auto-Refresh
- File list auto-refreshes every 5s if any file is processing
- Stops refreshing when all files are completed/failed

### Lazy Loading
- RDF schema only fetched when viewing visualization
- SPARQL queries limited to 10 sample triples per class

## Testing the Feature

### 1. Start Services
```bash
cd template-webapp
docker-compose up -d
```

### 2. Create Admin User
```bash
docker-compose exec backend python scripts/init_db.py
# Default admin: admin/admin123
```

### 3. Upload Test File
- Login as admin
- Navigate to "SCL Files"
- Drag-and-drop a .scd file
- Watch status change: uploaded → converting → validated

### 4. View RDF Schema
- Click "View RDF Schema" on a validated file
- Browse classes and samples
- Try SPARQL queries in Fuseki UI

## Troubleshooting

### Upload Fails
- Check file size < 100MB
- Verify file extension (.scd, .icd, .cid)
- Check backend logs: `docker-compose logs backend`

### Conversion Stuck on "converting"
- Check backend logs for errors
- Verify Fuseki is running: `docker-compose ps fuseki`
- Large files (>50MB) can take minutes

### RDF Schema Empty
- Ensure file status is "validated"
- Check Fuseki dataset exists: http://localhost:3030
- Query directly in Fuseki UI

### Missing Navigation Link
- Verify user has admin role or is_superuser
- Check `/api/auth/me` response for roles

## Future Enhancements

- [ ] Batch upload multiple files
- [ ] SPARQL query builder in UI
- [ ] Graph visualization (D3.js/vis.js)
- [ ] Diff viewer for before/after validation
- [ ] Export RDF to different formats (N-Triples, JSON-LD)
- [ ] Search/filter files by name, date, status
- [ ] Pagination for large file lists
- [ ] WebSocket for real-time status updates (vs polling)
