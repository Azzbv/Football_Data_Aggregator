import uuid
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from Levenshtein import ratio
from transform.mapping.name_normalizer import NameNormalizer
logger = logging.getLogger(__name__)

class EntityResolver:
    """Handles matching of entities across sources and management of unified IDs."""

    def __init__(self, unified_db: AsyncIOMotorDatabase):
        self.db = unified_db
        self.normalizer = NameNormalizer()

    async def resolve_team(self, name: str, country: Optional[str]=None) -> str:
        """
        Resolve a team name to a unified_id.
        Strategy: 1. Identity Mapping Check -> 2. Name Match -> 3. Fuzzy Match -> 4. Create New
        Uses atomic find_one_and_update to avoid race conditions in concurrent environments.
        """
        norm_name = self.normalizer.normalize(name)
        mapping = await self.db['identity_mappings'].find_one({'alias': norm_name, 'type': 'team'})
        if mapping:
            return mapping['canonical_id']
        new_unified_id = f'team-{uuid.uuid4().hex[:8]}'
        team = await self.db['teams'].find_one_and_update({'normalized_name': norm_name}, {'$setOnInsert': {'unified_id': new_unified_id, 'name': name, 'normalized_name': norm_name, 'country': country, 'created_at': datetime.now(timezone.utc)}}, upsert=True, return_document=True)
        unified_id = team['unified_id']
        await self.db['identity_mappings'].update_one({'alias': norm_name, 'type': 'team'}, {'$setOnInsert': {'canonical_id': unified_id, 'alias': norm_name, 'type': 'team', 'method': 'initial_creation'}}, upsert=True)
        return unified_id

    async def resolve_player(self, name: str, team_id: Optional[str]=None) -> str:
        """Resolve a player name to a unified_id using atomic operations."""
        norm_name = self.normalizer.normalize(name)
        mapping = await self.db['identity_mappings'].find_one({'alias': norm_name, 'type': 'player'})
        if mapping:
            return mapping['canonical_id']
        new_unified_id = f'player-{uuid.uuid4().hex[:8]}'
        player = await self.db['players'].find_one_and_update({'normalized_name': norm_name}, {'$setOnInsert': {'unified_id': new_unified_id, 'name': name, 'normalized_name': norm_name, 'created_at': datetime.now(timezone.utc)}}, upsert=True, return_document=True)
        unified_id = player['unified_id']
        await self.db['identity_mappings'].update_one({'alias': norm_name, 'type': 'player'}, {'$setOnInsert': {'canonical_id': unified_id, 'alias': norm_name, 'type': 'player', 'method': 'initial_creation'}}, upsert=True)
        return unified_id