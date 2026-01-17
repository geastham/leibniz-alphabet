#!/usr/bin/env python3
"""
CLI for ALPHABETUM analytics and visualization.

Generate evolution reports, figures, and data exports for editorial use.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown

from alphabetum.state.manager import StateManager
from alphabetum.analytics.history import HistoryTracker
from alphabetum.analytics.metrics import MetricsCalculator
from alphabetum.analytics.convergence import ConvergenceAnalyzer
from alphabetum.viz.reports import ReportGenerator

app = typer.Typer(help="ALPHABETUM Analytics & Visualization")
console = Console()


@app.command()
def status(
    path: Path = typer.Option(".", help="Path to alphabet repository"),
):
    """Show current evolution status and key metrics."""
    state_manager = StateManager(path)
    history = HistoryTracker(state_manager)
    config = state_manager.load_config()

    metrics_calc = MetricsCalculator(history, config)
    metrics = metrics_calc.calculate_all()

    if not metrics:
        console.print("[yellow]No history data available. Run some iterations first.[/yellow]")
        return

    # Summary panel
    summary = f"""
**Iteration:** {metrics.iteration}
**Primitives:** {metrics.growth.total_primitives}
**Coverage:** {metrics.convergence.coverage_score:.1%}
**Status:** {metrics.convergence.is_converging and 'Converging' or 'Not Converging'}
"""
    console.print(Panel(Markdown(summary), title="[bold blue]Evolution Status[/bold blue]"))

    # Metrics table
    table = Table(title="Key Metrics")
    table.add_column("Category", style="cyan")
    table.add_column("Metric", style="white")
    table.add_column("Value", style="green")
    table.add_column("Trend", style="yellow")

    # Growth
    table.add_row("Growth", "Total Primitives", str(metrics.growth.total_primitives), "")
    table.add_row("", "Growth Rate", f"{metrics.growth.growth_rate:.2f}/iter", metrics.growth.velocity_trend)

    # Efficiency
    table.add_row("Efficiency", "Acceptance Rate", f"{metrics.efficiency.acceptance_rate:.1%}",
                 metrics.efficiency.acceptance_trend)
    table.add_row("", "Productivity", f"{metrics.efficiency.productivity:.2f}/iter", "")

    # Convergence
    table.add_row("Convergence", "Coverage", f"{metrics.convergence.coverage_score:.1%}", "")
    table.add_row("", "Velocity", f"{metrics.convergence.coverage_velocity:.3%}/iter", "")
    if metrics.convergence.estimated_iterations_to_threshold:
        table.add_row("", "Est. Completion", f"~{metrics.convergence.estimated_iterations_to_threshold} iters", "")

    # Quality
    table.add_row("Quality", "Avg Confidence", f"{metrics.quality.avg_confidence:.2f}", metrics.quality.confidence_trend)
    table.add_row("", "Stability", f"{metrics.quality.stability_index:.2f}", "")

    console.print(table)


@app.command()
def convergence(
    path: Path = typer.Option(".", help="Path to alphabet repository"),
    detailed: bool = typer.Option(False, "--detailed", "-d", help="Show detailed analysis"),
):
    """Analyze convergence patterns."""
    state_manager = StateManager(path)
    history = HistoryTracker(state_manager)
    config = state_manager.load_config()

    analyzer = ConvergenceAnalyzer(history, config)
    report = analyzer.analyze()

    # Status panel
    status_colors = {
        "converging": "green",
        "stable": "yellow",
        "at_risk": "red",
        "mixed": "blue",
        "insufficient_data": "dim",
    }
    color = status_colors.get(report.overall_status, "white")

    console.print(Panel(
        f"[bold {color}]{report.overall_status.upper()}[/bold {color}]\n"
        f"Confidence: {report.overall_confidence:.0%}",
        title="[bold]Convergence Status[/bold]"
    ))

    if report.projected_completion:
        console.print(f"\n[bold]Projected Completion:[/bold] ~{report.projected_completion} iterations")

    # Indicators table
    if report.indicators:
        table = Table(title="Convergence Indicators")
        table.add_column("Indicator", style="cyan")
        table.add_column("Value", justify="right")
        table.add_column("Status", style="bold")
        table.add_column("Confidence", justify="right")

        for ind in report.indicators:
            status_style = "green" if ind.status == "converging" else "yellow" if ind.status == "stable" else "red"
            table.add_row(
                ind.name.replace('_', ' ').title(),
                f"{ind.value:.3f}",
                f"[{status_style}]{ind.status}[/{status_style}]",
                f"{ind.confidence:.0%}"
            )

        console.print(table)

    if detailed:
        # Interpretations
        if report.indicators:
            console.print("\n[bold]Interpretations:[/bold]")
            for ind in report.indicators:
                console.print(f"  • {ind.name}: {ind.interpretation}")

        # Risk factors
        if report.risk_factors:
            console.print("\n[bold red]Risk Factors:[/bold red]")
            for risk in report.risk_factors:
                console.print(f"  • {risk}")

        # Recommendations
        if report.recommendations:
            console.print("\n[bold green]Recommendations:[/bold green]")
            for rec in report.recommendations:
                console.print(f"  • {rec}")


@app.command()
def report(
    path: Path = typer.Option(".", help="Path to alphabet repository"),
    output: Path = typer.Option(None, "--output", "-o", help="Output directory"),
):
    """Generate comprehensive evolution report."""
    state_manager = StateManager(path)

    if output:
        generator = ReportGenerator(state_manager, output)
    else:
        generator = ReportGenerator(state_manager)

    console.print("Generating evolution report...")

    report_path = generator.generate_evolution_report()

    console.print(f"\n[green]Report generated:[/green] {report_path}")
    console.print(f"[dim]Check the reports directory for all outputs[/dim]")


@app.command()
def figures(
    path: Path = typer.Option(".", help="Path to alphabet repository"),
    output: Path = typer.Option(None, "--output", "-o", help="Output directory"),
    show: bool = typer.Option(False, "--show", "-s", help="Show plots interactively"),
):
    """Generate all visualization figures."""
    try:
        from alphabetum.viz.plots import AlphabetumPlotter
    except ImportError:
        console.print("[red]matplotlib is required for visualization.[/red]")
        console.print("Install with: pip install matplotlib")
        return

    state_manager = StateManager(path)
    history = HistoryTracker(state_manager)
    config = state_manager.load_config()

    output_dir = output or (path / "reports" / "figures")
    plotter = AlphabetumPlotter(history, output_dir)

    console.print("Generating figures...")

    figures_generated = plotter.generate_all(config)

    if figures_generated:
        console.print(f"\n[green]Generated {len(figures_generated)} figures:[/green]")
        for fig in figures_generated:
            console.print(f"  • {fig}")
    else:
        console.print("[yellow]No figures generated. Need more iteration data.[/yellow]")


@app.command()
def export(
    path: Path = typer.Option(".", help="Path to alphabet repository"),
    format: str = typer.Option("csv", "--format", "-f", help="Export format: csv or json"),
    output: Path = typer.Option(None, "--output", "-o", help="Output directory"),
):
    """Export historical data for external analysis."""
    state_manager = StateManager(path)

    if output:
        generator = ReportGenerator(state_manager, output)
    else:
        generator = ReportGenerator(state_manager)

    export_path = generator.generate_data_export(format)
    console.print(f"[green]Data exported:[/green] {export_path}")


@app.command()
def snapshot(
    path: Path = typer.Option(".", help="Path to alphabet repository"),
):
    """Capture a snapshot of current state."""
    state_manager = StateManager(path)
    history = HistoryTracker(state_manager)

    snapshot = history.capture_snapshot()

    console.print(f"[green]Snapshot captured for iteration {snapshot.iteration}[/green]")
    console.print(f"  • Primitives: {snapshot.total_primitives}")
    console.print(f"  • Coverage: {snapshot.coverage_score:.1%}")
    console.print(f"  • Phase: {snapshot.phase}")


@app.command()
def trend(
    path: Path = typer.Option(".", help="Path to alphabet repository"),
):
    """Show quick trend summary."""
    state_manager = StateManager(path)
    history = HistoryTracker(state_manager)
    config = state_manager.load_config()

    metrics_calc = MetricsCalculator(history, config)
    summary = metrics_calc.get_trend_summary()

    console.print(Panel(Markdown(summary), title="[bold]Trend Summary[/bold]"))


if __name__ == "__main__":
    app()
