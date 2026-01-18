#!/usr/bin/env python3
"""
CLI for ALPHABETUM Expressiveness Metrics.

Measures how well the alphabet can encode canonical logical concepts.
Provides Shannon encoding, MDL, and coverage analysis.
"""

import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn
import yaml

from alphabetum.state.manager import StateManager
from alphabetum.analytics.expressiveness import ExpressivenessAnalyzer

app = typer.Typer(help="ALPHABETUM Expressiveness Metrics")
console = Console()


@app.command()
def analyze(
    path: Path = typer.Option(".", help="Path to alphabet repository"),
    detailed: bool = typer.Option(False, "--detailed", "-d", help="Show detailed breakdown"),
    output: Path = typer.Option(None, "--output", "-o", help="Output YAML report to file"),
):
    """Run expressiveness analysis on current alphabet."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task("Analyzing expressiveness...", total=None)

        state_manager = StateManager(path)
        analyzer = ExpressivenessAnalyzer(state_manager)
        metrics = analyzer.analyze()

    # Summary panel
    summary = f"""
**Corpus Coverage:** {metrics.corpus_coverage:.1%} ({metrics.concepts_expressible} concepts)
**Weighted Coverage:** {metrics.weighted_coverage:.1%}
**Primitives:** {metrics.primitives_count}
**Expressiveness Ratio:** {metrics.expressiveness_ratio:.2f} concepts/primitive
"""
    console.print(Panel(Markdown(summary), title="[bold blue]Expressiveness Summary[/bold blue]"))

    # Information theory metrics
    info_table = Table(title="Information-Theoretic Metrics")
    info_table.add_column("Metric", style="cyan")
    info_table.add_column("Value", style="green", justify="right")
    info_table.add_column("Interpretation", style="dim")

    info_table.add_row(
        "Shannon Entropy",
        f"{metrics.shannon_entropy:.3f}",
        f"({metrics.normalized_entropy:.0%} of max)"
    )
    info_table.add_row(
        "Bits per Concept",
        f"{metrics.bits_per_concept:.2f}",
        "Average encoding size"
    )
    info_table.add_row(
        "MDL Score",
        f"{metrics.mdl_score:.4f}",
        "Higher = more efficient"
    )
    info_table.add_row(
        "Compression Ratio",
        f"{metrics.compression_ratio:.3f}",
        "vs naive enumeration"
    )
    info_table.add_row(
        "Avg Description Length",
        f"{metrics.description_length_avg:.2f}",
        "primitives per concept"
    )

    console.print(info_table)

    # Primitive importance
    if metrics.primitive_importance:
        imp_table = Table(title="Primitive Importance (by corpus usage)")
        imp_table.add_column("Primitive", style="cyan")
        imp_table.add_column("Usage %", style="green", justify="right")
        imp_table.add_column("Bar", style="yellow")

        for prim, importance in list(metrics.primitive_importance.items())[:11]:
            bar = "" * int(importance * 30)
            imp_table.add_row(prim, f"{importance:.1%}", bar)

        console.print(imp_table)

    # Corpus breakdown
    if detailed:
        corpus_table = Table(title="Corpus Coverage Breakdown")
        corpus_table.add_column("Corpus", style="cyan")
        corpus_table.add_column("Total", justify="right")
        corpus_table.add_column("Full", justify="right", style="green")
        corpus_table.add_column("Partial", justify="right", style="yellow")
        corpus_table.add_column("None", justify="right", style="red")
        corpus_table.add_column("Coverage", justify="right")

        for result in metrics.corpus_results:
            corpus_table.add_row(
                result.corpus_name.replace("_", " ").title(),
                str(result.total_concepts),
                str(result.fully_expressible),
                str(result.partially_expressible),
                str(result.inexpressible),
                f"{result.coverage_score:.0%}"
            )

        console.print(corpus_table)

    # Save report if requested
    if output:
        iteration_state = state_manager.load_iteration_state()
        iteration = iteration_state.get("iteration_state", {}).get("current_iteration", 0)
        report = analyzer.generate_report(iteration)
        report["expressiveness_report"]["timestamp"] = datetime.utcnow().isoformat() + "Z"

        with open(output, "w") as f:
            yaml.dump(report, f, default_flow_style=False, sort_keys=False)

        console.print(f"\n[green]Report saved to:[/green] {output}")


@app.command()
def encodings(
    path: Path = typer.Option(".", help="Path to alphabet repository"),
    corpus: str = typer.Option(None, "--corpus", "-c", help="Filter by corpus name"),
    output: Path = typer.Option(None, "--output", "-o", help="Output markdown to file"),
):
    """Show detailed concept encodings with symbols."""
    state_manager = StateManager(path)
    analyzer = ExpressivenessAnalyzer(state_manager)

    md_content = analyzer.generate_encoding_table()

    if output:
        with open(output, "w") as f:
            f.write(md_content)
        console.print(f"[green]Encoding table saved to:[/green] {output}")
    else:
        console.print(Markdown(md_content))


@app.command()
def gaps(
    path: Path = typer.Option(".", help="Path to alphabet repository"),
    top: int = typer.Option(10, "--top", "-n", help="Show top N missing primitives"),
):
    """Show most-needed missing primitives."""
    state_manager = StateManager(path)
    analyzer = ExpressivenessAnalyzer(state_manager)
    metrics = analyzer.analyze()

    # Aggregate missing primitives across all corpora
    from collections import Counter
    all_missing: Counter = Counter()

    for result in metrics.corpus_results:
        for enc in result.encodings:
            all_missing.update(enc.missing_primitives)

    if not all_missing:
        console.print("[green]No gaps found! All corpus concepts are expressible.[/green]")
        return

    console.print(Panel(
        f"[bold]Top {top} Missing Primitives[/bold]\n"
        "These primitives would most improve corpus coverage.",
        title="Coverage Gaps"
    ))

    table = Table()
    table.add_column("Rank", style="dim", justify="right")
    table.add_column("Primitive", style="cyan")
    table.add_column("Concepts Needing", style="green", justify="right")
    table.add_column("Impact", style="yellow")

    for i, (prim, count) in enumerate(all_missing.most_common(top), 1):
        total = sum(r.total_concepts for r in metrics.corpus_results)
        impact = count / total if total > 0 else 0
        bar = "" * int(impact * 20)
        table.add_row(str(i), prim, str(count), bar)

    console.print(table)


@app.command()
def compare(
    path: Path = typer.Option(".", help="Path to alphabet repository"),
    iteration1: int = typer.Argument(..., help="First iteration to compare"),
    iteration2: int = typer.Argument(..., help="Second iteration to compare"),
):
    """Compare expressiveness between two iterations."""
    reports_dir = Path(path) / "reports" / "expressiveness"

    file1 = reports_dir / f"iteration_{iteration1:03d}.yaml"
    file2 = reports_dir / f"iteration_{iteration2:03d}.yaml"

    if not file1.exists():
        console.print(f"[red]Report not found:[/red] {file1}")
        return
    if not file2.exists():
        console.print(f"[red]Report not found:[/red] {file2}")
        return

    with open(file1) as f:
        report1 = yaml.safe_load(f)
    with open(file2) as f:
        report2 = yaml.safe_load(f)

    r1 = report1.get("expressiveness_report", {})
    r2 = report2.get("expressiveness_report", {})

    console.print(f"\n[bold]Expressiveness Comparison: Iteration {iteration1} vs {iteration2}[/bold]\n")

    table = Table()
    table.add_column("Metric", style="cyan")
    table.add_column(f"Iter {iteration1}", justify="right")
    table.add_column(f"Iter {iteration2}", justify="right")
    table.add_column("Delta", justify="right")

    def get_delta(v1, v2):
        if isinstance(v1, str):
            v1 = float(v1.rstrip('%')) / 100
            v2 = float(v2.rstrip('%')) / 100
            delta = v2 - v1
            return f"{delta:+.1%}"
        else:
            delta = v2 - v1
            return f"{delta:+.3f}" if delta != 0 else "="

    s1 = r1.get("summary", {})
    s2 = r2.get("summary", {})

    table.add_row("Primitives", str(s1.get("primitives")), str(s2.get("primitives")),
                  f"{s2.get('primitives', 0) - s1.get('primitives', 0):+d}")
    table.add_row("Corpus Coverage", s1.get("corpus_coverage", "-"), s2.get("corpus_coverage", "-"),
                  get_delta(s1.get("corpus_coverage", "0%"), s2.get("corpus_coverage", "0%")))
    table.add_row("Concepts Expressible", str(s1.get("concepts_expressible")),
                  str(s2.get("concepts_expressible")),
                  f"{s2.get('concepts_expressible', 0) - s1.get('concepts_expressible', 0):+d}")

    i1 = r1.get("information_theory", {})
    i2 = r2.get("information_theory", {})

    table.add_row("Shannon Entropy", str(i1.get("shannon_entropy")), str(i2.get("shannon_entropy")),
                  get_delta(i1.get("shannon_entropy", 0), i2.get("shannon_entropy", 0)))
    table.add_row("Bits per Concept", str(i1.get("bits_per_concept")), str(i2.get("bits_per_concept")),
                  get_delta(i1.get("bits_per_concept", 0), i2.get("bits_per_concept", 0)))
    table.add_row("MDL Score", str(i1.get("mdl_score")), str(i2.get("mdl_score")),
                  get_delta(i1.get("mdl_score", 0), i2.get("mdl_score", 0)))

    console.print(table)


@app.command(name="report")
def generate_report(
    path: Path = typer.Option(".", help="Path to alphabet repository"),
):
    """Generate and save expressiveness report for current iteration."""
    state_manager = StateManager(path)
    analyzer = ExpressivenessAnalyzer(state_manager)

    iteration_state = state_manager.load_iteration_state()
    iteration = iteration_state.get("iteration_state", {}).get("current_iteration", 0)

    # Generate reports
    yaml_report = analyzer.generate_report(iteration)
    yaml_report["expressiveness_report"]["timestamp"] = datetime.utcnow().isoformat() + "Z"

    md_content = analyzer.generate_encoding_table()

    # Save to reports directory
    reports_dir = Path(path) / "reports" / "expressiveness"
    reports_dir.mkdir(parents=True, exist_ok=True)

    yaml_path = reports_dir / f"iteration_{iteration:03d}.yaml"
    md_path = reports_dir / f"iteration_{iteration:03d}_encodings.md"

    with open(yaml_path, "w") as f:
        yaml.dump(yaml_report, f, default_flow_style=False, sort_keys=False)

    with open(md_path, "w") as f:
        f.write(md_content)

    console.print(f"[green]Reports saved:[/green]")
    console.print(f"  YAML: {yaml_path}")
    console.print(f"  Markdown: {md_path}")

    # Show summary
    metrics = analyzer.analyze()
    console.print(f"\n[bold]Iteration {iteration} Summary:[/bold]")
    console.print(f"  Coverage: {metrics.corpus_coverage:.1%}")
    console.print(f"  Expressible Concepts: {metrics.concepts_expressible}")
    console.print(f"  Shannon Entropy: {metrics.shannon_entropy:.3f}")


if __name__ == "__main__":
    app()
