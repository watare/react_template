# Getting Started

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
- [ ] Database migrations
- [ ] API connected to real database

---

### Phase 4: Authentication & RBAC
**Goal:** Implement secure authentication and authorization

**What to learn:**
- JWT token generation and validation
- Password hashing with bcrypt
- Role-based access control
- Protected routes (frontend and backend)
- Permission checking

**Deliverables:**
- [ ] User registration and login
- [ ] JWT authentication
- [ ] RBAC system
- [ ] Protected API endpoints
- [ ] Role-based UI components

---

### Phase 5: RDF Integration
**Goal:** Add semantic data layer

**What to learn:**
- RDF/SPARQL basics
- Apache Jena Fuseki
- Integration with PostgreSQL data
- Graph queries

**Deliverables:**
- [ ] Fuseki setup
- [ ] RDF data model
- [ ] SPARQL queries
- [ ] Dual database architecture

---

### Phase 6: Docker & Deployment
**Goal:** Containerize and deploy the application

**What to learn:**
- Docker basics
- Docker Compose orchestration
- Environment variables
- Production configuration
- Reverse proxy with Nginx

**Deliverables:**
- [ ] Dockerfiles for all services
- [ ] docker-compose.yml
- [ ] Production deployment
- [ ] CI/CD basics
