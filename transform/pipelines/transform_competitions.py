from datetime import datetime, timezone
from transform.pipelines.base_transformer import BaseTransformer
from transform.mapping.source_linker import SourceLinker
import logging
logger = logging.getLogger(__name__)

class CompetitionTransformer(BaseTransformer):
    """Transforms raw competitions into unified documents."""

    async def transform(self):
        run_id = await self.start_run('competition')
        linker = SourceLinker(self.unified_db)
        count = 0
        try:
            if self.source_name == 'statsbomb':
                async for raw_comp in self.source_db['competitions'].find():
                    u_id = f"u-comp-{raw_comp['competition_id']}"
                    unified_doc = {'unified_id': u_id, 'name': raw_comp['competition_name'], 'country': raw_comp.get('country_name'), 'gender': raw_comp.get('competition_gender', 'male'), 'updated_at': datetime.now(timezone.utc)}
                    await self.unified_db['competitions'].update_one({'unified_id': u_id}, {'$set': unified_doc, '$setOnInsert': {'created_at': datetime.now(timezone.utc)}}, upsert=True)
                    await linker.link(unified_id=u_id, entity_type='competition', source_name='statsbomb', source_id=str(raw_comp['competition_id']), source_db='statsbomb_raw', source_collection='competitions')
                    s_u_id = f"u-season-{raw_comp['season_id']}"
                    season_doc = {'unified_id': s_u_id, 'competition_id': u_id, 'name': raw_comp['season_name'], 'updated_at': datetime.now(timezone.utc)}
                    await self.unified_db['seasons'].update_one({'unified_id': s_u_id}, {'$set': season_doc, '$setOnInsert': {'created_at': datetime.now(timezone.utc)}}, upsert=True)
                    count += 1
            await self.finish_run(run_id, count)
            return count
        except Exception as e:
            logger.error(f'Competition transformation failed: {e}')
            await self.finish_run(run_id, count, status='failed')
            raise