"""
Analytics module for tracking ALPHABETUM evolution over time.

Provides metrics for:
- Growth patterns
- Convergence indicators
- Domain balance
- Acceptance/rejection trends
"""

from .history import HistoryTracker, IterationSnapshot
from .metrics import MetricsCalculator
from .convergence import ConvergenceAnalyzer

__all__ = [
    "HistoryTracker",
    "IterationSnapshot",
    "MetricsCalculator",
    "ConvergenceAnalyzer",
]
