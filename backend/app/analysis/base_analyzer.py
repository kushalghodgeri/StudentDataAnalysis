"""BaseAnalyzer abstract class defining contract for all analytic modules."""

from abc import ABC, abstractmethod
from typing import Any, Dict
import pandas as pd


class BaseAnalyzer(ABC):
    """Abstract base analyzer class. All concrete analyzers accept a DataFrame and return dicts."""

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy() if df is not None else pd.DataFrame()

    @abstractmethod
    def analyze(self) -> Dict[str, Any]:
        """Compute analytics and return JSON-serializable dictionary."""
        raise NotImplementedError("Subclasses must implement analyze()")
