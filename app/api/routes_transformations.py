from fastapi import APIRouter, Query, HTTPException
from app.core.database import get_db_unified
from app.utils.pagination import paginate_cursor, PaginatedResponse
from typing import Optional
from bson import ObjectId
router = APIRouter()

@router.get('/runs', response_model=PaginatedResponse)
async def list_transformation_runs(page: int=Query(1, ge=1), size: int=Query(20, ge=1, le=100), status: Optional[str]=None, source_name: Optional[str]=None):
    """List all transformation pipeline runs."""
    db = get_db_unified()
    query = {}
    if status:
        query['status'] = status
    if source_name:
        query['source_name'] = source_name
    cursor = db['transformation_runs'].find(query).sort('started_at', -1)
    return await paginate_cursor(cursor, page, size)

@router.get('/runs/{run_id}')
async def get_run_details(run_id: str):
    """Get detailed information for a specific transformation run."""
    db = get_db_unified()
    query = {'run_id': run_id}
    try:
        if ObjectId.is_valid(run_id):
            query = {'$or': [{'run_id': run_id}, {'_id': ObjectId(run_id)}]}
    except:
        pass
    run = await db['transformation_runs'].find_one(query)
    if not run:
        raise HTTPException(status_code=404, detail='Transformation run not found')
    run['_id'] = str(run['_id'])
    return run

@router.get('/quality-reports', response_model=PaginatedResponse)
async def list_quality_reports(page: int=Query(1, ge=1), size: int=Query(20, ge=1, le=100), entity_type: Optional[str]=None):
    """List data quality checks and reports."""
    db = get_db_unified()
    query = {}
    if entity_type:
        query['entity_type'] = entity_type
    cursor = db['quality_reports'].find(query).sort('created_at', -1)
    return await paginate_cursor(cursor, page, size)

@router.get('/stats')
async def get_overall_stats():
    """Summary statistics across the unified platform."""
    db = get_db_unified()
    collections = ['competitions', 'teams', 'players', 'matches', 'player_match_stats']
    counts = {}
    for coll in collections:
        counts[coll] = await db[coll].count_documents({})
    last_run = await db['transformation_runs'].find_one(sort=[('finished_at', -1)])
    if last_run:
        last_run['_id'] = str(last_run['_id'])
    return {'entity_counts': counts, 'last_transformation': last_run}