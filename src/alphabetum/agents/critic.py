"""CRITIC agent: evaluates candidate primitives."""

import yaml
from typing import Any

from .base import BaseAgent
from ..state.models import IterationState, Candidate, Evaluation, AttackResult, Verdict


CRITIC_SYSTEM_PROMPT = """
# ROLE: CRITIC

You are the CRITIC in Project Alphabetum. Your mission: rigorously test whether proposed concepts are truly primitive.

## Your Mindset

Be adversarial but fair. Your job is to find weaknesses. Apply every attack with genuine effort to falsify the claim of primitiveness. But also acknowledge when a concept survives your attacks.

## Attack Protocol

For each candidate, apply these attacks in order:

### 1. DECOMPOSITION ATTACK
Try to break this concept into simpler parts:
- **Analytic**: Can you define it in terms of more basic concepts?
- **Synthetic**: Can you identify constituent parts or aspects?
- **Functional**: Can you describe what it does in terms of simpler operations?

### 2. CIRCULARITY CHECK
- Trace every concept used in the definition
- Do any of them presuppose the candidate itself?
- Do any of them rely on concepts not yet in our alphabet?

### 3. REDUNDANCY TEST
Can this candidate be expressed as a composition of existing primitives?
- If yes: it's not primitive
- If no: note what makes it distinct

### 4. EDGE CASES
Find contexts where:
- The concept's meaning shifts
- The concept doesn't apply cleanly
- The concept behaves unexpectedly

### 5. CULTURAL VARIANCE
- Is this concept truly universal across cultures?
- Evidence from linguistics? Developmental psychology?
- Could an alien civilization lack this concept?

### 6. PARSIMONY CHECK
- Do we really need this primitive?
- What expressiveness do we lose without it?
- Is there a more economical alternative?

## Verdicts

After applying all attacks, render one of:
- **ACCEPT**: Candidate survived all attacks. Recommend for alphabet.
- **REJECT**: Candidate failed critical attack. Specify which and why.
- **REFINE**: Core intuition is valid, but formulation needs work.

## Output Format

You MUST output valid YAML:

```yaml
evaluation:
  candidate_id: "the_id"

  decomposition:
    attempts:
      - approach: "analytic"
        attempt: "what you tried"
        result: "why it failed/succeeded"
        survived: true
    survived: true
    notes: "summary"

  circularity:
    concepts_traced: ["concept1", "concept2"]
    circular_paths: []
    survived: true
    notes: "summary"

  redundancy:
    can_be_expressed: false
    using_primitives: null
    notes: "summary"

  edge_cases:
    cases_found:
      - case: "description"
        severity: "low"
    overall_severity: "low"
    notes: "summary"

  cultural_variance:
    evidence_for_universality: ["evidence1"]
    evidence_against: []
    assessment: "universal"
    notes: "summary"

  parsimony:
    expressiveness_value: "high"
    necessary: true
    notes: "summary"

  verdict: "ACCEPT"  # or REJECT or REFINE
  confidence: 0.8
  reasoning_summary: "overall reasoning"
  key_insight: "something learned regardless of verdict"
```
"""


class CriticAgent(BaseAgent):
    """Evaluates candidate primitives for primitiveness."""

    @property
    def role_name(self) -> str:
        return "CRITIC"

    @property
    def temperature(self) -> float:
        return self.config["temperatures"]["critic"]

    def build_system_prompt(self, state: IterationState, **kwargs) -> str:
        return CRITIC_SYSTEM_PROMPT

    def build_user_prompt(self, state: IterationState, **kwargs) -> str:
        candidate: Candidate = kwargs["candidate"]
        alphabet_summary = kwargs.get("alphabet_summary", "No primitives yet.")

        prompt = f"""
## Candidate to Evaluate

```yaml
candidate:
  id: "{candidate.id}"
  label: "{candidate.label}"
  domain: "{candidate.domain.value}"
  proposed_symbol: "{candidate.proposed_symbol}"
  informal_definition: "{candidate.informal_definition}"
  ostensive_examples: {candidate.ostensive_examples}
  negative_examples: {candidate.negative_examples}
  primitiveness_argument: "{candidate.primitiveness_argument}"
  decomposition_resistance: "{candidate.decomposition_resistance}"
```

## Current Alphabet (for redundancy checking)

{alphabet_summary}

## Your Task

Apply all six attacks to this candidate. Be thorough but fair.
Remember: if this concept truly resists decomposition, that's valuable information.

Output your evaluation as valid YAML.
"""
        return prompt

    def parse_response(self, response: str) -> Evaluation:
        """Parse YAML response into Evaluation object."""
        yaml_content = response
        if "```yaml" in response:
            yaml_content = response.split("```yaml")[1].split("```")[0]
        elif "```" in response:
            parts = response.split("```")
            if len(parts) >= 2:
                yaml_content = parts[1]
                if yaml_content.startswith("yaml"):
                    yaml_content = yaml_content[4:]

        try:
            data = yaml.safe_load(yaml_content)
            e = data.get("evaluation", data)  # Handle both nested and flat
        except yaml.YAMLError:
            # Return a default rejection if parsing fails
            return Evaluation(
                candidate_id="unknown",
                verdict=Verdict.REJECT,
                confidence=0.5,
                reasoning_summary="Failed to parse evaluation response"
            )

        # Parse decomposition attacks
        decomposition_attacks = []
        decomp = e.get("decomposition", {})
        for attempt in decomp.get("attempts", []):
            decomposition_attacks.append(AttackResult(
                approach=attempt.get("approach", "unknown"),
                attempt=attempt.get("attempt", ""),
                result=attempt.get("result", ""),
                survived=attempt.get("survived", True),
            ))

        # Parse verdict
        verdict_str = e.get("verdict", "REJECT").upper()
        try:
            verdict = Verdict(verdict_str)
        except ValueError:
            verdict = Verdict.REJECT

        return Evaluation(
            candidate_id=e.get("candidate_id", "unknown"),
            decomposition_attacks=decomposition_attacks,
            decomposition_survived=decomp.get("survived", True),
            circularity_survived=e.get("circularity", {}).get("survived", True),
            circularity_notes=e.get("circularity", {}).get("notes", ""),
            redundancy_can_be_expressed=e.get("redundancy", {}).get("can_be_expressed", False),
            redundancy_using=e.get("redundancy", {}).get("using_primitives"),
            edge_cases_severity=e.get("edge_cases", {}).get("overall_severity", "low"),
            cultural_assessment=e.get("cultural_variance", {}).get("assessment", "universal"),
            parsimony_necessary=e.get("parsimony", {}).get("necessary", True),
            verdict=verdict,
            confidence=float(e.get("confidence", 0.5)),
            reasoning_summary=e.get("reasoning_summary", ""),
            key_insight=e.get("key_insight"),
        )
