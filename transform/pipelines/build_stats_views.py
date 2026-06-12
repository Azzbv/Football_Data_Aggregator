from datetime import datetime, timezone
from typing import Dict, Any, List
from transform.pipelines.base_transformer import BaseTransformer
from transform.mapping.entity_resolver import EntityResolver
import logging
logger = logging.getLogger(__name__)

class StatsTransformer(BaseTransformer):
    """Derives player and team match stats from raw events."""

    async def transform(self):
        run_id = await self.start_run('stats_view')
        resolver = EntityResolver(self.unified_db)
        count = 0
        try:
            if self.source_name == 'statsbomb':
                cursor = self.unified_db['source_links'].find({'source_name': 'statsbomb', 'entity_type': 'match'})
                async for link in cursor:
                    u_match_id = link['unified_id']
                    s_match_id = int(link['source_id'])
                    player_stats: Dict[str, Dict[str, Any]] = {}
                    team_stats: Dict[str, Dict[str, Any]] = {}
                    async for event in self.source_db['events'].find({'match_id': s_match_id}):
                        team_id = str(event['team']['id'])
                        team_name = event['team']['name']
                        if team_id not in team_stats:
                            u_team_id = await resolver.resolve_team(team_name)
                            team_stats[team_id] = {'unified_id': f'ts-{u_match_id}-{u_team_id}', 'unified_match_id': u_match_id, 'unified_team_id': u_team_id, 'goals': 0, 'shots': 0, 'xg': 0.0, 'source_coverage': ['statsbomb']}
                        if 'player' in event:
                            p_id = str(event['player']['id'])
                            p_name = event['player']['name']
                            if p_id not in player_stats:
                                u_player_id = await resolver.resolve_player(p_name)
                                player_stats[p_id] = {'unified_id': f'ps-{u_match_id}-{u_player_id}', 'unified_match_id': u_match_id, 'unified_player_id': u_player_id, 'unified_team_id': team_stats[team_id]['unified_team_id'], 'goals': 0, 'assists': 0, 'shots': 0, 'passes_attempted': 0, 'passes_completed': 0, 'xg': 0.0, 'source_coverage': ['statsbomb']}
                            stats = player_stats[p_id]
                            e_type = event['type']['name']
                            if e_type == 'Shot':
                                stats['shots'] += 1
                                team_stats[team_id]['shots'] += 1
                                xg = event.get('shot', {}).get('statsbomb_xg', 0.0)
                                stats['xg'] += xg
                                team_stats[team_id]['xg'] += xg
                                if event.get('shot', {}).get('outcome', {}).get('name') == 'Goal':
                                    stats['goals'] += 1
                                    team_stats[team_id]['goals'] += 1
                            elif e_type == 'Pass':
                                stats['passes_attempted'] += 1
                                if 'outcome' not in event['pass']:
                                    stats['passes_completed'] += 1
                                    if event['pass'].get('goal_assist'):
                                        stats['assists'] += 1
                    if player_stats:
                        for p_stat in player_stats.values():
                            p_stat['updated_at'] = datetime.now(timezone.utc)
                            await self.unified_db['player_match_stats'].update_one({'unified_id': p_stat['unified_id']}, {'$set': p_stat, '$setOnInsert': {'created_at': datetime.now(timezone.utc)}}, upsert=True)
                    if team_stats:
                        for t_stat in team_stats.values():
                            t_stat['updated_at'] = datetime.now(timezone.utc)
                            await self.unified_db['team_match_stats'].update_one({'unified_id': t_stat['unified_id']}, {'$set': t_stat, '$setOnInsert': {'created_at': datetime.now(timezone.utc)}}, upsert=True)
                    count += 1
                    if count % 10 == 0:
                        logger.info(f'Processed stats for {count} matches')
            await self.finish_run(run_id, count)
            return count
        except Exception as e:
            logger.error(f'Stats transformation failed: {e}')
            await self.finish_run(run_id, count, status='failed')
            raise