import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.config import settings
from app.core.database import connect_to_mongo, close_mongo_connection

@pytest_asyncio.fixture(scope='function')
async def client():
    await connect_to_mongo()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as ac:
        yield ac
    await close_mongo_connection()

@pytest.mark.asyncio
async def test_health_check(client):
    """Test the health check endpoint."""
    response = await client.get('/health')
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'ok'
    assert 'database' in data

@pytest.mark.asyncio
async def test_list_sources(client):
    """Test the sources listing endpoint."""
    response = await client.get(f'{settings.API_V1_STR}/sources')
    assert response.status_code == 200
    data = response.json()
    assert 'sources' in data
    assert 'statsbomb' in data['sources']

@pytest.mark.asyncio
async def test_unified_competitions(client):
    """Test browsing unified competitions."""
    response = await client.get(f'{settings.API_V1_STR}/unified/competitions')
    assert response.status_code == 200
    data = response.json()
    assert 'items' in data
    assert 'total' in data