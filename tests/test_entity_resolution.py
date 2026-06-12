import asyncio
import pytest
import pytest_asyncio
from app.core.database import connect_to_mongo, close_mongo_connection, get_db_unified
from transform.mapping.entity_resolver import EntityResolver
from app.core.config import settings

@pytest_asyncio.fixture(scope='function')
async def mongo_db():
    await connect_to_mongo()
    db = get_db_unified()
    await db['teams'].delete_many({})
    await db['players'].delete_many({})
    await db['identity_mappings'].delete_many({})
    yield db
    await close_mongo_connection()

@pytest.mark.asyncio
async def test_team_resolution(mongo_db):
    """Test that teams are correctly resolved and deduplicated."""
    resolver = EntityResolver(mongo_db)
    team_name = 'Real Madrid'
    u_id_1 = await resolver.resolve_team(team_name)
    assert u_id_1.startswith('team-')
    u_id_2 = await resolver.resolve_team('real madrid ')
    assert u_id_1 == u_id_2
    team = await mongo_db['teams'].find_one({'unified_id': u_id_1})
    assert team['name'] == team_name
    assert team['normalized_name'] == 'real madrid'

@pytest.mark.asyncio
async def test_player_resolution(mongo_db):
    """Test player resolution logic."""
    resolver = EntityResolver(mongo_db)
    p_name = 'Lionel Messi'
    u_id_1 = await resolver.resolve_player(p_name)
    assert u_id_1.startswith('player-')
    u_id_2 = await resolver.resolve_player('lionel messi')
    assert u_id_1 == u_id_2

@pytest.mark.asyncio
async def test_concurrent_team_resolution(mongo_db):
    """Verify that concurrent resolutions do not create duplicate records."""
    resolver = EntityResolver(mongo_db)
    team_name = 'Concurrent Team'
    results = await asyncio.gather(*[resolver.resolve_team(team_name) for _ in range(20)])
    assert len(set(results)) == 1
    count = await mongo_db['teams'].count_documents({'normalized_name': 'concurrent team'})
    assert count == 1
    mapping_count = await mongo_db['identity_mappings'].count_documents({'alias': 'concurrent team'})
    assert mapping_count == 1