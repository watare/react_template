# Web Development Learning Handbook

## Table of Contents
1. [Project Overview](#project-overview)
2. [Technology Stack](#technology-stack)
3. [Learning Phases](#learning-phases)
4. [Concepts & Decisions](#concepts--decisions)
5. [Setup & Configuration](#setup--configuration)
6. [Code Patterns](#code-patterns)
7. [Troubleshooting](#troubleshooting)

---

## Project Overview

**Purpose:** Learn modern web development by building a full-stack application with RBAC and dual databases (PostgreSQL + RDF).

**Learning Method:** Step-by-step implementation with deep understanding of each layer.

---

## Technology Stack

### Frontend
- **React** - UI library for building component-based interfaces
- **TypeScript** - Type-safe JavaScript for better code quality
- **Vite** - Fast build tool and dev server

### Backend
- **FastAPI** - Modern Python web framework with automatic API docs
- **Pydantic** - Data validation using Python type hints
- **SQLAlchemy** - SQL toolkit and ORM for Python

### Databases
- **PostgreSQL** - Relational database for structured data (users, roles, app data)
- **Apache Jena Fuseki** - RDF triplestore for semantic/graph data

### Authentication & Authorization
- **JWT (JSON Web Tokens)** - Stateless authentication
- **python-jose** - JWT implementation for Python
- **passlib** - Password hashing
- **Casbin** (or custom) - RBAC policy engine

### Infrastructure
- **Docker Compose** - Multi-container orchestration
- **Nginx** - Reverse proxy (production)

---

## Learning Phases

### Phase 1: React Frontend (Current)
**Goal:** Build standalone React app with mock data

**What to learn:**
- React component structure
- Props and state management
- Hooks (useState, useEffect)
- TypeScript integration
- Component composition

**Deliverables:**
- [ ] Vite + React + TypeScript setup
- [ ] Login form component
- [ ] Dashboard with mock data
- [ ] Understanding of component lifecycle

---

### Phase 2: FastAPI Backend
**Goal:** Create API that React can consume

**What to learn:**
- FastAPI application structure
- REST API design
- CORS configuration
- HTTP methods (GET, POST, PUT, DELETE)
- Request/response models with Pydantic

**Deliverables:**
- [ ] Basic FastAPI app
- [ ] API endpoints for mock data
- [ ] React connected to FastAPI
- [ ] Understanding of client-server communication

---

### Phase 3: PostgreSQL Integration
**Goal:** Add persistent data storage

**What to learn:**
- Relational database design
- SQLAlchemy ORM
- Database migrations (Alembic)
- CRUD operations
- Model relationships (User, Role, Permission)

**Deliverables:**
- [ ] PostgreSQL setup
- [ ] User and Role models
- [ ] CRUD endpoints
- [ ] Database schema design

---

### Phase 4: Authentication & RBAC
**Goal:** Secure the application with user auth and permissions

**What to learn:**
- JWT token flow
- Password hashing
- Protected routes (frontend & backend)
- Role-based permissions
- Middleware/decorators for auth

**Deliverables:**
- [ ] User registration/login
- [ ] JWT token generation/validation
- [ ] Role-based route protection
- [ ] Permission checking

---

### Phase 5: RDF Triplestore (Fuseki)
**Goal:** Add semantic data layer

**What to learn:**
- RDF concepts (triples, subjects, predicates, objects)
- SPARQL query language
- When to use RDF vs relational
- SPARQLWrapper library
- Hybrid data architecture

**Deliverables:**
- [ ] Fuseki setup
- [ ] SPARQL queries from FastAPI
- [ ] Use case for semantic data
- [ ] Integration with PostgreSQL data

---

## Concepts & Decisions

### Why This Stack?

**FastAPI over Django:**
- Lighter weight, easier to understand
- Automatic API documentation (Swagger)
- Async support built-in
- Better for learning API-first development

**React over Vue/Angular:**
- Industry standard with huge ecosystem
- Component-based architecture
- Strong community and learning resources

**TypeScript on Frontend:**
- Type safety catches errors early
- Better IDE support
- Easier to maintain as project grows

**PostgreSQL + RDF (Fuseki):**
- PostgreSQL: structured, relational data (users, transactions)
- RDF: flexible, semantic data (relationships, ontologies)
- Learn when to use each

---

## React Fundamentals

### Core Concepts

**1. Component-Based Architecture**
- React builds UIs from reusable, self-contained components
- Components are functions that return JSX (HTML-like syntax in JavaScript)
- Example:
  ```tsx
  function Greeting() {
    return <h1>Hello, World!</h1>;
  }
  ```

**2. Props (Data Flow Down)**
- Pass data from parent to child components
- Unidirectional data flow (one-way binding)
- Example:
  ```tsx
  <Greeting name="Alice" />

  function Greeting({ name }) {
    return <h1>Hello, {name}!</h1>;
  }
  ```

**3. State (Interactive Data)**
- Components remember data that changes over time
- When state updates, React re-renders the component
- Managed via the `useState` hook

**How useState Works:**
```tsx
import { useState } from 'react';

function Counter() {
  const [count, setCount] = useState(0);
  //     ↑       ↑             ↑
  //  current  setter     initial value

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>+1</button>
    </div>
  );
}
```

**Anatomy of useState:**
- **`count`** - Current state value (read-only, never modify directly)
- **`setCount`** - Function to update state (triggers re-render)
- **`useState(0)`** - Initial value (only used on first render)

**State Update Flow:**
1. User clicks button → `onClick` handler fires
2. `setCount(count + 1)` called → React queues update
3. React re-runs `Counter()` function with new state
4. New JSX generated with updated `count` value
5. React compares old vs new JSX (Virtual DOM diffing)
6. Only changed DOM elements updated (the `<p>` text)

**Critical Rules:**
- ❌ Never mutate state directly: `count = 5` (won't trigger re-render)
- ✅ Always use setter: `setCount(5)` (triggers re-render)
- State updates are **asynchronous** (not instant)
- Multiple `setState` calls in same event handler are batched

**Example - Batching:**
```tsx
function handleClick() {
  setCount(count + 1);  // count = 0 + 1 = 1
  setCount(count + 1);  // count = 0 + 1 = 1 (still uses old value!)
  // Result: count = 1 (not 2!)
}

// Fix: Use functional update
function handleClick() {
  setCount(c => c + 1);  // c = 0 + 1 = 1
  setCount(c => c + 1);  // c = 1 + 1 = 2
  // Result: count = 2 ✓
}
```

**When to Use State:**
- User input (form fields, toggles)
- UI visibility (modals, dropdowns)
- Data fetched from API
- Any value that changes and affects UI

**4. Virtual DOM**
- React maintains a lightweight copy of the DOM in memory
- When state changes:
  1. React compares old vs new virtual DOM
  2. Calculates minimal changes needed
  3. Updates only changed elements in real DOM
- Much faster than re-rendering entire page

**5. Component Rendering & Re-rendering**

**What is Rendering?**
Rendering = React calling your component function to get JSX → Converting JSX to DOM

**Initial Render (Mount):**
```tsx
function Greeting() {
  console.log('Rendering Greeting');  // Runs once on mount
  return <h1>Hello!</h1>;
}

// When <Greeting /> is first added to the page:
// 1. React calls Greeting()
// 2. Logs "Rendering Greeting"
// 3. Returns <h1>Hello!</h1>
// 4. React creates real DOM: <h1> element with text "Hello!"
```

**Re-render Triggers (when component runs again):**

1. **State changes** (via `setState`)
```tsx
function Counter() {
  const [count, setCount] = useState(0);

  console.log('Rendering Counter');  // Runs on every state change

  return <button onClick={() => setCount(count + 1)}>{count}</button>;
}
// Click button → setCount called → Component re-renders
```

2. **Props change** (parent passes new data)
```tsx
function Greeting({ name }) {
  console.log('Rendering Greeting');  // Runs when name changes
  return <h1>Hello, {name}!</h1>;
}

// Parent component:
<Greeting name={userName} />  // When userName changes, Greeting re-renders
```

3. **Parent re-renders** (children re-render by default)
```tsx
function Parent() {
  const [count, setCount] = useState(0);
  return (
    <div>
      <Child />  {/* Re-renders even if it has no props! */}
    </div>
  );
}
// Parent state changes → Child re-renders (even though it didn't change)
```

**Complete Rendering Cycle:**
```
User Event (click, type, etc.)
    ↓
setState called
    ↓
React schedules update (batches multiple updates)
    ↓
Component function re-runs
    ↓
New JSX returned
    ↓
Virtual DOM Diffing (compare old vs new)
    ↓
Commit Phase (update only changed real DOM elements)
    ↓
Browser repaints screen
```

**Performance Note:**
- Re-rendering the component ≠ updating the DOM
- React only updates DOM elements that actually changed
- Example: If only button text changes, React only updates that text node

**Common Misconception:**
```tsx
function Counter() {
  const [count, setCount] = useState(0);
  const doubled = count * 2;  // ❓ Does this recalculate every render?

  return <p>{doubled}</p>;
}
```
**Answer:** Yes! Every render re-runs the entire function (including `doubled = count * 2`)
- For expensive calculations, use `useMemo` hook (covered later)

**Rendering Best Practices:**
- Keep renders fast (no slow calculations in render function)
- Avoid unnecessary state (if value can be calculated from props/state, don't store it)
- Use React DevTools Profiler to identify slow renders

**6. React Hooks - "Hooking Into" React Features**

**What are Hooks?**
Hooks are special functions (starting with `use`) that let you "hook into" React features like state and lifecycle from function components.

**Before Hooks (2018):**
- Only class components could have state
- Function components were "dumb" (just props → JSX)

**After Hooks (2019+):**
- Function components can have state, effects, context, etc.
- Simpler syntax, easier to learn
- Modern React uses hooks exclusively

**Core Hooks:**

**1. useState - Remember Data**
```tsx
const [value, setValue] = useState(initialValue);
```
- Persists data between renders
- Triggers re-render when updated
- Example: form inputs, toggles, counters

**2. useEffect - Side Effects & Lifecycle**
```tsx
useEffect(() => {
  // Runs after render (like componentDidMount)
  console.log('Component rendered');

  return () => {
    // Cleanup (like componentWillUnmount)
    console.log('Component unmounted');
  };
}, [dependency]);  // Re-run only when dependency changes
```
- Fetch data from API
- Subscribe to events
- Update document title
- Set up timers

**3. useContext - Share Data Globally**
```tsx
const user = useContext(UserContext);
```
- Avoid prop drilling (passing props through many levels)
- Share auth, theme, language across app

**Hook Rules (CRITICAL):**
1. **Only call at top level** (not inside loops, conditions, functions)
   ```tsx
   // ❌ WRONG
   if (condition) {
     const [count, setCount] = useState(0);
   }

   // ✅ CORRECT
   const [count, setCount] = useState(0);
   if (condition) {
     setCount(5);
   }
   ```

2. **Only call from React functions** (components or custom hooks)
   ```tsx
   // ❌ WRONG - regular function
   function calculateTotal() {
     const [total, setTotal] = useState(0);  // Error!
   }

   // ✅ CORRECT - React component
   function Calculator() {
     const [total, setTotal] = useState(0);
   }

   // ✅ CORRECT - custom hook
   function useTotal() {
     const [total, setTotal] = useState(0);
     return total;
   }
   ```

**Why These Rules?**
React relies on **hook call order** to track state:
```tsx
function Component() {
  const [name, setName] = useState('');      // Hook #1
  const [age, setAge] = useState(0);         // Hook #2
  const [email, setEmail] = useState('');    // Hook #3

  // React internally: [nameState, ageState, emailState]
  // Order must be identical every render!
}
```

If hooks are called conditionally:
```tsx
function Component() {
  const [name, setName] = useState('');
  if (condition) {
    const [age, setAge] = useState(0);  // Sometimes Hook #2, sometimes skipped
  }
  const [email, setEmail] = useState('');  // Hook #2 or #3? React gets confused!
}
```
React crashes because hook order changed between renders.

**Custom Hooks - Reuse Logic**
```tsx
// Custom hook for form input
function useInput(initialValue) {
  const [value, setValue] = useState(initialValue);

  const handleChange = (e) => setValue(e.target.value);

  return { value, onChange: handleChange };
}

// Usage in component
function LoginForm() {
  const email = useInput('');
  const password = useInput('');

  return (
    <form>
      <input type="email" {...email} />
      <input type="password" {...password} />
    </form>
  );
}
```

**Hook Naming Convention:**
- Always start with `use` (e.g., `useState`, `useEffect`, `useCustomHook`)
- Signals to React and linters that hook rules apply

---

### Distinguishing Functions: Regular vs Component vs Custom Hook

React uses **naming conventions** to distinguish between different types of functions. Understanding these differences is critical for correct React development.

**1. Regular JavaScript Function**
```tsx
// Naming: camelCase, starts with lowercase
function calculateTotal(price, tax) {
  return price + (price * tax);
}

function formatDate(date) {
  return date.toISOString();
}

function validateEmail(email) {
  return email.includes('@');
}
```

**Characteristics:**
- ✅ Lowercase first letter (camelCase)
- ✅ Pure logic, no JSX
- ✅ Can be called anywhere (inside components, effects, etc.)
- ❌ **CANNOT** use hooks (`useState`, `useEffect`, etc.)
- ❌ **CANNOT** return JSX

**Purpose:** Helper functions for logic, calculations, validation

---

**2. React Component**
```tsx
// Naming: PascalCase, starts with UPPERCASE
function Button({ label, onClick }) {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <button
      onClick={onClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {label}
    </button>
  );
}

function UserProfile({ user }) {
  return (
    <div>
      <h1>{user.name}</h1>
      <p>{user.email}</p>
    </div>
  );
}
```

**Characteristics:**
- ✅ Uppercase first letter (PascalCase)
- ✅ **MUST** return JSX (or null)
- ✅ **CAN** use hooks
- ✅ Receives `props` as first argument
- ✅ Called by React (not directly by you): `<Button />` not `Button()`

**Purpose:** Render UI, compose other components

---

**3. Custom Hook**
```tsx
// Naming: camelCase, MUST start with "use"
function useCounter(initialValue = 0) {
  const [count, setCount] = useState(initialValue);

  const increment = () => setCount(c => c + 1);
  const decrement = () => setCount(c => c - 1);
  const reset = () => setCount(initialValue);

  return { count, increment, decrement, reset };
}

function useWindowWidth() {
  const [width, setWidth] = useState(window.innerWidth);

  useEffect(() => {
    const handleResize = () => setWidth(window.innerWidth);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return width;
}
```

**Characteristics:**
- ✅ Lowercase first letter (camelCase) BUT **MUST** start with `use`
- ✅ **CAN** use hooks (this is the whole point!)
- ✅ Called directly in component body: `const width = useWindowWidth()`
- ❌ **CANNOT** return JSX
- ❌ Does NOT receive props (receives regular parameters)

**Purpose:** Extract and reuse stateful logic across components

---

**Side-by-Side Comparison**

| Feature | Regular Function | React Component | Custom Hook |
|---------|-----------------|-----------------|-------------|
| **Naming** | `camelCase` | `PascalCase` | `useCamelCase` |
| **Example** | `calculateTotal` | `Button` | `useCounter` |
| **Can use hooks?** | ❌ No | ✅ Yes | ✅ Yes |
| **Returns JSX?** | ❌ No | ✅ Yes | ❌ No |
| **How called?** | `fn()` | `<Fn />` | `fn()` |
| **Where called?** | Anywhere | In JSX | Component body |
| **Purpose** | Logic/utils | UI rendering | Reusable state logic |

---

**Real-World Example: Using All Three Together**

```tsx
// ============================================
// 1. REGULAR FUNCTION - Utility Logic
// ============================================
function formatPrice(amount) {
  //     ↑ camelCase naming (lowercase start)
  //              ↑ parameter: regular JavaScript value

  return `$${amount.toFixed(2)}`;
  //     ↑ template literal (backticks)
  //       ↑ ${} interpolation: embed JavaScript in string
  //             ↑ toFixed(2): rounds to 2 decimal places
  //     Result: "$9.99"
}

// Why regular function?
// - Pure logic (input → output)
// - No state, no side effects
// - Reusable anywhere (components, hooks, other functions)


// ============================================
// 2. CUSTOM HOOK - Reusable State Logic
// ============================================
function useShoppingCart() {
  //     ↑ MUST start with "use" (React convention)
  //       ↑ camelCase after "use"

  // STATE: Array of cart items (persists across renders)
  const [items, setItems] = useState([]);
  //     ↑        ↑            ↑         ↑ initial value: empty array
  //     ↑        ↑            ↑ useState hook
  //     ↑        ↑ setter function
  //     ↑ current value (array of items)

  // DERIVED FUNCTION: Add item to cart
  const addItem = (item) => setItems([...items, item]);
  //                ↑ parameter: new item object { id, name, price }
  //                             ↑ setItems: triggers re-render
  //                                  ↑ [...items, item]
  //                                     spread operator: copy existing items
  //                                     then add new item at end
  //                                     Result: NEW array (immutable update)

  // DERIVED VALUE: Calculate total price
  const total = items.reduce((sum, item) => sum + item.price, 0);
  //            ↑ array.reduce(): accumulate values
  //                    ↑ accumulator (running total)
  //                         ↑ current item
  //                                ↑ add item.price to sum
  //                                                         ↑ initial value: 0
  // Example: [{ price: 10 }, { price: 20 }]
  //   Step 1: sum=0  + item.price=10 → 10
  //   Step 2: sum=10 + item.price=20 → 30
  //   Result: 30

  // RETURN: Object with state and functions
  return { items, addItem, total };
  //     ↑ object shorthand: { items: items, addItem: addItem, total: total }
}

// Why custom hook?
// - Uses hooks (useState) → MUST be a hook, not regular function
// - Encapsulates reusable logic (multiple components can use this cart)
// - Returns data + functions (not JSX)


// ============================================
// 3. REACT COMPONENT - UI Rendering
// ============================================
function ShoppingCart() {
  //     ↑ PascalCase (uppercase start)
  //     ↑ Component name = what it renders

  // DESTRUCTURING: Extract values from custom hook
  const { items, addItem, total } = useShoppingCart();
  //    ↑ destructuring assignment
  //      ↑ extract 3 properties from returned object
  //                                  ↑ call custom hook (runs on every render)

  // RETURN JSX: Component MUST return JSX (or null)
  return (
    <div>
      {/* Static heading */}
      <h2>Cart</h2>

      {/* DYNAMIC LIST: Loop through items array */}
      {items.map(item => (
        //   ↑ array.map(): transform each item → JSX
        //        ↑ arrow function: (item) => JSX

        <p key={item.id}>
          {/* ↑ key prop: REQUIRED for lists (React needs unique ID to track items)
                ↑ must be unique per item (usually database ID)
                ↑ helps React efficiently update DOM when list changes */}

          {item.name} - {formatPrice(item.price)}
          {/* ↑ access object property
                      ↑ call regular function
                            ↑ pass item.price as argument */}
        </p>
      ))}
      {/* Result if items = [{ id: 1, name: 'Book', price: 9.99 }]:
          <p key={1}>Book - $9.99</p> */}

      {/* Display total */}
      <h3>Total: {formatPrice(total)}</h3>
      {/*         ↑ {} = JavaScript expression in JSX
                      ↑ call formatPrice with total value */}

      {/* Button with click handler */}
      <button onClick={() => addItem({ id: 1, name: 'Book', price: 9.99 })}>
        {/*   ↑ onClick: React event handler (camelCase, not onclick)
                  ↑ arrow function: runs when button clicked
                       ↑ call addItem function from hook
                              ↑ object literal: create item object inline */}
        Add Item
      </button>
    </div>
  );
}

// Why React component?
// - Renders UI (returns JSX)
// - Uses custom hook to get state/logic
// - Calls regular function for formatting
// - Handles user interaction (button click)
```

---

**Detailed Syntax Breakdown:**

**1. Template Literals (Backticks)**
```tsx
`$${amount.toFixed(2)}`
 ↑ backtick (not single quote)
  ↑ literal text
   ${ } interpolation: JavaScript expression
        ↑ method call: rounds number to 2 decimals
```
**vs Regular Strings:**
```tsx
"$" + amount.toFixed(2)  // Old way (string concatenation)
`$${amount.toFixed(2)}`   // Modern way (template literal)
```

**2. Array Spread Operator**
```tsx
[...items, item]
 ↑ spread: unpack all elements from items array
         ↑ then add new item at end

// Example:
const items = ['apple', 'banana'];
const newItems = [...items, 'cherry'];
// Result: ['apple', 'banana', 'cherry']
```

**Why not `items.push(item)`?**
```tsx
// ❌ WRONG - mutates original array (doesn't trigger re-render)
items.push(item);
setItems(items);  // React sees same array reference, no re-render!

// ✅ CORRECT - creates NEW array (triggers re-render)
setItems([...items, item]);  // New array reference, React detects change
```

**3. Array.reduce() - Accumulator Pattern**
```tsx
items.reduce((sum, item) => sum + item.price, 0)
//           ↑ accumulator (previous result)
//                ↑ current element
//                        ↑ return new accumulator value
//                                              ↑ initial accumulator value

// Step-by-step example:
const items = [
  { name: 'Book', price: 10 },
  { name: 'Pen', price: 5 },
  { name: 'Bag', price: 20 }
];

items.reduce((sum, item) => sum + item.price, 0)
// Iteration 1: sum=0,  item={ name: 'Book', price: 10 } → return 0 + 10 = 10
// Iteration 2: sum=10, item={ name: 'Pen', price: 5 }   → return 10 + 5 = 15
// Iteration 3: sum=15, item={ name: 'Bag', price: 20 }  → return 15 + 20 = 35
// Final result: 35
```

**4. Object Destructuring**
```tsx
const { items, addItem, total } = useShoppingCart();
//    ↑ destructuring: extract properties from returned object

// Equivalent to:
const cart = useShoppingCart();
const items = cart.items;
const addItem = cart.addItem;
const total = cart.total;

// Hook returns: { items: [...], addItem: fn, total: 35 }
// Destructuring extracts each property into a variable
```

**5. Object Shorthand**
```tsx
return { items, addItem, total };

// Equivalent to:
return {
  items: items,      // property name = variable name
  addItem: addItem,
  total: total
};

// When property name matches variable name, use shorthand
```

**6. JSX {} Curly Braces - JavaScript Expressions**
```tsx
<p>{item.name}</p>              // Variable
<p>{formatPrice(total)}</p>      // Function call
<p>{count + 1}</p>               // Arithmetic
<p>{isActive ? 'Yes' : 'No'}</p> // Ternary operator

// ❌ Cannot use statements (if, for, while)
<p>{if (x) { return 'hi' }}</p>  // ERROR!

// ✅ Use expressions instead
<p>{x ? 'hi' : 'bye'}</p>        // Ternary
```

**7. JSX key Prop - Why It's Critical**
```tsx
{items.map(item => (
  <p key={item.id}>{item.name}</p>
))}

// Without keys:
// React re-renders ENTIRE list on every change (slow)

// With keys:
// React knows which items changed (fast updates)

// Example: Remove middle item
// Before: [A, B, C]  keys: [1, 2, 3]
// After:  [A, C]     keys: [1, 3]
// React: "Keep 1, delete 2, keep 3" (efficient!)

// ❌ WRONG - array index as key
items.map((item, index) => <p key={index}>...</p>)
// Problem: indices change when list reorders → React gets confused

// ✅ CORRECT - stable unique ID
items.map(item => <p key={item.id}>...</p>)
```

**8. Arrow Functions in Event Handlers**
```tsx
<button onClick={() => addItem({ id: 1, name: 'Book', price: 9.99 })}>
//              ↑ arrow function: creates new function on every render
//                 ↑ this function runs when button is clicked

// Why arrow function?
// Need to pass arguments to addItem

// ❌ WRONG - calls immediately (not on click)
<button onClick={addItem({ id: 1, name: 'Book', price: 9.99 })}>

// ✅ CORRECT - wraps in function, calls on click
<button onClick={() => addItem({ id: 1, name: 'Book', price: 9.99 })}>

// Alternative: pre-define function
const handleClick = () => addItem({ id: 1, name: 'Book', price: 9.99 });
<button onClick={handleClick}>
```

---

**Execution Flow (Step-by-Step):**

1. **React renders `<ShoppingCart />` component**
   - Calls `ShoppingCart()` function

2. **Custom hook called**
   ```tsx
   const { items, addItem, total } = useShoppingCart();
   ```
   - Initializes state: `items = []`
   - Calculates total: `total = 0`
   - Returns `{ items: [], addItem: fn, total: 0 }`

3. **JSX rendered**
   ```tsx
   <h2>Cart</h2>           // Static
   {items.map(...)}        // Empty array → no <p> elements rendered
   <h3>Total: $0.00</h3>   // formatPrice(0) → "$0.00"
   <button>Add Item</button>
   ```

4. **User clicks button**
   - `onClick` handler fires: `() => addItem({ id: 1, name: 'Book', price: 9.99 })`
   - Calls `addItem` function

5. **State updates**
   ```tsx
   setItems([...items, { id: 1, name: 'Book', price: 9.99 }])
   // Old: []
   // New: [{ id: 1, name: 'Book', price: 9.99 }]
   ```

6. **Component re-renders**
   - React calls `ShoppingCart()` again
   - Hook returns updated state: `items = [{ id: 1, name: 'Book', price: 9.99 }]`
   - Total recalculated: `total = 9.99`

7. **JSX updated**
   ```tsx
   {items.map(item => <p key={1}>Book - $9.99</p>)}  // Now renders 1 item
   <h3>Total: $9.99</h3>                             // Updated total
   ```

8. **React updates DOM**
   - Only changed elements updated (new `<p>` and `<h3>` text)
   - Button unchanged (not re-rendered in DOM)

---

**Common Mistakes & How to Avoid Them**

❌ **Wrong: Regular function using hooks**
```tsx
function calculateDiscount(price) {
  const [discount, setDiscount] = useState(0);  // ERROR! Breaks hook rules
  return price * (1 - discount);
}
```
**Fix:** Make it a custom hook (`useDiscount`) or remove hooks

---

❌ **Wrong: Component with lowercase name**
```tsx
function button() {  // Lowercase!
  return <button>Click</button>;
}

// Usage:
<button />  // React thinks it's HTML <button>, not your component!
```
**Fix:** Rename to `Button` (PascalCase)

---

❌ **Wrong: Custom hook without "use" prefix**
```tsx
function counter() {  // Missing "use" prefix
  const [count, setCount] = useState(0);
  return count;
}
```
**Fix:** Rename to `useCounter` - React linters won't enforce hook rules without `use` prefix

---

❌ **Wrong: Component called as regular function**
```tsx
function App() {
  return (
    <div>
      {Button({ label: 'Click' })}  {/* Wrong! Called as function */}
    </div>
  );
}
```
**Fix:** Use JSX syntax: `<Button label="Click" />`

---

**Quick Decision Guide:**

**Need to render UI?**
→ React Component (PascalCase, returns JSX)

**Need to reuse stateful logic across components?**
→ Custom Hook (useCamelCase, uses hooks, returns data/functions)

**Just utility logic (format, validate, calculate)?**
→ Regular Function (camelCase, pure logic)

---

**Why React?**
- **Declarative**: Describe *what* UI should look like, React handles *how* to update
- **Composable**: Build complex UIs from small, reusable pieces
- **Efficient**: Virtual DOM minimizes expensive DOM operations

---

## Vite Build Tool

### What is Vite?

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

### How Vite Works

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

### Vite vs Alternatives

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

## Setup & Configuration

### Project Structure
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

### Essential Configuration Files

#### 1. vite.config.ts - Vite's Brain
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

#### 2. index.html - The Entry Point
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

#### 3. tsconfig.json - TypeScript Compiler Rules
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

#### 4. package.json - Project Metadata & Dependencies
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

### How Configuration Files Work Together

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

### Vite Use Cases

#### Adding New Components
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

#### Adding a Database/Backend
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

### Prerequisites
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

## Code Patterns

### To be documented as we learn and build

---

## Troubleshooting

### Common Issues
*To be filled as we encounter and solve problems*

---

## Notes & Learnings

*Use this section to capture key insights during development*

---

**Last Updated:** 2025-10-06
**Current Phase:** Phase 1 - React Frontend Setup
