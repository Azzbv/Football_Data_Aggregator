from fastapi import APIRouter, Query, HTTPException
from app.core.database import db
from app.utils.pagination import paginate_cursor, PaginatedResponse
from app.utils.serialization import Serialization
from typing import Optional
from bson import ObjectId
router = APIRouter()
SOURCE_DB_MAP = {'statsbomb': 'statsbomb_raw', 'understat': 'understat_raw', 'fbref': 'fbref_raw'}

@router.get('/{source_name}/{collection_name}', response_model=PaginatedResponse)
async def get_raw_data_list(source_name: str, collection_name: str, page: int=Query(1, ge=1), size: int=Query(20, ge=1, le=100), sort_by: str=Query('metadata.ingested_at'), sort_desc: bool=Query(True), source_id: Optional[str]=None, match_id: Optional[int]=None, player_id: Optional[int]=None, team_id: Optional[int]=None, season: Optional[str]=None):
    if source_name not in SOURCE_DB_MAP:
        raise HTTPException(status_code=404, detail=f"Source '{source_name}' not found")
    database = db.client[SOURCE_DB_MAP[source_name]]
    query = {}
    if source_id:
        query['metadata.source_id'] = source_id
    if match_id:
        query['match_id'] = match_id
    if player_id:
        query['player_id'] = player_id
    if team_id:
        query['team_id'] = team_id
    if season:
        query['season'] = season
    sort_dir = -1 if sort_desc else 1
    cursor = database[collection_name].find(query).sort(sort_by, sort_dir)
    return await paginate_cursor(cursor, page, size)

@router.get('/{source_name}/{collection_name}/{document_id}')
async def get_raw_document(source_name: str, collection_name: str, document_id: str):
    if source_name not in SOURCE_DB_MAP:
        raise HTTPException(status_code=404, detail=f"Source '{source_name}' not found")
    database = db.client[SOURCE_DB_MAP[source_name]]
    query = {}
    try:
        query['_id'] = ObjectId(document_id)
    except:
        query['metadata.source_id'] = document_id
    doc = await database[collection_name].find_one(query)
    if not doc:
        raise HTTPException(status_code=404, detail='Document not found')
    return Serialization.fix_ids(doc)