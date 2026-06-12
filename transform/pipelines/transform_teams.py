from datetime import datetime, timezone
from transform.pipelines.base_transformer import BaseTransformer
from transform.mapping.entity_resolver import EntityResolver
from transform.mapping.source_linker import SourceLinker
import logging
logger = logging.getLogger(__name__)

class TeamTransformer(BaseTransformer):
    """Transforms raw teams into unified documents with entity resolution."""

    async def transform(self):
        run_id = await self.start_run('team')
        resolver = EntityResolver(self.unified_db)
        linker = SourceLinker(self.unified_db)
        count = 0
        try:
            if self.source_name == 'statsbomb':
                async for match in self.source_db['matches'].find():
                    for side in ['home_team', 'away_team']:
                        team_data = match[side]
                        team_name = team_data[f'{side}_name']
                        source_id = str(team_data[f'{side}_id'])
                        u_id = await resolver.resolve_team(team_name)
                        await linker.link(unified_id=u_id, entity_type='team', source_name='statsbomb', source_id=source_id, source_db='statsbomb_raw', source_collection='matches')
                        count += 1
            elif self.source_name == 'understat':
                async for team in self.source_db['teams'].find():
                    team_name = team['title']
                    source_id = str(team['id'])
                    u_id = await resolver.resolve_team(team_name)
                    await linker.link(unified_id=u_id, entity_type='team', source_name='understat', source_id=source_id, source_db='understat_raw', source_collection='teams')
                    count += 1
            await self.finish_run(run_id, count)
            return count
        except Exception as e:
            logger.error(f'Team transformation failed: {e}')
            await self.finish_run(run_id, count, status='failed')
            raise