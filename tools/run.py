#!/usr/bin/env python3
"""Main CLI for running ALPHABETUM."""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import typer
from rich.console import Console
from rich.table import Table

from alphabetum.loop.engine import AlphabetumLoop
from alphabetum.state.manager import StateManager
from alphabetum.validation.checker import AlphabetValidator

app = typer.Typer(
    name="alphabetum",
    help="ALPHABETUM: Autonomous reasoning system for Leibniz's Alphabet of Human Thought"
)
console = Console()


@app.command()
def run(
    path: Path = typer.Option(".", help="Path to alphabet repository"),
    iterations: int = typer.Option(10, help="Maximum iterations to run"),
):
    """Run the ALPHABETUM loop."""
    console.print(f"[bold blue]ALPHABETUM[/bold blue] - Starting autonomous reasoning loop")
    console.print(f"Path: {path.absolute()}")
    console.print(f"Max iterations: {iterations}")
    console.print()

    loop = AlphabetumLoop(path)
    report = loop.run(max_iterations=iterations)

    console.print()
    console.print("[bold green]Run completed![/bold green]")
    console.print(f"Final report saved to: {path / 'FINAL_REPORT.yaml'}")


@app.command()
def status(
    path: Path = typer.Option(".", help="Path to alphabet repository"),
):
    """Show current state of the alphabet."""
    state_manager = StateManager(path)
    state = state_manager.load_iteration_state()
    primitives = state_manager.load_alphabet_index()

    console.print()
    console.print("[bold blue]ALPHABETUM Status[/bold blue]")
    console.print()

    # State table
    table = Table(title="Iteration State")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Current Iteration", str(state.current_iteration))
    table.add_row("Phase", state.phase.value)
    table.add_row("Cycle in Phase", str(state.cycle_in_phase))
    table.add_row("Total Primitives", str(len(primitives)))
    table.add_row("Proposed", str(state.total_proposed))
    table.add_row("Accepted", str(state.total_accepted))
    table.add_row("Rejected", str(state.total_rejected))
    table.add_row("Coverage Score", f"{state.coverage_score:.1%}")

    console.print(table)

    # Primitives by domain
    if primitives:
        console.print()
        domain_table = Table(title="Primitives by Domain")
        domain_table.add_column("Domain", style="cyan")
        domain_table.add_column("Count", style="green")
        domain_table.add_column("Primitives", style="yellow")

        by_domain: dict[str, list] = {}
        for p in primitives:
            domain = p.domain.value
            if domain not in by_domain:
                by_domain[domain] = []
            by_domain[domain].append(p.label)

        for domain, labels in sorted(by_domain.items()):
            domain_table.add_row(
                domain,
                str(len(labels)),
                ", ".join(labels[:5]) + ("..." if len(labels) > 5 else "")
            )

        console.print(domain_table)


@app.command()
def validate(
    path: Path = typer.Option(".", help="Path to alphabet repository"),
    full: bool = typer.Option(False, help="Run full validation suite"),
):
    """Run validation checks on the alphabet."""
    validator = AlphabetValidator(path)
    state_manager = StateManager(path)
    state = state_manager.load_iteration_state()

    console.print()
    console.print("[bold blue]ALPHABETUM Validation[/bold blue]")
    console.print()

    if full:
        results = validator.run_full_validation()
        yaml_report, md_report = validator.generate_report(results, state.current_iteration)
        console.print(md_report)
    else:
        result = validator.run_quick_check()
        if result.passed:
            console.print("[green]Quick check passed![/green]")
        else:
            console.print("[red]Issues found:[/red]")
            for issue in result.issues:
                console.print(f"  - {issue}")


@app.command()
def coverage(
    path: Path = typer.Option(".", help="Path to alphabet repository"),
):
    """Check coverage against benchmarks."""
    validator = AlphabetValidator(path)
    result = validator.check_coverage_only()

    console.print()
    console.print("[bold blue]Coverage Report[/bold blue]")
    console.print()
    console.print(f"Total benchmarks: {result.total}")
    console.print(f"Expressible: {result.expressible}")
    console.print(f"Partial: {result.partial}")
    console.print(f"Inexpressible: {result.inexpressible}")
    console.print(f"[bold]Coverage Score: {result.coverage_score:.1%}[/bold]")

    if result.gaps:
        console.print()
        console.print("[yellow]Top gaps (primitives needed):[/yellow]")
        for gap in result.gaps[:10]:
            console.print(f"  - {gap['label']} (needed by {gap['count']} concepts)")


@app.command()
def list_primitives(
    path: Path = typer.Option(".", help="Path to alphabet repository"),
    domain: str = typer.Option(None, help="Filter by domain"),
):
    """List all primitives in the alphabet."""
    state_manager = StateManager(path)
    primitives = state_manager.load_alphabet_index()

    if domain:
        primitives = [p for p in primitives if p.domain.value == domain]

    console.print()
    table = Table(title=f"Alphabet ({len(primitives)} primitives)")
    table.add_column("ID", style="cyan")
    table.add_column("Label", style="green")
    table.add_column("Prime", style="yellow")
    table.add_column("Domain", style="blue")
    table.add_column("Confidence", style="magenta")

    for p in primitives:
        table.add_row(
            p.id,
            p.label,
            str(p.prime),
            p.domain.value,
            f"{p.confidence:.2f}"
        )

    console.print(table)


@app.command()
def compose(
    path: Path = typer.Option(".", help="Path to alphabet repository"),
    primitives: str = typer.Argument(..., help="Comma-separated primitive labels to compose"),
):
    """Compose primitives into a concept."""
    from alphabetum.calculus.composer import Calculus

    state_manager = StateManager(path)
    calc = Calculus(state_manager)

    labels = [l.strip() for l in primitives.split(",")]
    concept = calc.compose(*labels)

    console.print()
    console.print(f"[bold blue]Composition Result[/bold blue]")
    console.print()
    console.print(f"Labels: {labels}")
    console.print(f"Concept Number: {concept.number}")
    console.print(f"Expression: {concept.to_expression()}")

    valid, violations = calc.is_well_formed(concept)
    console.print(f"Well-formed: {valid}")
    if violations:
        console.print("[red]Violations:[/red]")
        for v in violations:
            console.print(f"  - {v}")


@app.command()
def reset(
    path: Path = typer.Option(".", help="Path to alphabet repository"),
    confirm: bool = typer.Option(False, "--yes", "-y", help="Confirm reset"),
):
    """Reset the alphabet to initial state (WARNING: deletes all primitives!)."""
    if not confirm:
        console.print("[yellow]This will delete all primitives and reset state![/yellow]")
        console.print("Run with --yes to confirm.")
        return

    state_manager = StateManager(path)

    # Reset iteration state
    state_manager.save_iteration_state(state_manager._parse_iteration_state({
        "current_iteration": 0,
        "phase": "EXPANSION",
        "cycle_in_phase": 0,
        "current_strategy": {
            "proposer_mode": "DOMAIN_SWEEP",
            "proposer_temperature": 0.7,
            "critic_strictness": 0.5,
            "domains_priority": ["being", "space", "time", "causation", "mind"],
        },
        "pending": {},
        "metrics": {},
        "history": {},
    }))

    # Reset alphabet index
    state_manager.save_alphabet_index([], 0)

    # Reset relationships
    from alphabetum.state.models import RelationshipGraph
    state_manager.save_relationships(RelationshipGraph(), 0)

    console.print("[green]Reset complete![/green]")


if __name__ == "__main__":
    app()
