import httpx
import logging
import re
import json
import uuid
from typing import Any, Dict, List, Optional
from ingestion.base.source_adapter import SourceAdapter
logger = logging.getLogger(__name__)

class UnderstatAdapter(SourceAdapter):
    """
    Adapter for Understat.com data.
    Demonstrates scraping-based ingestion with a fallback to simulated data 
    for environment stability in the portfolio demo.
    """
    BASE_URL = 'https://understat.com'

    def __init__(self, use_mock: bool=True):
        self.use_mock = use_mock
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        self.client = httpx.AsyncClient(headers=self.headers, timeout=30.0)

    async def fetch_data(self, url: str) -> str:
        if self.use_mock:
            return ''
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f'Error fetching Understat data from {url}: {e}')
            return ''

    def _extract_json(self, html: str, var_name: str) -> Optional[Any]:
        pattern = f"var {var_name}\\s+=\\s+JSON.parse\\('(.*?)'\\);"
        match = re.search(pattern, html)
        if match:
            data_str = match.group(1)
            try:
                decoded_str = re.sub('\\\\x([0-9a-fA-F]{2})', lambda m: chr(int(m.group(1), 16)), data_str)
                return json.loads(decoded_str)
            except (json.JSONDecodeError, ValueError) as e:
                logger.error(f'Failed to decode Understat JSON for {var_name}: {e}. Data snippet: {data_str[:100]}...')
                return None
        return None

    async def get_league_data(self, league: str, year: int) -> Dict[str, Any]:
        if self.use_mock:
            return {'matches': [{'id': 22221, 'isResult': True, 'h': {'title': 'Team A'}, 'a': {'title': 'Team B'}, 'datetime': '2023-08-11 20:00:00'}, {'id': 22222, 'isResult': True, 'h': {'title': 'Team C'}, 'a': {'title': 'Team D'}, 'datetime': '2023-08-12 15:00:00'}], 'teams': {'101': {'title': 'Team A', 'id': '101'}, '102': {'title': 'Team B', 'id': '102'}, '103': {'title': 'Team C', 'id': '103'}, '104': {'title': 'Team D', 'id': '104'}}}
        url = f'{self.BASE_URL}/league/{league}/{year}'
        html = await self.fetch_data(url)
        if not html:
            return {}
        return {'matches': self._extract_json(html, 'datesData'), 'teams': self._extract_json(html, 'teamsData')}

    async def get_match_shots(self, match_id: int) -> Dict[str, Any]:
        if self.use_mock:
            return {'h': [{'id': str(uuid.uuid4()), 'x': '0.5', 'y': '0.5', 'result': 'Goal', 'player': 'Player 1'}], 'a': [{'id': str(uuid.uuid4()), 'x': '0.1', 'y': '0.2', 'result': 'SavedShot', 'player': 'Player 2'}]}
        url = f'{self.BASE_URL}/match/{match_id}'
        html = await self.fetch_data(url)
        if not html:
            return {}
        return self._extract_json(html, 'shotsData') or {}

    async def close(self):
        await self.client.aclose()