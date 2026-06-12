from datetime import datetime, timezone
from transform.pipelines.base_transformer import BaseTransformer
from transform.mapping.entity_resolver import EntityResolver
from transform.mapping.source_linker import SourceLinker
import logging
logger = logging.getLogger(__name__)

class PlayerTransformer(BaseTransformer):
    """Transforms raw players into unified player documents."""

    async def transform(self):
        run_id = await self.start_run('player')
        resolver = EntityResolver(self.unified_db)
        linker = SourceLinker(self.unified_db)
        count = 0
        try:
            if self.source_name == 'statsbomb':
                async for lineup_doc in self.source_db['lineups'].find():
                    for team_lineup in lineup_doc['lineups']:
                        for player in team_lineup['lineup']:
                            p_name = player['player_name']
                            p_id = str(player['player_id'])
                            u_id = await resolver.resolve_player(p_name)
                            await linker.link(unified_id=u_id, entity_type='player', source_name='statsbomb', source_id=p_id, source_db='statsbomb_raw', source_collection='lineups')
                            count += 1
            await self.finish_run(run_id, count)
            return count
        except Exception as e:
            logger.error(f'Player transformation failed: {e}')
            await self.finish_run(run_id, count, status='failed')
            raise