import httpx
import logging
from typing import Any, Dict, List, Optional
from ingestion.base.source_adapter import SourceAdapter
logger = logging.getLogger(__name__)

class StatsBombAdapter(SourceAdapter):
    """Adapter for StatsBomb Open Data hosted on GitHub."""
    BASE_URL = 'https://raw.githubusercontent.com/statsbomb/open-data/master/data'

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)

    async def fetch_data(self, path: str) -> Any:
        """Fetch JSON data from the specified GitHub path."""
        url = f'{self.BASE_URL}/{path}'
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f'Error fetching StatsBomb data from {url}: {e}')
            return None

    async def get_competitions(self) -> List[Dict[str, Any]]:
        return await self.fetch_data('competitions.json') or []

    async def get_matches(self, competition_id: int, season_id: int) -> List[Dict[str, Any]]:
        return await self.fetch_data(f'matches/{competition_id}/{season_id}.json') or []

    async def get_lineups(self, match_id: int) -> List[Dict[str, Any]]:
        return await self.fetch_data(f'lineups/{match_id}.json') or []

    async def get_events(self, match_id: int) -> List[Dict[str, Any]]:
        return await self.fetch_data(f'events/{match_id}.json') or []

    async def close(self):
        await self.client.aclose()