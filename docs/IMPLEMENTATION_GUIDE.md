# Implementation Guide

## Step-by-Step Instructions for Building ALPHABETUM

**Version:** 1.0.0  
**Last Updated:** 2024-03-15  
**Status:** Canonical Reference  
**Audience:** Coding Agents / Developers

---

## Table of Contents

1. [Implementation Overview](#1-implementation-overview)
2. [Phase 1: Project Scaffolding](#2-phase-1-project-scaffolding)
3. [Phase 2: Core Data Layer](#3-phase-2-core-data-layer)
4. [Phase 3: Agent Roles](#4-phase-3-agent-roles)
5. [Phase 4: The Loop Engine](#5-phase-4-the-loop-engine)
6. [Phase 5: Logging & Archiving](#6-phase-5-logging--archiving)
7. [Phase 6: Validation Suite](#7-phase-6-validation-suite)
8. [Phase 7: Calculus Implementation](#8-phase-7-calculus-implementation)
9. [Phase 8: Tools & Utilities](#9-phase-8-tools--utilities)
10. [Phase 9: Testing & Validation](#10-phase-9-testing--validation)
11. [Phase 10: Running the System](#11-phase-10-running-the-system)

---

## 1. Implementation Overview

### 1.1 What You're Building

You are implementing an **autonomous philosophical reasoning system** that:

1. **Generates** candidate primitive concepts
2. **Evaluates** them rigorously
3. **Integrates** survivors into an alphabet
4. **Tests** expressiveness against benchmarks
5. **Reflects** on its own process
6. **Logs** everything transparently

### 1.2 Architecture Summary

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          ALPHABETUM SYSTEM                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                 │
│  │   CONFIG    │    │    STATE    │    │    LLM      │                 │
│  │   LAYER     │    │    LAYER    │    │   LAYER     │                 │
│  │             │    │             │    │             │                 │
│  │ config.yaml │    │ YAML files  │    │ API calls   │                 │
│  │ .env        │    │ in repo     │    │ Prompts     │                 │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘                 │
│         │                  │                  │                         │
│         └──────────────────┼──────────────────┘                         │
│                            │                                            │
│                            ▼                                            │
│                   ┌─────────────────┐                                   │
│                   │   LOOP ENGINE   │                                   │
│                   │                 │                                   │
│                   │ Orchestrates    │                                   │
│                   │ phases & roles  │                                   │
│                   └────────┬────────┘                                   │
│                            │                                            │
│         ┌──────────────────┼──────────────────┐                         │
│         │                  │                  │                         │
│         ▼                  ▼                  ▼                         │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                 │
│  │  PROPOSER   │    │   CRITIC    │    │   REFINER   │                 │
│  │   AGENT     │    │   AGENT     │    │   AGENT     │                 │
│  └─────────────┘    └─────────────┘    └─────────────┘                 │
│         │                  │                  │                         │
│         └──────────────────┼──────────────────┘                         │
│                            │                                            │
│                            ▼                                            │
│                   ┌─────────────────┐                                   │
│                   │   ARCHIVIST     │                                   │
│                   │                 │                                   │
│                   │ Logs everything │                                   │
│                   │ to filesystem   │                                   │
│                   └─────────────────┘                                   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 1.3 Implementation Order

```
PHASE 1: Scaffolding     ████░░░░░░░░░░░░░░░░  Setup, structure, deps
PHASE 2: Data Layer      ████████░░░░░░░░░░░░  State management, YAML I/O
PHASE 3: Agent Roles     ████████████░░░░░░░░  Prompts, LLM calls
PHASE 4: Loop Engine     ████████████████░░░░  Orchestration
PHASE 5: Logging         ████████████████████  Archivist system
PHASE 6: Validation      ██████████████████░░  Consistency checks
PHASE 7: Calculus        ████████████████████  Composition system
PHASE 8: Tools           ██████████░░░░░░░░░░  CLI, utilities
PHASE 9: Testing         ████████████░░░░░░░░  Unit & integration tests
PHASE 10: Running        ████████████████████  Execute the loop
```

---

## 2. Phase 1: Project Scaffolding

### 2.1 Create Directory Structure

```bash
# Run from repository root
mkdir -p alphabet/primitives/{detailed,by_domain}
mkdir -p alphabet/relationships
mkdir -p alphabet/versions
mkdir -p calculus/{implementations,examples}
mkdir -p reasoning/{logs,decisions,paradoxes,rejected,meta_reflections}
mkdir -p validation/{benchmarks/results,comparisons,consistency}
mkdir -p sources/{leibniz,philosophical,modern_ontologies}
mkdir -p tools
mkdir -p src/alphabetum/{agents,state,loop,logging,validation,calculus}
mkdir -p tests/{unit,integration}
```

### 2.2 Create Configuration Files

**`config.yaml`**:

```yaml
# Main configuration file
version: "1.0.0"

llm:
  provider: anthropic  # or 'openai'
  model: claude-3-opus-20240229
  max_tokens: 4096
  timeout_seconds: 120
  retry_attempts: 3
  retry_delay_seconds: 5

temperatures:
  proposer: 0.7
  critic: 0.3
  refiner: 0.5
  meta_reasoner: 0.5

iteration:
  candidates_per_cycle: 3
  expansion_cycles: 4
  consolidation_cycles: 2
  composition_cycles: 3
  meta_reflection_interval: 5

stopping:
  coverage_threshold: 0.90
  diminishing_returns_window: 10
  diminishing_returns_threshold: 2
  max_iterations: 500
  stability_window: 10

logging:
  level: DEBUG
  include_raw_llm_output: true
  pretty_print_yaml: true

validation:
  run_consistency_check: true
  run_coverage_check: true
  check_interval: 10

paths:
  alphabet: alphabet/
  reasoning: reasoning/
  calculus: calculus/
  validation: validation/
```

**`.env`** (template):

```bash
# API Keys
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here

# Optional
LOG_LEVEL=DEBUG
```

**`requirements.txt`**:

```
# Core
anthropic>=0.25.0
openai>=1.12.0
pyyaml>=6.0
pydantic>=2.6.0

# Utilities
python-dotenv>=1.0.0
rich>=13.7.0
typer>=0.9.0

# Graph operations
networkx>=3.2

# Math
sympy>=1.12

# Optional: visualization
matplotlib>=3.8.0
graphviz>=0.20

# Testing
pytest>=8.0.0
pytest-asyncio>=0.23.0
```

**`pyproject.toml`**:

```toml
[project]
name = "alphabetum"
version = "0.1.0"
description = "Reconstructing Leibniz's Alphabet of Human Thought"
requires-python = ">=3.11"

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

### 2.3 Create Initial State Files

**`alphabet/primitives/index.yaml`**:

```yaml
alphabet_index:
  version: "1.0.0"
  last_updated: null
  iteration: 0
  
  statistics:
    total_primitives: 0
    by_domain: {}
    by_status:
      stable: 0
      recent: 0
      contested: 0
      
  primitives: []
```

**`reasoning/iteration_state.yaml`**:

```yaml
iteration_state:
  current_iteration: 0
  phase: EXPANSION
  cycle_in_phase: 0
  last_updated: null
  
  current_strategy:
    proposer_mode: DOMAIN_SWEEP
    proposer_temperature: 0.7
    critic_strictness: 0.5
    domains_priority:
      - being
      - space
      - time
      - causation
      - mind
      
  pending:
    candidates_to_evaluate: []
    candidates_to_revise: []
    conflicts_to_resolve: []
    gaps_to_fill: []
    
  metrics:
    recent_acceptance_rate: null
    coverage_score: 0.0
    consistency_score: 1.0
    
  triggers:
    meta_reflection_due: false
    iterations_since_meta: 0
    iterations_since_primitive: 0
    
  history:
    total_proposed: 0
    total_accepted: 0
    total_rejected: 0
```

**`alphabet/relationships/graph.yaml`**:

```yaml
relationship_graph:
  version: "1.0.0"
  last_updated: null
  iteration: 0
  
  contrasts: []
  presupposes: []
  composes_well: []
```

---

## 3. Phase 2: Core Data Layer

### 3.1 State Models

**`src/alphabetum/state/models.py`**:

```python
"""Pydantic models for all data structures."""

from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class Phase(str, Enum):
    EXPANSION = "EXPANSION"
    CONSOLIDATION = "CONSOLIDATION"
    COMPOSITION = "COMPOSITION"
    META_REFLECTION = "META_REFLECTION"


class Verdict(str, Enum):
    ACCEPT = "ACCEPT"
    REJECT = "REJECT"
    REFINE = "REFINE"
    DEFER = "DEFER"


class PrimitiveStatus(str, Enum):
    STABLE = "stable"
    RECENT = "recent"
    CONTESTED = "contested"
    DEPRECATED = "deprecated"


class Domain(str, Enum):
    BEING = "being"
    SPACE = "space"
    TIME = "time"
    CAUSATION = "causation"
    MIND = "mind"
    MATTER = "matter"
    QUANTITY = "quantity"
    QUALITY = "quality"
    RELATION = "relation"
    ETHICS = "ethics"
    EMOTION = "emotion"
    ACTION = "action"
    KNOWLEDGE = "knowledge"
    SOCIAL = "social"
    LANGUAGE = "language"


class PrimitiveIndexEntry(BaseModel):
    """Compact entry in the alphabet index."""
    id: str
    label: str
    prime: int
    domain: Domain
    status: PrimitiveStatus
    added_iteration: int
    last_reviewed: int
    confidence: float = Field(ge=0.0, le=1.0)


class Definition(BaseModel):
    """Definition structure for a primitive."""
    informal: str
    formal: Optional[str] = None
    ostensive: list[str] = Field(default_factory=list)
    negative: list[str] = Field(default_factory=list)


class Relationship(BaseModel):
    """A relationship to another primitive."""
    id: str
    label: str
    reason: str


class PrimitiveDetailed(BaseModel):
    """Full primitive specification."""
    id: str
    symbol: str
    label: str
    definition: Definition
    domain_primary: Domain
    domains_secondary: list[Domain] = Field(default_factory=list)
    
    contrasts_with: list[Relationship] = Field(default_factory=list)
    presupposes: list[Relationship] = Field(default_factory=list)
    often_combined_with: list[Relationship] = Field(default_factory=list)
    
    proposed_iteration: int
    accepted_iteration: Optional[int] = None
    prime_number: int
    confidence: float = Field(ge=0.0, le=1.0)
    version: int = 1


class IterationState(BaseModel):
    """Current iteration state."""
    current_iteration: int
    phase: Phase
    cycle_in_phase: int
    last_updated: Optional[datetime] = None
    
    proposer_mode: str
    proposer_temperature: float
    critic_strictness: float
    domains_priority: list[Domain]
    
    candidates_to_evaluate: list[str] = Field(default_factory=list)
    gaps_to_fill: list[str] = Field(default_factory=list)
    
    coverage_score: float = 0.0
    consistency_score: float = 1.0
    recent_acceptance_rate: Optional[float] = None
    
    total_proposed: int = 0
    total_accepted: int = 0
    total_rejected: int = 0


class Candidate(BaseModel):
    """A candidate primitive proposed by PROPOSER."""
    id: str
    label: str
    domain: Domain
    proposed_symbol: str
    informal_definition: str
    ostensive_examples: list[str]
    negative_examples: list[str]
    primitiveness_argument: str
    decomposition_resistance: str
    relevance_to_gaps: str
    confidence: float


class AttackResult(BaseModel):
    """Result of a CRITIC attack."""
    approach: str
    attempt: str
    result: str
    survived: bool


class Evaluation(BaseModel):
    """CRITIC's evaluation of a candidate."""
    candidate_id: str
    
    decomposition_attacks: list[AttackResult]
    decomposition_survived: bool
    
    circularity_survived: bool
    circularity_notes: str
    
    redundancy_can_be_expressed: bool
    redundancy_using: Optional[list[str]] = None
    
    edge_cases_severity: str  # low, medium, high
    
    cultural_assessment: str  # universal, near_universal, culturally_bound
    
    parsimony_necessary: bool
    
    verdict: Verdict
    confidence: float
    reasoning_summary: str
    key_insight: Optional[str] = None
```

### 3.2 State Manager

**`src/alphabetum/state/manager.py`**:

```python
"""State management for the alphabet and reasoning logs."""

import yaml
from pathlib import Path
from datetime import datetime
from typing import Optional

from .models import (
    IterationState, PrimitiveIndexEntry, PrimitiveDetailed,
    Phase, Domain, PrimitiveStatus
)


class StateManager:
    """Manages all persistent state for ALPHABETUM."""
    
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.alphabet_path = base_path / "alphabet"
        self.reasoning_path = base_path / "reasoning"
        
    # === ITERATION STATE ===
    
    def load_iteration_state(self) -> IterationState:
        """Load current iteration state from YAML."""
        state_file = self.reasoning_path / "iteration_state.yaml"
        with open(state_file) as f:
            data = yaml.safe_load(f)
        return self._parse_iteration_state(data["iteration_state"])
    
    def save_iteration_state(self, state: IterationState) -> None:
        """Save iteration state to YAML."""
        state_file = self.reasoning_path / "iteration_state.yaml"
        state.last_updated = datetime.utcnow()
        data = {"iteration_state": self._serialize_iteration_state(state)}
        with open(state_file, "w") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
    
    # === ALPHABET ===
    
    def load_alphabet_index(self) -> list[PrimitiveIndexEntry]:
        """Load the alphabet index."""
        index_file = self.alphabet_path / "primitives" / "index.yaml"
        with open(index_file) as f:
            data = yaml.safe_load(f)
        return [
            PrimitiveIndexEntry(**p) 
            for p in data["alphabet_index"]["primitives"]
        ]
    
    def save_alphabet_index(
        self, 
        primitives: list[PrimitiveIndexEntry],
        iteration: int
    ) -> None:
        """Save the alphabet index."""
        index_file = self.alphabet_path / "primitives" / "index.yaml"
        
        # Compute statistics
        by_domain = {}
        by_status = {"stable": 0, "recent": 0, "contested": 0}
        
        for p in primitives:
            domain = p.domain.value
            by_domain[domain] = by_domain.get(domain, 0) + 1
            by_status[p.status.value] = by_status.get(p.status.value, 0) + 1
        
        data = {
            "alphabet_index": {
                "version": "1.0.0",
                "last_updated": datetime.utcnow().isoformat() + "Z",
                "iteration": iteration,
                "statistics": {
                    "total_primitives": len(primitives),
                    "by_domain": by_domain,
                    "by_status": by_status,
                },
                "primitives": [p.model_dump() for p in primitives]
            }
        }
        
        with open(index_file, "w") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
    
    def load_primitive_detailed(self, primitive_id: str) -> PrimitiveDetailed:
        """Load a detailed primitive entry."""
        # Find the file
        detailed_dir = self.alphabet_path / "primitives" / "detailed"
        for f in detailed_dir.glob(f"{primitive_id}_*.yaml"):
            with open(f) as file:
                data = yaml.safe_load(file)
            return PrimitiveDetailed(**data["primitive"])
        raise FileNotFoundError(f"Primitive {primitive_id} not found")
    
    def save_primitive_detailed(self, primitive: PrimitiveDetailed) -> Path:
        """Save a detailed primitive entry."""
        filename = f"{primitive.id}_{primitive.label}.yaml"
        filepath = self.alphabet_path / "primitives" / "detailed" / filename
        
        data = {"primitive": primitive.model_dump()}
        with open(filepath, "w") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        return filepath
    
    # === PRIMES ===
    
    def get_next_prime(self) -> int:
        """Get the next available prime number for a new primitive."""
        primitives = self.load_alphabet_index()
        if not primitives:
            return 2  # First prime
        
        used_primes = {p.prime for p in primitives}
        candidate = max(used_primes) + 1
        
        while not self._is_prime(candidate):
            candidate += 1
        
        return candidate
    
    def _is_prime(self, n: int) -> bool:
        """Check if n is prime."""
        if n < 2:
            return False
        for i in range(2, int(n**0.5) + 1):
            if n % i == 0:
                return False
        return True
    
    # === ITERATION LOGS ===
    
    def ensure_iteration_log_dir(self, iteration: int) -> Path:
        """Create iteration log directory if needed."""
        log_dir = self.reasoning_path / "logs" / f"iteration_{iteration:03d}"
        log_dir.mkdir(parents=True, exist_ok=True)
        return log_dir
    
    def save_log(
        self, 
        iteration: int, 
        filename: str, 
        content: dict | str
    ) -> Path:
        """Save a log file for an iteration."""
        log_dir = self.ensure_iteration_log_dir(iteration)
        filepath = log_dir / filename
        
        with open(filepath, "w") as f:
            if isinstance(content, dict):
                yaml.dump(content, f, default_flow_style=False, sort_keys=False)
            else:
                f.write(content)
        
        return filepath
    
    # === HELPERS ===
    
    def _parse_iteration_state(self, data: dict) -> IterationState:
        """Parse iteration state from YAML data."""
        return IterationState(
            current_iteration=data["current_iteration"],
            phase=Phase(data["phase"]),
            cycle_in_phase=data["cycle_in_phase"],
            proposer_mode=data["current_strategy"]["proposer_mode"],
            proposer_temperature=data["current_strategy"]["proposer_temperature"],
            critic_strictness=data["current_strategy"]["critic_strictness"],
            domains_priority=[Domain(d) for d in data["current_strategy"]["domains_priority"]],
            candidates_to_evaluate=data["pending"]["candidates_to_evaluate"],
            gaps_to_fill=data["pending"]["gaps_to_fill"],
            coverage_score=data["metrics"]["coverage_score"],
            consistency_score=data["metrics"]["consistency_score"],
            recent_acceptance_rate=data["metrics"]["recent_acceptance_rate"],
            total_proposed=data["history"]["total_proposed"],
            total_accepted=data["history"]["total_accepted"],
            total_rejected=data["history"]["total_rejected"],
        )
    
    def _serialize_iteration_state(self, state: IterationState) -> dict:
        """Serialize iteration state to YAML format."""
        return {
            "current_iteration": state.current_iteration,
            "phase": state.phase.value,
            "cycle_in_phase": state.cycle_in_phase,
            "last_updated": state.last_updated.isoformat() + "Z" if state.last_updated else None,
            "current_strategy": {
                "proposer_mode": state.proposer_mode,
                "proposer_temperature": state.proposer_temperature,
                "critic_strictness": state.critic_strictness,
                "domains_priority": [d.value for d in state.domains_priority],
            },
            "pending": {
                "candidates_to_evaluate": state.candidates_to_evaluate,
                "candidates_to_revise": [],
                "conflicts_to_resolve": [],
                "gaps_to_fill": state.gaps_to_fill,
            },
            "metrics": {
                "recent_acceptance_rate": state.recent_acceptance_rate,
                "coverage_score": state.coverage_score,
                "consistency_score": state.consistency_score,
            },
            "triggers": {
                "meta_reflection_due": state.current_iteration > 0 and state.current_iteration % 5 == 0,
                "iterations_since_meta": state.current_iteration % 5,
                "iterations_since_primitive": 0,  # Update based on actual data
            },
            "history": {
                "total_proposed": state.total_proposed,
                "total_accepted": state.total_accepted,
                "total_rejected": state.total_rejected,
            },
        }
```

---

## 4. Phase 3: Agent Roles

### 4.1 Base Agent

**`src/alphabetum/agents/base.py`**:

```python
"""Base agent class for all roles."""

from abc import ABC, abstractmethod
from typing import Any
import anthropic
import openai

from ..state.models import IterationState


class BaseAgent(ABC):
    """Base class for PROPOSER, CRITIC, REFINER, META-REASONER."""
    
    def __init__(self, config: dict):
        self.config = config
        self.provider = config["llm"]["provider"]
        self.model = config["llm"]["model"]
        
        if self.provider == "anthropic":
            self.client = anthropic.Anthropic()
        else:
            self.client = openai.OpenAI()
    
    @property
    @abstractmethod
    def role_name(self) -> str:
        """Name of this agent role."""
        pass
    
    @property
    @abstractmethod
    def temperature(self) -> float:
        """Temperature for this agent's LLM calls."""
        pass
    
    @abstractmethod
    def build_system_prompt(self, state: IterationState, **kwargs) -> str:
        """Build the system prompt for this role."""
        pass
    
    @abstractmethod
    def build_user_prompt(self, state: IterationState, **kwargs) -> str:
        """Build the user prompt for this role."""
        pass
    
    @abstractmethod
    def parse_response(self, response: str) -> Any:
        """Parse the LLM response into structured data."""
        pass
    
    def call_llm(self, system_prompt: str, user_prompt: str) -> str:
        """Make an LLM call and return the response."""
        if self.provider == "anthropic":
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.config["llm"]["max_tokens"],
                temperature=self.temperature,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )
            return response.content[0].text
        else:
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=self.config["llm"]["max_tokens"],
                temperature=self.temperature,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            return response.choices[0].message.content
    
    def execute(self, state: IterationState, **kwargs) -> tuple[Any, str]:
        """
        Execute this agent's role.
        
        Returns:
            Tuple of (parsed_result, raw_response)
        """
        system_prompt = self.build_system_prompt(state, **kwargs)
        user_prompt = self.build_user_prompt(state, **kwargs)
        
        raw_response = self.call_llm(system_prompt, user_prompt)
        parsed_result = self.parse_response(raw_response)
        
        return parsed_result, raw_response
```

### 4.2 PROPOSER Agent

**`src/alphabetum/agents/proposer.py`**:

```python
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

## Guidelines

1. Draw from multiple sources: Leibniz's writings, philosophical traditions, linguistics, mathematics, common sense
2. Think creatively but rigorously. Ask: "Could an alien understand human experience without this concept?"
3. Don't worry about being wrong—that's the CRITIC's job. Your job is to generate interesting candidates.

## Output Format

You MUST output valid YAML with exactly this structure:

```yaml
candidates:
  - label: "concept_name"
    domain: "one of: being, space, time, causation, mind, matter, quantity, quality, relation, ethics, emotion, action, knowledge, social, language"
    proposed_symbol: "suggested symbol"
    informal_definition: "what this concept means"
    ostensive_examples:
      - "example 1"
      - "example 2"
      - "example 3"
    negative_examples:
      - "what this is NOT"
    primitiveness_argument: "why this cannot be decomposed"
    decomposition_resistance: "what happens when you try to break it down"
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
        
        prompt = f"""
## Current State

- **Iteration**: {state.current_iteration}
- **Alphabet size**: {state.total_accepted} primitives
- **Current strategy**: {state.proposer_mode}
- **Priority domains**: {", ".join(d.value for d in state.domains_priority)}

## Current Gaps (concepts we can't yet express)

{chr(10).join(f"- {g}" for g in gaps) if gaps else "- None identified yet"}

## Current Alphabet Summary

{alphabet_summary}

## Your Task

Using the **{state.proposer_mode}** strategy, generate **{n}** candidate primitives.

Focus especially on domains: {", ".join(d.value for d in state.domains_priority[:3])}

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
            yaml_content = response.split("```")[1].split("```")[0]
        
        data = yaml.safe_load(yaml_content)
        
        candidates = []
        for i, c in enumerate(data.get("candidates", [])):
            candidate = Candidate(
                id=f"CAND_{i:03d}",  # Will be updated with iteration
                label=c["label"],
                domain=Domain(c["domain"]),
                proposed_symbol=c.get("proposed_symbol", "?"),
                informal_definition=c["informal_definition"],
                ostensive_examples=c.get("ostensive_examples", []),
                negative_examples=c.get("negative_examples", []),
                primitiveness_argument=c["primitiveness_argument"],
                decomposition_resistance=c["decomposition_resistance"],
                relevance_to_gaps=c.get("relevance_to_gaps", ""),
                confidence=c.get("confidence", 0.5),
            )
            candidates.append(candidate)
        
        return candidates
```

### 4.3 CRITIC Agent

**`src/alphabetum/agents/critic.py`**:

```python
"""CRITIC agent: evaluates candidate primitives."""

import yaml
from typing import Any

from .base import BaseAgent
from ..state.models import IterationState, Candidate, Evaluation, AttackResult, Verdict


CRITIC_SYSTEM_PROMPT = """
# ROLE: CRITIC

You are the CRITIC in Project Alphabetum. Your mission: rigorously test whether proposed concepts are truly primitive.

## Your Mindset

Be adversarial but fair. Your job is to find weaknesses. Apply every attack with genuine effort to falsify the claim of primitiveness.

## Attack Protocol

For each candidate, apply these attacks:

1. **DECOMPOSITION**: Try to break into simpler parts (analytic, synthetic, functional)
2. **CIRCULARITY**: Check if definition relies on itself or undefined concepts
3. **REDUNDANCY**: Can this be expressed using existing primitives?
4. **EDGE CASES**: Find contexts where meaning shifts or fails
5. **CULTURAL VARIANCE**: Is this truly universal?
6. **PARSIMONY**: Do we really need this primitive?

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
  key_insight: "something learned"
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
Output your evaluation as valid YAML.
"""
        return prompt
    
    def parse_response(self, response: str) -> Evaluation:
        """Parse YAML response into Evaluation object."""
        yaml_content = response
        if "```yaml" in response:
            yaml_content = response.split("```yaml")[1].split("```")[0]
        elif "```" in response:
            yaml_content = response.split("```")[1].split("```")[0]
        
        data = yaml.safe_load(yaml_content)
        e = data["evaluation"]
        
        decomposition_attacks = []
        for attempt in e.get("decomposition", {}).get("attempts", []):
            decomposition_attacks.append(AttackResult(
                approach=attempt["approach"],
                attempt=attempt["attempt"],
                result=attempt["result"],
                survived=attempt.get("survived", True),
            ))
        
        return Evaluation(
            candidate_id=e["candidate_id"],
            decomposition_attacks=decomposition_attacks,
            decomposition_survived=e.get("decomposition", {}).get("survived", True),
            circularity_survived=e.get("circularity", {}).get("survived", True),
            circularity_notes=e.get("circularity", {}).get("notes", ""),
            redundancy_can_be_expressed=e.get("redundancy", {}).get("can_be_expressed", False),
            redundancy_using=e.get("redundancy", {}).get("using_primitives"),
            edge_cases_severity=e.get("edge_cases", {}).get("overall_severity", "low"),
            cultural_assessment=e.get("cultural_variance", {}).get("assessment", "universal"),
            parsimony_necessary=e.get("parsimony", {}).get("necessary", True),
            verdict=Verdict(e["verdict"]),
            confidence=e.get("confidence", 0.5),
            reasoning_summary=e.get("reasoning_summary", ""),
            key_insight=e.get("key_insight"),
        )
```

### 4.4 Additional Agents

Create similar files for:
- `src/alphabetum/agents/refiner.py` - Integrates accepted primitives
- `src/alphabetum/agents/meta_reasoner.py` - Reflects on progress

(See the full prompt templates in `AGENT_LOOP.md`)

---

## 5. Phase 4: The Loop Engine

### 5.1 Main Loop

**`src/alphabetum/loop/engine.py`**:

```python
"""The main loop engine for ALPHABETUM."""

from pathlib import Path
from datetime import datetime
from typing import Optional

from ..state.manager import StateManager
from ..state.models import (
    IterationState, Phase, Candidate, Evaluation, 
    PrimitiveIndexEntry, PrimitiveDetailed, PrimitiveStatus, Verdict
)
from ..agents.proposer import ProposerAgent
from ..agents.critic import CriticAgent
from ..logging.archivist import Archivist


class LoopEngine:
    """Orchestrates the ALPHABETUM iteration loop."""
    
    def __init__(self, config: dict, base_path: Path):
        self.config = config
        self.base_path = base_path
        self.state_manager = StateManager(base_path)
        self.archivist = Archivist(base_path)
        
        # Initialize agents
        self.proposer = ProposerAgent(config)
        self.critic = CriticAgent(config)
        # self.refiner = RefinerAgent(config)
        # self.meta_reasoner = MetaReasonerAgent(config)
    
    def run(self, max_iterations: Optional[int] = None) -> None:
        """Run the main loop until stopping condition."""
        if max_iterations is None:
            max_iterations = self.config["stopping"]["max_iterations"]
        
        state = self.state_manager.load_iteration_state()
        
        while state.current_iteration < max_iterations:
            # Check stopping conditions
            should_stop, reason = self.check_stopping_conditions(state)
            if should_stop:
                self.archivist.log_termination(state, reason)
                self.generate_final_report(state, reason)
                break
            
            # Execute current phase
            state = self.execute_phase(state)
            
            # Check for phase transitions
            state = self.check_phase_transition(state)
            
            # Save state
            self.state_manager.save_iteration_state(state)
            
            # Increment iteration if phase cycle complete
            if state.phase == Phase.EXPANSION and state.cycle_in_phase == 0:
                state.current_iteration += 1
    
    def execute_phase(self, state: IterationState) -> IterationState:
        """Execute the current phase."""
        if state.phase == Phase.EXPANSION:
            return self.execute_expansion(state)
        elif state.phase == Phase.CONSOLIDATION:
            return self.execute_consolidation(state)
        elif state.phase == Phase.COMPOSITION:
            return self.execute_composition(state)
        elif state.phase == Phase.META_REFLECTION:
            return self.execute_meta_reflection(state)
        
        return state
    
    def execute_expansion(self, state: IterationState) -> IterationState:
        """Execute an EXPANSION cycle."""
        iteration = state.current_iteration
        
        # 1. PROPOSER generates candidates
        alphabet_summary = self.get_alphabet_summary()
        gaps = state.gaps_to_fill
        
        candidates, proposer_raw = self.proposer.execute(
            state,
            n=self.config["iteration"]["candidates_per_cycle"],
            alphabet_summary=alphabet_summary,
            gaps=gaps,
        )
        
        # Update candidate IDs with iteration
        for i, c in enumerate(candidates):
            c.id = f"CAND_{iteration:03d}_{i:03d}"
        
        # Log PROPOSER output
        self.archivist.log_proposer(iteration, candidates, proposer_raw)
        state.total_proposed += len(candidates)
        
        # 2. CRITIC evaluates each candidate
        evaluations = []
        for candidate in candidates:
            evaluation, critic_raw = self.critic.execute(
                state,
                candidate=candidate,
                alphabet_summary=alphabet_summary,
            )
            evaluation.candidate_id = candidate.id
            evaluations.append((candidate, evaluation, critic_raw))
        
        # Log CRITIC output
        self.archivist.log_critic(iteration, evaluations)
        
        # 3. Process verdicts
        for candidate, evaluation, _ in evaluations:
            if evaluation.verdict == Verdict.ACCEPT:
                self.integrate_primitive(candidate, evaluation, state)
                state.total_accepted += 1
            elif evaluation.verdict == Verdict.REJECT:
                self.archive_rejection(candidate, evaluation)
                state.total_rejected += 1
            elif evaluation.verdict == Verdict.REFINE:
                state.candidates_to_evaluate.append(candidate.id)
        
        # Update cycle counter
        state.cycle_in_phase += 1
        
        return state
    
    def integrate_primitive(
        self, 
        candidate: Candidate, 
        evaluation: Evaluation,
        state: IterationState
    ) -> None:
        """Integrate an accepted candidate into the alphabet."""
        # Get next ID and prime
        primitives = self.state_manager.load_alphabet_index()
        next_num = len(primitives) + 1
        primitive_id = f"PRM_{next_num:04d}"
        prime = self.state_manager.get_next_prime()
        
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
            definition={
                "informal": candidate.informal_definition,
                "formal": None,
                "ostensive": candidate.ostensive_examples,
                "negative": candidate.negative_examples,
            },
            domain_primary=candidate.domain,
            proposed_iteration=state.current_iteration,
            accepted_iteration=state.current_iteration,
            prime_number=prime,
            confidence=evaluation.confidence,
        )
        
        # Save
        primitives.append(index_entry)
        self.state_manager.save_alphabet_index(primitives, state.current_iteration)
        self.state_manager.save_primitive_detailed(detailed)
        
        # Log integration
        self.archivist.log_integration(state.current_iteration, primitive_id, candidate.label)
    
    def archive_rejection(self, candidate: Candidate, evaluation: Evaluation) -> None:
        """Archive a rejected candidate."""
        self.archivist.log_rejection(candidate, evaluation)
    
    def check_phase_transition(self, state: IterationState) -> IterationState:
        """Check if we should transition to next phase."""
        cycles = {
            Phase.EXPANSION: self.config["iteration"]["expansion_cycles"],
            Phase.CONSOLIDATION: self.config["iteration"]["consolidation_cycles"],
            Phase.COMPOSITION: self.config["iteration"]["composition_cycles"],
            Phase.META_REFLECTION: 1,
        }
        
        if state.cycle_in_phase >= cycles[state.phase]:
            state.cycle_in_phase = 0
            
            if state.phase == Phase.EXPANSION:
                state.phase = Phase.CONSOLIDATION
            elif state.phase == Phase.CONSOLIDATION:
                state.phase = Phase.COMPOSITION
            elif state.phase == Phase.COMPOSITION:
                # Check if meta-reflection is due
                if state.current_iteration % self.config["iteration"]["meta_reflection_interval"] == 0:
                    state.phase = Phase.META_REFLECTION
                else:
                    state.phase = Phase.EXPANSION
            elif state.phase == Phase.META_REFLECTION:
                state.phase = Phase.EXPANSION
        
        return state
    
    def check_stopping_conditions(self, state: IterationState) -> tuple[bool, str]:
        """Check if any stopping condition is met."""
        config = self.config["stopping"]
        
        # Coverage threshold
        if state.coverage_score >= config["coverage_threshold"]:
            return True, "COVERAGE_ACHIEVED"
        
        # Max iterations
        if state.current_iteration >= config["max_iterations"]:
            return True, "MAX_ITERATIONS"
        
        # Diminishing returns
        # (Would need to track recent additions)
        
        return False, ""
    
    def get_alphabet_summary(self) -> str:
        """Get a summary of the current alphabet for context."""
        primitives = self.state_manager.load_alphabet_index()
        if not primitives:
            return "No primitives in alphabet yet."
        
        lines = ["Current primitives:"]
        for p in primitives[-20:]:  # Last 20 for context
            lines.append(f"- {p.id} ({p.label}): {p.domain.value}")
        
        if len(primitives) > 20:
            lines.insert(1, f"... ({len(primitives) - 20} earlier primitives)")
        
        return "\n".join(lines)
    
    def execute_consolidation(self, state: IterationState) -> IterationState:
        """Execute a CONSOLIDATION cycle."""
        # TODO: Implement consistency checks
        state.cycle_in_phase += 1
        return state
    
    def execute_composition(self, state: IterationState) -> IterationState:
        """Execute a COMPOSITION cycle."""
        # TODO: Implement coverage testing
        state.cycle_in_phase += 1
        return state
    
    def execute_meta_reflection(self, state: IterationState) -> IterationState:
        """Execute META-REFLECTION."""
        # TODO: Implement meta-reasoning
        state.cycle_in_phase += 1
        return state
    
    def generate_final_report(self, state: IterationState, reason: str) -> None:
        """Generate the final report."""
        self.archivist.generate_final_report(state, reason)
```

---

## 6. Phase 5: Logging & Archiving

### 6.1 Archivist

**`src/alphabetum/logging/archivist.py`**:

```python
"""The ARCHIVIST: logs everything."""

from pathlib import Path
from datetime import datetime
import yaml

from ..state.models import (
    Candidate, Evaluation, IterationState
)


class Archivist:
    """Comprehensive logging for ALPHABETUM."""
    
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.reasoning_path = base_path / "reasoning"
    
    def _get_log_dir(self, iteration: int) -> Path:
        """Get or create log directory for iteration."""
        log_dir = self.reasoning_path / "logs" / f"iteration_{iteration:03d}"
        log_dir.mkdir(parents=True, exist_ok=True)
        return log_dir
    
    def log_proposer(
        self, 
        iteration: int, 
        candidates: list[Candidate],
        raw_response: str
    ) -> None:
        """Log PROPOSER output."""
        log_dir = self._get_log_dir(iteration)
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        # Structured log
        structured = {
            "proposer_output": {
                "timestamp": timestamp,
                "iteration": iteration,
                "candidates_count": len(candidates),
                "candidates": [c.model_dump() for c in candidates],
            }
        }
        
        with open(log_dir / "proposer.yaml", "w") as f:
            yaml.dump(structured, f, default_flow_style=False)
        
        # Narrative log
        narrative = f"""# Proposer Log: Iteration {iteration}

*Generated at: {timestamp}*

## Candidates Proposed

"""
        for c in candidates:
            narrative += f"""
### {c.label} ({c.domain.value})

**Definition:** {c.informal_definition}

**Primitiveness Argument:** {c.primitiveness_argument}

**Confidence:** {c.confidence}

---
"""
        
        with open(log_dir / "proposer.md", "w") as f:
            f.write(narrative)
        
        # Raw response (for debugging)
        with open(log_dir / "proposer_raw.txt", "w") as f:
            f.write(raw_response)
    
    def log_critic(
        self,
        iteration: int,
        evaluations: list[tuple[Candidate, Evaluation, str]]
    ) -> None:
        """Log CRITIC evaluations."""
        log_dir = self._get_log_dir(iteration)
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        # Structured log
        structured = {
            "critic_output": {
                "timestamp": timestamp,
                "iteration": iteration,
                "evaluations": [
                    {
                        "candidate_id": e.candidate_id,
                        "verdict": e.verdict.value,
                        "confidence": e.confidence,
                        "reasoning_summary": e.reasoning_summary,
                    }
                    for _, e, _ in evaluations
                ]
            }
        }
        
        with open(log_dir / "critic.yaml", "w") as f:
            yaml.dump(structured, f, default_flow_style=False)
        
        # Narrative log
        narrative = f"""# Critic Log: Iteration {iteration}

*Generated at: {timestamp}*

## Evaluations

"""
        for c, e, _ in evaluations:
            narrative += f"""
### {c.label} → **{e.verdict.value}**

**Confidence:** {e.confidence}

**Reasoning:** {e.reasoning_summary}

**Key Insight:** {e.key_insight or "None recorded"}

---
"""
        
        with open(log_dir / "critic.md", "w") as f:
            f.write(narrative)
    
    def log_integration(self, iteration: int, primitive_id: str, label: str) -> None:
        """Log a primitive integration."""
        log_dir = self._get_log_dir(iteration)
        
        integration_log = log_dir / "integrations.yaml"
        
        # Append to existing or create new
        integrations = {"integrations": []}
        if integration_log.exists():
            with open(integration_log) as f:
                integrations = yaml.safe_load(f) or {"integrations": []}
        
        integrations["integrations"].append({
            "primitive_id": primitive_id,
            "label": label,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        })
        
        with open(integration_log, "w") as f:
            yaml.dump(integrations, f, default_flow_style=False)
    
    def log_rejection(self, candidate: Candidate, evaluation: Evaluation) -> None:
        """Log a rejected candidate."""
        rejected_file = self.reasoning_path / "rejected" / "rejected_candidates.yaml"
        rejected_file.parent.mkdir(parents=True, exist_ok=True)
        
        rejections = {"rejections": []}
        if rejected_file.exists():
            with open(rejected_file) as f:
                rejections = yaml.safe_load(f) or {"rejections": []}
        
        rejections["rejections"].append({
            "candidate_id": candidate.id,
            "label": candidate.label,
            "domain": candidate.domain.value,
            "verdict": evaluation.verdict.value,
            "reason": evaluation.reasoning_summary,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        })
        
        with open(rejected_file, "w") as f:
            yaml.dump(rejections, f, default_flow_style=False)
    
    def log_termination(self, state: IterationState, reason: str) -> None:
        """Log system termination."""
        log_file = self.reasoning_path / "termination.yaml"
        
        data = {
            "termination": {
                "reason": reason,
                "final_iteration": state.current_iteration,
                "final_metrics": {
                    "total_primitives": state.total_accepted,
                    "coverage_score": state.coverage_score,
                    "total_proposed": state.total_proposed,
                    "total_rejected": state.total_rejected,
                },
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }
        }
        
        with open(log_file, "w") as f:
            yaml.dump(data, f, default_flow_style=False)
    
    def generate_final_report(self, state: IterationState, reason: str) -> None:
        """Generate FINAL_REPORT.md"""
        report_path = self.base_path / "FINAL_REPORT.md"
        
        report = f"""# ALPHABETUM: Final Report

## Termination

**Reason:** {reason}
**Final Iteration:** {state.current_iteration}
**Timestamp:** {datetime.utcnow().isoformat()}Z

## Statistics

- **Total Primitives:** {state.total_accepted}
- **Total Proposed:** {state.total_proposed}
- **Total Rejected:** {state.total_rejected}
- **Acceptance Rate:** {state.total_accepted / max(state.total_proposed, 1):.1%}
- **Coverage Score:** {state.coverage_score:.1%}

## The Alphabet

(See `alphabet/primitives/index.yaml` for complete list)

## Key Insights

(To be filled from meta_reflections)

## Recommendations for Future Work

(To be filled)

---

*Calculemus!*
"""
        
        with open(report_path, "w") as f:
            f.write(report)
```

---

## 7-10: Remaining Phases

The remaining phases follow similar patterns:

- **Phase 6**: Implement consistency checkers in `src/alphabetum/validation/`
- **Phase 7**: Implement calculus in `src/alphabetum/calculus/`
- **Phase 8**: Implement CLI tools in `tools/`
- **Phase 9**: Write tests in `tests/`
- **Phase 10**: Create `main.py` entry point

### 7.1 Main Entry Point

**`main.py`**:

```python
"""Main entry point for ALPHABETUM."""

from pathlib import Path
import yaml

from src.alphabetum.loop.engine import LoopEngine


def main():
    """Run ALPHABETUM."""
    # Load config
    with open("config.yaml") as f:
        config = yaml.safe_load(f)
    
    # Initialize engine
    base_path = Path(".")
    engine = LoopEngine(config, base_path)
    
    # Run the loop
    print("Starting ALPHABETUM...")
    print("=" * 60)
    engine.run()
    print("=" * 60)
    print("ALPHABETUM complete. See FINAL_REPORT.md")


if __name__ == "__main__":
    main()
```

---

## Summary Checklist

- [ ] Phase 1: Directory structure created
- [ ] Phase 1: Config files created
- [ ] Phase 1: Initial state files created
- [ ] Phase 2: State models implemented
- [ ] Phase 2: State manager implemented
- [ ] Phase 3: Base agent implemented
- [ ] Phase 3: PROPOSER agent implemented
- [ ] Phase 3: CRITIC agent implemented
- [ ] Phase 3: REFINER agent implemented
- [ ] Phase 3: META-REASONER agent implemented
- [ ] Phase 4: Loop engine implemented
- [ ] Phase 5: Archivist implemented
- [ ] Phase 6: Validation suite implemented
- [ ] Phase 7: Calculus implementations
- [ ] Phase 8: CLI tools
- [ ] Phase 9: Tests passing
- [ ] Phase 10: System running end-to-end

**The implementation is complete when the system can:**

1. Start from scratch and initialize seed primitives
2. Run through EXPANSION → CONSOLIDATION → COMPOSITION → META_REFLECTION cycles
3. Generate and evaluate candidate primitives
4. Integrate accepted primitives into the alphabet
5. Log everything to the filesystem
6. Stop when stopping conditions are met
7. Generate a final report
