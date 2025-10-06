# Chapitre 5 : Code Patterns

## Component Nesting in React

**Understanding Component Hierarchy**

React applications are built by nesting components. Here's how to visualize the component tree in our application:

### File Structure
```
src/
├── main.tsx              # Entry point (renders <App />)
├── App.tsx               # Root component
├── types.ts              # TypeScript definitions
├── index.css             # Global styles
│
└── components/
    ├── Login.tsx         # Login component
    ├── Login.css         # Login styles
    ├── Dashboard.tsx     # Dashboard component
    └── Dashboard.css     # Dashboard styles
```

### Component Nesting in Code

**Level 1: Entry Point (`src/main.tsx`)**
```tsx
ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />                    ← App component rendered here
  </React.StrictMode>,
)
```

**Level 2: Root Component (`src/App.tsx`)**
```tsx
function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [currentUser, setCurrentUser] = useState('')

  return (
    <>
      {isLoggedIn ? (
        <Dashboard username={currentUser} onLogout={handleLogout} />  ← Dashboard here
      ) : (
        <Login onLogin={handleLogin} />                                ← Login here
      )}
    </>
  )
}
```

**Level 3: Child Components (Login & Dashboard)**
- `Login.tsx` - No child components (leaf node)
- `Dashboard.tsx` - No child components (leaf node)

### Visual Component Tree

```
index.html (#root)
  │
  └─ main.tsx
      └─ <React.StrictMode>
          └─ <App />
              │
              ├─ State: isLoggedIn, currentUser
              │
              └─ Conditional Render:
                  │
                  ├─ if !isLoggedIn → <Login onLogin={fn} />
                  │                     └─ State: username, password, error
                  │
                  └─ if isLoggedIn → <Dashboard username={str} onLogout={fn} />
                                      └─ Displays mock data
```

### Data Flow (Props & Callbacks)

**Parent → Child (Props):**
- `App` passes `onLogin` function to `Login`
- `App` passes `username` and `onLogout` to `Dashboard`

**Child → Parent (Callbacks):**
- `Login` calls `onLogin(username)` when user logs in → updates `App` state
- `Dashboard` calls `onLogout()` when user logs out → updates `App` state

**State Lifting:**
- `isLoggedIn` and `currentUser` are stored in `App` (parent)
- Child components don't manage authentication state
- This allows App to control which component is displayed

### How to Find Component Nesting

1. **Start at the entry point:** `src/main.tsx`
2. **Look for JSX in return statements:** Components are rendered using `<ComponentName />`
3. **Follow the imports:** See which components are imported at the top
4. **Trace the data flow:** Props down, events up

**Example - Finding nesting in App.tsx:**
```tsx
// Imports tell us which components are used
import Login from './components/Login'      ← Login is nested
import Dashboard from './components/Dashboard'  ← Dashboard is nested

// Return statement shows actual nesting
return (
  <>
    {isLoggedIn ? (
      <Dashboard ... />   ← Dashboard rendered conditionally
    ) : (
      <Login ... />       ← Login rendered conditionally
    )}
  </>
)
```

---
