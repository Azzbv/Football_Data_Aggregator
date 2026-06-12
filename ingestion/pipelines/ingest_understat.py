import logging
import uuid
from typing import List, Optional, Dict, Any
from app.core.database import get_db_understat
from app.services.raw_browser import RawRepository
from ingestion.sources.understat_adapter import UnderstatAdapter
from ingestion.base.source_adapter import LoaderResult
logger = logging.getLogger(__name__)

async def ingest_understat(leagues: List[str], years: List[int], limit_matches: Optional[int]=None, use_mock: bool=False):
    """
    Pipeline to ingest Understat data.
    Processes leagues -> years -> teams/matches -> shots.
    """
    run_id = str(uuid.uuid4())
    db = get_db_understat()
    adapter = UnderstatAdapter(use_mock=use_mock)
    result = LoaderResult('Understat')
    try:
        logger.info(f'Starting Understat ingestion run: {run_id}')
        match_repo = RawRepository(db['matches'], 'understat', 'match')
        team_repo = RawRepository(db['teams'], 'understat', 'team')
        shot_repo = RawRepository(db['shots'], 'understat', 'shot')
        for league in leagues:
            for year in years:
                logger.info(f'Ingesting {league} for season {year}')
                data = await adapter.get_league_data(league, year)
                teams_data = data.get('teams', {})
                if teams_data:
                    for team_id, team_info in teams_data.items():
                        team_info['id'] = team_id
                        await team_repo.upsert(str(team_id), team_info, run_id)
                    result.add_count('teams', len(teams_data))
                matches_data = data.get('matches', [])
                if matches_data:
                    await match_repo.bulk_upsert(matches_data, 'id', run_id)
                    result.add_count('matches', len(matches_data))
                    matches_to_process = matches_data[:limit_matches] if limit_matches else matches_data
                    for match in matches_to_process:
                        match_id = match['id']
                        if match.get('isResult'):
                            shots_data = await adapter.get_match_shots(match_id)
                            if shots_data:
                                await shot_repo.upsert(str(match_id), {'match_id': match_id, 'shots': shots_data}, run_id)
                                result.add_count('shot_sets', 1)
                logger.info(f'Finished {league} {year}')
        logger.info(f'Understat ingestion complete. {result}')
        return result
    finally:
        await adapter.close()