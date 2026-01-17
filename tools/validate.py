#!/usr/bin/env python3
"""CLI for running validation checks."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import typer
from rich.console import Console

from alphabetum.validation.checker import AlphabetValidator
from alphabetum.state.manager import StateManager

app = typer.Typer()
console = Console()


@app.command()
def full(
    path: Path = typer.Option(".", help="Path to alphabet repository"),
):
    """Run full validation suite."""
    validator = AlphabetValidator(path)
    state_manager = StateManager(path)
    state = state_manager.load_iteration_state()

    results = validator.run_full_validation()
    yaml_report, md_report = validator.generate_report(results, state.current_iteration)

    console.print(md_report)

    # Save reports
    output_dir = path / "validation" / "consistency"
    output_dir.mkdir(parents=True, exist_ok=True)

    import yaml as yaml_lib
    with open(output_dir / "report.yaml", "w") as f:
        yaml_lib.dump(yaml_report, f, default_flow_style=False)

    with open(output_dir / "report.md", "w") as f:
        f.write(md_report)

    console.print(f"\nReports saved to {output_dir}")


@app.command()
def quick(
    path: Path = typer.Option(".", help="Path to alphabet repository"),
):
    """Run quick consistency check."""
    validator = AlphabetValidator(path)
    result = validator.run_quick_check()

    if result.passed:
        console.print("[green]Quick check passed[/green]")
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

    console.print(f"Coverage: {result.coverage_score:.1%}")
    console.print(f"Expressible: {result.expressible}/{result.total}")

    if result.gaps:
        console.print("\nTop gaps:")
        for gap in result.gaps[:10]:
            console.print(f"  - {gap['label']} (needed by {gap['count']} concepts)")


if __name__ == "__main__":
    app()
