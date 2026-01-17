"""PROPOSER agent: generates candidate primitives."""

import yaml
from typing import Any

from .base import BaseAgent
from ..state.models import IterationState, Candidate, Domain


PROPOSER_SYSTEM_PROMPT = """
# ROLE: PROPOSER

You are the PROPOSER in Project Alphabetum, an attempt to reconstruct Leibniz's Alphabet of Human Thought.

## Your Mission

Generate candidate **primitive concepts**—irreducible, simple ideas that cannot be broken down further and from which complex concepts can be composed.

## What Makes a Good Primitive

1. **Irreducible**: Cannot be defined in terms of simpler concepts without circularity
2. **Universal**: Applies across cultures and contexts
3. **Necessary**: Required to express important complex concepts
4. **Independent**: Not redundant with existing primitives
5. **Clear**: Has determinate boundaries of application

## Guidelines

1. Draw from multiple sources: Leibniz's writings, philosophical traditions, linguistics, mathematics, common sense
2. Think creatively but rigorously. Ask: "Could an alien understand human experience without this concept?"
3. Don't worry about being wrong—that's the CRITIC's job. Your job is to generate interesting candidates.
4. Focus on concepts that seem to resist further analysis

## Output Format

You MUST output valid YAML with exactly this structure:

```yaml
candidates:
  - label: "concept_name"
    domain: "one of: being, space, time, causation, mind, matter, quantity, quality, relation, ethics, emotion, action, knowledge, social, language"
    proposed_symbol: "suggested symbol (unicode preferred)"
    informal_definition: "what this concept means (some circularity acceptable for true primitives)"
    ostensive_examples:
      - "example 1 pointing to this concept"
      - "example 2"
      - "example 3"
    negative_examples:
      - "what this is NOT (to clarify boundaries)"
    primitiveness_argument: "why this cannot be decomposed into simpler parts"
    decomposition_resistance: "what happens when you try to break it down—why does it resist?"
    relevance_to_gaps: "how this helps express concepts we can't currently express"
    confidence: 0.7  # your confidence 0.0-1.0
```

Generate exactly {n} candidates.
"""


class ProposerAgent(BaseAgent):
    """Generates candidate primitive concepts."""

    @property
    def role_name(self) -> str:
        return "PROPOSER"

    @property
    def temperature(self) -> float:
        return self.config["temperatures"]["proposer"]

    def build_system_prompt(self, state: IterationState, **kwargs) -> str:
        n = kwargs.get("n", 3)
        return PROPOSER_SYSTEM_PROMPT.format(n=n)

    def build_user_prompt(self, state: IterationState, **kwargs) -> str:
        n = kwargs.get("n", 3)
        alphabet_summary = kwargs.get("alphabet_summary", "No primitives yet.")
        gaps = kwargs.get("gaps", [])

        domains_str = ", ".join(d.value for d in state.domains_priority)
        gaps_str = "\n".join(f"- {g}" for g in gaps) if gaps else "- None identified yet (early in project)"

        # Strategy descriptions
        strategy_descriptions = {
            "DOMAIN_SWEEP": "systematically survey the priority domains for fundamental concepts",
            "DECOMPOSITION_MINING": "take complex concepts and decompose them until you hit irreducible elements",
            "GAP_FILLING": "identify concepts needed to express currently inexpressible ideas",
            "CROSS_REFERENCE": "find concepts that appear repeatedly in different decompositions",
            "THOUGHT_EXPERIMENT": "imagine explaining human experience to an alien—what concepts are essential?",
        }

        strategy_desc = strategy_descriptions.get(
            state.proposer_mode,
            "generate promising primitive candidates"
        )

        prompt = f"""
## Current State

- **Iteration**: {state.current_iteration}
- **Alphabet size**: {state.total_accepted} primitives accepted so far
- **Current strategy**: {state.proposer_mode}
- **Priority domains**: {domains_str}

## Your Strategy This Cycle

Using the **{state.proposer_mode}** strategy, your task is to: {strategy_desc}

## Current Gaps (concepts we cannot yet express)

{gaps_str}

## Current Alphabet Summary

{alphabet_summary}

## Your Task

Generate **{n}** candidate primitives. Focus especially on domains: {domains_str}

Think carefully about:
1. What concepts seem to resist all attempts at definition?
2. What concepts appear as "atoms" when you decompose complex ideas?
3. What would be missing from a minimal language of thought?

Output valid YAML now.
"""
        return prompt

    def parse_response(self, response: str) -> list[Candidate]:
        """Parse YAML response into Candidate objects."""
        # Extract YAML from response (handle markdown code blocks)
        yaml_content = response
        if "```yaml" in response:
            yaml_content = response.split("```yaml")[1].split("```")[0]
        elif "```" in response:
            parts = response.split("```")
            if len(parts) >= 2:
                yaml_content = parts[1]
                # Remove language identifier if present
                if yaml_content.startswith("yaml"):
                    yaml_content = yaml_content[4:]

        try:
            data = yaml.safe_load(yaml_content)
        except yaml.YAMLError:
            # If parsing fails, try to extract just the candidates section
            data = {"candidates": []}

        candidates = []
        for i, c in enumerate(data.get("candidates", [])):
            try:
                # Parse domain, handling potential invalid values
                domain_str = c.get("domain", "being")
                try:
                    domain = Domain(domain_str)
                except ValueError:
                    domain = Domain.BEING  # Default fallback

                candidate = Candidate(
                    id=f"CAND_{i:03d}",  # Will be updated with iteration
                    label=c.get("label", f"unnamed_{i}"),
                    domain=domain,
                    proposed_symbol=c.get("proposed_symbol", "?"),
                    informal_definition=c.get("informal_definition", ""),
                    ostensive_examples=c.get("ostensive_examples", []),
                    negative_examples=c.get("negative_examples", []),
                    primitiveness_argument=c.get("primitiveness_argument", ""),
                    decomposition_resistance=c.get("decomposition_resistance", ""),
                    relevance_to_gaps=c.get("relevance_to_gaps", ""),
                    confidence=float(c.get("confidence", 0.5)),
                )
                candidates.append(candidate)
            except Exception:
                # Skip malformed candidates
                continue

        return candidates
