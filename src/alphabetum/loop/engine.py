"""Main loop engine for ALPHABETUM."""

from pathlib import Path
from datetime import datetime
from typing import Optional
import yaml

from ..state.manager import StateManager
from ..state.models import (
    IterationState, Phase, Verdict, Domain,
    Candidate, PrimitiveIndexEntry
)
from ..agents import ProposerAgent, CriticAgent, RefinerAgent, MetaReasonerAgent
from ..logging import Archivist
from ..analytics.expressiveness import ExpressivenessAnalyzer


class AlphabetumLoop:
    """Main orchestration engine for the Alphabet of Human Thought construction."""

    def __init__(self, base_path: Path, config: Optional[dict] = None):
        self.base_path = Path(base_path)
        self.state_manager = StateManager(base_path)
        self.config = config or self.state_manager.load_config()

        # Initialize agents
        self.proposer = ProposerAgent(self.config)
        self.critic = CriticAgent(self.config)
        self.refiner = RefinerAgent(self.config, self.state_manager)
        self.meta_reasoner = MetaReasonerAgent(self.config)

        # Initialize archivist
        self.archivist = Archivist(self.state_manager)

    def run(self, max_iterations: Optional[int] = None) -> dict:
        """
        Run the main loop until stopping condition is met.

        Returns:
            Final report dictionary
        """
        if max_iterations is None:
            max_iterations = self.config["stopping"]["max_iterations"]

        state = self.state_manager.load_iteration_state()
        print(f"Starting ALPHABETUM at iteration {state.current_iteration}")
        print(f"Current phase: {state.phase.value}")

        while not self._should_stop(state, max_iterations):
            print(f"\n{'='*60}")
            print(f"ITERATION {state.current_iteration} | Phase: {state.phase.value} | Cycle: {state.cycle_in_phase}")
            print(f"{'='*60}")

            # Execute current phase
            if state.phase == Phase.EXPANSION:
                state = self._expansion_phase(state)
            elif state.phase == Phase.CONSOLIDATION:
                state = self._consolidation_phase(state)
            elif state.phase == Phase.COMPOSITION:
                state = self._composition_phase(state)
            elif state.phase == Phase.META_REFLECTION:
                state = self._meta_reflection_phase(state)

            # Update cycle/phase counters
            state = self._advance_state(state)

            # Save state
            self.state_manager.save_iteration_state(state)

        # Generate final report
        return self._generate_final_report(state)

    def _expansion_phase(self, state: IterationState) -> IterationState:
        """Execute one cycle of the EXPANSION phase."""
        print(f"\n--- EXPANSION Cycle {state.cycle_in_phase + 1} ---")

        # Get alphabet summary for context
        alphabet_summary = self._get_alphabet_summary()

        # PROPOSER generates candidates
        n_candidates = self.config["iteration"]["candidates_per_cycle"]
        print(f"PROPOSER generating {n_candidates} candidates...")

        candidates, proposer_raw = self.proposer.execute(
            state,
            n=n_candidates,
            alphabet_summary=alphabet_summary,
            gaps=state.gaps_to_fill,
        )

        # Update candidate IDs with iteration
        for i, c in enumerate(candidates):
            c.id = f"CAND_{state.current_iteration:03d}_{i:03d}"

        print(f"  Generated {len(candidates)} candidates: {[c.label for c in candidates]}")

        # Log proposer output
        self.archivist.log_proposer(state.current_iteration, candidates, proposer_raw)

        state.total_proposed += len(candidates)

        # CRITIC evaluates each candidate
        evaluations = []
        for candidate in candidates:
            print(f"\nCRITIC evaluating '{candidate.label}'...")

            evaluation, critic_raw = self.critic.execute(
                state,
                candidate=candidate,
                alphabet_summary=alphabet_summary,
            )
            evaluation.candidate_id = candidate.id
            evaluations.append((candidate, evaluation))

            # Log critic output
            self.archivist.log_critic(state.current_iteration, candidate.id, evaluation, critic_raw)

            print(f"  Verdict: {evaluation.verdict.value} (confidence: {evaluation.confidence:.2f})")
            if evaluation.key_insight:
                print(f"  Key insight: {evaluation.key_insight}")

        # REFINER integrates accepted candidates
        for candidate, evaluation in evaluations:
            if evaluation.verdict == Verdict.ACCEPT:
                print(f"\nREFINER integrating '{candidate.label}'...")

                # Get relationship suggestions
                relationships, refiner_raw = self.refiner.execute(
                    state,
                    candidate=candidate,
                    alphabet_summary=alphabet_summary,
                )

                # Integrate into alphabet
                index_entry, detailed = self.refiner.integrate_primitive(
                    candidate, evaluation, state, relationships
                )

                # Log refiner output
                self.archivist.log_refiner(
                    state.current_iteration,
                    index_entry,
                    detailed,
                    refiner_raw
                )

                state.total_accepted += 1
                print(f"  Assigned ID: {index_entry.id}, Prime: {index_entry.prime}")

            elif evaluation.verdict == Verdict.REJECT:
                state.total_rejected += 1
                # Log rejection
                self.archivist.log_rejection(
                    state.current_iteration,
                    candidate,
                    evaluation
                )

        # Update acceptance rate
        if state.total_proposed > 0:
            state.recent_acceptance_rate = state.total_accepted / state.total_proposed

        return state

    def _consolidation_phase(self, state: IterationState) -> IterationState:
        """Execute one cycle of the CONSOLIDATION phase."""
        print(f"\n--- CONSOLIDATION Cycle {state.cycle_in_phase + 1} ---")

        # Check for consistency issues
        issues = self.refiner.check_consistency(state)

        if issues:
            print(f"  Found {len(issues)} consistency issues:")
            for issue in issues:
                print(f"    - {issue['type']}: {issue}")

            # Log issues
            self.archivist.log_consolidation(
                state.current_iteration,
                issues,
                []  # Resolutions would go here
            )
        else:
            print("  No consistency issues found.")

        return state

    def _composition_phase(self, state: IterationState) -> IterationState:
        """Execute one cycle of the COMPOSITION phase."""
        print(f"\n--- COMPOSITION Cycle {state.cycle_in_phase + 1} ---")

        # Load benchmarks
        benchmarks = self._load_benchmarks()
        primitives = self.state_manager.load_alphabet_index()

        # Test a subset of benchmarks
        n_test = min(5, len(benchmarks))
        test_concepts = benchmarks[:n_test]

        expressible = 0
        gaps = []

        for concept in test_concepts:
            # Simple expressibility check: do we have primitives that could compose this?
            hints = concept.get("decomposition_hints", [])
            primitive_labels = {p.label for p in primitives}

            matched = [h for h in hints if h in primitive_labels]
            coverage = len(matched) / len(hints) if hints else 0

            if coverage >= 0.7:
                expressible += 1
                status = "expressible"
            elif coverage >= 0.3:
                status = "partial"
                gaps.extend([h for h in hints if h not in primitive_labels])
            else:
                status = "inexpressible"
                gaps.extend([h for h in hints if h not in primitive_labels])

            print(f"  {concept['name']}: {status} (matched {len(matched)}/{len(hints)} hints)")

        # Update coverage score
        state.coverage_score = expressible / n_test if n_test > 0 else 0
        print(f"\n  Coverage score: {state.coverage_score:.2%}")

        # Store unique gaps for next expansion
        state.gaps_to_fill = list(set(gaps))[:10]
        if state.gaps_to_fill:
            print(f"  Gaps identified: {state.gaps_to_fill}")

        # Log composition results
        self.archivist.log_composition(
            state.current_iteration,
            test_concepts,
            expressible,
            gaps
        )

        return state

    def _meta_reflection_phase(self, state: IterationState) -> IterationState:
        """Execute the META-REFLECTION phase."""
        print(f"\n--- META-REFLECTION ---")

        start_iteration = max(0, state.current_iteration - 5)

        # Get recent logs summary
        recent_logs = self._get_recent_logs_summary(start_iteration)

        # Execute meta-reasoner
        reflection, raw_response = self.meta_reasoner.execute(
            state,
            start_iteration=start_iteration,
            recent_logs=recent_logs,
            current_gaps=state.gaps_to_fill,
        )

        reflection.iteration_range = (start_iteration, state.current_iteration)

        print(f"  Decision: {reflection.decision}")
        print(f"  Justification: {reflection.decision_justification[:100]}...")

        # Apply adjustments
        if reflection.decision == "CONTINUE":
            state = self.meta_reasoner.apply_adjustments(state, reflection)
            print(f"  Applied adjustments. New priorities: {[d.value for d in state.domains_priority]}")

        # Log reflection
        self.archivist.log_meta_reflection(
            state.current_iteration,
            reflection,
            raw_response
        )

        # Handle decision
        if reflection.decision == "CONCLUDE":
            print("\n  META-REASONER recommends CONCLUSION.")
            # This will trigger stop condition

        return state

    def _advance_state(self, state: IterationState) -> IterationState:
        """Advance cycle/phase counters after a cycle."""
        config = self.config["iteration"]

        cycle_limits = {
            Phase.EXPANSION: config["expansion_cycles"],
            Phase.CONSOLIDATION: config["consolidation_cycles"],
            Phase.COMPOSITION: config["composition_cycles"],
            Phase.META_REFLECTION: 1,
        }

        state.cycle_in_phase += 1

        # Check if phase is complete
        if state.cycle_in_phase >= cycle_limits[state.phase]:
            state.cycle_in_phase = 0

            # Transition to next phase
            phase_order = [Phase.EXPANSION, Phase.CONSOLIDATION, Phase.COMPOSITION, Phase.META_REFLECTION]
            current_idx = phase_order.index(state.phase)
            next_idx = (current_idx + 1) % len(phase_order)
            state.phase = phase_order[next_idx]

            # If we've completed a full cycle, increment iteration
            if state.phase == Phase.EXPANSION:
                # Run expressiveness metrics before advancing
                self._compute_expressiveness_metrics(state)
                state.current_iteration += 1
                print(f"\n>>> Advancing to iteration {state.current_iteration}")

        return state

    def _compute_expressiveness_metrics(self, state: IterationState) -> None:
        """Compute and save expressiveness metrics for the iteration."""
        print(f"\n--- EXPRESSIVENESS METRICS ---")

        try:
            analyzer = ExpressivenessAnalyzer(self.state_manager)
            metrics = analyzer.analyze()

            # Print summary
            print(f"  Corpus Coverage: {metrics.corpus_coverage:.1%}")
            print(f"  Concepts Expressible: {metrics.concepts_expressible}")
            print(f"  Shannon Entropy: {metrics.shannon_entropy:.3f}")
            print(f"  Bits per Concept: {metrics.bits_per_concept:.2f}")
            print(f"  MDL Score: {metrics.mdl_score:.4f}")

            # Save report
            report = analyzer.generate_report(state.current_iteration)
            report["expressiveness_report"]["timestamp"] = datetime.utcnow().isoformat() + "Z"

            # Save to reports directory
            reports_dir = self.base_path / "reports" / "expressiveness"
            reports_dir.mkdir(parents=True, exist_ok=True)

            yaml_path = reports_dir / f"iteration_{state.current_iteration:03d}.yaml"
            with open(yaml_path, "w") as f:
                yaml.dump(report, f, default_flow_style=False, sort_keys=False)

            # Also save encoding table
            md_content = analyzer.generate_encoding_table()
            md_path = reports_dir / f"iteration_{state.current_iteration:03d}_encodings.md"
            with open(md_path, "w") as f:
                f.write(md_content)

            print(f"  Reports saved to: {reports_dir}")

            # Update state with expressiveness coverage
            state.coverage_score = max(state.coverage_score, metrics.corpus_coverage)

        except Exception as e:
            print(f"  [WARN] Could not compute expressiveness metrics: {e}")

    def _should_stop(self, state: IterationState, max_iterations: int) -> bool:
        """Check if any stopping condition is met."""
        config = self.config["stopping"]

        # Check max iterations
        if state.current_iteration >= max_iterations:
            print("\n[STOP] Maximum iterations reached")
            return True

        # Check coverage threshold
        if state.coverage_score >= config["coverage_threshold"]:
            print(f"\n[STOP] Coverage threshold reached: {state.coverage_score:.2%}")
            return True

        # Check stability (no primitives added in window)
        if state.current_iteration > config["stability_window"]:
            # This would need more sophisticated tracking
            pass

        return False

    def _get_alphabet_summary(self) -> str:
        """Get a summary of current primitives for context."""
        primitives = self.state_manager.load_alphabet_index()

        if not primitives:
            return "The alphabet is empty. No primitives have been accepted yet."

        lines = [f"Current alphabet has {len(primitives)} primitives:\n"]

        # Group by domain
        by_domain: dict[str, list] = {}
        for p in primitives:
            domain = p.domain.value
            if domain not in by_domain:
                by_domain[domain] = []
            by_domain[domain].append(p.label)

        for domain, labels in sorted(by_domain.items()):
            lines.append(f"  {domain}: {', '.join(labels)}")

        return "\n".join(lines)

    def _load_benchmarks(self) -> list[dict]:
        """Load benchmark concepts."""
        benchmarks_file = self.base_path / "validation" / "benchmarks" / "test_concepts.yaml"
        with open(benchmarks_file) as f:
            data = yaml.safe_load(f)
        return data.get("benchmark_concepts", [])

    def _get_recent_logs_summary(self, start_iteration: int) -> str:
        """Get summary of recent logs for meta-reflection."""
        lines = []

        state = self.state_manager.load_iteration_state()
        for i in range(start_iteration, state.current_iteration + 1):
            summary = self.state_manager.load_log(i, "summary.yaml")
            if summary:
                lines.append(f"Iteration {i}: {summary.get('highlights', ['no highlights'])}")

        return "\n".join(lines) if lines else "No recent logs available."

    def _generate_final_report(self, state: IterationState) -> dict:
        """Generate the final report."""
        primitives = self.state_manager.load_alphabet_index()

        report = {
            "final_report": {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "iterations_completed": state.current_iteration,
                "alphabet": {
                    "total_primitives": len(primitives),
                    "primitives": [
                        {"id": p.id, "label": p.label, "domain": p.domain.value}
                        for p in primitives
                    ]
                },
                "metrics": {
                    "coverage_score": state.coverage_score,
                    "consistency_score": state.consistency_score,
                    "total_proposed": state.total_proposed,
                    "total_accepted": state.total_accepted,
                    "total_rejected": state.total_rejected,
                    "acceptance_rate": state.recent_acceptance_rate or 0,
                },
            }
        }

        # Save final report
        report_path = self.base_path / "FINAL_REPORT.yaml"
        with open(report_path, "w") as f:
            yaml.dump(report, f, default_flow_style=False, sort_keys=False)

        print(f"\nFinal report saved to: {report_path}")
        return report
