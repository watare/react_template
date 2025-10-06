# State Management

*Advanced state management patterns for React applications*

---

## Context API

### What is Context?

Context provides a way to pass data through the component tree without having to pass props manually at every level.

**When to use Context:**
- Global app state (user, theme, language)
- Authenticated user data
- Permissions/RBAC
- Rarely changing data

**When NOT to use Context:**
- Frequently changing data (performance issues)
- Local component state
- Data used by only 1-2 components

### Creating a Context

```tsx
import { createContext, useContext, useState } from 'react'

// 1. Create Context
interface User {
  id: string
  name: string
  email: string
}

interface UserContextType {
  user: User | null
  setUser: (user: User | null) => void
}

const UserContext = createContext<UserContextType | undefined>(undefined)

// 2. Create Provider Component
export function UserProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)

  return (
    <UserContext.Provider value={{ user, setUser }}>
      {children}
    </UserContext.Provider>
  )
}

// 3. Create Custom Hook for Consumption
export function useUser() {
  const context = useContext(UserContext)
  if (context === undefined) {
    throw new Error('useUser must be used within UserProvider')
  }
  return context
}
```

### Using the Context

```tsx
// App.tsx - Wrap app with provider
function App() {
  return (
    <UserProvider>
      <Dashboard />
    </UserProvider>
  )
}

// Dashboard.tsx - Consume context
function Dashboard() {
  const { user, setUser } = useUser()

  return (
    <div>
      {user ? (
        <p>Welcome, {user.name}</p>
      ) : (
        <button onClick={() => setUser({ id: '1', name: 'Alice', email: 'alice@example.com' })}>
          Login
        </button>
      )}
    </div>
  )
}
```

---

## React Query

### What is React Query?

A powerful data-fetching and state management library for server state.

**Key Features:**
- Automatic caching
- Background refetching
- Stale-while-revalidate
- Request deduplication
- Optimistic updates

### Basic Usage

```tsx
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'

// Fetch data
function UsersList() {
  const { data: users, isLoading, error } = useQuery({
    queryKey: ['users'],
    queryFn: async () => {
      const response = await fetch('/api/users')
      return response.json()
    }
  })

  if (isLoading) return <div>Loading...</div>
  if (error) return <div>Error: {error.message}</div>

  return (
    <ul>
      {users.map(user => (
        <li key={user.id}>{user.name}</li>
      ))}
    </ul>
  )
}

// Mutate data
function CreateUser() {
  const queryClient = useQueryClient()

  const mutation = useMutation({
    mutationFn: async (newUser: { name: string, email: string }) => {
      const response = await fetch('/api/users', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newUser)
      })
      return response.json()
    },
    onSuccess: () => {
      // Invalidate and refetch
      queryClient.invalidateQueries({ queryKey: ['users'] })
    }
  })

  return (
    <button onClick={() => mutation.mutate({ name: 'Bob', email: 'bob@example.com' })}>
      Create User
    </button>
  )
}
```

### Configuration

```tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      cacheTime: 1000 * 60 * 30, // 30 minutes
      retry: 3,
      refetchOnWindowFocus: false
    }
  }
})

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <YourApp />
    </QueryClientProvider>
  )
}
```

---

## Zustand (Optional)

### What is Zustand?

A small, fast, and scalable state management solution.

**When to use:**
- Complex client state
- Alternative to Context for frequent updates
- Simple API compared to Redux

### Basic Usage

```tsx
import { create } from 'zustand'

interface StoreState {
  count: number
  increment: () => void
  decrement: () => void
}

const useStore = create<StoreState>((set) => ({
  count: 0,
  increment: () => set((state) => ({ count: state.count + 1 })),
  decrement: () => set((state) => ({ count: state.count - 1 }))
}))

// Usage in component
function Counter() {
  const { count, increment, decrement } = useStore()

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={increment}>+</button>
      <button onClick={decrement}>-</button>
    </div>
  )
}
```

---

## Comparison

| Feature | Context API | React Query | Zustand |
|---------|-------------|-------------|---------|
| **Use Case** | Global app state | Server state | Client state |
| **Performance** | Re-renders all consumers | Excellent | Excellent |
| **Learning Curve** | Low | Medium | Low |
| **Bundle Size** | 0 (built-in) | ~13KB | ~1KB |
| **Caching** | Manual | Automatic | Manual |
| **Best For** | Auth, theme | API data | Complex client state |

---

## Best Practices

**1. Separate Server State from Client State**
- Use React Query for server data (API calls)
- Use Context/Zustand for client state (UI state, preferences)

**2. Keep Context Small**
- Split large contexts into smaller ones
- Avoid putting everything in one context

**3. Optimize Re-renders**
- Use `useMemo` for expensive calculations
- Split contexts by update frequency

**4. Type Safety**
- Always type your contexts and stores
- Use TypeScript for better DX

---

## To be continued...

*This section will be expanded as we implement more state management patterns*
