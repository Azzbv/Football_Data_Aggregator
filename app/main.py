from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.database import connect_to_mongo, close_mongo_connection
from app.api import routes_health, routes_raw, routes_unified, routes_transformations, routes_sources

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo_connection()
app = FastAPI(title=settings.PROJECT_NAME, description='\n# Unified Football Data Platform\nA robust, portfolio-ready data engineering platform that ingests raw football data from multiple sources, \nnormalizes it into a unified schema, and exposes it through a clean REST API.\n\n## Core Features\n- **Multi-Source Ingestion**: Ingests data from StatsBomb, Understat, and FBref.\n- **Entity Resolution**: Automatically matches players and teams across different data providers.\n- **Data Provenance**: Every unified record links back to its original raw source document.\n- **Analytical Views**: Pre-aggregated match statistics for players and teams.\n- **Observability**: Detailed tracking of transformation runs and data quality audits.\n\n## Data Exploration\n- **[Unified API](/docs#unified)**: Browse standardized competitions, teams, players, and matches.\n- **[Raw API](/docs#raw)**: Explore original, un-transformed data payloads from each source.\n- **[Observability API](/docs#observability)**: Inspect pipeline health and processing history.\n    ', version='1.0.0', openapi_url=f'{settings.API_V1_STR}/openapi.json', lifespan=lifespan)
limiter = Limiter(key_func=get_remote_address, default_limits=[settings.RATE_LIMIT_GLOBAL])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True, allow_methods=['*'], allow_headers=['*'])
app.include_router(routes_health.router, prefix='/health', tags=['system'])
app.include_router(routes_sources.router, prefix=f'{settings.API_V1_STR}/sources', tags=['sources'])
app.include_router(routes_unified.router, prefix=f'{settings.API_V1_STR}/unified', tags=['unified'])
app.include_router(routes_raw.router, prefix=f'{settings.API_V1_STR}/raw', tags=['raw'])
app.include_router(routes_transformations.router, prefix=f'{settings.API_V1_STR}/transformations', tags=['observability'])

@app.get('/', summary='Project Overview', tags=['system'])
async def root():
    """
    Overview of the platform, supported sources, and entry points.
    """
    return {'project': settings.PROJECT_NAME, 'description': 'Unified Football Data Engineering Platform', 'supported_sources': ['statsbomb', 'understat', 'fbref'], 'api_sections': {'unified': f'{settings.API_V1_STR}/unified', 'raw': f'{settings.API_V1_STR}/raw', 'observability': f'{settings.API_V1_STR}/transformations', 'sources': f'{settings.API_V1_STR}/sources'}, 'documentation': '/docs', 'health': '/health'}
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)