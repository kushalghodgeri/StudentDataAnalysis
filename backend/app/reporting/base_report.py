"""Base report generation abstract class."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict


class BaseReport(ABC):
    """Abstract base class for all report generators."""

    @abstractmethod
    def generate(self) -> Dict[str, Path]:
        """Generate formatted reports and return mapping of format name to Path."""
        raise NotImplementedError("Subclasses must implement generate()")
