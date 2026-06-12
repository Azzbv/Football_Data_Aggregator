from fastapi import APIRouter, Query, HTTPException
from app.core.database import get_db_unified
from app.utils.pagination import paginate_cursor, PaginatedResponse
from app.utils.serialization import Serialization
from typing import Optional, List
from bson import ObjectId
router = APIRouter()

async def _attach_provenance(items: List[dict], db):
    """Internal helper to attach source links to a list of unified items."""
    for item in items:
        u_id = item.get('unified_id')
        if u_id:
            links = await db['source_links'].find({'unified_id': u_id}).to_list(length=10)
            item['_provenance'] = Serialization.fix_ids(links)
    return items

@router.get('/competitions', response_model=PaginatedResponse, summary='List Competitions', description='Browse normalized football competitions. Use `include_provenance=true` to see raw source links.')
async def get_competitions(page: int=Query(1, ge=1), size: int=Query(20, ge=1, le=100), include_provenance: bool=Query(False, description='Attach source provenance links to every item')):
    db = get_db_unified()
    cursor = db['competitions'].find({})
    resp = await paginate_cursor(cursor, page, size)
    if include_provenance:
        resp.items = await _attach_provenance(resp.items, db)
    return resp

@router.get('/seasons', response_model=PaginatedResponse, summary='List Seasons', description='Explore seasons within a specific competition.')
async def get_seasons(competition_id: Optional[str]=Query(None, description='Filter by unified competition ID'), page: int=Query(1, ge=1), size: int=Query(20, ge=1, le=100)):
    db = get_db_unified()
    query = {}
    if competition_id:
        query['competition_id'] = competition_id
    cursor = db['seasons'].find(query)
    return await paginate_cursor(cursor, page, size)

@router.get('/teams', response_model=PaginatedResponse, summary='List Teams', description='Browse unified teams. Entities are matched across sources using name normalization and identity mappings.')
async def get_teams(page: int=Query(1, ge=1), size: int=Query(20, ge=1, le=100), country: Optional[str]=Query(None, description='Filter by team country'), name: Optional[str]=Query(None, description='Search by team name (case-insensitive)'), include_provenance: bool=False):
    db = get_db_unified()
    query = {}
    if country:
        query['country'] = country
    if name:
        query['name'] = {'$regex': name, '$options': 'i'}
    cursor = db['teams'].find(query)
    resp = await paginate_cursor(cursor, page, size)
    if include_provenance:
        resp.items = await _attach_provenance(resp.items, db)
    return resp

@router.get('/players', response_model=PaginatedResponse, summary='List Players', description='Browse the unified player database.')
async def get_players(page: int=Query(1, ge=1), size: int=Query(20, ge=1, le=100), name: Optional[str]=Query(None, description='Search by player name'), include_provenance: bool=False):
    db = get_db_unified()
    query = {}
    if name:
        query['name'] = {'$regex': name, '$options': 'i'}
    cursor = db['players'].find(query)
    resp = await paginate_cursor(cursor, page, size)
    if include_provenance:
        resp.items = await _attach_provenance(resp.items, db)
    return resp

@router.get('/matches', response_model=PaginatedResponse, summary='List Matches', description='Access standardized match data. Supports filtering by competition, season, and participating team.')
async def get_matches(page: int=Query(1, ge=1), size: int=Query(20, ge=1, le=100), competition_id: Optional[str]=Query(None, description='Filter by unified competition ID'), season_id: Optional[str]=Query(None, description='Filter by unified season ID'), team_id: Optional[str]=Query(None, description='Filter by team (home or away)'), include_provenance: bool=False):
    db = get_db_unified()
    query = {}
    if competition_id:
        query['competition_id'] = competition_id
    if season_id:
        query['season_id'] = season_id
    if team_id:
        query['$or'] = [{'home_team_id': team_id}, {'away_team_id': team_id}]
    cursor = db['matches'].find(query).sort('match_date', -1)
    resp = await paginate_cursor(cursor, page, size)
    if include_provenance:
        resp.items = await _attach_provenance(resp.items, db)
    return resp

@router.get('/player-match-stats', response_model=PaginatedResponse, summary='Player Performance Stats', description='Query granular performance metrics for players per match (goals, xG, passes, etc.).')
async def get_all_player_stats(player_id: Optional[str]=Query(None, description='Filter by unified player ID'), match_id: Optional[str]=Query(None, description='Filter by unified match ID'), team_id: Optional[str]=Query(None, description='Filter by unified team ID'), page: int=Query(1, ge=1), size: int=Query(20, ge=1, le=100)):
    db = get_db_unified()
    query = {}
    if player_id:
        query['unified_player_id'] = player_id
    if match_id:
        query['unified_match_id'] = match_id
    if team_id:
        query['unified_team_id'] = team_id
    cursor = db['player_match_stats'].find(query).sort('goals', -1)
    return await paginate_cursor(cursor, page, size)

@router.get('/team-match-stats', response_model=PaginatedResponse, summary='Team Performance Stats', description='Query aggregated performance metrics for teams per match.')
async def get_all_team_stats(team_id: Optional[str]=Query(None, description='Filter by unified team ID'), match_id: Optional[str]=Query(None, description='Filter by unified match ID'), page: int=Query(1, ge=1), size: int=Query(20, ge=1, le=100)):
    db = get_db_unified()
    query = {}
    if team_id:
        query['unified_team_id'] = team_id
    if match_id:
        query['unified_match_id'] = match_id
    cursor = db['team_match_stats'].find(query)
    return await paginate_cursor(cursor, page, size)

@router.get('/{collection_name}/{document_id}', summary='Get Unified Document', description='Retrieve a specific normalized entity by ID with full provenance data.')
async def get_unified_document(collection_name: str, document_id: str):
    db = get_db_unified()
    allowed = ['competitions', 'seasons', 'teams', 'players', 'matches', 'player_match_stats', 'team_match_stats']
    if collection_name not in allowed:
        raise HTTPException(status_code=404, detail='Collection not found')
    query = {}
    try:
        query['_id'] = ObjectId(document_id)
    except:
        query['unified_id'] = document_id
    doc = await db[collection_name].find_one(query)
    if not doc:
        raise HTTPException(status_code=404, detail='Document not found')
    doc = Serialization.fix_ids(doc)
    u_id = doc.get('unified_id')
    if u_id:
        links = await db['source_links'].find({'unified_id': u_id}).to_list(length=10)
        doc['_provenance'] = Serialization.fix_ids(links)
    return doc