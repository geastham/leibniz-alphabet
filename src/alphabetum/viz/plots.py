"""
Visualization plots for ALPHABETUM evolution.

Creates publication-ready figures for:
- Growth curves
- Convergence analysis
- Domain distributions
- Acceptance rates
- Network graphs
"""

from pathlib import Path
from typing import Optional
from datetime import datetime

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.ticker import MaxNLocator
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

from ..analytics.history import HistoryTracker, IterationSnapshot
from ..analytics.metrics import MetricsCalculator
from ..analytics.convergence import ConvergenceAnalyzer


# Color palette for consistent styling
COLORS = {
    "primary": "#2E86AB",      # Blue
    "secondary": "#A23B72",    # Magenta
    "success": "#28A745",      # Green
    "warning": "#F18F01",      # Orange
    "danger": "#C73E1D",       # Red
    "neutral": "#6C757D",      # Gray

    # Domain colors
    "being": "#264653",
    "space": "#2A9D8F",
    "time": "#E9C46A",
    "causation": "#F4A261",
    "mind": "#E76F51",
    "matter": "#606C38",
    "quantity": "#283618",
    "quality": "#DDA15E",
    "relation": "#BC6C25",
    "ethics": "#780000",
    "emotion": "#C1121F",
    "action": "#003049",
    "knowledge": "#669BBC",
    "social": "#FDF0D5",
    "language": "#9B2226",
}


class AlphabetumPlotter:
    """
    Creates visualizations for ALPHABETUM evolution analysis.

    All plots are designed for publication/editorial use with:
    - Clean, minimal aesthetics
    - Clear labels and legends
    - High resolution export
    """

    def __init__(self, history: HistoryTracker, output_dir: Optional[Path] = None):
        if not HAS_MATPLOTLIB:
            raise ImportError("matplotlib is required for visualization. Install with: pip install matplotlib")

        self.history = history
        self.output_dir = output_dir or Path("reports/figures")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Set style
        plt.style.use('seaborn-v0_8-whitegrid')
        plt.rcParams['figure.figsize'] = (10, 6)
        plt.rcParams['figure.dpi'] = 150
        plt.rcParams['font.size'] = 11
        plt.rcParams['axes.titlesize'] = 14
        plt.rcParams['axes.labelsize'] = 12

    def plot_growth_curve(self, save: bool = True, show: bool = False) -> Optional[Path]:
        """
        Plot alphabet growth over iterations.

        Shows total primitives with acceptance rate overlay.
        """
        snapshots = self.history.get_snapshots()
        if not snapshots:
            return None

        fig, ax1 = plt.subplots(figsize=(12, 6))

        iterations = [s.iteration for s in snapshots]
        totals = [s.total_primitives for s in snapshots]
        acceptance_rates = [s.cumulative_acceptance_rate * 100 for s in snapshots]

        # Primary axis: Total primitives
        color1 = COLORS["primary"]
        ax1.fill_between(iterations, totals, alpha=0.3, color=color1)
        ax1.plot(iterations, totals, color=color1, linewidth=2.5, marker='o', markersize=4)
        ax1.set_xlabel('Iteration')
        ax1.set_ylabel('Total Primitives', color=color1)
        ax1.tick_params(axis='y', labelcolor=color1)
        ax1.xaxis.set_major_locator(MaxNLocator(integer=True))

        # Secondary axis: Acceptance rate
        ax2 = ax1.twinx()
        color2 = COLORS["secondary"]
        ax2.plot(iterations, acceptance_rates, color=color2, linewidth=2, linestyle='--', alpha=0.8)
        ax2.set_ylabel('Cumulative Acceptance Rate (%)', color=color2)
        ax2.tick_params(axis='y', labelcolor=color2)
        ax2.set_ylim(0, 100)

        plt.title('Alphabet Growth Over Time', fontsize=16, fontweight='bold')

        # Legend
        from matplotlib.lines import Line2D
        legend_elements = [
            Line2D([0], [0], color=color1, linewidth=2.5, label='Total Primitives'),
            Line2D([0], [0], color=color2, linewidth=2, linestyle='--', label='Acceptance Rate'),
        ]
        ax1.legend(handles=legend_elements, loc='upper left')

        plt.tight_layout()

        if save:
            filepath = self.output_dir / "growth_curve.png"
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            return filepath

        if show:
            plt.show()

        return None

    def plot_convergence(self, threshold: float = 0.9, save: bool = True, show: bool = False) -> Optional[Path]:
        """
        Plot coverage convergence toward threshold.

        Shows coverage score with target threshold line and confidence band.
        """
        snapshots = self.history.get_snapshots()
        if not snapshots:
            return None

        fig, ax = plt.subplots(figsize=(12, 6))

        iterations = [s.iteration for s in snapshots]
        coverage = [s.coverage_score * 100 for s in snapshots]

        # Calculate rolling average and confidence band
        window = 3
        rolling_avg = []
        rolling_std = []
        for i in range(len(coverage)):
            start = max(0, i - window + 1)
            window_data = coverage[start:i+1]
            rolling_avg.append(sum(window_data) / len(window_data))
            if len(window_data) > 1:
                mean = rolling_avg[-1]
                var = sum((x - mean) ** 2 for x in window_data) / len(window_data)
                rolling_std.append(var ** 0.5)
            else:
                rolling_std.append(0)

        # Plot confidence band
        upper = [a + s for a, s in zip(rolling_avg, rolling_std)]
        lower = [a - s for a, s in zip(rolling_avg, rolling_std)]
        ax.fill_between(iterations, lower, upper, alpha=0.2, color=COLORS["primary"])

        # Plot actual coverage
        ax.plot(iterations, coverage, color=COLORS["primary"], linewidth=2.5, marker='o',
                markersize=5, label='Coverage Score')

        # Plot threshold line
        ax.axhline(y=threshold * 100, color=COLORS["success"], linestyle='--',
                  linewidth=2, label=f'Target ({threshold:.0%})')

        # Mark current position
        current = coverage[-1]
        remaining = threshold * 100 - current
        ax.annotate(f'{current:.1f}%\n({remaining:+.1f}% to goal)',
                   xy=(iterations[-1], current),
                   xytext=(10, 10), textcoords='offset points',
                   fontsize=10, fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))

        ax.set_xlabel('Iteration')
        ax.set_ylabel('Coverage Score (%)')
        ax.set_ylim(0, 100)
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        ax.legend(loc='lower right')

        plt.title('Convergence Toward Coverage Threshold', fontsize=16, fontweight='bold')
        plt.tight_layout()

        if save:
            filepath = self.output_dir / "convergence.png"
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            return filepath

        if show:
            plt.show()

        return None

    def plot_domain_evolution(self, save: bool = True, show: bool = False) -> Optional[Path]:
        """
        Plot domain distribution evolution as stacked area chart.

        Shows how primitives accumulate across domains over time.
        """
        snapshots = self.history.get_snapshots()
        if not snapshots:
            return None

        fig, ax = plt.subplots(figsize=(14, 7))

        iterations = [s.iteration for s in snapshots]

        # Collect all domains
        all_domains = set()
        for s in snapshots:
            all_domains.update(s.domain_counts.keys())
        domains = sorted(all_domains)

        # Build data matrix
        data = {d: [s.domain_counts.get(d, 0) for s in snapshots] for d in domains}

        # Stack the areas
        colors = [COLORS.get(d, COLORS["neutral"]) for d in domains]
        ax.stackplot(iterations, *[data[d] for d in domains],
                    labels=domains, colors=colors, alpha=0.8)

        ax.set_xlabel('Iteration')
        ax.set_ylabel('Number of Primitives')
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))

        # Legend outside plot
        ax.legend(loc='center left', bbox_to_anchor=(1.02, 0.5), ncol=1)

        plt.title('Domain Distribution Evolution', fontsize=16, fontweight='bold')
        plt.tight_layout()

        if save:
            filepath = self.output_dir / "domain_evolution.png"
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            return filepath

        if show:
            plt.show()

        return None

    def plot_domain_balance(self, save: bool = True, show: bool = False) -> Optional[Path]:
        """
        Plot current domain balance as horizontal bar chart.
        """
        snapshots = self.history.get_snapshots()
        if not snapshots:
            return None

        latest = snapshots[-1]

        fig, ax = plt.subplots(figsize=(10, 8))

        # Sort domains by count
        sorted_domains = sorted(latest.domain_counts.items(), key=lambda x: x[1], reverse=True)
        domains = [d[0] for d in sorted_domains]
        counts = [d[1] for d in sorted_domains]
        colors = [COLORS.get(d, COLORS["neutral"]) for d in domains]

        y_pos = range(len(domains))
        ax.barh(y_pos, counts, color=colors, alpha=0.8)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(domains)
        ax.invert_yaxis()  # Top to bottom
        ax.set_xlabel('Number of Primitives')

        # Add value labels
        for i, (d, c) in enumerate(zip(domains, counts)):
            ax.text(c + 0.1, i, str(c), va='center', fontsize=10)

        plt.title(f'Domain Distribution (Iteration {latest.iteration})', fontsize=16, fontweight='bold')
        plt.tight_layout()

        if save:
            filepath = self.output_dir / "domain_balance.png"
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            return filepath

        if show:
            plt.show()

        return None

    def plot_acceptance_trend(self, save: bool = True, show: bool = False) -> Optional[Path]:
        """
        Plot acceptance rate trend with rolling average.
        """
        snapshots = self.history.get_snapshots()
        if len(snapshots) < 2:
            return None

        fig, ax = plt.subplots(figsize=(12, 6))

        iterations = [s.iteration for s in snapshots]
        rates = [s.acceptance_rate * 100 for s in snapshots]

        # Rolling average
        window = min(5, len(rates))
        rolling = []
        for i in range(len(rates)):
            start = max(0, i - window + 1)
            rolling.append(sum(rates[start:i+1]) / (i - start + 1))

        # Plot raw and rolling
        ax.bar(iterations, rates, alpha=0.3, color=COLORS["primary"], label='Per-Iteration')
        ax.plot(iterations, rolling, color=COLORS["secondary"], linewidth=3,
               label=f'{window}-Iteration Rolling Avg')

        ax.set_xlabel('Iteration')
        ax.set_ylabel('Acceptance Rate (%)')
        ax.set_ylim(0, 100)
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        ax.legend()

        plt.title('Acceptance Rate Trend', fontsize=16, fontweight='bold')
        plt.tight_layout()

        if save:
            filepath = self.output_dir / "acceptance_trend.png"
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            return filepath

        if show:
            plt.show()

        return None

    def plot_velocity_dashboard(self, save: bool = True, show: bool = False) -> Optional[Path]:
        """
        Plot multi-metric dashboard showing velocity indicators.
        """
        snapshots = self.history.get_snapshots()
        if len(snapshots) < 3:
            return None

        fig, axes = plt.subplots(2, 2, figsize=(14, 10))

        iterations = [s.iteration for s in snapshots]

        # 1. Growth velocity (primitives added per iteration)
        ax1 = axes[0, 0]
        added = [s.primitives_added for s in snapshots]
        ax1.bar(iterations, added, color=COLORS["primary"], alpha=0.7)
        ax1.axhline(y=sum(added)/len(added), color=COLORS["danger"], linestyle='--', label='Average')
        ax1.set_title('Growth Velocity', fontweight='bold')
        ax1.set_xlabel('Iteration')
        ax1.set_ylabel('Primitives Added')
        ax1.legend()

        # 2. Coverage velocity (delta per iteration)
        ax2 = axes[0, 1]
        deltas = [s.coverage_delta * 100 for s in snapshots]
        colors = [COLORS["success"] if d > 0 else COLORS["danger"] for d in deltas]
        ax2.bar(iterations, deltas, color=colors, alpha=0.7)
        ax2.axhline(y=0, color='black', linewidth=0.5)
        ax2.set_title('Coverage Velocity', fontweight='bold')
        ax2.set_xlabel('Iteration')
        ax2.set_ylabel('Coverage Delta (%)')

        # 3. Cumulative metrics
        ax3 = axes[1, 0]
        totals = [s.total_primitives for s in snapshots]
        coverage = [s.coverage_score * 100 for s in snapshots]
        ax3.plot(iterations, totals, color=COLORS["primary"], linewidth=2, label='Primitives')
        ax3_twin = ax3.twinx()
        ax3_twin.plot(iterations, coverage, color=COLORS["secondary"], linewidth=2, linestyle='--', label='Coverage %')
        ax3.set_title('Cumulative Progress', fontweight='bold')
        ax3.set_xlabel('Iteration')
        ax3.set_ylabel('Primitives', color=COLORS["primary"])
        ax3_twin.set_ylabel('Coverage %', color=COLORS["secondary"])
        ax3.legend(loc='upper left')
        ax3_twin.legend(loc='lower right')

        # 4. Quality metrics
        ax4 = axes[1, 1]
        confidence = [s.avg_confidence for s in snapshots]
        consistency = [s.consistency_score for s in snapshots]
        ax4.plot(iterations, confidence, color=COLORS["primary"], linewidth=2, marker='o', label='Avg Confidence')
        ax4.plot(iterations, consistency, color=COLORS["success"], linewidth=2, marker='s', label='Consistency')
        ax4.set_title('Quality Metrics', fontweight='bold')
        ax4.set_xlabel('Iteration')
        ax4.set_ylabel('Score')
        ax4.set_ylim(0, 1.1)
        ax4.legend()

        plt.suptitle('ALPHABETUM Velocity Dashboard', fontsize=18, fontweight='bold', y=1.02)
        plt.tight_layout()

        if save:
            filepath = self.output_dir / "velocity_dashboard.png"
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            return filepath

        if show:
            plt.show()

        return None

    def plot_convergence_indicators(self, config: dict, save: bool = True, show: bool = False) -> Optional[Path]:
        """
        Plot convergence indicator summary.
        """
        analyzer = ConvergenceAnalyzer(self.history, config)
        report = analyzer.analyze()

        if report.overall_status == "insufficient_data":
            return None

        fig, ax = plt.subplots(figsize=(10, 6))

        indicators = report.indicators
        names = [i.name.replace('_', ' ').title() for i in indicators]
        values = [i.value for i in indicators]
        colors = []
        for i in indicators:
            if i.status == "converging":
                colors.append(COLORS["success"])
            elif i.status == "stable":
                colors.append(COLORS["warning"])
            else:
                colors.append(COLORS["danger"])

        y_pos = range(len(names))
        ax.barh(y_pos, values, color=colors, alpha=0.8)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(names)
        ax.set_xlim(0, 1.1)
        ax.set_xlabel('Indicator Value')

        # Add status labels
        for i, ind in enumerate(indicators):
            ax.text(values[i] + 0.02, i, ind.status, va='center', fontsize=9,
                   color=colors[i], fontweight='bold')

        # Overall status badge
        status_colors = {
            "converging": COLORS["success"],
            "stable": COLORS["warning"],
            "at_risk": COLORS["danger"],
            "mixed": COLORS["neutral"],
        }
        ax.text(0.95, 0.95, f"Overall: {report.overall_status.upper()}",
               transform=ax.transAxes, fontsize=12, fontweight='bold',
               ha='right', va='top',
               bbox=dict(boxstyle='round', facecolor=status_colors.get(report.overall_status, COLORS["neutral"]),
                        alpha=0.3))

        plt.title('Convergence Indicators', fontsize=16, fontweight='bold')
        plt.tight_layout()

        if save:
            filepath = self.output_dir / "convergence_indicators.png"
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            return filepath

        if show:
            plt.show()

        return None

    def generate_all(self, config: Optional[dict] = None) -> list[Path]:
        """Generate all available plots."""
        plots = []

        growth = self.plot_growth_curve()
        if growth:
            plots.append(growth)

        convergence = self.plot_convergence()
        if convergence:
            plots.append(convergence)

        domain_evo = self.plot_domain_evolution()
        if domain_evo:
            plots.append(domain_evo)

        domain_bal = self.plot_domain_balance()
        if domain_bal:
            plots.append(domain_bal)

        acceptance = self.plot_acceptance_trend()
        if acceptance:
            plots.append(acceptance)

        velocity = self.plot_velocity_dashboard()
        if velocity:
            plots.append(velocity)

        if config:
            conv_ind = self.plot_convergence_indicators(config)
            if conv_ind:
                plots.append(conv_ind)

        return plots
