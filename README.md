# Football Data Engineering Platform

A professional, portfolio-ready data engineering platform designed to ingest, normalize, and expose football data from diverse providers (StatsBomb, Understat, FBref). This platform demonstrates a robust ETL lifecycle, multi-source entity resolution, and a clean API layer for data exploration.

## Why This Project Matters
In football analytics, data is fragmented across providers with different schemas, naming conventions, and granularities. This platform solves the "Siloed Data Problem" by:
- Unifying Identities: Resolving "Real Madrid" and "real madrid cf" to a single global entity.
- Maintaining Provenance: Every normalized record links back to its original source document.
- Enabling Hybrid Access: Providing both high-level unified statistics and deep-dives into original raw payloads.

## Architecture
The platform follows a multi-stage data lake/warehouse pattern using MongoDB for flexible storage and FastAPI for accessibility.

1.  Raw Layer: Source-faithful data stored in separate databases (statsbomb_raw, understat_raw, etc.) with enriched ingestion metadata.
2.  Transformation Layer: An idempotent pipeline that normalizes entities, resolves cross-source identities, and calculates analytical views (Player/Team Match Stats).
3.  Unified Layer: A standardized schema in football_unified optimized for cross-provider analysis.
4.  API Layer: A RESTful interface with pagination, recursive serialization, and comprehensive observability.
---

## Getting Started

### 1. Prerequisites
- Python 3.14+
- MongoDB instance (Local or VPS)
- Docker (optional)

### 2. Setup
```bash
# Clone and install
git clone <repository-url>
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your MONGODB_URL
```

### 3. Run the ETL Pipeline
The project uses a structured CLI workflow for data management. Note for Windows/PowerShell users: Ensure you set PYTHONPATH when running scripts.

```powershell
# Initialize database indexes
$env:PYTHONPATH = "."; python scripts/bootstrap_indexes.py

# Step 1: Ingest raw data from all sources (Big 5 European Leagues + Champions League)
$env:PYTHONPATH = "."; python ingestion/runners/ingest_all.py

# Step 2: Run normalization and build analytical views
$env:PYTHONPATH = "."; python transform/runners/run_full_pipeline.py
```

### 4. Launch the API
```bash
# Local development
uvicorn app.main:app --reload

# With Docker
docker-compose up --build
```

---

## Data Exploration (API)

Explore the platform through the Swagger UI at http://localhost:8000/docs.

### Key Endpoints
| Endpoint | Purpose |
| :--- | :--- |
| `GET /api/v1/sources` | Discover available data providers and their collections. |
| `GET /api/v1/raw/{src}/{coll}` | Browse original, un-transformed provider documents. |
| `GET /api/v1/unified/matches` | Access standardized match records across all sources. |
| `GET /api/v1/unified/player-match-stats` | Query high-level performance metrics (xG, Goals, etc.). |
| `GET /api/v1/transformations/runs` | Inspect pipeline health and processing history. |

### Example: Unified Document with Provenance
```json
{
  "unified_id": "u-match-3869685",
  "home_score": 3,
  "away_score": 3,
  "status": "played",
  "_provenance": [
    {
      "source_name": "statsbomb",
      "source_id": "3869685",
      "source_db": "statsbomb_raw"
    }
  ]
}
```
