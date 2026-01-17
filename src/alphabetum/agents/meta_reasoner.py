"""META-REASONER agent: reflects on progress and adjusts strategy."""

import yaml
from typing import Any
from datetime import datetime

from .base import BaseAgent
from ..state.models import IterationState, MetaReflection, Domain


META_REASONER_SYSTEM_PROMPT = """
# ROLE: META-REASONER

You are the META-REASONER in Project Alphabetum. Your mission: step back from the work
and reflect on the process itself.

## Your Responsibilities

1. **Assess Progress**: Are we moving toward our goals?
2. **Identify Patterns**: What's working? What isn't?
3. **Audit Philosophy**: What assumptions are we making? Are we being true to Leibniz's vision?
4. **Adjust Strategy**: What should we change?
5. **Decide Direction**: Continue, pivot, or conclude?

## Decision Options

- **CONTINUE**: Keep current course with minor adjustments
- **PIVOT**: Make major strategy change (requires strong justification)
- **CONCLUDE**: We've gone as far as we can (requires very strong justification)

## Output Format

```yaml
meta_reflection:
  progress:
    primitives_added: 5
    primitives_rejected: 3
    acceptance_rate: 0.625
    coverage_before: 0.45
    coverage_after: 0.52
    assessment: "overall narrative of progress"

  patterns_observed:
    - pattern: "description"
      frequency: 3
      implications: "what this means"

  strategy_assessment:
    proposer_effectiveness: 4
    proposer_notes: "observations"
    critic_calibration: "balanced"
    critic_notes: "observations"
    domain_coverage_balance: "observations"

  philosophical_observations:
    assumptions_identified:
      - assumption: "description"
        problematic: false
        mitigation: null
    tradition_bias: "notes on any bias toward particular traditions"
    leibniz_alignment: 4
    leibniz_notes: "how well we're matching Leibniz's vision"

  course_corrections:
    strategy_adjustments:
      - component: "PROPOSER"
        adjustment: "what to change"
        rationale: "why"
    domain_priorities: ["mind", "ethics"]
    criterion_calibration: "notes"
    new_approaches: ["idea1"]

  decision: "CONTINUE"
  decision_justification: "why this decision"

  predictions:
    - prediction: "what will happen"
      confidence: 0.7

  insights_for_archive:
    - insight: "worth preserving"
      category: "philosophical"
```
"""


class MetaReasonerAgent(BaseAgent):
    """Reflects on progress and adjusts strategy."""

    @property
    def role_name(self) -> str:
        return "META-REASONER"

    @property
    def temperature(self) -> float:
        return self.config["temperatures"]["meta_reasoner"]

    def build_system_prompt(self, state: IterationState, **kwargs) -> str:
        return META_REASONER_SYSTEM_PROMPT

    def build_user_prompt(self, state: IterationState, **kwargs) -> str:
        start_iteration = kwargs.get("start_iteration", max(0, state.current_iteration - 5))
        recent_logs = kwargs.get("recent_logs", "")
        rejection_patterns = kwargs.get("rejection_patterns", "Not enough data yet.")
        current_gaps = kwargs.get("current_gaps", [])

        acceptance_rate = (
            state.total_accepted / state.total_proposed * 100
            if state.total_proposed > 0 else 0
        )

        gaps_str = "\n".join(f"- {g}" for g in current_gaps) if current_gaps else "- None identified"

        return f"""
## Current State

- **Iteration range under review**: {start_iteration} - {state.current_iteration}
- **Primitives accepted so far**: {state.total_accepted}
- **Candidates proposed**: {state.total_proposed}
- **Candidates rejected**: {state.total_rejected}
- **Acceptance rate**: {acceptance_rate:.1f}%
- **Coverage score**: {state.coverage_score * 100:.1f}%
- **Current proposer mode**: {state.proposer_mode}
- **Current domains priority**: {', '.join(d.value for d in state.domains_priority)}

## Recent Logs Summary

{recent_logs or "Early in project - limited logs available."}

## Rejection Patterns

{rejection_patterns}

## Current Gaps (concepts we cannot express)

{gaps_str}

## Your Task

1. Assess our progress honestly
2. Identify patterns in what's working and what isn't
3. Consider whether we're being true to Leibniz's vision
4. Decide: CONTINUE, PIVOT, or CONCLUDE
5. Provide specific recommendations

Be honest about challenges. This reflection is for improving the process.

Output valid YAML.
"""

    def parse_response(self, response: str) -> MetaReflection:
        """Parse YAML response into MetaReflection."""
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
            mr = data.get("meta_reflection", data)
        except yaml.YAMLError:
            # Return a default reflection
            return MetaReflection(
                id="MR_error",
                iteration_range=(0, 0),
                timestamp=datetime.utcnow(),
                decision="CONTINUE",
                decision_justification="Failed to parse meta-reflection, continuing by default"
            )

        progress = mr.get("progress", {})
        strategy = mr.get("strategy_assessment", {})
        philo = mr.get("philosophical_observations", {})
        corrections = mr.get("course_corrections", {})

        # Parse domain priorities
        domain_priorities = []
        for d in corrections.get("domain_priorities", []):
            try:
                domain_priorities.append(d)
            except ValueError:
                pass

        return MetaReflection(
            id=f"MR_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            iteration_range=(0, 0),  # Will be set by caller
            timestamp=datetime.utcnow(),
            primitives_added=progress.get("primitives_added", 0),
            primitives_rejected=progress.get("primitives_rejected", 0),
            acceptance_rate=float(progress.get("acceptance_rate", 0)),
            coverage_before=float(progress.get("coverage_before", 0)),
            coverage_after=float(progress.get("coverage_after", 0)),
            patterns_observed=mr.get("patterns_observed", []),
            proposer_effectiveness=int(strategy.get("proposer_effectiveness", 3)),
            critic_calibration=strategy.get("critic_calibration", "balanced"),
            strategy_adjustments=corrections.get("strategy_adjustments", []),
            domain_priorities=domain_priorities,
            decision=mr.get("decision", "CONTINUE"),
            decision_justification=mr.get("decision_justification", ""),
            predictions=mr.get("predictions", []),
            insights=mr.get("insights_for_archive", []),
        )

    def apply_adjustments(
        self,
        state: IterationState,
        reflection: MetaReflection
    ) -> IterationState:
        """Apply meta-reflection adjustments to state."""
        # Update domain priorities if suggested
        if reflection.domain_priorities:
            try:
                state.domains_priority = [
                    Domain(d) if isinstance(d, str) else d
                    for d in reflection.domain_priorities[:5]
                ]
            except ValueError:
                pass  # Keep existing if invalid

        # Adjust critic strictness based on calibration
        if reflection.critic_calibration == "too_strict":
            state.critic_strictness = max(0.3, state.critic_strictness - 0.1)
        elif reflection.critic_calibration == "too_lenient":
            state.critic_strictness = min(0.8, state.critic_strictness + 0.1)

        # Check for strategy adjustments
        for adj in reflection.strategy_adjustments:
            if adj.get("component") == "PROPOSER" and "mode" in adj.get("adjustment", "").lower():
                # Try to extract new mode
                adjustment = adj.get("adjustment", "")
                for mode in ["DOMAIN_SWEEP", "DECOMPOSITION_MINING", "GAP_FILLING",
                             "CROSS_REFERENCE", "THOUGHT_EXPERIMENT"]:
                    if mode in adjustment.upper():
                        state.proposer_mode = mode
                        break

        return state
