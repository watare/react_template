# Future Enhancements

## 🚀 High Priority

### 1. SCL Conversion Progress Tracking

**Problem:** Users upload large files (50-100MB) and only see "converting" status for 5-7 minutes with no progress indication.

**Solution:** Add granular progress tracking with progress bar

#### Backend Changes

**Option A: WebSocket Real-time Updates**
```python
# app/api/scl_files.py
from fastapi import WebSocket

@router.websocket("/ws/{file_id}")
async def conversion_progress(websocket: WebSocket, file_id: int):
    await websocket.accept()
    # Stream progress updates
    await websocket.send_json({"stage": "parsing", "progress": 10})
    await websocket.send_json({"stage": "converting", "progress": 50})
    await websocket.send_json({"stage": "uploading", "progress": 80})
    await websocket.send_json({"stage": "validating", "progress": 95})
    await websocket.send_json({"stage": "complete", "progress": 100})
```

**Option B: Extended Status Field**
```python
# Add to scl_file.py model
conversion_stage = Column(String(50))  # parsing|converting|uploading|validating
progress_percent = Column(Integer, default=0)  # 0-100
stage_message = Column(String(255))  # "Parsing XML elements..."

# Update in process_scl_file()
scl_file.conversion_stage = "parsing"
scl_file.progress_percent = 10
scl_file.stage_message = "Parsing XML structure..."
db.commit()

scl_file.conversion_stage = "converting"
scl_file.progress_percent = 30
scl_file.stage_message = f"Converting to RDF: {current_element}/{total_elements} elements"
db.commit()
```

**Option C: Redis + Server-Sent Events (SSE)**
```python
# Use Redis for progress tracking
import redis
r = redis.Redis(host='redis', port=6379)

# In background task
r.set(f"scl_file:{file_id}:progress", json.dumps({
    "stage": "converting",
    "progress": 45,
    "message": "Converting element 50000/100000"
}))

# SSE endpoint
@router.get("/progress/{file_id}")
async def stream_progress(file_id: int):
    async def event_generator():
        while True:
            data = r.get(f"scl_file:{file_id}:progress")
            yield f"data: {data}\n\n"
            await asyncio.sleep(1)
    return EventSourceResponse(event_generator())
```

#### Frontend Changes

```tsx
// useSCLFiles.ts
const [progress, setProgress] = useState<{
  stage: string
  percent: number
  message: string
} | null>(null)

// Option 1: Polling (simple)
useEffect(() => {
  if (file.status === 'converting') {
    const interval = setInterval(async () => {
      const response = await api.get(`/scl-files/${file.id}/progress`)
      setProgress(response.data)
    }, 2000)
    return () => clearInterval(interval)
  }
}, [file.status])

// Option 2: WebSocket (real-time)
useEffect(() => {
  if (file.status === 'converting') {
    const ws = new WebSocket(`ws://localhost:8000/api/scl-files/ws/${file.id}`)
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      setProgress(data)
    }
    return () => ws.close()
  }
}, [file.status])
```

```tsx
// SCLFilesPage.tsx - Progress bar component
{file.status === 'converting' && progress && (
  <div className="progress-container">
    <div className="progress-bar">
      <div
        className="progress-fill"
        style={{ width: `${progress.percent}%` }}
      />
    </div>
    <div className="progress-details">
      <span className="progress-stage">{progress.stage}</span>
      <span className="progress-percent">{progress.percent}%</span>
    </div>
    <div className="progress-message">{progress.message}</div>
  </div>
)}
```

#### Progress Stages

1. **Parsing XML** (0-20%)
   - "Parsing SCL structure..."
   - "Found X IEDs, Y LNodes"

2. **Converting to RDF** (20-60%)
   - "Converting element 10000/50000..."
   - Track: IEDs → LDevices → LNodes → DOIs → DAIs

3. **Uploading to Fuseki** (60-80%)
   - "Creating Fuseki dataset..."
   - "Uploading triples: 50000/500000..."

4. **Round-trip Validation** (80-95%)
   - "Regenerating SCL from RDF..."
   - "Comparing with original..."

5. **Complete** (100%)
   - "Validation passed! ✓"

---

### 2. Better Error Handling

**Add specific error types:**
```python
class SCLConversionError(Exception):
    pass

class XMLParseError(SCLConversionError):
    pass

class RDFConversionError(SCLConversionError):
    pass

class ValidationError(SCLConversionError):
    pass
```

**Store detailed error info:**
```python
# In scl_file.py model
error_type = Column(String(50))  # xml_parse|rdf_conversion|validation
error_details = Column(JSON)  # Structured error info
failed_at_stage = Column(String(50))
```

**Frontend error display:**
```tsx
{file.error_message && (
  <div className="error-details">
    <h4>Conversion Failed</h4>
    <p><strong>Stage:</strong> {file.failed_at_stage}</p>
    <p><strong>Error:</strong> {file.error_message}</p>
    {file.error_details && (
      <pre>{JSON.stringify(file.error_details, null, 2)}</pre>
    )}
  </div>
)}
```

---

### 3. Conversion Cancellation

**Allow users to cancel long-running conversions:**

```python
# Add to model
is_cancelled = Column(Boolean, default=False)

# Check in background task
def process_scl_file(file_id, scl_path, db):
    for element in elements:
        # Check cancellation every 1000 elements
        if i % 1000 == 0:
            db.refresh(scl_file)
            if scl_file.is_cancelled:
                scl_file.status = "cancelled"
                db.commit()
                return

        # Process element...
```

```tsx
// Frontend
<button onClick={() => cancelConversion(file.id)}>
  Cancel Conversion
</button>
```

---

### 4. Conversion Time Estimation

**Use file size to estimate time:**

```python
def estimate_conversion_time(file_size_bytes: int) -> dict:
    """Estimate conversion time based on file size"""
    size_mb = file_size_bytes / (1024 * 1024)

    # Based on benchmark: 75MB = 5-7 minutes
    estimated_minutes = (size_mb / 75) * 6

    return {
        "min_minutes": int(estimated_minutes * 0.8),
        "max_minutes": int(estimated_minutes * 1.2),
        "avg_minutes": int(estimated_minutes)
    }
```

```tsx
// Show estimate on upload
{file.status === 'converting' && (
  <p className="estimate">
    Estimated time: {estimate.min_minutes}-{estimate.max_minutes} minutes
  </p>
)}
```

---

### 5. Batch Upload

**Upload multiple files at once:**

```tsx
<input
  type="file"
  multiple  // Allow multiple file selection
  accept=".scd,.icd,.cid"
/>

// Show queue
<div className="upload-queue">
  {files.map(f => (
    <div key={f.name}>
      {f.name} - {f.status} - {f.progress}%
    </div>
  ))}
</div>
```

---

### 6. Resume on Restart

**If backend restarts during conversion, resume:**

```python
# On startup, check for stuck files
@app.on_event("startup")
async def resume_conversions():
    with SessionLocal() as db:
        stuck_files = db.query(SCLFile).filter(
            SCLFile.status.in_(['uploaded', 'converting'])
        ).all()

        for scl_file in stuck_files:
            # Restart conversion
            background_tasks.add_task(process_scl_file, scl_file.id, ...)
```

---

### 7. Conversion Statistics Dashboard

**Admin page showing:**
- Total files converted
- Average conversion time by file size
- Success rate
- Most common errors
- Largest file converted
- Total RDF triples generated

---

## 🎨 UI/UX Improvements

### 1. Progress Bar Styles

```css
.progress-container {
  margin: 1rem 0;
  padding: 1rem;
  background: #f5f5f5;
  border-radius: 8px;
}

.progress-bar {
  height: 8px;
  background: #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #4CAF50, #81C784);
  transition: width 0.3s ease;
  animation: progress-shimmer 2s infinite;
}

@keyframes progress-shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

.progress-details {
  display: flex;
  justify-content: space-between;
  margin-top: 0.5rem;
  font-size: 0.875rem;
}

.progress-message {
  margin-top: 0.25rem;
  font-size: 0.75rem;
  color: #666;
}
```

### 2. Animated Status Badges

```tsx
<span className={`status-badge ${file.status}`}>
  {file.status === 'converting' && <Spinner />}
  {file.status}
</span>
```

---

## 📦 Infrastructure

### 1. Add Redis to Docker Compose

```yaml
redis:
  image: redis:7-alpine
  container_name: template_redis
  ports:
    - "6379:6379"
  volumes:
    - redis_data:/data
```

### 2. Background Task Queue (Celery)

Instead of FastAPI BackgroundTasks, use Celery for better control:

```python
# celery_app.py
from celery import Celery

celery_app = Celery(
    'tasks',
    broker='redis://redis:6379/0',
    backend='redis://redis:6379/0'
)

@celery_app.task(bind=True)
def process_scl_file_task(self, file_id, scl_path):
    # Update progress
    self.update_state(
        state='PROGRESS',
        meta={'stage': 'parsing', 'progress': 10}
    )

    # ... conversion logic ...
```

Benefits:
- Task retries on failure
- Task cancellation
- Progress tracking built-in
- Distributed workers for parallel processing

---

## 🔧 Technical Debt

1. **Fix bcrypt warning**
   ```
   WARNING:passlib.handlers.bcrypt:(trapped) error reading bcrypt version
   AttributeError: module 'bcrypt' has no attribute '__about__'
   ```
   Solution: Update passlib or use different hasher

2. **Fix Fuseki dataset creation**
   ```
   ✗ Error creating dataset: Expecting value: line 1 column 1 (char 0)
   ```
   Solution: Check Fuseki API endpoint format

3. **Add proper logging configuration**
   - Structured logging (JSON)
   - Log levels per module
   - Rotation and retention

---

## 📝 Documentation

1. Add troubleshooting guide for stuck conversions
2. Document performance benchmarks
3. Add examples of SPARQL queries for common use cases
4. Create video tutorial for SCL upload workflow

---

## 🧪 Testing

1. Unit tests for converter
2. Integration tests for upload workflow
3. Load testing for large files (100MB+)
4. Concurrent upload testing

---

## Recommended Implementation Order

1. **Phase 1** (High Impact, Low Effort)
   - Extended status field (conversion_stage, progress_percent)
   - Polling-based progress display
   - Time estimation
   - Better error messages

2. **Phase 2** (High Impact, Medium Effort)
   - WebSocket or SSE for real-time updates
   - Progress bar with animations
   - Conversion cancellation

3. **Phase 3** (Nice to Have)
   - Redis + Celery for robust task management
   - Batch upload
   - Statistics dashboard
   - Resume on restart

---

**Priority for next sprint:** Implement Phase 1 (extended status + progress display)
