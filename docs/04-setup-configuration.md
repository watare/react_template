# Chapitre 4 : Setup & Configuration

## Project Structure
```
mooc/
├── src/
│   ├── main.tsx         # Entry point (renders App)
│   ├── App.tsx          # Main React component
│   └── index.css        # Global styles
├── index.html           # HTML shell
├── package.json         # Dependencies & scripts
├── tsconfig.json        # TypeScript rules
├── vite.config.ts       # Vite configuration
└── BOOK.md              # This handbook
```

## Essential Configuration Files

### 1. vite.config.ts - Vite's Brain
**Purpose:** Tells Vite how to build and serve your app

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],    // Enable React JSX transformation
  server: {
    port: 3000,          // Dev server runs on localhost:3000
  },
})
```

**What `plugins: [react()]` does:**
- Transforms JSX → JavaScript
- Enables Fast Refresh (hot reload without losing component state)

**Common additions:**
```typescript
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    open: true,              // Auto-open browser
  },
  build: {
    outDir: 'dist',          // Production build output
    sourcemap: true,         // Enable debugging in production
  },
  resolve: {
    alias: {
      '@': '/src',           // Use @/components instead of ../../../components
    }
  }
})
```

### 2. index.html - The Entry Point
**Purpose:** HTML shell where React mounts

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>React Learning App</title>
  </head>
  <body>
    <div id="root"></div>                    <!-- React mounts here -->
    <script type="module" src="/src/main.tsx"></script>  <!-- Entry point -->
  </body>
</html>
```

**How it works:**
1. Browser loads `index.html`
2. Sees `<script src="/src/main.tsx">`
3. Vite intercepts, transforms TypeScript → JavaScript
4. JavaScript runs, renders React into `<div id="root">`

**Why `type="module"`?**
- Enables modern JavaScript imports/exports
- Vite uses native ES modules (faster than traditional bundlers)

### 3. tsconfig.json - TypeScript Compiler Rules
**Purpose:** Controls how TypeScript checks and compiles code

```json
{
  "compilerOptions": {
    // Output Settings
    "target": "ES2020",              // Compile to ES2020 JavaScript
    "module": "ESNext",              // Use modern import/export syntax
    "jsx": "react-jsx",              // Transform JSX (React 18+ auto-import)

    // Type Checking
    "strict": true,                  // Enable all strict type checks
    "lib": ["ES2020", "DOM"],        // Include browser & modern JS types

    // Vite Integration
    "noEmit": true,                  // Don't output .js files (Vite handles it)
    "isolatedModules": true,         // Each file compiles independently

    // Code Quality
    "noUnusedLocals": true,          // Error on unused variables
    "noUnusedParameters": true       // Error on unused function params
  },
  "include": ["src"]                 // Only check files in src/
}
```

**Key settings explained:**

- `"jsx": "react-jsx"` - New React 18 transform (no need to `import React`)
- `"noEmit": true"` - TypeScript only checks types, Vite compiles
- `"strict": true"` - Catches type errors early (recommended for learning)

### 4. package.json - Project Metadata & Dependencies
**Purpose:** Defines scripts, dependencies, and project info

```json
{
  "name": "mooc",
  "private": true,          // Don't publish to npm
  "version": "0.0.1",
  "type": "module",         // Use ES modules (import/export)

  "scripts": {
    "dev": "vite",                    // Start dev server
    "build": "tsc && vite build",     // Type-check, then build
    "preview": "vite preview"         // Test production build locally
  },

  "dependencies": {
    "react": "^18.2.0",              // React library
    "react-dom": "^18.2.0",          // React → DOM renderer
    "react-router-dom": "^6.22.0"    // Client-side routing
  },

  "devDependencies": {
    "@types/react": "^18.2.66",          // TypeScript types for React
    "@types/react-dom": "^18.2.22",      // TypeScript types for ReactDOM
    "@vitejs/plugin-react": "^4.2.1",    // Vite React plugin
    "typescript": "^5.2.2",              // TypeScript compiler
    "vite": "^5.2.0"                     // Vite build tool
  }
}
```

**Scripts explained:**
- `npm run dev` → Start development server (localhost:3000)
- `npm run build` → Type-check with `tsc`, then create production bundle in `dist/`
- `npm run preview` → Test production build locally before deployment

**Version syntax (`^18.2.0`):**
- `^` = Accept minor/patch updates (18.2.x → 18.3.0 ✓, 19.0.0 ✗)
- Allows bug fixes without breaking changes

**Dependencies vs DevDependencies:**
- **dependencies**: Needed at runtime (included in final bundle)
- **devDependencies**: Only for development (TypeScript, types, build tools)

## How Configuration Files Work Together

```
npm run dev
    ↓
1. package.json: Run "vite" script
    ↓
2. vite.config.ts: Load config (port 3000, React plugin)
    ↓
3. index.html: Serve HTML, load /src/main.tsx
    ↓
4. tsconfig.json: Apply TypeScript rules while transforming
    ↓
5. Browser opens localhost:3000 with React app
```

## Vite Use Cases

### Adding New Components
**Impact:** Zero configuration needed

Create `src/components/Button.tsx`:
```tsx
export function Button({ label }: { label: string }) {
  return <button>{label}</button>;
}
```

Import and use:
```tsx
import { Button } from './components/Button';  // Vite handles automatically
```

**What Vite does:**
- ✓ Detects new `.tsx` file
- ✓ Transforms TypeScript → JavaScript
- ✓ Hot Module Replacement (instant update in browser)
- ✗ No config changes needed

### Adding a Database/Backend
**Important:** Vite is frontend-only (runs in browser)

**Architecture:**
```
┌─────────────────┐         ┌──────────────────┐
│  Vite (Frontend)│  HTTP   │  Backend Server  │
│  localhost:3000 │ ◄─────► │  localhost:8000  │  ◄──► Database
│  React/TS       │         │  FastAPI/Python  │
└─────────────────┘         └──────────────────┘
```

**To connect frontend to backend, add API proxy:**

```typescript
// vite.config.ts
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',  // Backend server
        changeOrigin: true,
      }
    }
  },
})
```

**Why proxy?**
- Browser requests `/api/users`
- Vite forwards to `http://localhost:8000/api/users`
- Avoids CORS (Cross-Origin Resource Sharing) issues

**What Vite does/doesn't do:**
- ✓ Proxy API requests to backend
- ✗ Does NOT run database
- ✗ Does NOT run backend server

**Separate services needed:**
- Backend: FastAPI server (Python)
- Database: PostgreSQL/Fuseki (Docker containers)
- Orchestration: Docker Compose

## Prerequisites
```bash
# Node.js (includes npm)
node --version  # v18+ recommended

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

---
