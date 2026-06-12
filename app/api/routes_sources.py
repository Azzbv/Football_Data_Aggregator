from fastapi import APIRouter
from app.core.config import settings
router = APIRouter()
SOURCES = {'statsbomb': {'db': settings.MONGODB_DB_STATSBOMB_RAW, 'collections': ['competitions', 'matches', 'lineups', 'events', 'metadata'], 'description': 'Open data from StatsBomb (JSON via GitHub).'}, 'understat': {'db': settings.MONGODB_DB_UNDERSTAT_RAW, 'collections': ['teams', 'matches', 'shots', 'metadata'], 'description': 'Advanced xG data scraped from Understat.com.'}, 'fbref': {'db': settings.MONGODB_DB_FBREF_RAW, 'collections': ['matches', 'player_stats', 'team_stats', 'metadata'], 'description': 'Comprehensive statistics parsed from FBref HTML tables.'}}

@router.get('', summary='List Sources', description='Retrieve all available raw data sources supported by the platform.')
async def list_sources():
    """List all available raw data sources."""
    return {'sources': SOURCES}

@router.get('/{source_name}/collections', summary='List Collections', description='Explore available MongoDB collections for a specific data source.')
async def list_source_collections(source_name: str):
    """List collections available for a specific source."""
    if source_name not in SOURCES:
        return {'error': 'Source not found'}
    return {'source': source_name, 'collections': SOURCES[source_name]['collections']}