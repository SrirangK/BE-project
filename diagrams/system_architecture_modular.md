# Module-Based System Architecture (Abstract Design)

## Overview
This architecture diagram focuses on **functional modules** and **data flow** rather than specific technologies.

---

## Module Structure

### 1. OFFLINE PIPELINE
**Purpose:** Pre-processing and indexing of paper corpus

**Modules:**
- **Data Ingestion Module**
  - Loads research paper corpus
  - Validates and cleans data
  
- **Text Processing Module**
  - Normalizes and preprocesses text
  - Extracts relevant features
  
- **Feature Extraction Module**
  - Generates lexical features
  - Generates semantic embeddings
  
- **Clustering Module**
  - Groups similar papers
  - Optimizes search space
  
- **Index Builder Module**
  - Creates search indices per cluster
  - Optimizes for fast retrieval

---

### 2. ONLINE PIPELINE (Three-Tier Architecture)

#### TIER 1: Presentation Layer
**Purpose:** User interaction and interface

**Modules:**
- **Query Interface**
  - Accepts user queries
  - Validates input
  
- **Result Presentation**
  - Displays recommendations
  - Organizes results by source
  
- **Interaction Handler**
  - Manages user selections
  - Triggers refinement requests

---

#### TIER 2: Application Layer
**Purpose:** Business logic and orchestration

**Modules:**
- **Query Orchestrator**
  - Routes queries to appropriate modules
  - Coordinates parallel processing
  
- **Local Retrieval Engine**
  - Encodes queries using hybrid approach
  - Performs cluster selection
  - Executes similarity search
  - Ranks results
  
- **Web Discovery Engine**
  - Manages asynchronous external searches
  - Handles job queuing
  - Polls for completion
  
- **Refinement Engine**
  - Resolves paper identifiers
  - Generates refined recommendations
  - Merges and ranks results

---

#### TIER 3: Data Layer
**Purpose:** Data storage and retrieval

**Modules:**
- **Offline Data Store**
  - Feature vectors (lexical)
  - Semantic embeddings
  - Cluster assignments
  - Search indices
  
- **External Data Connector**
  - Interfaces with external paper databases
  - Handles API communication
  - Caches responses
  
- **Job Queue Manager**
  - Tracks asynchronous tasks
  - Maintains task status
  - Stores intermediate results

---

## Data Flow Paths

### Path A: Local Hybrid Retrieval (Synchronous)
```
User Query 
  → Query Orchestrator 
  → Local Retrieval Engine
    → Encode query (hybrid features)
    → Select top-K clusters
    → Search indices
    → Compute hybrid scores
    → Rank candidates
  → Result Presentation
```

### Path B: Web Discovery (Asynchronous)
```
User Query 
  → Query Orchestrator 
  → Web Discovery Engine
    → Create background job
    → Query external database
    → Poll for completion
    → Retrieve results
  → Result Presentation
```

### Path C: Interactive Refinement (Synchronous)
```
Selected Papers 
  → Refinement Engine
    → Resolve identifiers
    → Query recommendation service
    → Retrieve related papers
    → Rank and filter
  → Result Presentation
```

---

## Key Characteristics

### Hybrid Approach
- Combines local corpus search (fast, domain-specific)
- With web discovery (comprehensive, up-to-date)
- And interactive refinement (user-guided)

### Parallel Processing
- Local and web searches execute concurrently
- Reduces perceived latency
- Improves user experience

### Modular Design
- Clear separation of concerns
- Independent module development
- Easy to test and maintain

### Scalability
- Clustering reduces search space
- Asynchronous processing for long operations
- Caching for repeated queries

---

## Visual Layout Suggestion

```
┌─────────────────────────────────────────────────────────────┐
│                   OFFLINE PIPELINE                           │
│  [Data Ingestion] → [Text Processing] → [Feature Extraction]│
│                  ↓                                           │
│              [Clustering] → [Index Builder]                  │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                   ONLINE PIPELINE                            │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │        TIER 1: PRESENTATION LAYER                   │    │
│  │  [Query Interface] [Result Presentation] [Interaction] │  │
│  └───────────────────────┬─────────────────────────────┘   │
│                          │                                  │
│  ┌───────────────────────▼──────────────────────────────┐  │
│  │        TIER 2: APPLICATION LAYER                      │  │
│  │                                                        │  │
│  │  [Query Orchestrator]                                 │  │
│  │          ├──────────┬─────────────┐                  │  │
│  │          ▼          ▼             ▼                   │  │
│  │  [Local Retrieval] [Web Discovery] [Refinement]      │  │
│  │                                                        │  │
│  └───────────────────────┬──────────────────────────────┘  │
│                          │                                  │
│  ┌───────────────────────▼──────────────────────────────┐  │
│  │        TIER 3: DATA LAYER                             │  │
│  │                                                        │  │
│  │  [Offline Data Store] [External Connector] [Job Queue]│  │
│  │                                                        │  │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘

     ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
     │   PATH A     │  │   PATH B     │  │   PATH C     │
     │    Local     │  │     Web      │  │  Refinement  │
     │  (Sync)      │  │  (Async)     │  │   (Sync)     │
     └──────────────┘  └──────────────┘  └──────────────┘
```

---

## Color Scheme (Module-Based)

- **Offline Pipeline:** Light Gray (#F5F5F5) - Pre-processing
- **Tier 1 (Presentation):** Light Blue (#E3F2FD) - User-facing
- **Tier 2 (Application):** Light Green (#E8F5E9) - Business logic
- **Tier 3 (Data):** Light Yellow (#FFF9C4) - Storage
- **External Systems:** Light Orange (#FFE0B2) - Third-party
- **Data Flow Paths:** Different colors for A/B/C paths

---

## Implementation Notes

### What's Hidden (Abstracted Away):
- Specific frameworks (React, FastAPI)
- Programming languages
- Server configurations (Nginx, port numbers)
- Specific libraries (TF-IDF, SPECTER, FAISS)
- Database systems

### What's Emphasized:
- Functional modules and their responsibilities
- Data flow between modules
- Logical organization (tiers)
- Processing patterns (sync vs async)
- Integration points (external systems)

This approach makes the architecture:
- Technology-agnostic
- Easier to understand at a high level
- Focused on system behavior rather than implementation
- Suitable for academic/research presentations
- Maintainable as technologies evolve
