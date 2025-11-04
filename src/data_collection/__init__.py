from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, Mapping, Any


class DataCollector(ABC):
    """Abstract interface for data collectors.

    Implementations should fetch data from a source (API, file, DB) and yield
    normalized records as mappings (e.g., dictionaries) suitable for downstream
    processing.
    """

    @abstractmethod
    def collect(self) -> Iterable[Mapping[str, Any]]:
        """Yield normalized records from the data source.

        Returns:
            An iterable of mapping-like records.
        """
        raise NotImplementedError
