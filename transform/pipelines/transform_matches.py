from datetime import datetime, timezone
from dateutil.parser import isoparse
from transform.pipelines.base_transformer import BaseTransformer
from transform.mapping.entity_resolver import EntityResolver
from transform.mapping.source_linker import SourceLinker
import logging
logger = logging.getLogger(__name__)

class MatchTransformer(BaseTransformer):
    """Transforms raw matches into unified match documents."""

    async def transform(self):
        run_id = await self.start_run('match')
        resolver = EntityResolver(self.unified_db)
        linker = SourceLinker(self.unified_db)
        count = 0
        try:
            if self.source_name == 'statsbomb':
                async for raw_match in self.source_db['matches'].find():
                    match_id = str(raw_match['match_id'])
                    comp_u_id = f"u-comp-{raw_match['competition']['competition_id']}"
                    season_u_id = f"u-season-{raw_match['season']['season_id']}"
                    home_u_id = await resolver.resolve_team(raw_match['home_team']['home_team_name'])
                    away_u_id = await resolver.resolve_team(raw_match['away_team']['away_team_name'])
                    u_match_id = f'u-match-{match_id}'
                    unified_doc = {'unified_id': u_match_id, 'competition_id': comp_u_id, 'season_id': season_u_id, 'match_date': isoparse(raw_match['match_date']), 'home_team_id': home_u_id, 'away_team_id': away_u_id, 'home_score': raw_match['home_score'], 'away_score': raw_match['away_score'], 'status': 'played', 'updated_at': datetime.now(timezone.utc)}
                    await self.unified_db['matches'].update_one({'unified_id': u_match_id}, {'$set': unified_doc, '$setOnInsert': {'created_at': datetime.now(timezone.utc)}}, upsert=True)
                    await linker.link(unified_id=u_match_id, entity_type='match', source_name='statsbomb', source_id=match_id, source_db='statsbomb_raw', source_collection='matches')
                    count += 1
            await self.finish_run(run_id, count)
            return count
        except Exception as e:
            logger.error(f'Match transformation failed: {e}')
            await self.finish_run(run_id, count, status='failed')
            raise