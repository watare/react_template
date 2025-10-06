# Chapitre 3 : Vite Build Tool

## What is Vite?

A **frontend build tool** that solves the browser compatibility problem:

**Problems browsers have:**
- Can't understand TypeScript → needs compilation to JavaScript
- Can't understand JSX/TSX → needs transformation
- Can't resolve npm package imports → needs bundling
- May not support latest JavaScript → needs transpilation

**Vite provides:**
1. **Development Server** - Runs app locally with instant hot reload
2. **Module Bundler** - Packages code for production
3. **Transpiler** - Converts TypeScript/JSX to JavaScript

## How Vite Works

**Development Mode (`npm run dev`):**
```
Your code (TSX) → Vite transforms on-the-fly → Browser
```
- Instant server startup (no bundling upfront)
- Hot Module Replacement (HMR) - changes appear without full reload
- Only transforms files currently being viewed (lazy loading)

**Production Mode (`npm run build`):**
```
Your code → Vite bundles & optimizes → dist/ folder (deployable)
```
- Minification (removes whitespace, shortens names)
- Tree-shaking (removes unused code)
- Code splitting (breaks into smaller chunks)

## Vite vs Alternatives

| Tool | Speed | Complexity | Status |
|------|-------|------------|--------|
| **Vite** | ⚡ Very fast | Simple | Active |
| Create React App | Slower | Simple | Deprecated |
| Webpack | Slow | Complex | Active |
| Parcel | Fast | Very simple | Active |

**Why Vite is Fast:**

Traditional bundlers (Webpack/CRA):
```
[Bundle ALL files] → [Wait] → [Start server] → [Slow reload]
```

Vite:
```
[Start server instantly] → [Transform only what's needed] → [Native ES modules]
```

---
