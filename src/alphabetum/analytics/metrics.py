"""
Metrics calculation for ALPHABETUM evolution analysis.

Computes derived metrics from history snapshots to assess:
- Growth velocity and acceleration
- Domain balance and entropy
- Efficiency and productivity
- Quality trends
"""

from dataclasses import dataclass
from typing import Optional
import math

from .history import HistoryTracker, IterationSnapshot


@dataclass
class GrowthMetrics:
    """Metrics related to alphabet growth."""
    total_primitives: int
    growth_rate: float  # Primitives per iteration (recent)
    growth_acceleration: float  # Change in growth rate
    doubling_time: Optional[float]  # Iterations to double at current rate
    velocity_trend: str  # "accelerating", "steady", "decelerating", "stalled"


@dataclass
class EfficiencyMetrics:
    """Metrics related to process efficiency."""
    acceptance_rate: float  # Recent acceptance rate
    acceptance_trend: str  # "improving", "stable", "declining"
    productivity: float  # Accepted primitives per iteration
    waste_ratio: float  # Rejected / Proposed


@dataclass
class BalanceMetrics:
    """Metrics related to domain balance."""
    domain_entropy: float  # Higher = more balanced (max ~2.7 for 15 domains)
    gini_coefficient: float  # Lower = more equal distribution
    coverage_by_domain: dict[str, float]
    neglected_domains: list[str]
    dominant_domains: list[str]


@dataclass
class ConvergenceMetrics:
    """Metrics related to convergence toward goals."""
    coverage_score: float
    coverage_velocity: float  # Coverage gain per iteration
    estimated_iterations_to_threshold: Optional[int]
    is_converging: bool
    convergence_confidence: float  # 0-1


@dataclass
class QualityMetrics:
    """Metrics related to alphabet quality."""
    avg_confidence: float
    confidence_trend: str
    consistency_score: float
    stability_index: float  # How stable is the alphabet


@dataclass
class SummaryMetrics:
    """Combined summary of all metrics."""
    iteration: int
    growth: GrowthMetrics
    efficiency: EfficiencyMetrics
    balance: BalanceMetrics
    convergence: ConvergenceMetrics
    quality: QualityMetrics

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "iteration": self.iteration,
            "growth": {
                "total_primitives": self.growth.total_primitives,
                "growth_rate": round(self.growth.growth_rate, 3),
                "growth_acceleration": round(self.growth.growth_acceleration, 3),
                "doubling_time": self.growth.doubling_time,
                "velocity_trend": self.growth.velocity_trend,
            },
            "efficiency": {
                "acceptance_rate": round(self.efficiency.acceptance_rate, 3),
                "acceptance_trend": self.efficiency.acceptance_trend,
                "productivity": round(self.efficiency.productivity, 3),
                "waste_ratio": round(self.efficiency.waste_ratio, 3),
            },
            "balance": {
                "domain_entropy": round(self.balance.domain_entropy, 3),
                "gini_coefficient": round(self.balance.gini_coefficient, 3),
                "neglected_domains": self.balance.neglected_domains,
                "dominant_domains": self.balance.dominant_domains,
            },
            "convergence": {
                "coverage_score": round(self.convergence.coverage_score, 3),
                "coverage_velocity": round(self.convergence.coverage_velocity, 4),
                "estimated_iterations_to_threshold": self.convergence.estimated_iterations_to_threshold,
                "is_converging": self.convergence.is_converging,
                "convergence_confidence": round(self.convergence.convergence_confidence, 3),
            },
            "quality": {
                "avg_confidence": round(self.quality.avg_confidence, 3),
                "confidence_trend": self.quality.confidence_trend,
                "consistency_score": round(self.quality.consistency_score, 3),
                "stability_index": round(self.quality.stability_index, 3),
            },
        }


class MetricsCalculator:
    """
    Calculates derived metrics from history snapshots.

    Provides insights into the health and progress of the ALPHABETUM process.
    """

    def __init__(self, history: HistoryTracker, config: Optional[dict] = None):
        self.history = history
        self.config = config or {}
        self.coverage_threshold = self.config.get("stopping", {}).get("coverage_threshold", 0.9)

    def calculate_all(self) -> Optional[SummaryMetrics]:
        """Calculate all metrics from current history."""
        snapshots = self.history.get_snapshots()
        if not snapshots:
            return None

        latest = snapshots[-1]

        return SummaryMetrics(
            iteration=latest.iteration,
            growth=self._calculate_growth(snapshots),
            efficiency=self._calculate_efficiency(snapshots),
            balance=self._calculate_balance(latest),
            convergence=self._calculate_convergence(snapshots),
            quality=self._calculate_quality(snapshots),
        )

    def _calculate_growth(self, snapshots: list[IterationSnapshot]) -> GrowthMetrics:
        """Calculate growth-related metrics."""
        if not snapshots:
            return GrowthMetrics(
                total_primitives=0, growth_rate=0, growth_acceleration=0,
                doubling_time=None, velocity_trend="stalled"
            )

        latest = snapshots[-1]
        total = latest.total_primitives

        # Calculate recent growth rate (last 5 iterations or available)
        window = min(5, len(snapshots))
        if window < 2:
            growth_rate = latest.primitives_added
            growth_acceleration = 0
        else:
            recent = snapshots[-window:]
            recent_growth = sum(s.primitives_added for s in recent)
            growth_rate = recent_growth / window

            # Calculate acceleration (change in growth rate)
            if len(snapshots) >= 2 * window:
                earlier = snapshots[-2*window:-window]
                earlier_growth = sum(s.primitives_added for s in earlier) / len(earlier)
                growth_acceleration = growth_rate - earlier_growth
            else:
                growth_acceleration = 0

        # Doubling time
        if growth_rate > 0 and total > 0:
            doubling_time = total / growth_rate
        else:
            doubling_time = None

        # Velocity trend
        if growth_rate < 0.1:
            velocity_trend = "stalled"
        elif growth_acceleration > 0.1:
            velocity_trend = "accelerating"
        elif growth_acceleration < -0.1:
            velocity_trend = "decelerating"
        else:
            velocity_trend = "steady"

        return GrowthMetrics(
            total_primitives=total,
            growth_rate=growth_rate,
            growth_acceleration=growth_acceleration,
            doubling_time=doubling_time,
            velocity_trend=velocity_trend,
        )

    def _calculate_efficiency(self, snapshots: list[IterationSnapshot]) -> EfficiencyMetrics:
        """Calculate efficiency-related metrics."""
        if not snapshots:
            return EfficiencyMetrics(
                acceptance_rate=0, acceptance_trend="stable",
                productivity=0, waste_ratio=0
            )

        latest = snapshots[-1]

        # Recent acceptance rate (last 5 iterations)
        window = min(5, len(snapshots))
        recent = snapshots[-window:]
        recent_accepted = sum(s.primitives_added for s in recent)
        recent_proposed = sum(s.candidates_proposed - (snapshots[max(0, snapshots.index(s)-1)].candidates_proposed if snapshots.index(s) > 0 else 0) for s in recent)

        if recent_proposed > 0:
            acceptance_rate = recent_accepted / recent_proposed
        else:
            acceptance_rate = latest.cumulative_acceptance_rate

        # Acceptance trend
        if len(snapshots) >= 10:
            earlier_window = snapshots[-10:-5]
            earlier_accepted = sum(s.primitives_added for s in earlier_window)
            earlier_proposed = len(earlier_window) * 2  # Approximate
            earlier_rate = earlier_accepted / earlier_proposed if earlier_proposed > 0 else 0

            if acceptance_rate > earlier_rate + 0.05:
                acceptance_trend = "improving"
            elif acceptance_rate < earlier_rate - 0.05:
                acceptance_trend = "declining"
            else:
                acceptance_trend = "stable"
        else:
            acceptance_trend = "stable"

        # Productivity
        total_iterations = len(snapshots)
        productivity = latest.total_primitives / total_iterations if total_iterations > 0 else 0

        # Waste ratio
        total_rejected = latest.candidates_proposed - latest.total_primitives
        waste_ratio = total_rejected / latest.candidates_proposed if latest.candidates_proposed > 0 else 0

        return EfficiencyMetrics(
            acceptance_rate=acceptance_rate,
            acceptance_trend=acceptance_trend,
            productivity=productivity,
            waste_ratio=waste_ratio,
        )

    def _calculate_balance(self, latest: IterationSnapshot) -> BalanceMetrics:
        """Calculate domain balance metrics."""
        counts = list(latest.domain_counts.values())
        total = sum(counts)

        # Shannon entropy
        if total > 0:
            probabilities = [c / total for c in counts if c > 0]
            entropy = -sum(p * math.log2(p) for p in probabilities)
            # Normalize by max possible entropy
            max_entropy = math.log2(15)  # 15 domains
            normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0
        else:
            entropy = 0
            normalized_entropy = 0

        # Gini coefficient
        if total > 0 and len(counts) > 1:
            sorted_counts = sorted(counts)
            n = len(sorted_counts)
            cumsum = sum((i + 1) * c for i, c in enumerate(sorted_counts))
            gini = (2 * cumsum) / (n * total) - (n + 1) / n
        else:
            gini = 0

        # Identify neglected and dominant domains
        all_domains = [d.value for d in __import__('alphabetum.state.models', fromlist=['Domain']).Domain]
        neglected = [d for d in all_domains if latest.domain_counts.get(d, 0) == 0]

        if counts:
            threshold = total / len(all_domains) * 2  # Dominant if > 2x average
            dominant = [d for d, c in latest.domain_counts.items() if c > threshold]
        else:
            dominant = []

        return BalanceMetrics(
            domain_entropy=entropy,
            gini_coefficient=gini,
            coverage_by_domain=latest.domain_ratios,
            neglected_domains=neglected,
            dominant_domains=dominant,
        )

    def _calculate_convergence(self, snapshots: list[IterationSnapshot]) -> ConvergenceMetrics:
        """Calculate convergence metrics."""
        if not snapshots:
            return ConvergenceMetrics(
                coverage_score=0, coverage_velocity=0,
                estimated_iterations_to_threshold=None,
                is_converging=False, convergence_confidence=0
            )

        latest = snapshots[-1]
        coverage = latest.coverage_score

        # Coverage velocity (average delta over last 5 iterations)
        window = min(5, len(snapshots))
        recent = snapshots[-window:]
        velocity = sum(s.coverage_delta for s in recent) / window if window > 0 else 0

        # Estimated iterations to threshold
        remaining = self.coverage_threshold - coverage
        if velocity > 0.001 and remaining > 0:
            estimated = int(remaining / velocity)
        else:
            estimated = None

        # Is converging? (positive velocity and improving trend)
        is_converging = velocity > 0.001

        # Convergence confidence (based on velocity consistency)
        if len(snapshots) >= 5:
            deltas = [s.coverage_delta for s in recent]
            if deltas:
                mean_delta = sum(deltas) / len(deltas)
                variance = sum((d - mean_delta) ** 2 for d in deltas) / len(deltas)
                # Lower variance = higher confidence
                confidence = 1.0 / (1.0 + math.sqrt(variance) * 10)
            else:
                confidence = 0.5
        else:
            confidence = 0.3  # Low confidence with little data

        return ConvergenceMetrics(
            coverage_score=coverage,
            coverage_velocity=velocity,
            estimated_iterations_to_threshold=estimated,
            is_converging=is_converging,
            convergence_confidence=confidence,
        )

    def _calculate_quality(self, snapshots: list[IterationSnapshot]) -> QualityMetrics:
        """Calculate quality metrics."""
        if not snapshots:
            return QualityMetrics(
                avg_confidence=0, confidence_trend="stable",
                consistency_score=1, stability_index=0
            )

        latest = snapshots[-1]

        # Confidence trend
        if len(snapshots) >= 5:
            recent = snapshots[-5:]
            earlier = snapshots[-10:-5] if len(snapshots) >= 10 else snapshots[:5]

            recent_conf = sum(s.avg_confidence for s in recent) / len(recent)
            earlier_conf = sum(s.avg_confidence for s in earlier) / len(earlier)

            if recent_conf > earlier_conf + 0.02:
                confidence_trend = "improving"
            elif recent_conf < earlier_conf - 0.02:
                confidence_trend = "declining"
            else:
                confidence_trend = "stable"
        else:
            confidence_trend = "stable"

        # Stability index (how consistent is acceptance rate)
        if len(snapshots) >= 3:
            rates = [s.acceptance_rate for s in snapshots[-10:]]
            mean_rate = sum(rates) / len(rates)
            variance = sum((r - mean_rate) ** 2 for r in rates) / len(rates)
            stability = 1.0 / (1.0 + math.sqrt(variance) * 5)
        else:
            stability = 0.5

        return QualityMetrics(
            avg_confidence=latest.avg_confidence,
            confidence_trend=confidence_trend,
            consistency_score=latest.consistency_score,
            stability_index=stability,
        )

    def get_trend_summary(self) -> str:
        """Get a natural language summary of current trends."""
        metrics = self.calculate_all()
        if not metrics:
            return "Insufficient data for trend analysis."

        lines = []

        # Growth summary
        g = metrics.growth
        lines.append(f"**Growth**: {g.total_primitives} primitives, {g.velocity_trend} "
                    f"({g.growth_rate:.1f}/iteration)")

        # Efficiency summary
        e = metrics.efficiency
        lines.append(f"**Efficiency**: {e.acceptance_rate:.0%} acceptance rate ({e.acceptance_trend}), "
                    f"{e.productivity:.1f} primitives/iteration")

        # Convergence summary
        c = metrics.convergence
        if c.is_converging:
            if c.estimated_iterations_to_threshold:
                lines.append(f"**Convergence**: On track, ~{c.estimated_iterations_to_threshold} iterations to "
                           f"{self.coverage_threshold:.0%} coverage (confidence: {c.convergence_confidence:.0%})")
            else:
                lines.append(f"**Convergence**: Progressing at {c.coverage_velocity:.2%}/iteration")
        else:
            lines.append(f"**Convergence**: Stalled at {c.coverage_score:.0%} coverage")

        # Balance summary
        b = metrics.balance
        if b.neglected_domains:
            lines.append(f"**Balance**: {len(b.neglected_domains)} neglected domains: "
                        f"{', '.join(b.neglected_domains[:3])}...")

        return "\n".join(lines)
