#!/usr/bin/env python3
"""
ALPHABETUM: An Autonomous Reasoning System

Reconstructing Leibniz's Alphabet of Human Thought

This is the main entry point for running the ALPHABETUM system.

Usage:
    python main.py              # Run with default settings
    python main.py --help       # Show help
    python main.py --iterations 5   # Run for 5 iterations
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import argparse
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

from alphabetum.loop.engine import AlphabetumLoop
from alphabetum.state.manager import StateManager


def print_banner(console: Console):
    """Print the ALPHABETUM banner."""
    banner = """
# ALPHABETUM

## The Alphabet of Human Thought

*"The only way to rectify our reasonings is to make them as tangible as those of
the Mathematicians, so that we can find our error at a glance."*

— Gottfried Wilhelm Leibniz, 1677
"""
    console.print(Panel(Markdown(banner), title="[bold blue]ALPHABETUM[/bold blue]"))


def main():
    parser = argparse.ArgumentParser(
        description="ALPHABETUM: Autonomous reasoning system for Leibniz's Alphabet of Human Thought"
    )
    parser.add_argument(
        "--path", "-p",
        type=Path,
        default=Path("."),
        help="Path to the alphabet repository (default: current directory)"
    )
    parser.add_argument(
        "--iterations", "-n",
        type=int,
        default=10,
        help="Maximum number of iterations to run (default: 10)"
    )
    parser.add_argument(
        "--status", "-s",
        action="store_true",
        help="Show current status and exit"
    )
    parser.add_argument(
        "--validate", "-v",
        action="store_true",
        help="Run validation and exit"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Reduce output verbosity"
    )

    args = parser.parse_args()
    console = Console()

    if not args.quiet:
        print_banner(console)

    # Verify path exists and has required files
    config_path = args.path / "config.yaml"
    if not config_path.exists():
        console.print(f"[red]Error: config.yaml not found in {args.path}[/red]")
        console.print("Please run from the alphabet repository root or specify --path")
        sys.exit(1)

    state_manager = StateManager(args.path)

    if args.status:
        # Show status only
        show_status(console, state_manager)
        return

    if args.validate:
        # Run validation only
        run_validation(console, args.path)
        return

    # Run the main loop
    console.print()
    console.print(f"[bold]Starting ALPHABETUM[/bold]")
    console.print(f"Path: {args.path.absolute()}")
    console.print(f"Max iterations: {args.iterations}")
    console.print()

    try:
        loop = AlphabetumLoop(args.path)
        report = loop.run(max_iterations=args.iterations)

        console.print()
        console.print("[bold green]Run completed successfully![/bold green]")
        console.print()

        # Show summary
        show_summary(console, report)

    except KeyboardInterrupt:
        console.print()
        console.print("[yellow]Interrupted by user[/yellow]")
        console.print("State has been saved. Run again to continue.")
        sys.exit(0)

    except Exception as e:
        console.print()
        console.print(f"[red]Error: {e}[/red]")
        raise


def show_status(console: Console, state_manager: StateManager):
    """Show current status."""
    state = state_manager.load_iteration_state()
    primitives = state_manager.load_alphabet_index()

    console.print()
    console.print("[bold]Current Status[/bold]")
    console.print()
    console.print(f"  Iteration:     {state.current_iteration}")
    console.print(f"  Phase:         {state.phase.value}")
    console.print(f"  Primitives:    {len(primitives)}")
    console.print(f"  Proposed:      {state.total_proposed}")
    console.print(f"  Accepted:      {state.total_accepted}")
    console.print(f"  Rejected:      {state.total_rejected}")
    console.print(f"  Coverage:      {state.coverage_score:.1%}")
    console.print()

    if primitives:
        console.print("[bold]Primitives by Domain:[/bold]")
        by_domain: dict[str, list] = {}
        for p in primitives:
            domain = p.domain.value
            if domain not in by_domain:
                by_domain[domain] = []
            by_domain[domain].append(p.label)

        for domain, labels in sorted(by_domain.items()):
            console.print(f"  {domain}: {', '.join(labels)}")


def show_summary(console: Console, report: dict):
    """Show run summary."""
    r = report.get("final_report", {})

    console.print("[bold]Summary[/bold]")
    console.print()
    console.print(f"  Iterations completed: {r.get('iterations_completed', 0)}")

    alphabet = r.get("alphabet", {})
    console.print(f"  Total primitives:     {alphabet.get('total_primitives', 0)}")

    metrics = r.get("metrics", {})
    console.print(f"  Coverage score:       {metrics.get('coverage_score', 0):.1%}")
    console.print(f"  Acceptance rate:      {metrics.get('acceptance_rate', 0):.1%}")


def run_validation(console: Console, path: Path):
    """Run validation."""
    from alphabetum.validation.checker import AlphabetValidator

    validator = AlphabetValidator(path)
    results = validator.run_full_validation()

    console.print()
    console.print("[bold]Validation Results[/bold]")
    console.print()

    for name, result in results.items():
        status = "[green]PASS[/green]" if result.passed else "[red]FAIL[/red]"
        console.print(f"  {name:20} {status} (score: {result.score:.2f})")

        if result.issues:
            for issue in result.issues[:3]:
                console.print(f"    - {issue}")


if __name__ == "__main__":
    main()
