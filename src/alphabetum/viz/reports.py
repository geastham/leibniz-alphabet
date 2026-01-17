"""
Report generation for ALPHABETUM evolution.

Creates comprehensive reports combining metrics, analysis, and visualizations
suitable for editorial and research purposes.
"""

from pathlib import Path
from datetime import datetime
from typing import Optional
import yaml
import json

from ..analytics.history import HistoryTracker
from ..analytics.metrics import MetricsCalculator
from ..analytics.convergence import ConvergenceAnalyzer
from ..state.manager import StateManager


class ReportGenerator:
    """
    Generates comprehensive evolution reports for ALPHABETUM.

    Combines:
    - Quantitative metrics
    - Convergence analysis
    - Visualizations
    - Narrative summaries
    """

    def __init__(self, state_manager: StateManager, output_dir: Optional[Path] = None):
        self.state_manager = state_manager
        self.base_path = state_manager.base_path
        self.output_dir = output_dir or self.base_path / "reports"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.history = HistoryTracker(state_manager)
        self.config = state_manager.load_config()

    def generate_evolution_report(self) -> Path:
        """
        Generate comprehensive evolution report.

        Returns path to the generated report.
        """
        metrics_calc = MetricsCalculator(self.history, self.config)
        convergence = ConvergenceAnalyzer(self.history, self.config)

        metrics = metrics_calc.calculate_all()
        conv_report = convergence.analyze()

        # Generate report content
        report = self._build_report(metrics, conv_report)

        # Save as multiple formats
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

        # YAML (structured data)
        yaml_path = self.output_dir / f"evolution_report_{timestamp}.yaml"
        with open(yaml_path, "w") as f:
            yaml.dump(report, f, default_flow_style=False, sort_keys=False)

        # Markdown (narrative)
        md_path = self.output_dir / f"evolution_report_{timestamp}.md"
        md_content = self._generate_markdown(report, metrics, conv_report)
        with open(md_path, "w") as f:
            f.write(md_content)

        # JSON (for web/interactive use)
        json_path = self.output_dir / f"evolution_report_{timestamp}.json"
        with open(json_path, "w") as f:
            json.dump(report, f, indent=2)

        # Generate figures
        try:
            from .plots import AlphabetumPlotter
            plotter = AlphabetumPlotter(self.history, self.output_dir / "figures")
            figures = plotter.generate_all(self.config)
            report["figures"] = [str(f) for f in figures]
        except ImportError:
            report["figures"] = []
            report["note"] = "matplotlib not installed - figures not generated"

        return md_path

    def _build_report(self, metrics, conv_report) -> dict:
        """Build the report data structure."""
        state = self.state_manager.load_iteration_state()
        primitives = self.state_manager.load_alphabet_index()
        snapshots = self.history.get_snapshots()

        return {
            "report_metadata": {
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "report_type": "evolution_analysis",
                "version": "1.0.0",
            },
            "summary": {
                "current_iteration": state.current_iteration,
                "total_primitives": len(primitives),
                "coverage_score": round(state.coverage_score, 4),
                "overall_status": conv_report.overall_status,
                "health_score": round(conv_report.overall_confidence, 3),
            },
            "metrics": metrics.to_dict() if metrics else {},
            "convergence": conv_report.to_dict(),
            "history_summary": {
                "total_snapshots": len(snapshots),
                "first_iteration": snapshots[0].iteration if snapshots else 0,
                "last_iteration": snapshots[-1].iteration if snapshots else 0,
            },
            "primitives": {
                "total": len(primitives),
                "by_domain": self._count_by_domain(primitives),
                "recent": [
                    {"id": p.id, "label": p.label, "domain": p.domain.value}
                    for p in sorted(primitives, key=lambda x: x.added_iteration, reverse=True)[:5]
                ],
            },
        }

    def _count_by_domain(self, primitives) -> dict:
        """Count primitives by domain."""
        counts = {}
        for p in primitives:
            domain = p.domain.value
            counts[domain] = counts.get(domain, 0) + 1
        return counts

    def _generate_markdown(self, report: dict, metrics, conv_report) -> str:
        """Generate Markdown narrative report."""
        lines = [
            "# ALPHABETUM Evolution Report",
            "",
            f"**Generated:** {report['report_metadata']['generated_at']}",
            "",
            "---",
            "",
            "## Executive Summary",
            "",
        ]

        summary = report["summary"]
        lines.extend([
            f"After **{summary['current_iteration']} iterations**, the alphabet contains "
            f"**{summary['total_primitives']} primitives** with a coverage score of "
            f"**{summary['coverage_score']:.1%}**.",
            "",
            f"**Overall Status:** {summary['overall_status'].upper()}",
            f"**Health Score:** {summary['health_score']:.0%}",
            "",
            "---",
            "",
            "## Growth Analysis",
            "",
        ])

        if metrics:
            g = metrics.growth
            lines.extend([
                f"- **Total Primitives:** {g.total_primitives}",
                f"- **Growth Rate:** {g.growth_rate:.2f} primitives/iteration",
                f"- **Velocity Trend:** {g.velocity_trend}",
            ])
            if g.doubling_time:
                lines.append(f"- **Doubling Time:** ~{g.doubling_time:.0f} iterations at current rate")
            lines.append("")

        # Efficiency
        if metrics:
            e = metrics.efficiency
            lines.extend([
                "## Efficiency Metrics",
                "",
                f"- **Acceptance Rate:** {e.acceptance_rate:.1%} ({e.acceptance_trend})",
                f"- **Productivity:** {e.productivity:.2f} accepted/iteration",
                f"- **Waste Ratio:** {e.waste_ratio:.1%}",
                "",
            ])

        # Convergence
        lines.extend([
            "## Convergence Analysis",
            "",
        ])

        c = conv_report
        lines.extend([
            f"**Status:** {c.overall_status.upper()} (confidence: {c.overall_confidence:.0%})",
            "",
        ])

        if c.projected_completion:
            lines.append(f"**Projected Completion:** ~{c.projected_completion} iterations to reach threshold")
            lines.append("")

        if c.indicators:
            lines.extend([
                "### Convergence Indicators",
                "",
                "| Indicator | Value | Status |",
                "|-----------|-------|--------|",
            ])
            for ind in c.indicators:
                name = ind.name.replace('_', ' ').title()
                lines.append(f"| {name} | {ind.value:.3f} | {ind.status} |")
            lines.append("")

        # Risk factors
        if c.risk_factors:
            lines.extend([
                "### Risk Factors",
                "",
            ])
            for risk in c.risk_factors:
                lines.append(f"- {risk}")
            lines.append("")

        # Recommendations
        if c.recommendations:
            lines.extend([
                "### Recommendations",
                "",
            ])
            for rec in c.recommendations:
                lines.append(f"- {rec}")
            lines.append("")

        # Domain distribution
        lines.extend([
            "## Domain Distribution",
            "",
        ])

        if metrics:
            b = metrics.balance
            lines.extend([
                f"- **Domain Entropy:** {b.domain_entropy:.2f} (higher = more balanced)",
                f"- **Gini Coefficient:** {b.gini_coefficient:.2f} (lower = more equal)",
            ])
            if b.neglected_domains:
                lines.append(f"- **Neglected Domains:** {', '.join(b.neglected_domains)}")
            if b.dominant_domains:
                lines.append(f"- **Dominant Domains:** {', '.join(b.dominant_domains)}")
            lines.append("")

        # Recent primitives
        lines.extend([
            "## Recent Additions",
            "",
        ])

        for p in report["primitives"]["recent"]:
            lines.append(f"- **{p['label']}** ({p['domain']}) - {p['id']}")
        lines.append("")

        # Footer
        lines.extend([
            "---",
            "",
            "*Report generated by ALPHABETUM Analytics*",
        ])

        return "\n".join(lines)

    def generate_data_export(self, format: str = "csv") -> Path:
        """
        Export historical data for external analysis.

        Args:
            format: "csv" or "json"

        Returns:
            Path to exported file
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

        if format == "csv":
            filepath = self.output_dir / f"history_export_{timestamp}.csv"
            self.history.export_to_csv(filepath)
        else:
            filepath = self.output_dir / f"history_export_{timestamp}.json"
            self.history.export_to_json(filepath)

        return filepath

    def generate_quick_summary(self) -> str:
        """Generate a quick text summary for console output."""
        metrics_calc = MetricsCalculator(self.history, self.config)
        return metrics_calc.get_trend_summary()
