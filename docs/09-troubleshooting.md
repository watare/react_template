# Troubleshooting

*Common issues and solutions*

---

## React Common Issues

### Issue: "Hooks can only be called inside function components"

**Cause:** Calling hooks in wrong context

```tsx
// ❌ WRONG
function MyComponent() {
  if (condition) {
    const [state, setState] = useState(0)  // Conditional hook call
  }
}

// ✅ CORRECT
function MyComponent() {
  const [state, setState] = useState(0)
  if (condition) {
    setState(5)
  }
}
```

---

### Issue: State not updating immediately

**Cause:** State updates are asynchronous

```tsx
// ❌ WRONG
function Counter() {
  const [count, setCount] = useState(0)

  const handleClick = () => {
    setCount(count + 1)
    console.log(count)  // Still shows old value!
  }
}

// ✅ CORRECT
function Counter() {
  const [count, setCount] = useState(0)

  const handleClick = () => {
    setCount(count + 1)
    // Use useEffect to react to state changes
  }

  useEffect(() => {
    console.log(count)  // Now shows updated value
  }, [count])
}
```

---

### Issue: Infinite re-render loop

**Cause:** Setting state directly in render

```tsx
// ❌ WRONG
function MyComponent() {
  const [count, setCount] = useState(0)
  setCount(count + 1)  // Causes infinite loop!
  return <div>{count}</div>
}

// ✅ CORRECT
function MyComponent() {
  const [count, setCount] = useState(0)

  useEffect(() => {
    setCount(count + 1)
  }, [])  // Empty dependency array = runs once

  return <div>{count}</div>
}
```

---

## TypeScript Issues

### Issue: "Object is possibly 'null'"

**Solution:** Use optional chaining or null checks

```tsx
// ❌ ERROR
const userName = user.name  // user might be null

// ✅ CORRECT - Optional chaining
const userName = user?.name

// ✅ CORRECT - Null check
const userName = user ? user.name : 'Guest'
```

---

## Vite Issues

### Issue: "Failed to resolve import"

**Cause:** Missing dependency or wrong import path

**Solution:**
```bash
# Install missing dependency
npm install <package-name>

# Check import path (relative paths need ./ or ../)
import { Component } from './Component'  # ✅
import { Component } from 'Component'    # ❌
```

---

### Issue: Environment variables not working

**Cause:** Wrong naming or not prefixed with VITE_

**Solution:**
```bash
# .env file
VITE_API_URL=http://localhost:8000  # ✅ Starts with VITE_
API_URL=http://localhost:8000       # ❌ Wrong, won't work

# Access in code
const apiUrl = import.meta.env.VITE_API_URL
```

---

## Database Issues

### Issue: "relation does not exist"

**Cause:** Migrations not applied

**Solution:**
```bash
# Apply pending migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "Description"
```

---

### Issue: "Database connection failed"

**Check:**
1. PostgreSQL is running
2. Credentials are correct
3. Database exists
4. Network connection

```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Test connection
psql -U username -d database_name
```

---

## API Issues

### Issue: CORS errors in browser

**Cause:** Backend not configured for CORS

**Solution:**
```python
# FastAPI - add CORS middleware
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### Issue: 401 Unauthorized on protected routes

**Check:**
1. Token is being sent in headers
2. Token format is correct (`Bearer <token>`)
3. Token hasn't expired
4. Token signature is valid

```tsx
// React - check token in localStorage
const token = localStorage.getItem('token')
console.log('Token:', token)

// Backend - verify token
from jose import jwt
payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
```

---

## Performance Issues

### Issue: Slow component renders

**Solutions:**

**1. Use React DevTools Profiler**
```bash
# Install React DevTools browser extension
# Record component renders
# Identify slow components
```

**2. Memoize expensive calculations**
```tsx
import { useMemo } from 'react'

function MyComponent({ data }) {
  const expensiveValue = useMemo(() => {
    return data.reduce((acc, item) => acc + item.value, 0)
  }, [data])  // Only recalculate when data changes
}
```

**3. Prevent unnecessary re-renders**
```tsx
import { memo } from 'react'

const ExpensiveComponent = memo(function ExpensiveComponent({ data }) {
  // Only re-renders when data prop changes
  return <div>{data}</div>
})
```

---

## Debugging Tips

### 1. Use Browser DevTools

**Console:**
```tsx
console.log('State:', state)
console.table(users)  // Pretty table format
console.error('Error:', error)
```

**React DevTools:**
- Inspect component props
- View state and hooks
- Profile performance

---

### 2. Add Error Boundaries

```tsx
import { Component, ErrorInfo, ReactNode } from 'react'

class ErrorBoundary extends Component<
  { children: ReactNode },
  { hasError: boolean }
> {
  constructor(props) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Error caught:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return <h1>Something went wrong.</h1>
    }

    return this.props.children
  }
}

// Usage
<ErrorBoundary>
  <App />
</ErrorBoundary>
```

---

### 3. Use Strict Mode

```tsx
import { StrictMode } from 'react'

<StrictMode>
  <App />
</StrictMode>
```

**Benefits:**
- Identifies unsafe lifecycles
- Warns about deprecated APIs
- Detects unexpected side effects

---

## Getting Help

**Resources:**
- [React Docs](https://react.dev)
- [FastAPI Docs](https://fastapi.tiangolo.com)
- [Stack Overflow](https://stackoverflow.com)
- [Discord Communities](https://discord.gg/reactiflux)

**When asking for help:**
1. Describe what you expected to happen
2. Describe what actually happened
3. Include error messages
4. Share relevant code snippets
5. Mention what you've already tried

---

## To be continued...

*This section will be updated with more common issues as we encounter them*
