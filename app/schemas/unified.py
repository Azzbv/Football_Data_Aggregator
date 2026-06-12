from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class UnifiedBase(BaseModel):
    unified_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class UnifiedCompetition(UnifiedBase):
    name: str
    country: Optional[str] = None
    gender: str = 'male'
    metadata: Dict[str, Any] = {}

class UnifiedSeason(UnifiedBase):
    competition_id: str
    name: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class UnifiedTeam(UnifiedBase):
    name: str
    short_name: Optional[str] = None
    country: Optional[str] = None
    stadium: Optional[str] = None

class UnifiedPlayer(UnifiedBase):
    name: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    nationality: Optional[str] = None
    birth_date: Optional[datetime] = None
    position: Optional[str] = None

class UnifiedMatch(UnifiedBase):
    competition_id: str
    season_id: str
    match_date: datetime
    home_team_id: str
    away_team_id: str
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    status: str = 'played'

class PlayerMatchStats(UnifiedBase):
    unified_match_id: str
    unified_player_id: str
    unified_team_id: str
    minutes_played: int = 0
    goals: int = 0
    assists: int = 0
    shots: int = 0
    passes_attempted: int = 0
    passes_completed: int = 0
    xg: float = 0.0
    source_coverage: List[str] = []

class TeamMatchStats(UnifiedBase):
    unified_match_id: str
    unified_team_id: str
    goals: int = 0
    shots: int = 0
    possession_pct: float = 0.0
    xg: float = 0.0
    source_coverage: List[str] = []

class SourceLink(BaseModel):
    unified_id: str
    entity_type: str
    source_name: str
    source_id: str
    source_db: str
    source_collection: str
    linked_at: datetime = Field(default_factory=datetime.utcnow)