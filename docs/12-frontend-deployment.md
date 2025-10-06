# Guide de Déploiement Complet : Phase 5 - Frontend React

---

## Phase 5 : Frontend React avec TypeScript et Vite

### Étape 5.1 : Configuration Initiale Node.js

**Actions :**

1. Vérifier Node.js :
```bash
node --version  # Doit être >= 18
npm --version   # Doit être >= 9
```

2. Créer `frontend/package.json` :
```json
{
  "name": "mooc-frontend",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.21.1",
    "@tanstack/react-query": "^5.17.9",
    "lucide-react": "^0.303.0",
    "clsx": "^2.1.0",
    "tailwind-merge": "^2.2.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.48",
    "@types/react-dom": "^18.2.18",
    "@vitejs/plugin-react-swc": "^3.5.0",
    "typescript": "^5.3.3",
    "vite": "^5.0.11",
    "tailwindcss": "^3.4.1",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.33",
    "eslint": "^8.56.0",
    "@typescript-eslint/eslint-plugin": "^6.19.0",
    "@typescript-eslint/parser": "^6.19.0",
    "eslint-plugin-react-hooks": "^4.6.0",
    "eslint-plugin-react-refresh": "^0.4.5"
  }
}
```

**Points mis à jour 2025 :**
- React 18.2 (stable)
- React Query v5 (dernière version majeure)
- Vite 5.0
- TypeScript 5.3
- Tailwind 3.4

3. Installer les dépendances :
```bash
cd frontend
npm install
```

**Points d'attention :**
- L'installation prend 2-3 minutes
- Peut afficher des warnings npm (normal si pas de vulnérabilités critiques)

**Test de validation :**
```bash
# Vérifier que node_modules existe
ls node_modules | wc -l
# Doit afficher > 500

# Vérifier les versions installées
npm list react react-dom vite typescript
```

**Checkpoint 12 :** ✅ Dépendances Node.js installées

---

### Étape 5.2 : Configuration TypeScript

**Actions :**

1. Créer `frontend/tsconfig.json` :
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,

    /* Bundler mode */
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",

    /* Linting */
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,

    /* Path mapping */
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

2. Créer `frontend/tsconfig.node.json` :
```json
{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true
  },
  "include": ["vite.config.ts"]
}
```

**Test de validation :**
```bash
# Vérifier la configuration TypeScript
npx tsc --noEmit
# Ne doit afficher AUCUNE erreur (peut être vide si pas encore de fichiers .ts)
```

**Checkpoint 12b :** ✅ TypeScript configuré

---

### Étape 5.3 : Configuration Vite et Tailwind

**Actions :**

1. Créer `frontend/vite.config.ts` :
```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/auth': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
```

2. Créer `frontend/tailwind.config.js` :
```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        border: "hsl(var(--border))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
    },
  },
  plugins: [],
}
```

3. Créer `frontend/postcss.config.js` :
```javascript
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
```

4. Créer `frontend/.env` :
```bash
VITE_API_URL=http://localhost:8000
```

**Checkpoint 12c :** ✅ Vite et Tailwind configurés

---

### Étape 5.4 : Structure CSS et Variables

**Actions :**

1. Créer `frontend/src/index.css` :
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
    --card: 0 0% 100%;
    --card-foreground: 222.2 84% 4.9%;
    --popover: 0 0% 100%;
    --popover-foreground: 222.2 84% 4.9%;
    --primary: 221.2 83.2% 53.3%;
    --primary-foreground: 210 40% 98%;
    --secondary: 210 40% 96.1%;
    --secondary-foreground: 222.2 47.4% 11.2%;
    --muted: 210 40% 96.1%;
    --muted-foreground: 215.4 16.3% 46.9%;
    --accent: 210 40% 96.1%;
    --accent-foreground: 222.2 47.4% 11.2%;
    --destructive: 0 84.2% 60.2%;
    --destructive-foreground: 210 40% 98%;
    --border: 214.3 31.8% 91.4%;
    --input: 214.3 31.8% 91.4%;
    --ring: 221.2 83.2% 53.3%;
    --radius: 0.5rem;
  }
}

@layer base {
  * {
    @apply border-border;
  }
  body {
    @apply bg-background text-foreground;
  }
}
```

**Checkpoint 12d :** ✅ CSS configuré avec variables

---

### Étape 5.5 : Système d'Authentification React

**Actions :**

1. Créer `frontend/src/auth/SessionProvider.tsx` :
```typescript
import { createContext, useState, useEffect, ReactNode } from 'react'

type Session = {
  sub: string
  email: string
  full_name: string | null
  roles: string[]
  perms: string[]
}

type SessionContextType = {
  session: Session | null
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => void
}

export const SessionContext = createContext<SessionContextType | null>(null)

export function SessionProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<Session | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (token) {
      fetchMe(token)
    } else {
      setLoading(false)
    }
  }, [])

  const fetchMe = async (token: string) => {
    try {
      const response = await fetch('/auth/me', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        setSession(data)
      } else {
        localStorage.removeItem('token')
      }
    } catch (error) {
      console.error('Erreur chargement session:', error)
      localStorage.removeItem('token')
    } finally {
      setLoading(false)
    }
  }

  const login = async (email: string, password: string) => {
    const response = await fetch('/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Erreur de connexion')
    }

    const data = await response.json()
    localStorage.setItem('token', data.access_token)
    await fetchMe(data.access_token)
  }

  const logout = () => {
    localStorage.removeItem('token')
    setSession(null)
    window.location.href = '/login'
  }

  return (
    <SessionContext.Provider value={{ session, loading, login, logout }}>
      {children}
    </SessionContext.Provider>
  )
}
```

2. Créer `frontend/src/auth/useSession.ts` :
```typescript
import { useContext } from 'react'
import { SessionContext } from './SessionProvider'

export function useSession() {
  const context = useContext(SessionContext)
  if (!context) {
    throw new Error('useSession must be used within SessionProvider')
  }
  return context
}
```

3. Créer `frontend/src/auth/useCan.ts` :
```typescript
import { useMemo } from 'react'
import { useSession } from './useSession'

export function useCan() {
  const { session } = useSession()

  const permSet = useMemo(() => {
    return new Set(session?.perms || [])
  }, [session?.perms])

  return {
    has: (code: string) => permSet.has(code),
    any: (codes: string[]) => codes.some(c => permSet.has(c)),
    all: (codes: string[]) => codes.every(c => permSet.has(c))
  }
}
```

4. Créer `frontend/src/auth/Guard.tsx` :
```typescript
import { ReactNode } from 'react'
import { useCan } from './useCan'

type GuardProps = {
  need: string
  children: ReactNode
  fallback?: ReactNode
}

export function Guard({ need, children, fallback = null }: GuardProps) {
  const { has } = useCan()

  if (!has(need)) {
    return <>{fallback}</>
  }

  return <>{children}</>
}
```

5. Créer `frontend/src/auth/GuardRoute.tsx` :
```typescript
import { ReactNode } from 'react'
import { Navigate } from 'react-router-dom'
import { useCan } from './useCan'

type GuardRouteProps = {
  need: string
  children: ReactNode
  redirect?: string
}

export function GuardRoute({ need, children, redirect = '/403' }: GuardRouteProps) {
  const { has } = useCan()

  if (!has(need)) {
    return <Navigate to={redirect} replace />
  }

  return <>{children}</>
}
```

6. Créer `frontend/src/auth/IfCan.tsx` :
```typescript
import { ReactNode } from 'react'
import { useCan } from './useCan'

type IfCanProps = {
  need: string
  children: ReactNode
}

export function IfCan({ need, children }: IfCanProps) {
  const { has } = useCan()
  return has(need) ? <>{children}</> : null
}
```

**Checkpoint 13 :** ✅ Système d'authentification React créé

---

### Étape 5.6 : Composants UI de Base

**Actions :**

1. Créer `frontend/src/components/ui/Button.tsx` :
```typescript
import { ButtonHTMLAttributes, forwardRef } from 'react'
import { clsx } from 'clsx'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'destructive' | 'outline' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'md', ...props }, ref) => {
    return (
      <button
        ref={ref}
        className={clsx(
          'inline-flex items-center justify-center rounded-md font-medium transition-colors',
          'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring',
          'disabled:pointer-events-none disabled:opacity-50',
          {
            'bg-primary text-primary-foreground hover:bg-primary/90': variant === 'primary',
            'bg-secondary text-secondary-foreground hover:bg-secondary/80': variant === 'secondary',
            'bg-destructive text-destructive-foreground hover:bg-destructive/90': variant === 'destructive',
            'border border-input bg-background hover:bg-accent hover:text-accent-foreground': variant === 'outline',
            'hover:bg-accent hover:text-accent-foreground': variant === 'ghost',
          },
          {
            'h-9 px-3 text-sm': size === 'sm',
            'h-10 px-4': size === 'md',
            'h-11 px-8 text-lg': size === 'lg',
          },
          className
        )}
        {...props}
      />
    )
  }
)

Button.displayName = 'Button'
```

2. Créer `frontend/src/components/ui/Card.tsx` :
```typescript
import { HTMLAttributes, forwardRef } from 'react'
import { clsx } from 'clsx'

export const Card = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      className={clsx('rounded-lg border bg-card text-card-foreground shadow-sm', className)}
      {...props}
    />
  )
)

export const CardHeader = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={clsx('flex flex-col space-y-1.5 p-6', className)} {...props} />
  )
)

export const CardTitle = forwardRef<HTMLHeadingElement, HTMLAttributes<HTMLHeadingElement>>(
  ({ className, ...props }, ref) => (
    <h3 ref={ref} className={clsx('text-2xl font-semibold leading-none tracking-tight', className)} {...props} />
  )
)

export const CardDescription = forwardRef<HTMLParagraphElement, HTMLAttributes<HTMLParagraphElement>>(
  ({ className, ...props }, ref) => (
    <p ref={ref} className={clsx('text-sm text-muted-foreground', className)} {...props} />
  )
)

export const CardContent = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={clsx('p-6 pt-0', className)} {...props} />
  )
)

Card.displayName = 'Card'
CardHeader.displayName = 'CardHeader'
CardTitle.displayName = 'CardTitle'
CardDescription.displayName = 'CardDescription'
CardContent.displayName = 'CardContent'
```

3. Créer `frontend/src/components/ui/Input.tsx` :
```typescript
import { InputHTMLAttributes, forwardRef } from 'react'
import { clsx } from 'clsx'

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, ...props }, ref) => {
    return (
      <input
        type={type}
        className={clsx(
          'flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm',
          'ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium',
          'placeholder:text-muted-foreground',
          'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2',
          'disabled:cursor-not-allowed disabled:opacity-50',
          className
        )}
        ref={ref}
        {...props}
      />
    )
  }
)

Input.displayName = 'Input'
```

**Checkpoint 13b :** ✅ Composants UI de base créés

---

### Étape 5.7 : Layout et Navigation

**Actions :**

1. Créer `frontend/src/components/Navbar.tsx` :
```typescript
import { useSession } from '@/auth/useSession'
import { Button } from '@/components/ui/Button'
import { LogOut, User } from 'lucide-react'

export function Navbar() {
  const { session, logout } = useSession()

  return (
    <nav className="border-b bg-background">
      <div className="container mx-auto px-4 h-16 flex items-center justify-between">
        <div className="flex items-center space-x-8">
          <h1 className="text-xl font-bold">MOOC Learning App</h1>
          <div className="hidden md:flex space-x-4">
            <a href="/dashboard" className="text-sm hover:text-primary">
              Dashboard
            </a>
          </div>
        </div>

        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <User className="h-4 w-4" />
            <span className="text-sm">{session?.email}</span>
          </div>
          <Button variant="ghost" size="sm" onClick={logout}>
            <LogOut className="h-4 w-4 mr-2" />
            Déconnexion
          </Button>
        </div>
      </div>
    </nav>
  )
}
```

2. Créer `frontend/src/components/Layout.tsx` :
```typescript
import { Outlet } from 'react-router-dom'
import { useSession } from '@/auth/useSession'
import { Navbar } from './Navbar'

export function Layout() {
  const { loading } = useSession()

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-muted-foreground">Chargement...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <main className="container mx-auto px-4 py-8">
        <Outlet />
      </main>
    </div>
  )
}
```

**Checkpoint 13c :** ✅ Layout et navigation créés

---

### Étape 5.8 : Pages Principales

**Actions :**

1. Créer `frontend/src/features/auth/LoginPage.tsx` :
```typescript
import { useState, FormEvent } from 'react'
import { useSession } from '@/auth/useSession'
import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card'

export function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { login } = useSession()
  const navigate = useNavigate()

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      await login(email, password)
      navigate('/dashboard')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur de connexion')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-1">
          <CardTitle className="text-2xl font-bold text-center">Connexion</CardTitle>
          <CardDescription className="text-center">
            MOOC Learning Application
          </CardDescription>
        </CardHeader>
        <CardContent>
          {error && (
            <div className="mb-4 p-3 rounded-md bg-destructive/10 text-destructive text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <label htmlFor="email" className="text-sm font-medium">
                Email
              </label>
              <Input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="admin@localhost"
                required
                disabled={loading}
              />
            </div>

            <div className="space-y-2">
              <label htmlFor="password" className="text-sm font-medium">
                Mot de passe
              </label>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
                disabled={loading}
              />
            </div>

            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? 'Connexion...' : 'Se connecter'}
            </Button>
          </form>

          <div className="mt-6 p-4 rounded-md bg-muted">
            <p className="text-sm font-medium mb-2">Comptes de test :</p>
            <ul className="text-sm space-y-1 text-muted-foreground">
              <li>admin@localhost / admin123</li>
              <li>engineer@localhost / engineer123</li>
              <li>viewer@localhost / viewer123</li>
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
```

2. Créer `frontend/src/features/dashboard/DashboardPage.tsx` :
```typescript
import { useSession } from '@/auth/useSession'
import { Guard } from '@/auth/Guard'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card'
import { Shield, User } from 'lucide-react'

export function DashboardPage() {
  const { session } = useSession()

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Tableau de bord</h1>
        <p className="text-muted-foreground mt-2">
          Bienvenue, {session?.full_name || session?.email}
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <Guard need="admin:access">
          <Card className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <Shield className="h-8 w-8 text-purple-600 mb-2" />
              <CardTitle>Administration</CardTitle>
              <CardDescription>
                Gestion des utilisateurs et rôles
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Panneau administrateur (à implémenter)
              </p>
            </CardContent>
          </Card>
        </Guard>

        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader>
            <User className="h-8 w-8 text-green-600 mb-2" />
            <CardTitle>Profil</CardTitle>
            <CardDescription>
              Paramètres du compte
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-sm space-y-1">
              <p><span className="font-medium">Email:</span> {session?.email}</p>
              <p><span className="font-medium">Rôles:</span> {session?.roles.join(', ')}</p>
              <p><span className="font-medium">Permissions:</span> {session?.perms.length}</p>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Vos permissions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            {session?.perms.map(perm => (
              <span
                key={perm}
                className="px-3 py-1 rounded-full bg-primary/10 text-primary text-sm"
              >
                {perm}
              </span>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
```

3. Créer `frontend/src/features/errors/NotFoundPage.tsx` :
```typescript
import { Button } from '@/components/ui/Button'
import { useNavigate } from 'react-router-dom'

export function NotFoundPage() {
  const navigate = useNavigate()

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-6xl font-bold text-primary">404</h1>
        <p className="text-xl text-muted-foreground mt-4">Page non trouvée</p>
        <Button onClick={() => navigate('/dashboard')} className="mt-6">
          Retour au dashboard
        </Button>
      </div>
    </div>
  )
}
```

4. Créer `frontend/src/features/errors/ForbiddenPage.tsx` :
```typescript
import { Button } from '@/components/ui/Button'
import { useNavigate } from 'react-router-dom'
import { ShieldAlert } from 'lucide-react'

export function ForbiddenPage() {
  const navigate = useNavigate()

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <ShieldAlert className="h-24 w-24 text-destructive mx-auto mb-4" />
        <h1 className="text-4xl font-bold">Accès refusé</h1>
        <p className="text-muted-foreground mt-4">
          Vous n'avez pas les permissions nécessaires pour accéder à cette page
        </p>
        <Button onClick={() => navigate('/dashboard')} className="mt-6">
          Retour au dashboard
        </Button>
      </div>
    </div>
  )
}
```

**Checkpoint 13d :** ✅ Pages principales créées

---

### Étape 5.9 : Routing et Application

**Actions :**

1. Créer `frontend/src/app/routes.tsx` :
```typescript
import { createBrowserRouter, Navigate } from 'react-router-dom'
import { Layout } from '@/components/Layout'
import { LoginPage } from '@/features/auth/LoginPage'
import { DashboardPage } from '@/features/dashboard/DashboardPage'
import { NotFoundPage } from '@/features/errors/NotFoundPage'
import { ForbiddenPage } from '@/features/errors/ForbiddenPage'
import { GuardRoute } from '@/auth/GuardRoute'

export const router = createBrowserRouter([
  {
    path: '/login',
    element: <LoginPage />,
  },
  {
    path: '/',
    element: <Layout />,
    children: [
      {
        index: true,
        element: <Navigate to="/dashboard" replace />,
      },
      {
        path: 'dashboard',
        element: (
          <GuardRoute need="dashboard:view">
            <DashboardPage />
          </GuardRoute>
        ),
      },
      {
        path: '403',
        element: <ForbiddenPage />,
      },
      {
        path: '*',
        element: <NotFoundPage />,
      },
    ],
  },
])
```

2. Créer `frontend/src/app/App.tsx` :
```typescript
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { RouterProvider } from 'react-router-dom'
import { SessionProvider } from '@/auth/SessionProvider'
import { router } from './routes'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      retry: 1,
    },
  },
})

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <SessionProvider>
        <RouterProvider router={router} />
      </SessionProvider>
    </QueryClientProvider>
  )
}
```

3. Créer `frontend/src/main.tsx` :
```typescript
import React from 'react'
import ReactDOM from 'react-dom/client'
import { App } from './app/App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
```

4. Créer `frontend/index.html` :
```html
<!doctype html>
<html lang="fr">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>MOOC Learning App</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

**Checkpoint 13e :** ✅ Routing et application configurés

---

### Étape 5.10 : Démarrage et Tests Frontend

**Actions :**

1. Démarrer le serveur de développement :
```bash
cd frontend
npm run dev
```

**Points d'attention :**
- Le serveur doit démarrer sur http://localhost:5173
- Le backend doit être démarré (uvicorn sur port 8000)
- Les deux doivent tourner simultanément

**Tests de validation :**

```bash
# Test 1 : Dev server accessible
curl -I http://localhost:5173
# Doit retourner : HTTP/1.1 200 OK

# Test 2 : Ouvrir dans le navigateur
# Naviguer vers http://localhost:5173
# Doit afficher la page de login
```

**Tests manuels dans le navigateur :**

**Test 1 : Page de login**
- Ouvrir http://localhost:5173
- Doit afficher un formulaire de connexion avec les comptes de test

**Test 2 : Login ADMIN**
- Email : admin@localhost
- Password : admin123
- Cliquer "Se connecter"
- Doit rediriger vers /dashboard
- Doit afficher les cartes (Administration, Profil)

**Test 3 : Permissions affichées**
- Sur le dashboard, vérifier que toutes les permissions sont listées
- ADMIN doit avoir 6 permissions

**Test 4 : Logout**
- Cliquer sur "Déconnexion"
- Doit retourner à /login
- Le token doit être supprimé (vérifier dans DevTools > Application > Local Storage)

**Test 5 : Login ENGINEER**
- Se connecter avec engineer@localhost / engineer123
- Dashboard doit afficher carte Profil
- La carte "Administration" ne doit PAS être visible

**Test 6 : Test d'accès refusé**
- Connecté comme ENGINEER
- Créer un lien vers admin et cliquer (si implémenté)
- Doit rediriger vers /403 (Accès refusé)

**Test 7 : Login VIEWER**
- Se connecter avec viewer@localhost / viewer123
- Dashboard doit afficher carte Profil
- Permissions : dashboard:view uniquement

**Test 8 : Vérifier les appels API (DevTools > Network)**
- Lors du login, doit voir :
  - POST /auth/login (retourne le token)
  - GET /auth/me (retourne les infos utilisateur)
- Les requêtes doivent passer par le proxy Vite

**Test 9 : Refresh de page**
- Connecté, rafraîchir la page (F5)
- Doit rester connecté (session restaurée depuis localStorage)

**Checkpoint 14 :** ✅ Application complète fonctionnelle

**Points d'arrêt critiques :**

- **Si "Failed to fetch" au login :**
  ```bash
  # Vérifier que le backend tourne
  curl http://localhost:8000/health

  # Vérifier le proxy Vite
  cat vite.config.ts | grep proxy
  ```

- **Si redirection infinie :**
  - Vérifier que le token est bien stocké dans localStorage
  - Vérifier que /auth/me retourne bien des données

- **Si permissions ne s'affichent pas :**
  - Ouvrir DevTools Console pour voir les erreurs
  - Vérifier la réponse de /auth/me dans Network

- **Si composants ne s'affichent pas :**
  - Vérifier les erreurs TypeScript : `npm run build`
  - Vérifier les erreurs dans la console du navigateur

---

## Phase 6 : Tests Finaux et Documentation

### Étape 6.1 : Tests d'Intégration Complets

**Scénario complet à tester :**

1. **Démarrage des services**
```bash
# Terminal 1 : Bases de données
docker compose up -d
docker compose ps  # Vérifier que tout est "running"

# Terminal 2 : Backend
cd backend
source venv/bin/activate  # ou venv\Scripts\activate sur Windows
uvicorn main:app --reload

# Terminal 3 : Frontend
cd frontend
npm run dev
```

2. **Test du flux utilisateur ADMIN**
- Login admin@localhost / admin123
- Voir toutes les cartes
- Logout

3. **Test du flux utilisateur ENGINEER**
- Login engineer@localhost / engineer123
- Voir carte Profil uniquement
- Logout

4. **Test du flux utilisateur VIEWER**
- Login viewer@localhost / viewer123
- Voir cartes limitées
- Permissions limitées à lecture

**Checkpoint 15 :** ✅ Tous les flux utilisateurs testés

---

### Étape 6.2 : Mise à Jour BOOK.md

**Actions :**

Ajouter une nouvelle entrée dans `BOOK.md` :

```markdown
- **[12. Frontend Deployment](./docs/12-frontend-deployment.md)**
  - React + TypeScript + Vite Setup
  - Authentication System
  - RBAC Guards & Routes
  - UI Components (Tailwind)
  - Integration Testing
```

---

## Checklist Finale de Validation

### Backend
- [ ] PostgreSQL démarré et accessible
- [ ] Fuseki démarré et accessible
- [ ] 6 tables créées (users, roles, permissions, user_roles, role_permissions, audit_logs)
- [ ] 3 utilisateurs seedés
- [ ] 3 rôles créés
- [ ] 6 permissions créées
- [ ] API démarre sans erreur (uvicorn)
- [ ] /health retourne 200
- [ ] /auth/login fonctionne pour les 3 users
- [ ] /auth/me retourne les bonnes permissions
- [ ] JWT créé et validé correctement
- [ ] Mots de passe hashés en base

### Frontend
- [ ] npm install sans erreur
- [ ] npm run dev démarre sur port 5173
- [ ] Page login s'affiche correctement
- [ ] Login ADMIN fonctionne
- [ ] Login ENGINEER fonctionne
- [ ] Login VIEWER fonctionne
- [ ] Dashboard affiche les bonnes cartes selon rôle
- [ ] Guards masquent les éléments non autorisés
- [ ] Redirection 403 fonctionne
- [ ] Logout supprime le token
- [ ] Refresh page restaure la session
- [ ] Pas d'erreurs dans Console DevTools

### Sécurité
- [ ] .env dans .gitignore
- [ ] Pas de credentials dans le code
- [ ] Token JWT signé
- [ ] Routes backend protégées
- [ ] CORS configuré correctement

---

## Commandes de Démarrage Rapide Récapitulatives

```bash
# 1. Bases de données
docker compose up -d

# 2. Backend (terminal séparé)
cd backend
source venv/bin/activate
uvicorn main:app --reload

# 3. Frontend (terminal séparé)
cd frontend
npm run dev

# 4. Vérifications
curl http://localhost:8000/health  # Backend OK
curl http://localhost:5173         # Frontend OK
```

**Vous avez maintenant une application complète et fonctionnelle !**
