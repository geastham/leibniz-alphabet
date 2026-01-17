"""Archivist: logs and archives all reasoning for ALPHABETUM."""

from datetime import datetime
from pathlib import Path
from typing import Optional, Any
import yaml

from ..state.manager import StateManager
from ..state.models import (
    Candidate, Evaluation, PrimitiveIndexEntry, PrimitiveDetailed,
    MetaReflection, Verdict
)


class Archivist:
    """
    Captures and preserves all reasoning in both structured (YAML) and narrative (Markdown) formats.

    The reasoning IS the product - this class ensures complete transparency and traceability.
    """

    def __init__(self, state_manager: StateManager):
        self.state_manager = state_manager

    def log_proposer(
        self,
        iteration: int,
        candidates: list[Candidate],
        raw_response: str
    ) -> None:
        """Log PROPOSER output."""
        # Structured log
        structured = {
            "proposer_output": {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "iteration": iteration,
                "candidates_generated": len(candidates),
                "candidates": [
                    {
                        "id": c.id,
                        "label": c.label,
                        "domain": c.domain.value,
                        "proposed_symbol": c.proposed_symbol,
                        "confidence": c.confidence,
                        "definition_preview": c.informal_definition[:100] + "..."
                        if len(c.informal_definition) > 100 else c.informal_definition,
                    }
                    for c in candidates
                ]
            }
        }
        self.state_manager.save_log(iteration, "proposer.yaml", structured)

        # Narrative log
        narrative = self._generate_proposer_narrative(iteration, candidates, raw_response)
        self.state_manager.save_log(iteration, "proposer.md", narrative)

    def _generate_proposer_narrative(
        self,
        iteration: int,
        candidates: list[Candidate],
        raw_response: str
    ) -> str:
        """Generate narrative Markdown for PROPOSER output."""
        lines = [
            f"# Proposer Log: Iteration {iteration}",
            "",
            f"**Generated:** {datetime.utcnow().isoformat()}Z",
            f"**Candidates:** {len(candidates)}",
            "",
            "---",
            "",
        ]

        for c in candidates:
            lines.extend([
                f"## Candidate: {c.label.upper()}",
                "",
                f"**Domain:** {c.domain.value}",
                f"**Symbol:** {c.proposed_symbol}",
                f"**Confidence:** {c.confidence:.2f}",
                "",
                "### Definition",
                "",
                c.informal_definition,
                "",
                "### Examples",
                "",
            ])
            for ex in c.ostensive_examples:
                lines.append(f"- {ex}")
            lines.extend([
                "",
                "### Primitiveness Argument",
                "",
                c.primitiveness_argument,
                "",
                "---",
                "",
            ])

        lines.extend([
            "## Raw LLM Response",
            "",
            "```",
            raw_response[:2000] + "..." if len(raw_response) > 2000 else raw_response,
            "```",
        ])

        return "\n".join(lines)

    def log_critic(
        self,
        iteration: int,
        candidate_id: str,
        evaluation: Evaluation,
        raw_response: str
    ) -> None:
        """Log CRITIC output for a single candidate."""
        # Load existing or create new
        existing = self.state_manager.load_log(iteration, "critic.yaml")
        if existing is None:
            existing = {
                "critic_output": {
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "iteration": iteration,
                    "evaluations": []
                }
            }

        # Add this evaluation
        existing["critic_output"]["evaluations"].append({
            "candidate_id": evaluation.candidate_id,
            "verdict": evaluation.verdict.value,
            "confidence": evaluation.confidence,
            "decomposition_survived": evaluation.decomposition_survived,
            "circularity_survived": evaluation.circularity_survived,
            "redundancy_can_be_expressed": evaluation.redundancy_can_be_expressed,
            "cultural_assessment": evaluation.cultural_assessment,
            "parsimony_necessary": evaluation.parsimony_necessary,
            "reasoning_summary": evaluation.reasoning_summary[:200] if evaluation.reasoning_summary else "",
            "key_insight": evaluation.key_insight,
        })

        self.state_manager.save_log(iteration, "critic.yaml", existing)

        # Append to narrative log
        narrative_path = self.state_manager.ensure_iteration_log_dir(iteration) / "critic.md"
        narrative = self._generate_critic_narrative(candidate_id, evaluation, raw_response)

        with open(narrative_path, "a") as f:
            f.write(narrative)

    def _generate_critic_narrative(
        self,
        candidate_id: str,
        evaluation: Evaluation,
        raw_response: str
    ) -> str:
        """Generate narrative Markdown for a CRITIC evaluation."""
        verdict_emoji = {
            Verdict.ACCEPT: "ACCEPT",
            Verdict.REJECT: "REJECT",
            Verdict.REFINE: "REFINE",
            Verdict.DEFER: "DEFER",
        }

        lines = [
            f"## Evaluation: {candidate_id}",
            "",
            f"**Verdict:** {verdict_emoji.get(evaluation.verdict, evaluation.verdict.value)}",
            f"**Confidence:** {evaluation.confidence:.2f}",
            "",
            "### Attack Results",
            "",
            f"- Decomposition Survived: {'Yes' if evaluation.decomposition_survived else 'No'}",
            f"- Circularity Survived: {'Yes' if evaluation.circularity_survived else 'No'}",
            f"- Can Be Expressed via Others: {'Yes' if evaluation.redundancy_can_be_expressed else 'No'}",
            f"- Cultural Assessment: {evaluation.cultural_assessment}",
            f"- Parsimony Necessary: {'Yes' if evaluation.parsimony_necessary else 'No'}",
            "",
            "### Reasoning Summary",
            "",
            evaluation.reasoning_summary or "(No summary provided)",
            "",
        ]

        if evaluation.key_insight:
            lines.extend([
                "### Key Insight",
                "",
                f"> {evaluation.key_insight}",
                "",
            ])

        lines.extend([
            "---",
            "",
        ])

        return "\n".join(lines)

    def log_refiner(
        self,
        iteration: int,
        index_entry: PrimitiveIndexEntry,
        detailed: PrimitiveDetailed,
        raw_response: str
    ) -> None:
        """Log REFINER integration of an accepted primitive."""
        # Load existing or create new
        existing = self.state_manager.load_log(iteration, "refiner.yaml")
        if existing is None:
            existing = {
                "refiner_output": {
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "iteration": iteration,
                    "integrations": []
                }
            }

        # Add this integration
        existing["refiner_output"]["integrations"].append({
            "primitive_id": index_entry.id,
            "label": index_entry.label,
            "domain": index_entry.domain.value,
            "prime_assigned": index_entry.prime,
            "relationships": {
                "contrasts_with": [
                    {"id": r.id, "label": r.label}
                    for r in detailed.contrasts_with
                ],
                "presupposes": [
                    {"id": r.id, "label": r.label}
                    for r in detailed.presupposes
                ],
            }
        })

        self.state_manager.save_log(iteration, "refiner.yaml", existing)

        # Narrative log
        narrative = self._generate_refiner_narrative(index_entry, detailed)
        narrative_path = self.state_manager.ensure_iteration_log_dir(iteration) / "refiner.md"
        with open(narrative_path, "a") as f:
            f.write(narrative)

    def _generate_refiner_narrative(
        self,
        index_entry: PrimitiveIndexEntry,
        detailed: PrimitiveDetailed
    ) -> str:
        """Generate narrative Markdown for REFINER integration."""
        lines = [
            f"## Integrated: {detailed.label.upper()} ({index_entry.id})",
            "",
            f"**Prime Number:** {index_entry.prime}",
            f"**Symbol:** {detailed.symbol}",
            f"**Domain:** {index_entry.domain.value}",
            "",
            "### Definition",
            "",
            detailed.definition.informal,
            "",
            "### Relationships",
            "",
        ]

        if detailed.contrasts_with:
            lines.append("**Contrasts with:**")
            for r in detailed.contrasts_with:
                lines.append(f"- {r.label} ({r.id}): {r.reason}")
            lines.append("")

        if detailed.presupposes:
            lines.append("**Presupposes:**")
            for r in detailed.presupposes:
                lines.append(f"- {r.label} ({r.id}): {r.reason}")
            lines.append("")

        lines.extend([
            "---",
            "",
        ])

        return "\n".join(lines)

    def log_rejection(
        self,
        iteration: int,
        candidate: Candidate,
        evaluation: Evaluation
    ) -> None:
        """Log a rejected candidate."""
        # Save to rejections directory
        reject_dir = self.state_manager.reasoning_path / "rejected"
        reject_dir.mkdir(parents=True, exist_ok=True)

        rejection = {
            "rejection": {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "iteration": iteration,
                "candidate": {
                    "id": candidate.id,
                    "label": candidate.label,
                    "domain": candidate.domain.value,
                    "definition": candidate.informal_definition,
                },
                "evaluation": {
                    "verdict": evaluation.verdict.value,
                    "confidence": evaluation.confidence,
                    "reasoning": evaluation.reasoning_summary,
                    "key_insight": evaluation.key_insight,
                }
            }
        }

        filename = f"{candidate.id}_{candidate.label}.yaml"
        filepath = reject_dir / filename
        with open(filepath, "w") as f:
            yaml.dump(rejection, f, default_flow_style=False, sort_keys=False)

    def log_consolidation(
        self,
        iteration: int,
        issues: list[dict],
        resolutions: list[dict]
    ) -> None:
        """Log CONSOLIDATION phase results."""
        structured = {
            "consolidation_output": {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "iteration": iteration,
                "issues_found": len(issues),
                "issues": issues,
                "resolutions": resolutions,
            }
        }
        self.state_manager.save_log(iteration, "consolidation.yaml", structured)

    def log_composition(
        self,
        iteration: int,
        concepts_tested: list[dict],
        expressible_count: int,
        gaps: list[str]
    ) -> None:
        """Log COMPOSITION phase results."""
        structured = {
            "composition_output": {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "iteration": iteration,
                "concepts_tested": len(concepts_tested),
                "expressible": expressible_count,
                "coverage_ratio": expressible_count / len(concepts_tested) if concepts_tested else 0,
                "gaps_identified": gaps,
            }
        }
        self.state_manager.save_log(iteration, "composition.yaml", structured)

    def log_meta_reflection(
        self,
        iteration: int,
        reflection: MetaReflection,
        raw_response: str
    ) -> None:
        """Log META-REFLECTION output."""
        # Save to meta_reflections directory
        reflect_dir = self.state_manager.reasoning_path / "meta_reflections"
        reflect_dir.mkdir(parents=True, exist_ok=True)

        structured = {
            "meta_reflection": {
                "id": reflection.id,
                "timestamp": reflection.timestamp.isoformat() + "Z",
                "iteration_range": list(reflection.iteration_range),
                "progress": {
                    "primitives_added": reflection.primitives_added,
                    "acceptance_rate": reflection.acceptance_rate,
                    "coverage_before": reflection.coverage_before,
                    "coverage_after": reflection.coverage_after,
                },
                "strategy_assessment": {
                    "proposer_effectiveness": reflection.proposer_effectiveness,
                    "critic_calibration": reflection.critic_calibration,
                },
                "course_corrections": {
                    "strategy_adjustments": reflection.strategy_adjustments,
                    "domain_priorities": reflection.domain_priorities,
                },
                "decision": reflection.decision,
                "decision_justification": reflection.decision_justification,
                "predictions": reflection.predictions,
                "insights": reflection.insights,
            }
        }

        filename = f"{reflection.id}_iteration_{iteration:03d}.yaml"
        filepath = reflect_dir / filename
        with open(filepath, "w") as f:
            yaml.dump(structured, f, default_flow_style=False, sort_keys=False)

        # Also save to iteration log
        self.state_manager.save_log(iteration, "meta_reflection.yaml", structured)

        # Generate narrative
        narrative = self._generate_meta_narrative(reflection, raw_response)
        self.state_manager.save_log(iteration, "meta_reflection.md", narrative)

    def _generate_meta_narrative(
        self,
        reflection: MetaReflection,
        raw_response: str
    ) -> str:
        """Generate narrative Markdown for META-REFLECTION."""
        lines = [
            f"# Meta-Reflection: {reflection.id}",
            "",
            f"**Generated:** {reflection.timestamp.isoformat()}Z",
            f"**Iteration Range:** {reflection.iteration_range[0]} - {reflection.iteration_range[1]}",
            "",
            "---",
            "",
            "## Progress Assessment",
            "",
            f"- Primitives Added: {reflection.primitives_added}",
            f"- Acceptance Rate: {reflection.acceptance_rate:.1%}",
            f"- Coverage Before: {reflection.coverage_before:.1%}",
            f"- Coverage After: {reflection.coverage_after:.1%}",
            "",
            "## Strategy Assessment",
            "",
            f"- PROPOSER Effectiveness: {reflection.proposer_effectiveness}/5",
            f"- CRITIC Calibration: {reflection.critic_calibration}",
            "",
            "## Decision",
            "",
            f"**{reflection.decision}**",
            "",
            reflection.decision_justification,
            "",
        ]

        if reflection.insights:
            lines.extend([
                "## Insights for Archive",
                "",
            ])
            for i in reflection.insights:
                category = i.get("category", "general")
                insight = i.get("insight", str(i))
                lines.append(f"- [{category}] {insight}")
            lines.append("")

        lines.extend([
            "---",
            "",
            "## Raw Response",
            "",
            "```",
            raw_response[:3000] + "..." if len(raw_response) > 3000 else raw_response,
            "```",
        ])

        return "\n".join(lines)

    def log_iteration_summary(
        self,
        iteration: int,
        candidates_proposed: int,
        candidates_accepted: int,
        candidates_rejected: int,
        primitives_added: list[str],
        coverage_score: float
    ) -> None:
        """Log iteration summary."""
        summary = {
            "iteration_summary": {
                "iteration": iteration,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "candidates": {
                    "proposed": candidates_proposed,
                    "accepted": candidates_accepted,
                    "rejected": candidates_rejected,
                },
                "primitives_added": primitives_added,
                "metrics": {
                    "coverage": coverage_score,
                },
                "highlights": [],
            }
        }
        self.state_manager.save_log(iteration, "summary.yaml", summary)
