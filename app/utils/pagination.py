from typing import List, Any, Optional
from pydantic import BaseModel
from app.utils.serialization import Serialization

class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    size: int
    has_more: bool

async def paginate_cursor(cursor, page: int, size: int) -> PaginatedResponse:
    """Standardized helper to paginate a MongoDB cursor with serialization."""
    items = await cursor.skip((page - 1) * size).limit(size).to_list(length=size)
    items = Serialization.fix_ids(items)
    try:
        total = await cursor.collection.count_documents(cursor.delegate._QueryBatch__filter or {})
    except:
        total = len(items)
    return PaginatedResponse(items=items, total=total, page=page, size=size, has_more=page * size < total)