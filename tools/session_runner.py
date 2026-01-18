#!/usr/bin/env python3
"""
Session Runner: Execute ALPHABETUM framework using Claude session as reasoning engine.

This script orchestrates the reasoning workflow interactively, allowing a Claude
session to act as all four agent roles (PROPOSER, CRITIC, REFINER, META-REASONER).

Usage:
    python tools/session_runner.py --phase proposer --output-prompt
    python tools/session_runner.py --phase critic --candidate-file PATH
    python tools/session_runner.py --save-candidates "YAML_CONTENT"
    python tools/session_runner.py --save-evaluation "YAML_CONTENT"
    python tools/session_runner.py --save-primitive "YAML_CONTENT"
"""

import argparse
import yaml
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from alphabetum.state.models import (
    IterationState, Candidate, Evaluation, PrimitiveDetailed,
    PrimitiveIndexEntry, Domain, Verdict, PrimitiveStatus
)


class SessionRunner:
    """Orchestrates ALPHABETUM execution for interactive Claude sessions."""

    def __init__(self, base_path: Path = None):
        self.base_path = base_path or Path(__file__).parent.parent
        self.config = self._load_config()
        self.state = self._load_state()
        self.alphabet = self._load_alphabet()

    def _load_config(self) -> dict:
        config_path = self.base_path / "config.yaml"
        with open(config_path) as f:
            return yaml.safe_load(f)

    def _load_state(self) -> dict:
        state_path = self.base_path / "reasoning" / "iteration_state.yaml"
        with open(state_path) as f:
            return yaml.safe_load(f)

    def _load_alphabet(self) -> dict:
        alphabet_path = self.base_path / "alphabet" / "primitives" / "index.yaml"
        with open(alphabet_path) as f:
            return yaml.safe_load(f)

    def _save_state(self):
        state_path = self.base_path / "reasoning" / "iteration_state.yaml"
        with open(state_path, 'w') as f:
            yaml.dump(self.state, f, default_flow_style=False, sort_keys=False)

    def _save_alphabet(self):
        alphabet_path = self.base_path / "alphabet" / "primitives" / "index.yaml"
        with open(alphabet_path, 'w') as f:
            yaml.dump(self.alphabet, f, default_flow_style=False, sort_keys=False)

    def get_alphabet_summary(self) -> str:
        """Generate a summary of current alphabet for prompts."""
        primitives = self.alphabet.get("primitives", [])
        if not primitives:
            return "No primitives in alphabet yet. This is iteration 0 - you are starting fresh."

        summary_lines = [f"Current alphabet contains {len(primitives)} primitives:"]
        for p in primitives:
            summary_lines.append(f"- **{p['label']}** ({p['domain']}): {p.get('brief_definition', 'No definition')}")
        return "\n".join(summary_lines)

    def generate_proposer_prompt(self, n: int = 3) -> str:
        """Generate the full prompt for PROPOSER role."""
        iter_state = self.state.get("iteration_state", {})
        strategy = iter_state.get("current_strategy", {})

        domains_priority = strategy.get("domains_priority", ["being", "space", "time", "causation", "mind"])
        proposer_mode = strategy.get("proposer_mode", "DOMAIN_SWEEP")

        gaps = iter_state.get("pending", {}).get("gaps_to_fill", [])
        gaps_str = "\n".join(f"- {g}" for g in gaps) if gaps else "- None identified yet (early in project)"

        strategy_descriptions = {
            "DOMAIN_SWEEP": "systematically survey the priority domains for fundamental concepts",
            "DECOMPOSITION_MINING": "take complex concepts and decompose them until you hit irreducible elements",
            "GAP_FILLING": "identify concepts needed to express currently inexpressible ideas",
            "CROSS_REFERENCE": "find concepts that appear repeatedly in different decompositions",
            "THOUGHT_EXPERIMENT": "imagine explaining human experience to an alien—what concepts are essential?",
        }

        prompt = f"""
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

## Current State

- **Iteration**: {iter_state.get('current_iteration', 0)}
- **Alphabet size**: {self.alphabet.get('statistics', {}).get('total_primitives', 0)} primitives
- **Current strategy**: {proposer_mode}
- **Priority domains**: {', '.join(domains_priority)}

## Your Strategy This Cycle

Using the **{proposer_mode}** strategy, your task is to: {strategy_descriptions.get(proposer_mode, 'generate promising primitive candidates')}

## Current Gaps (concepts we cannot yet express)

{gaps_str}

## Current Alphabet Summary

{self.get_alphabet_summary()}

## Your Task

Generate **{n}** candidate primitives. Focus especially on domains: {', '.join(domains_priority)}

Think carefully about:
1. What concepts seem to resist all attempts at definition?
2. What concepts appear as "atoms" when you decompose complex ideas?
3. What would be missing from a minimal language of thought?

## Output Format

You MUST output valid YAML with exactly this structure:

```yaml
candidates:
  - label: "concept_name"
    domain: "one of: being, space, time, causation, mind, matter, quantity, quality, relation, ethics, emotion, action, knowledge, social, language"
    proposed_symbol: "suggested symbol (unicode preferred)"
    informal_definition: "what this concept means"
    ostensive_examples:
      - "example 1 pointing to this concept"
      - "example 2"
      - "example 3"
    negative_examples:
      - "what this is NOT (to clarify boundaries)"
    primitiveness_argument: "why this cannot be decomposed into simpler parts"
    decomposition_resistance: "what happens when you try to break it down—why does it resist?"
    relevance_to_gaps: "how this helps express concepts we can't currently express"
    confidence: 0.7
```

Generate exactly {n} candidates now.
"""
        return prompt.strip()

    def generate_critic_prompt(self, candidate: dict) -> str:
        """Generate the full prompt for CRITIC role."""
        prompt = f"""
# ROLE: CRITIC

You are the CRITIC in Project Alphabetum. Your mission: rigorously test whether proposed concepts are truly primitive.

## Your Mindset

Be adversarial but fair. Your job is to find weaknesses. Apply every attack with genuine effort to falsify the claim of primitiveness. But also acknowledge when a concept survives your attacks.

## Attack Protocol

Apply these attacks in order:

### 1. DECOMPOSITION ATTACK
Try to break this concept into simpler parts:
- **Analytic**: Can you define it in terms of more basic concepts?
- **Synthetic**: Can you identify constituent parts or aspects?
- **Functional**: Can you describe what it does in terms of simpler operations?

### 2. CIRCULARITY CHECK
- Trace every concept used in the definition
- Do any of them presuppose the candidate itself?

### 3. REDUNDANCY TEST
Can this candidate be expressed as a composition of existing primitives?

### 4. EDGE CASES
Find contexts where the concept's meaning shifts or doesn't apply cleanly

### 5. CULTURAL VARIANCE
Is this concept truly universal across cultures?

### 6. PARSIMONY CHECK
Do we really need this primitive? What expressiveness do we lose without it?

## Candidate to Evaluate

```yaml
{yaml.dump(candidate, default_flow_style=False)}
```

## Current Alphabet (for redundancy checking)

{self.get_alphabet_summary()}

## Verdicts

After applying all attacks, render one of:
- **ACCEPT**: Candidate survived all attacks. Recommend for alphabet.
- **REJECT**: Candidate failed critical attack. Specify which and why.
- **REFINE**: Core intuition is valid, but formulation needs work.

## Output Format

```yaml
evaluation:
  candidate_label: "{candidate.get('label', 'unknown')}"

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

  verdict: "ACCEPT"
  confidence: 0.8
  reasoning_summary: "overall reasoning"
  key_insight: "something learned regardless of verdict"
```
"""
        return prompt.strip()

    def generate_refiner_prompt(self, candidate: dict, evaluation: dict) -> str:
        """Generate the full prompt for REFINER role."""
        next_prime = self._get_next_prime()
        next_id = f"P{self.alphabet.get('statistics', {}).get('total_primitives', 0) + 1:03d}"

        prompt = f"""
# ROLE: REFINER

You are the REFINER in Project Alphabetum. Your mission: integrate accepted primitives into the alphabet, establishing their relationships to existing concepts.

## Your Task

The CRITIC has accepted the following candidate. Your job is to:
1. Assign it a permanent ID and prime number
2. Identify its relationships to existing primitives
3. Finalize its definition for the alphabet

## Accepted Candidate

```yaml
{yaml.dump(candidate, default_flow_style=False)}
```

## CRITIC's Evaluation

```yaml
{yaml.dump(evaluation, default_flow_style=False)}
```

## Current Alphabet

{self.get_alphabet_summary()}

## Integration Details

- **Assigned ID**: {next_id}
- **Assigned Prime**: {next_prime}

## Output Format

```yaml
primitive:
  id: "{next_id}"
  label: "{candidate.get('label', 'unknown')}"
  domain: "{candidate.get('domain', 'being')}"
  symbol: "{candidate.get('proposed_symbol', '?')}"
  prime_number: {next_prime}

  definition:
    informal: "refined informal definition"
    formal: null  # to be developed later

  examples:
    ostensive: {candidate.get('ostensive_examples', [])}
    negative: {candidate.get('negative_examples', [])}

  relationships:
    contrasts_with: []  # list of primitive IDs that are mutually exclusive
    presupposes: []  # list of primitive IDs required to understand this
    composes_well_with: []  # primitives often combined with this
    similar_to: []  # related but distinct primitives

  confidence: 0.8
  status: "stable"

  notes: "any additional observations about this primitive"
```
"""
        return prompt.strip()

    def _get_next_prime(self) -> int:
        """Get the next available prime number for assignment."""
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
        used = self.alphabet.get("statistics", {}).get("total_primitives", 0)
        return primes[used] if used < len(primes) else primes[-1] + (used - len(primes) + 1) * 2

    def save_candidates(self, candidates_yaml: str) -> list[dict]:
        """Parse and save candidate proposals."""
        # Parse YAML
        if "```yaml" in candidates_yaml:
            yaml_content = candidates_yaml.split("```yaml")[1].split("```")[0]
        elif "```" in candidates_yaml:
            parts = candidates_yaml.split("```")
            yaml_content = parts[1] if len(parts) >= 2 else candidates_yaml
        else:
            yaml_content = candidates_yaml

        data = yaml.safe_load(yaml_content)
        candidates = data.get("candidates", [])

        # Assign IDs
        for i, c in enumerate(candidates):
            c["id"] = f"CAND_{self.state.get('iteration_state', {}).get('current_iteration', 0):03d}_{i:02d}"

        # Save to reasoning logs
        iteration = self.state.get("iteration_state", {}).get("current_iteration", 0)
        log_dir = self.base_path / "reasoning" / "logs" / f"iteration_{iteration:03d}"
        log_dir.mkdir(parents=True, exist_ok=True)

        # Save YAML log
        log_path = log_dir / "proposer.yaml"
        with open(log_path, 'w') as f:
            yaml.dump({
                "timestamp": datetime.now().isoformat(),
                "role": "PROPOSER",
                "iteration": iteration,
                "candidates": candidates
            }, f, default_flow_style=False, sort_keys=False)

        # Update state with pending candidates
        if "iteration_state" not in self.state:
            self.state["iteration_state"] = {}
        if "pending" not in self.state["iteration_state"]:
            self.state["iteration_state"]["pending"] = {}

        self.state["iteration_state"]["pending"]["candidates_to_evaluate"] = [c["id"] for c in candidates]
        self.state["iteration_state"]["last_updated"] = datetime.now().isoformat()
        self._save_state()

        print(f"Saved {len(candidates)} candidates to {log_path}")
        return candidates

    def save_evaluation(self, candidate_id: str, evaluation_yaml: str) -> dict:
        """Parse and save a critic evaluation."""
        # Parse YAML
        if "```yaml" in evaluation_yaml:
            yaml_content = evaluation_yaml.split("```yaml")[1].split("```")[0]
        elif "```" in evaluation_yaml:
            parts = evaluation_yaml.split("```")
            yaml_content = parts[1] if len(parts) >= 2 else evaluation_yaml
        else:
            yaml_content = evaluation_yaml

        data = yaml.safe_load(yaml_content)
        evaluation = data.get("evaluation", data)
        evaluation["candidate_id"] = candidate_id

        # Save to reasoning logs
        iteration = self.state.get("iteration_state", {}).get("current_iteration", 0)
        log_dir = self.base_path / "reasoning" / "logs" / f"iteration_{iteration:03d}"
        log_dir.mkdir(parents=True, exist_ok=True)

        log_path = log_dir / "critic.yaml"

        # Load existing evaluations or create new
        if log_path.exists():
            with open(log_path) as f:
                log_data = yaml.safe_load(f)
        else:
            log_data = {"timestamp": datetime.now().isoformat(), "role": "CRITIC", "evaluations": []}

        log_data["evaluations"].append(evaluation)

        with open(log_path, 'w') as f:
            yaml.dump(log_data, f, default_flow_style=False, sort_keys=False)

        # Update metrics
        verdict = evaluation.get("verdict", "REJECT").upper()
        history = self.state.get("iteration_state", {}).get("history", {})
        history["total_proposed"] = history.get("total_proposed", 0) + 1

        if verdict == "ACCEPT":
            history["total_accepted"] = history.get("total_accepted", 0) + 1
        else:
            history["total_rejected"] = history.get("total_rejected", 0) + 1

        self.state["iteration_state"]["history"] = history
        self._save_state()

        print(f"Saved evaluation for {candidate_id}: {verdict}")
        return evaluation

    def save_primitive(self, primitive_yaml: str) -> dict:
        """Parse and save a new primitive to the alphabet."""
        # Parse YAML
        if "```yaml" in primitive_yaml:
            yaml_content = primitive_yaml.split("```yaml")[1].split("```")[0]
        elif "```" in primitive_yaml:
            parts = primitive_yaml.split("```")
            yaml_content = parts[1] if len(parts) >= 2 else primitive_yaml
        else:
            yaml_content = primitive_yaml

        data = yaml.safe_load(yaml_content)
        primitive = data.get("primitive", data)

        # Create index entry
        index_entry = {
            "id": primitive.get("id"),
            "label": primitive.get("label"),
            "domain": primitive.get("domain"),
            "symbol": primitive.get("symbol"),
            "prime": primitive.get("prime_number"),
            "brief_definition": primitive.get("definition", {}).get("informal", ""),
            "status": primitive.get("status", "stable"),
            "added_iteration": self.state.get("iteration_state", {}).get("current_iteration", 0)
        }

        # Add to index
        if "primitives" not in self.alphabet:
            self.alphabet["primitives"] = []
        self.alphabet["primitives"].append(index_entry)

        # Update statistics
        stats = self.alphabet.get("statistics", {})
        stats["total_primitives"] = len(self.alphabet["primitives"])

        domain = primitive.get("domain", "being")
        by_domain = stats.get("by_domain", {})
        by_domain[domain] = by_domain.get(domain, 0) + 1
        stats["by_domain"] = by_domain

        by_status = stats.get("by_status", {"stable": 0, "recent": 0, "contested": 0})
        by_status["stable"] = by_status.get("stable", 0) + 1
        stats["by_status"] = by_status

        self.alphabet["statistics"] = stats
        self.alphabet["last_updated"] = datetime.now().isoformat()
        self.alphabet["iteration"] = self.state.get("iteration_state", {}).get("current_iteration", 0)

        self._save_alphabet()

        # Save detailed entry
        detailed_dir = self.base_path / "alphabet" / "primitives" / "detailed"
        detailed_dir.mkdir(parents=True, exist_ok=True)

        detailed_path = detailed_dir / f"{primitive.get('id', 'unknown')}.yaml"
        with open(detailed_path, 'w') as f:
            yaml.dump(primitive, f, default_flow_style=False, sort_keys=False)

        # Save refiner log
        iteration = self.state.get("iteration_state", {}).get("current_iteration", 0)
        log_dir = self.base_path / "reasoning" / "logs" / f"iteration_{iteration:03d}"
        log_dir.mkdir(parents=True, exist_ok=True)

        log_path = log_dir / "refiner.yaml"
        with open(log_path, 'w') as f:
            yaml.dump({
                "timestamp": datetime.now().isoformat(),
                "role": "REFINER",
                "iteration": iteration,
                "integrated_primitive": primitive
            }, f, default_flow_style=False, sort_keys=False)

        print(f"Added primitive {primitive.get('id')} ({primitive.get('label')}) to alphabet")
        print(f"Alphabet now contains {stats['total_primitives']} primitives")

        return primitive

    def advance_iteration(self):
        """Advance to the next iteration."""
        iter_state = self.state.get("iteration_state", {})
        iter_state["current_iteration"] = iter_state.get("current_iteration", 0) + 1
        iter_state["cycle_in_phase"] = 0
        iter_state["last_updated"] = datetime.now().isoformat()
        self.state["iteration_state"] = iter_state
        self._save_state()
        print(f"Advanced to iteration {iter_state['current_iteration']}")


def main():
    parser = argparse.ArgumentParser(description="Session Runner for ALPHABETUM")
    parser.add_argument("--phase", choices=["proposer", "critic", "refiner"], help="Generate prompt for phase")
    parser.add_argument("--output-prompt", action="store_true", help="Output the prompt for the phase")
    parser.add_argument("--candidate", type=str, help="Candidate YAML for critic phase")
    parser.add_argument("--save-candidates", type=str, help="Save PROPOSER output")
    parser.add_argument("--save-evaluation", type=str, help="Save CRITIC output")
    parser.add_argument("--candidate-id", type=str, help="Candidate ID for evaluation")
    parser.add_argument("--save-primitive", type=str, help="Save REFINER output")
    parser.add_argument("--advance", action="store_true", help="Advance to next iteration")
    parser.add_argument("--status", action="store_true", help="Show current status")
    parser.add_argument("-n", type=int, default=3, help="Number of candidates to generate")

    args = parser.parse_args()
    runner = SessionRunner()

    if args.status:
        iter_state = runner.state.get("iteration_state", {})
        stats = runner.alphabet.get("statistics", {})
        print("=== ALPHABETUM Status ===")
        print(f"Iteration: {iter_state.get('current_iteration', 0)}")
        print(f"Phase: {iter_state.get('phase', 'EXPANSION')}")
        print(f"Primitives: {stats.get('total_primitives', 0)}")
        print(f"History: {iter_state.get('history', {})}")
        return

    if args.phase == "proposer" and args.output_prompt:
        print(runner.generate_proposer_prompt(n=args.n))
        return

    if args.phase == "critic" and args.candidate:
        candidate = yaml.safe_load(args.candidate)
        print(runner.generate_critic_prompt(candidate))
        return

    if args.save_candidates:
        runner.save_candidates(args.save_candidates)
        return

    if args.save_evaluation:
        if not args.candidate_id:
            print("Error: --candidate-id required with --save-evaluation")
            return
        runner.save_evaluation(args.candidate_id, args.save_evaluation)
        return

    if args.save_primitive:
        runner.save_primitive(args.save_primitive)
        return

    if args.advance:
        runner.advance_iteration()
        return

    parser.print_help()


if __name__ == "__main__":
    main()
