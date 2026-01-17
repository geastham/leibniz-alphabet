"""REFINER agent: integrates accepted primitives and maintains consistency."""

import yaml
from typing import Any, Optional
from datetime import datetime

from .base import BaseAgent
from ..state.models import (
    IterationState, Candidate, Evaluation,
    PrimitiveIndexEntry, PrimitiveDetailed, Definition, Relationship,
    Domain, PrimitiveStatus
)
from ..state.manager import StateManager


class RefinerAgent(BaseAgent):
    """Integrates accepted primitives, maintains consistency, updates relationships."""

    def __init__(self, config: dict, state_manager: StateManager):
        super().__init__(config)
        self.state_manager = state_manager

    @property
    def role_name(self) -> str:
        return "REFINER"

    @property
    def temperature(self) -> float:
        return self.config["temperatures"]["refiner"]

    def build_system_prompt(self, state: IterationState, **kwargs) -> str:
        return """
# ROLE: REFINER

You are the REFINER in Project Alphabetum. Your mission: integrate accepted primitives
into the alphabet while maintaining consistency.

## Your Responsibilities

1. **Integrate accepted primitives** with proper IDs and prime numbers
2. **Identify relationships** between new primitive and existing ones
3. **Check for conflicts** with existing primitives
4. **Maintain taxonomies** and domain organization

## Output Format

```yaml
integration:
  relationships:
    contrasts_with:
      - id: "PRM_XXXX"
        label: "primitive_name"
        reason: "why they contrast"
    presupposes:
      - id: "PRM_XXXX"
        label: "primitive_name"
        reason: "why this presupposition"
    composes_well_with:
      - id: "PRM_XXXX"
        label: "primitive_name"
        reason: "why they compose well"

  conflicts_detected: []

  notes: "any additional observations"
```
"""

    def build_user_prompt(self, state: IterationState, **kwargs) -> str:
        candidate: Candidate = kwargs["candidate"]
        alphabet_summary = kwargs.get("alphabet_summary", "No primitives yet.")

        return f"""
## Primitive to Integrate

Label: {candidate.label}
Domain: {candidate.domain.value}
Definition: {candidate.informal_definition}

## Current Alphabet

{alphabet_summary}

## Your Task

Identify relationships between this new primitive and existing ones.
What does it contrast with? What does it presuppose? What does it compose well with?

Output valid YAML.
"""

    def parse_response(self, response: str) -> dict:
        """Parse YAML response."""
        yaml_content = response
        if "```yaml" in response:
            yaml_content = response.split("```yaml")[1].split("```")[0]
        elif "```" in response:
            parts = response.split("```")
            if len(parts) >= 2:
                yaml_content = parts[1]

        try:
            return yaml.safe_load(yaml_content) or {}
        except yaml.YAMLError:
            return {}

    def integrate_primitive(
        self,
        candidate: Candidate,
        evaluation: Evaluation,
        state: IterationState,
        relationships: Optional[dict] = None
    ) -> tuple[PrimitiveIndexEntry, PrimitiveDetailed]:
        """
        Integrate an accepted candidate into the alphabet.

        Returns:
            Tuple of (index_entry, detailed_entry)
        """
        # Get current primitives and next ID/prime
        primitives = self.state_manager.load_alphabet_index()
        next_num = len(primitives) + 1
        primitive_id = f"PRM_{next_num:04d}"
        prime = self.state_manager.get_next_prime()

        # Build relationship lists from LLM response
        contrasts_with = []
        presupposes = []
        often_combined_with = []

        if relationships:
            integration = relationships.get("integration", relationships)

            for r in integration.get("relationships", {}).get("contrasts_with", []):
                contrasts_with.append(Relationship(
                    id=r.get("id", ""),
                    label=r.get("label", ""),
                    reason=r.get("reason", "")
                ))

            for r in integration.get("relationships", {}).get("presupposes", []):
                presupposes.append(Relationship(
                    id=r.get("id", ""),
                    label=r.get("label", ""),
                    reason=r.get("reason", "")
                ))

            for r in integration.get("relationships", {}).get("composes_well_with", []):
                often_combined_with.append(Relationship(
                    id=r.get("id", ""),
                    label=r.get("label", ""),
                    reason=r.get("reason", "")
                ))

        # Create index entry
        index_entry = PrimitiveIndexEntry(
            id=primitive_id,
            label=candidate.label,
            prime=prime,
            domain=candidate.domain,
            status=PrimitiveStatus.RECENT,
            added_iteration=state.current_iteration,
            last_reviewed=state.current_iteration,
            confidence=evaluation.confidence,
        )

        # Create detailed entry
        detailed = PrimitiveDetailed(
            id=primitive_id,
            symbol=candidate.proposed_symbol,
            label=candidate.label,
            definition=Definition(
                informal=candidate.informal_definition,
                formal=None,
                ostensive=candidate.ostensive_examples,
                negative=candidate.negative_examples,
            ),
            domain_primary=candidate.domain,
            domains_secondary=[],
            contrasts_with=contrasts_with,
            presupposes=presupposes,
            often_combined_with=often_combined_with,
            proposed_iteration=state.current_iteration,
            accepted_iteration=state.current_iteration,
            prime_number=prime,
            confidence=evaluation.confidence,
            version=1,
        )

        # Save to filesystem
        primitives.append(index_entry)
        self.state_manager.save_alphabet_index(primitives, state.current_iteration)
        self.state_manager.save_primitive_detailed(detailed)

        # Update relationship graph
        self._update_relationship_graph(
            primitive_id,
            contrasts_with,
            presupposes,
            often_combined_with,
            state.current_iteration
        )

        return index_entry, detailed

    def _update_relationship_graph(
        self,
        primitive_id: str,
        contrasts: list[Relationship],
        presupposes: list[Relationship],
        composes_well: list[Relationship],
        iteration: int
    ) -> None:
        """Update the relationship graph with new relationships."""
        graph = self.state_manager.load_relationships()

        # Add contrast relationships (bidirectional)
        for r in contrasts:
            if r.id:
                pair = tuple(sorted([primitive_id, r.id]))
                if pair not in graph.contrasts:
                    graph.contrasts.append(pair)

        # Add presupposition relationships
        for r in presupposes:
            if r.id:
                graph.presupposes.append({
                    "source": primitive_id,
                    "target": r.id,
                    "reason": r.reason
                })

        # Add composition affinities
        for r in composes_well:
            if r.id:
                pair = sorted([primitive_id, r.id])
                if pair not in graph.composes_well:
                    graph.composes_well.append(pair)

        self.state_manager.save_relationships(graph, iteration)

    def check_consistency(self, state: IterationState) -> list[dict]:
        """
        Check the alphabet for consistency issues.

        Returns list of issues found.
        """
        issues = []
        primitives = self.state_manager.load_alphabet_index()
        graph = self.state_manager.load_relationships()

        # Check for orphaned presuppositions
        primitive_ids = {p.id for p in primitives}
        for presup in graph.presupposes:
            if presup.get("target") not in primitive_ids:
                issues.append({
                    "type": "orphaned_presupposition",
                    "source": presup.get("source"),
                    "missing_target": presup.get("target"),
                    "severity": "high"
                })

        # Check for invalid contrasts
        for contrast in graph.contrasts:
            if isinstance(contrast, (list, tuple)) and len(contrast) == 2:
                if contrast[0] not in primitive_ids or contrast[1] not in primitive_ids:
                    issues.append({
                        "type": "invalid_contrast",
                        "primitives": contrast,
                        "severity": "medium"
                    })

        return issues
