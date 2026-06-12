from abc import ABC, abstractmethod
from typing import Any, Dict, List

class SourceAdapter(ABC):
    """Abstract base class for all source adapters."""

    @abstractmethod
    async def fetch_data(self, endpoint: str, **kwargs) -> Any:
        """Fetch data from the source API or repository."""
        pass

class LoaderResult:
    """Model to track the results of an ingestion run."""

    def __init__(self, source_name: str):
        self.source_name = source_name
        self.counts: Dict[str, int] = {}

    def add_count(self, entity_type: str, count: int):
        self.counts[entity_type] = self.counts.get(entity_type, 0) + count

    def __str__(self):
        return f'Ingestion Results for {self.source_name}: {self.counts}'