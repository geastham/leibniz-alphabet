"""
History tracking for ALPHABETUM evolution.

Captures snapshots of the alphabet state at each iteration to enable
longitudinal analysis of growth, convergence, and adaptation patterns.
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional
import yaml
import json

from ..state.manager import StateManager
from ..state.models import Domain


@dataclass
class IterationSnapshot:
    """Snapshot of alphabet state at a specific iteration."""
    iteration: int
    timestamp: datetime

    # Counts
    total_primitives: int
    primitives_added: int
    primitives_rejected: int
    candidates_proposed: int

    # Rates
    acceptance_rate: float
    cumulative_acceptance_rate: float

    # Coverage
    coverage_score: float
    coverage_delta: float  # Change from previous iteration

    # Domain distribution
    domain_counts: dict[str, int] = field(default_factory=dict)
    domain_ratios: dict[str, float] = field(default_factory=dict)

    # Quality metrics
    avg_confidence: float = 0.0
    consistency_score: float = 1.0

    # Strategy state
    phase: str = "EXPANSION"
    proposer_mode: str = "DOMAIN_SWEEP"
    priority_domains: list[str] = field(default_factory=list)

    # Gaps
    gaps_count: int = 0
    top_gaps: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "iteration": self.iteration,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "counts": {
                "total_primitives": self.total_primitives,
                "primitives_added": self.primitives_added,
                "primitives_rejected": self.primitives_rejected,
                "candidates_proposed": self.candidates_proposed,
            },
            "rates": {
                "acceptance_rate": round(self.acceptance_rate, 4),
                "cumulative_acceptance_rate": round(self.cumulative_acceptance_rate, 4),
            },
            "coverage": {
                "score": round(self.coverage_score, 4),
                "delta": round(self.coverage_delta, 4),
            },
            "domains": {
                "counts": self.domain_counts,
                "ratios": {k: round(v, 4) for k, v in self.domain_ratios.items()},
            },
            "quality": {
                "avg_confidence": round(self.avg_confidence, 4),
                "consistency_score": round(self.consistency_score, 4),
            },
            "strategy": {
                "phase": self.phase,
                "proposer_mode": self.proposer_mode,
                "priority_domains": self.priority_domains,
            },
            "gaps": {
                "count": self.gaps_count,
                "top": self.top_gaps[:5],
            },
        }


class HistoryTracker:
    """
    Tracks the evolution of the alphabet across iterations.

    Maintains a time series of snapshots that can be analyzed for:
    - Growth curves
    - Convergence patterns
    - Strategy effectiveness
    - Domain balance evolution
    """

    def __init__(self, state_manager: StateManager):
        self.state_manager = state_manager
        self.base_path = state_manager.base_path
        self.history_file = self.base_path / "analytics" / "history.yaml"
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        self._snapshots: list[IterationSnapshot] = []
        self._load_history()

    def _load_history(self) -> None:
        """Load existing history from file."""
        if self.history_file.exists():
            with open(self.history_file) as f:
                data = yaml.safe_load(f) or {}

            for snap_data in data.get("snapshots", []):
                self._snapshots.append(self._parse_snapshot(snap_data))

    def _parse_snapshot(self, data: dict) -> IterationSnapshot:
        """Parse a snapshot from stored data."""
        counts = data.get("counts", {})
        rates = data.get("rates", {})
        coverage = data.get("coverage", {})
        domains = data.get("domains", {})
        quality = data.get("quality", {})
        strategy = data.get("strategy", {})
        gaps = data.get("gaps", {})

        timestamp = data.get("timestamp")
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))

        return IterationSnapshot(
            iteration=data.get("iteration", 0),
            timestamp=timestamp or datetime.utcnow(),
            total_primitives=counts.get("total_primitives", 0),
            primitives_added=counts.get("primitives_added", 0),
            primitives_rejected=counts.get("primitives_rejected", 0),
            candidates_proposed=counts.get("candidates_proposed", 0),
            acceptance_rate=rates.get("acceptance_rate", 0),
            cumulative_acceptance_rate=rates.get("cumulative_acceptance_rate", 0),
            coverage_score=coverage.get("score", 0),
            coverage_delta=coverage.get("delta", 0),
            domain_counts=domains.get("counts", {}),
            domain_ratios=domains.get("ratios", {}),
            avg_confidence=quality.get("avg_confidence", 0),
            consistency_score=quality.get("consistency_score", 1),
            phase=strategy.get("phase", "EXPANSION"),
            proposer_mode=strategy.get("proposer_mode", "DOMAIN_SWEEP"),
            priority_domains=strategy.get("priority_domains", []),
            gaps_count=gaps.get("count", 0),
            top_gaps=gaps.get("top", []),
        )

    def _save_history(self) -> None:
        """Save history to file."""
        data = {
            "version": "1.0.0",
            "last_updated": datetime.utcnow().isoformat() + "Z",
            "total_snapshots": len(self._snapshots),
            "snapshots": [s.to_dict() for s in self._snapshots],
        }
        with open(self.history_file, "w") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)

    def capture_snapshot(self) -> IterationSnapshot:
        """
        Capture current state as a snapshot.

        Should be called at the end of each iteration.
        """
        state = self.state_manager.load_iteration_state()
        primitives = self.state_manager.load_alphabet_index()

        # Get previous snapshot for deltas
        prev = self._snapshots[-1] if self._snapshots else None
        prev_total = prev.total_primitives if prev else 0
        prev_coverage = prev.coverage_score if prev else 0

        # Calculate domain distribution
        domain_counts: dict[str, int] = {}
        total_confidence = 0.0

        for p in primitives:
            domain = p.domain.value
            domain_counts[domain] = domain_counts.get(domain, 0) + 1
            total_confidence += p.confidence

        total = len(primitives)
        domain_ratios = {
            d: c / total if total > 0 else 0
            for d, c in domain_counts.items()
        }

        # Calculate rates
        proposed_this_iter = state.total_proposed - (prev.candidates_proposed if prev else 0) if prev else state.total_proposed
        accepted_this_iter = total - prev_total
        rejected_this_iter = proposed_this_iter - accepted_this_iter if proposed_this_iter > 0 else 0

        acceptance_rate = accepted_this_iter / proposed_this_iter if proposed_this_iter > 0 else 0
        cumulative_rate = state.total_accepted / state.total_proposed if state.total_proposed > 0 else 0

        snapshot = IterationSnapshot(
            iteration=state.current_iteration,
            timestamp=datetime.utcnow(),
            total_primitives=total,
            primitives_added=accepted_this_iter,
            primitives_rejected=rejected_this_iter,
            candidates_proposed=state.total_proposed,
            acceptance_rate=acceptance_rate,
            cumulative_acceptance_rate=cumulative_rate,
            coverage_score=state.coverage_score,
            coverage_delta=state.coverage_score - prev_coverage,
            domain_counts=domain_counts,
            domain_ratios=domain_ratios,
            avg_confidence=total_confidence / total if total > 0 else 0,
            consistency_score=state.consistency_score,
            phase=state.phase.value,
            proposer_mode=state.proposer_mode,
            priority_domains=[d.value for d in state.domains_priority],
            gaps_count=len(state.gaps_to_fill),
            top_gaps=state.gaps_to_fill[:5],
        )

        self._snapshots.append(snapshot)
        self._save_history()

        return snapshot

    def get_snapshots(self) -> list[IterationSnapshot]:
        """Get all snapshots."""
        return self._snapshots.copy()

    def get_latest(self) -> Optional[IterationSnapshot]:
        """Get the most recent snapshot."""
        return self._snapshots[-1] if self._snapshots else None

    def get_time_series(self, metric: str) -> list[tuple[int, float]]:
        """
        Get a time series for a specific metric.

        Returns list of (iteration, value) tuples.
        """
        series = []
        for snap in self._snapshots:
            value = self._extract_metric(snap, metric)
            if value is not None:
                series.append((snap.iteration, value))
        return series

    def _extract_metric(self, snap: IterationSnapshot, metric: str) -> Optional[float]:
        """Extract a metric value from a snapshot."""
        metric_map = {
            "total_primitives": snap.total_primitives,
            "primitives_added": snap.primitives_added,
            "acceptance_rate": snap.acceptance_rate,
            "cumulative_acceptance_rate": snap.cumulative_acceptance_rate,
            "coverage_score": snap.coverage_score,
            "coverage_delta": snap.coverage_delta,
            "avg_confidence": snap.avg_confidence,
            "consistency_score": snap.consistency_score,
            "gaps_count": snap.gaps_count,
        }
        return metric_map.get(metric)

    def get_domain_evolution(self) -> dict[str, list[tuple[int, int]]]:
        """
        Get domain count evolution over time.

        Returns dict mapping domain -> [(iteration, count), ...]
        """
        evolution: dict[str, list[tuple[int, int]]] = {}

        for snap in self._snapshots:
            for domain, count in snap.domain_counts.items():
                if domain not in evolution:
                    evolution[domain] = []
                evolution[domain].append((snap.iteration, count))

        return evolution

    def export_to_csv(self, filepath: Path) -> None:
        """Export history to CSV for external analysis."""
        import csv

        if not self._snapshots:
            return

        # Collect all domain names
        all_domains = set()
        for snap in self._snapshots:
            all_domains.update(snap.domain_counts.keys())
        all_domains = sorted(all_domains)

        headers = [
            "iteration", "timestamp",
            "total_primitives", "primitives_added", "candidates_proposed",
            "acceptance_rate", "cumulative_acceptance_rate",
            "coverage_score", "coverage_delta",
            "avg_confidence", "consistency_score",
            "phase", "proposer_mode", "gaps_count",
        ] + [f"domain_{d}" for d in all_domains]

        with open(filepath, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(headers)

            for snap in self._snapshots:
                row = [
                    snap.iteration,
                    snap.timestamp.isoformat() if snap.timestamp else "",
                    snap.total_primitives,
                    snap.primitives_added,
                    snap.candidates_proposed,
                    snap.acceptance_rate,
                    snap.cumulative_acceptance_rate,
                    snap.coverage_score,
                    snap.coverage_delta,
                    snap.avg_confidence,
                    snap.consistency_score,
                    snap.phase,
                    snap.proposer_mode,
                    snap.gaps_count,
                ] + [snap.domain_counts.get(d, 0) for d in all_domains]
                writer.writerow(row)

    def export_to_json(self, filepath: Path) -> None:
        """Export history to JSON for external analysis."""
        data = {
            "metadata": {
                "version": "1.0.0",
                "exported_at": datetime.utcnow().isoformat() + "Z",
                "total_iterations": len(self._snapshots),
            },
            "snapshots": [s.to_dict() for s in self._snapshots],
        }
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
