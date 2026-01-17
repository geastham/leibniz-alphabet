"""
Convergence analysis for ALPHABETUM.

Provides tools to assess whether the alphabet construction is converging
toward its goals or has stalled/diverged.
"""

from dataclasses import dataclass, field
from typing import Optional
import math

from .history import HistoryTracker, IterationSnapshot


@dataclass
class ConvergenceIndicator:
    """A single convergence indicator."""
    name: str
    value: float
    status: str  # "converging", "stable", "diverging", "insufficient_data"
    confidence: float
    interpretation: str


@dataclass
class ConvergenceReport:
    """Full convergence analysis report."""
    iteration: int
    overall_status: str  # "converging", "stable", "at_risk", "stalled"
    overall_confidence: float

    indicators: list[ConvergenceIndicator] = field(default_factory=list)

    projected_completion: Optional[int] = None  # Estimated iterations to goal
    risk_factors: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "iteration": self.iteration,
            "overall_status": self.overall_status,
            "overall_confidence": round(self.overall_confidence, 3),
            "projected_completion": self.projected_completion,
            "indicators": [
                {
                    "name": i.name,
                    "value": round(i.value, 4),
                    "status": i.status,
                    "confidence": round(i.confidence, 3),
                    "interpretation": i.interpretation,
                }
                for i in self.indicators
            ],
            "risk_factors": self.risk_factors,
            "recommendations": self.recommendations,
        }


class ConvergenceAnalyzer:
    """
    Analyzes convergence patterns in the ALPHABETUM process.

    Uses multiple indicators to assess whether the system is making
    progress toward its goals or has entered a state of diminishing returns.
    """

    def __init__(self, history: HistoryTracker, config: Optional[dict] = None):
        self.history = history
        self.config = config or {}
        self.coverage_threshold = self.config.get("stopping", {}).get("coverage_threshold", 0.9)
        self.diminishing_window = self.config.get("stopping", {}).get("diminishing_returns_window", 10)

    def analyze(self) -> ConvergenceReport:
        """Perform full convergence analysis."""
        snapshots = self.history.get_snapshots()

        if len(snapshots) < 3:
            return ConvergenceReport(
                iteration=snapshots[-1].iteration if snapshots else 0,
                overall_status="insufficient_data",
                overall_confidence=0.2,
                indicators=[],
                risk_factors=["Insufficient iteration history for meaningful analysis"],
                recommendations=["Continue running to gather more data"],
            )

        indicators = [
            self._analyze_coverage_convergence(snapshots),
            self._analyze_growth_sustainability(snapshots),
            self._analyze_acceptance_stability(snapshots),
            self._analyze_diminishing_returns(snapshots),
            self._analyze_domain_saturation(snapshots),
        ]

        # Calculate overall status
        converging_count = sum(1 for i in indicators if i.status == "converging")
        stable_count = sum(1 for i in indicators if i.status == "stable")
        diverging_count = sum(1 for i in indicators if i.status == "diverging")

        if converging_count >= 3:
            overall_status = "converging"
        elif diverging_count >= 2:
            overall_status = "at_risk"
        elif stable_count >= 3:
            overall_status = "stable"
        else:
            overall_status = "mixed"

        # Overall confidence (weighted average)
        weights = [i.confidence for i in indicators]
        values = [1 if i.status == "converging" else 0.5 if i.status == "stable" else 0 for i in indicators]
        overall_confidence = sum(w * v for w, v in zip(weights, values)) / sum(weights) if weights else 0.5

        # Projected completion
        coverage_indicator = next((i for i in indicators if i.name == "coverage_convergence"), None)
        if coverage_indicator and coverage_indicator.status == "converging":
            projected = self._project_completion(snapshots)
        else:
            projected = None

        # Risk factors and recommendations
        risk_factors = self._identify_risk_factors(snapshots, indicators)
        recommendations = self._generate_recommendations(snapshots, indicators, risk_factors)

        return ConvergenceReport(
            iteration=snapshots[-1].iteration,
            overall_status=overall_status,
            overall_confidence=overall_confidence,
            indicators=indicators,
            projected_completion=projected,
            risk_factors=risk_factors,
            recommendations=recommendations,
        )

    def _analyze_coverage_convergence(self, snapshots: list[IterationSnapshot]) -> ConvergenceIndicator:
        """Analyze whether coverage is converging toward threshold."""
        if len(snapshots) < 2:
            return ConvergenceIndicator(
                name="coverage_convergence",
                value=0,
                status="insufficient_data",
                confidence=0.2,
                interpretation="Need more iterations to assess coverage trend"
            )

        # Calculate coverage velocity (recent 5 iterations)
        window = min(5, len(snapshots))
        recent = snapshots[-window:]
        deltas = [s.coverage_delta for s in recent]
        avg_delta = sum(deltas) / len(deltas)

        # Variance in deltas (consistency)
        variance = sum((d - avg_delta) ** 2 for d in deltas) / len(deltas)
        consistency = 1.0 / (1.0 + math.sqrt(variance) * 10)

        current_coverage = snapshots[-1].coverage_score
        remaining = self.coverage_threshold - current_coverage

        if avg_delta > 0.005 and remaining > 0:
            status = "converging"
            interpretation = f"Coverage increasing at {avg_delta:.2%}/iteration, {remaining:.1%} remaining"
        elif avg_delta > 0:
            status = "stable"
            interpretation = f"Coverage slowly increasing at {avg_delta:.3%}/iteration"
        elif current_coverage >= self.coverage_threshold * 0.95:
            status = "converging"
            interpretation = f"Near threshold at {current_coverage:.1%}"
        else:
            status = "diverging"
            interpretation = f"Coverage stalled or declining at {current_coverage:.1%}"

        return ConvergenceIndicator(
            name="coverage_convergence",
            value=avg_delta,
            status=status,
            confidence=consistency,
            interpretation=interpretation,
        )

    def _analyze_growth_sustainability(self, snapshots: list[IterationSnapshot]) -> ConvergenceIndicator:
        """Analyze whether primitive growth is sustainable."""
        if len(snapshots) < 5:
            return ConvergenceIndicator(
                name="growth_sustainability",
                value=0,
                status="insufficient_data",
                confidence=0.3,
                interpretation="Need more iterations to assess growth sustainability"
            )

        # Compare recent growth to earlier growth
        mid = len(snapshots) // 2
        recent = snapshots[mid:]
        earlier = snapshots[:mid]

        recent_growth = sum(s.primitives_added for s in recent) / len(recent)
        earlier_growth = sum(s.primitives_added for s in earlier) / len(earlier)

        if earlier_growth > 0:
            growth_ratio = recent_growth / earlier_growth
        else:
            growth_ratio = recent_growth if recent_growth > 0 else 0

        if growth_ratio > 0.8:
            status = "converging"
            interpretation = f"Growth sustained at {growth_ratio:.0%} of initial rate"
        elif growth_ratio > 0.4:
            status = "stable"
            interpretation = f"Growth slowing to {growth_ratio:.0%} of initial rate"
        else:
            status = "diverging"
            interpretation = f"Growth collapsed to {growth_ratio:.0%} of initial rate"

        # Confidence based on data volume
        confidence = min(0.9, len(snapshots) / 20)

        return ConvergenceIndicator(
            name="growth_sustainability",
            value=growth_ratio,
            status=status,
            confidence=confidence,
            interpretation=interpretation,
        )

    def _analyze_acceptance_stability(self, snapshots: list[IterationSnapshot]) -> ConvergenceIndicator:
        """Analyze stability of acceptance rate."""
        if len(snapshots) < 3:
            return ConvergenceIndicator(
                name="acceptance_stability",
                value=0,
                status="insufficient_data",
                confidence=0.3,
                interpretation="Need more iterations to assess acceptance stability"
            )

        rates = [s.acceptance_rate for s in snapshots[-10:]]
        avg_rate = sum(rates) / len(rates)
        variance = sum((r - avg_rate) ** 2 for r in rates) / len(rates)
        std_dev = math.sqrt(variance)

        # Coefficient of variation
        cv = std_dev / avg_rate if avg_rate > 0 else float('inf')

        if cv < 0.2 and avg_rate > 0.3:
            status = "converging"
            interpretation = f"Stable acceptance at {avg_rate:.0%} (CV={cv:.2f})"
        elif cv < 0.4:
            status = "stable"
            interpretation = f"Moderate variation in acceptance rate (CV={cv:.2f})"
        else:
            status = "diverging"
            interpretation = f"High variation in acceptance rate (CV={cv:.2f})"

        confidence = 0.8 if len(rates) >= 5 else 0.5

        return ConvergenceIndicator(
            name="acceptance_stability",
            value=1 - min(1, cv),  # Invert so higher = better
            status=status,
            confidence=confidence,
            interpretation=interpretation,
        )

    def _analyze_diminishing_returns(self, snapshots: list[IterationSnapshot]) -> ConvergenceIndicator:
        """Detect diminishing returns pattern."""
        if len(snapshots) < self.diminishing_window:
            return ConvergenceIndicator(
                name="diminishing_returns",
                value=0,
                status="insufficient_data",
                confidence=0.3,
                interpretation=f"Need {self.diminishing_window} iterations to detect diminishing returns"
            )

        # Check recent window for zero or minimal growth
        recent = snapshots[-self.diminishing_window:]
        recent_additions = sum(s.primitives_added for s in recent)

        # Also check coverage delta
        recent_coverage_gain = sum(s.coverage_delta for s in recent)

        if recent_additions >= self.diminishing_window // 2:
            status = "converging"
            interpretation = f"Productive: {recent_additions} primitives in last {self.diminishing_window} iterations"
            value = 1.0
        elif recent_additions >= 2:
            status = "stable"
            interpretation = f"Slowing: only {recent_additions} primitives in last {self.diminishing_window} iterations"
            value = 0.5
        else:
            status = "diverging"
            interpretation = f"Diminishing returns: {recent_additions} primitives in last {self.diminishing_window} iterations"
            value = 0.1

        return ConvergenceIndicator(
            name="diminishing_returns",
            value=value,
            status=status,
            confidence=0.8,
            interpretation=interpretation,
        )

    def _analyze_domain_saturation(self, snapshots: list[IterationSnapshot]) -> ConvergenceIndicator:
        """Analyze domain coverage saturation."""
        if not snapshots:
            return ConvergenceIndicator(
                name="domain_saturation",
                value=0,
                status="insufficient_data",
                confidence=0.3,
                interpretation="No data available"
            )

        latest = snapshots[-1]
        domains_with_primitives = len([d for d, c in latest.domain_counts.items() if c > 0])
        total_domains = 15  # Total expected domains

        coverage_ratio = domains_with_primitives / total_domains

        if coverage_ratio > 0.8:
            status = "converging"
            interpretation = f"Good domain spread: {domains_with_primitives}/{total_domains} domains covered"
        elif coverage_ratio > 0.5:
            status = "stable"
            interpretation = f"Moderate domain spread: {domains_with_primitives}/{total_domains} domains covered"
        else:
            status = "diverging"
            interpretation = f"Limited domain spread: only {domains_with_primitives}/{total_domains} domains covered"

        return ConvergenceIndicator(
            name="domain_saturation",
            value=coverage_ratio,
            status=status,
            confidence=0.7,
            interpretation=interpretation,
        )

    def _project_completion(self, snapshots: list[IterationSnapshot]) -> Optional[int]:
        """Project iterations to reach coverage threshold."""
        if len(snapshots) < 3:
            return None

        current = snapshots[-1].coverage_score
        remaining = self.coverage_threshold - current

        if remaining <= 0:
            return 0

        # Use exponential smoothing for velocity estimate
        alpha = 0.3
        velocity = snapshots[-1].coverage_delta
        for s in reversed(snapshots[-5:-1]):
            velocity = alpha * s.coverage_delta + (1 - alpha) * velocity

        if velocity > 0.001:
            return int(remaining / velocity)
        return None

    def _identify_risk_factors(
        self,
        snapshots: list[IterationSnapshot],
        indicators: list[ConvergenceIndicator]
    ) -> list[str]:
        """Identify risk factors from analysis."""
        risks = []

        # Check for diverging indicators
        for indicator in indicators:
            if indicator.status == "diverging":
                risks.append(f"{indicator.name}: {indicator.interpretation}")

        # Check for low acceptance rate
        latest = snapshots[-1]
        if latest.cumulative_acceptance_rate < 0.2:
            risks.append(f"Low cumulative acceptance rate: {latest.cumulative_acceptance_rate:.0%}")

        # Check for neglected domains
        if latest.domain_counts:
            all_domains = 15
            covered = len(latest.domain_counts)
            if covered < all_domains * 0.5:
                risks.append(f"Many domains neglected: only {covered}/{all_domains} covered")

        # Check for stalled coverage
        if len(snapshots) >= 5:
            recent_delta = sum(s.coverage_delta for s in snapshots[-5:])
            if recent_delta < 0.01:
                risks.append(f"Coverage stalled: only {recent_delta:.2%} gain in last 5 iterations")

        return risks

    def _generate_recommendations(
        self,
        snapshots: list[IterationSnapshot],
        indicators: list[ConvergenceIndicator],
        risk_factors: list[str]
    ) -> list[str]:
        """Generate recommendations based on analysis."""
        recommendations = []
        latest = snapshots[-1]

        # Low acceptance rate
        acceptance_indicator = next((i for i in indicators if i.name == "acceptance_stability"), None)
        if acceptance_indicator and acceptance_indicator.value < 0.3:
            recommendations.append("Consider adjusting CRITIC strictness - acceptance rate is low")

        # Diminishing returns
        dim_indicator = next((i for i in indicators if i.name == "diminishing_returns"), None)
        if dim_indicator and dim_indicator.status == "diverging":
            recommendations.append("Consider changing PROPOSER strategy - current approach showing diminishing returns")
            recommendations.append("Try GAP_FILLING or DECOMPOSITION_MINING modes")

        # Domain imbalance
        domain_indicator = next((i for i in indicators if i.name == "domain_saturation"), None)
        if domain_indicator and domain_indicator.status == "diverging":
            # Find neglected domains
            all_domains = ["being", "space", "time", "causation", "mind", "matter",
                         "quantity", "quality", "relation", "ethics", "emotion",
                         "action", "knowledge", "social", "language"]
            neglected = [d for d in all_domains if latest.domain_counts.get(d, 0) == 0]
            if neglected:
                recommendations.append(f"Focus on neglected domains: {', '.join(neglected[:3])}")

        # Coverage stall
        coverage_indicator = next((i for i in indicators if i.name == "coverage_convergence"), None)
        if coverage_indicator and coverage_indicator.status == "diverging":
            recommendations.append("Analyze gaps to understand why coverage is not improving")
            if latest.top_gaps:
                recommendations.append(f"Priority gaps to address: {', '.join(latest.top_gaps[:3])}")

        # If everything is good
        if not recommendations:
            recommendations.append("System is progressing well - continue current approach")

        return recommendations
