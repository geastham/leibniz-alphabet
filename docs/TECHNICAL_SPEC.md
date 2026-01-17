# Technical Specification

## ALPHABETUM: System Architecture & Implementation Details

**Version:** 1.0.0  
**Last Updated:** 2024-03-15  
**Status:** Canonical Reference

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Agent Architecture](#2-agent-architecture)
3. [State Management](#3-state-management)
4. [LLM Configuration](#4-llm-configuration)
5. [File System Layout](#5-file-system-layout)
6. [Execution Environment](#6-execution-environment)
7. [Error Handling](#7-error-handling)
8. [Performance Considerations](#8-performance-considerations)

---

## 1. System Overview

### 1.1 Core Principle

ALPHABETUM is a **stateful, iterative, multi-role reasoning system** that maintains:

1. **Persistent State**: The alphabet, relationships, and all reasoning are persisted to the filesystem
2. **Iterative Refinement**: Progress happens through discrete iterations, each logged completely
3. **Multi-Role Processing**: Different "cognitive modes" (PROPOSER, CRITIC, REFINER, META-REASONER) operate on shared state
4. **Complete Transparency**: Every decision, consideration, and conclusion is captured

### 1.2 Design Philosophy

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        DESIGN PRINCIPLES                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  1. STATE IS TRUTH                                                      │
│     The filesystem is the single source of truth.                       │
│     The agent reads state, reasons, writes updated state.              │
│     No in-memory-only reasoning.                                        │
│                                                                         │
│  2. REASONING IS ARTIFACT                                               │
│     The logs are as important as the alphabet itself.                   │
│     Every thought is captured. Nothing is ephemeral.                    │
│                                                                         │
│  3. ITERATION IS PROGRESS                                               │
│     Each iteration is atomic and complete.                              │
│     The system can stop and resume at any iteration boundary.          │
│                                                                         │
│  4. ROLES ARE PERSPECTIVES                                              │
│     Same underlying model, different prompts and temperatures.          │
│     Each role sees the same state but reasons differently.             │
│                                                                         │
│  5. FAILURE IS DATA                                                     │
│     Rejected candidates are logged as thoroughly as accepted ones.     │
│     Dead ends are documented for future reference.                      │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 1.3 High-Level Data Flow

```
                                    ┌─────────────────┐
                                    │   FILESYSTEM    │
                                    │                 │
                                    │ alphabet/       │
                                    │ reasoning/      │
                                    │ calculus/       │
                                    │ validation/     │
                                    └────────┬────────┘
                                             │
                    ┌────────────────────────┼────────────────────────┐
                    │                        │                        │
                    ▼                        ▼                        ▼
              ┌──────────┐            ┌──────────┐            ┌──────────┐
              │   READ   │            │  REASON  │            │  WRITE   │
              │   STATE  │───────────▶│          │───────────▶│  STATE   │
              │          │            │   (LLM)  │            │          │
              └──────────┘            └──────────┘            └──────────┘
                    │                        │                        │
                    └────────────────────────┴────────────────────────┘
                                             │
                                             ▼
                                    ┌─────────────────┐
                                    │  NEXT ITERATION │
                                    └─────────────────┘
```

---

## 2. Agent Architecture

### 2.1 Role Specifications

#### 2.1.1 PROPOSER

**Purpose**: Generate candidate primitive concepts

**Cognitive Mode**: Creative, exploratory, drawing connections

**Input Context**:
- Current alphabet state (summary)
- Recent gaps identified by validation
- Current strategy emphasis (from META-REASONER)
- Domains not yet well-covered

**Output Structure**:
```yaml
proposer_output:
  candidates:
    - label: string
      informal_definition: string
      domain: string
      proposed_symbol: string
      ostensive_examples: list[string]
      negative_examples: list[string]  # What this is NOT
      primitiveness_argument: string
      decomposition_resistance: string  # Why can't this be broken down?
      sources:
        - philosophical_tradition: string
          specific_reference: string
```

**Generation Strategies** (cycled through):

| Strategy | Description | When to Use |
|----------|-------------|-------------|
| DOMAIN_SWEEP | Systematically survey a domain | Early iterations, building coverage |
| DECOMPOSITION_MINING | Take complex concepts, decompose until stuck | Finding hidden primitives |
| CROSS_REFERENCE | Find concepts appearing in multiple decompositions | Mid-to-late iterations |
| LINGUISTIC_ANALYSIS | Identify concepts resisting paraphrase | Validation of candidates |
| THOUGHT_EXPERIMENT | What would aliens need to understand humans? | Creative exploration |
| GAP_FILLING | Target specific expressiveness gaps | After validation reveals holes |

#### 2.1.2 CRITIC

**Purpose**: Attempt to falsify primitiveness claims

**Cognitive Mode**: Adversarial, rigorous, skeptical

**Input Context**:
- Candidate(s) to evaluate
- Current alphabet (for redundancy checking)
- Previous rejection patterns (to avoid repetition)

**Attack Protocol**:

```
FOR each candidate:
    
    ATTACK 1: DECOMPOSITION
    ├── Attempt analytic decomposition (definition-based)
    ├── Attempt synthetic decomposition (part-whole)
    ├── Attempt functional decomposition (role-based)
    └── Record: attempts made, results, confidence
    
    ATTACK 2: CIRCULARITY
    ├── Trace all concepts used in definition
    ├── Check if any trace back to candidate
    ├── Check if definition uses concepts not yet in alphabet
    └── Record: dependency graph, circular paths found
    
    ATTACK 3: REDUNDANCY
    ├── Attempt to express candidate using existing primitives
    ├── If expressible: candidate is not primitive
    └── Record: expression attempted, success/failure
    
    ATTACK 4: EDGE CASES
    ├── Find contexts where meaning shifts
    ├── Find contexts where concept doesn't apply
    ├── Test across domains
    └── Record: edge cases found, implications
    
    ATTACK 5: CULTURAL VARIANCE
    ├── Is this truly universal?
    ├── Evidence from cross-linguistic research
    ├── Evidence from developmental psychology
    └── Record: variance found, universality assessment
    
    ATTACK 6: PARSIMONY
    ├── Do we really need this?
    ├── What expressiveness do we lose without it?
    ├── Is there a more parsimonious alternative?
    └── Record: necessity assessment
    
    SYNTHESIZE verdict:
    ├── ACCEPT: Survived all attacks
    ├── REJECT: Failed critical attack (specify which)
    └── REFINE: Core intuition valid, formulation problematic
```

**Output Structure**:
```yaml
critic_output:
  candidate_id: string
  
  attacks:
    decomposition:
      attempts: list[DecompositionAttempt]
      survived: boolean
      notes: string
      
    circularity:
      dependency_trace: list[string]
      circular_paths: list[list[string]]
      survived: boolean
      notes: string
      
    redundancy:
      expression_attempts: list[ExpressionAttempt]
      can_be_expressed: boolean
      using_primitives: list[string] | null
      notes: string
      
    edge_cases:
      cases_found: list[EdgeCase]
      severity: low | medium | high
      notes: string
      
    cultural_variance:
      evidence_for_universality: list[string]
      evidence_against: list[string]
      assessment: universal | near_universal | culturally_bound
      notes: string
      
    parsimony:
      expressiveness_value: high | medium | low
      alternatives_considered: list[string]
      necessary: boolean
      notes: string
  
  verdict: ACCEPT | REJECT | REFINE
  confidence: float  # 0-1
  
  reasoning_summary: string
  key_insight: string | null  # Something learned regardless of verdict
```

#### 2.1.3 REFINER

**Purpose**: Integrate accepted primitives, maintain consistency

**Cognitive Mode**: Systematic, integrative, careful

**Responsibilities**:

1. **Add accepted primitives to alphabet**
   - Assign unique ID (PRM_XXXX)
   - Assign prime number (for Leibniz composition)
   - Create detailed entry file

2. **Update relationship graphs**
   - Contrast relationships (mutually exclusive)
   - Presupposition relationships (dependencies)
   - Composition affinities (often combined)

3. **Check for emergent conflicts**
   - Does new primitive conflict with existing?
   - Does it require revising existing primitives?
   - Does it reveal new redundancies?

4. **Maintain taxonomies**
   - Update domain categorization
   - Update abstraction level categorization
   - Update frequency-of-use metrics

**Output Structure**:
```yaml
refiner_output:
  action: INTEGRATE | REVISE | MERGE | SPLIT
  
  integration:
    primitive_id: string
    assigned_prime: int
    relationships_added:
      - type: contrasts_with | presupposes | composes_with
        target: string
        justification: string
    
  revisions:  # If existing primitives were modified
    - primitive_id: string
      field_changed: string
      old_value: any
      new_value: any
      reason: string
      
  conflicts_detected: list[Conflict]
  conflicts_resolved: list[Resolution]
  
  alphabet_state:
    total_primitives: int
    by_domain: dict[string, int]
    consistency_score: float
```

#### 2.1.4 META-REASONER

**Purpose**: Reflect on the process, adjust strategy

**Cognitive Mode**: Reflective, strategic, philosophical

**Trigger Conditions**:
- After every N iterations (default: 5)
- When acceptance rate drops below 20%
- When circularity detected in alphabet itself
- When coverage tests reveal major gaps
- When requested by previous meta-reflection

**Reflection Framework**:

```
META-REFLECTION PROTOCOL:

1. PROGRESS ASSESSMENT
   ├── Primitives added this period
   ├── Rejection rate and patterns
   ├── Coverage improvement
   └── Trend analysis

2. STRATEGY EVALUATION
   ├── Is current PROPOSER strategy effective?
   ├── Is CRITIC too strict or too lenient?
   ├── Are we biased toward certain domains?
   └── What patterns do rejections show?

3. PHILOSOPHICAL AUDIT
   ├── What assumptions are we making?
   ├── Which philosophical traditions are we leaning toward?
   ├── Are we being true to Leibniz's vision?
   └── What would critics of this project say?

4. COURSE CORRECTION
   ├── Recommended strategy adjustments
   ├── Domains to prioritize
   ├── Primitiveness criterion calibration
   └── New approaches to try

5. DOCUMENTATION
   ├── Key insights worth preserving
   ├── Paradoxes encountered
   ├── Open questions
   └── Predictions for next period
```

**Output Structure**:
```yaml
meta_reflection:
  iteration_range: [start, end]
  timestamp: datetime
  
  progress:
    primitives_added: int
    primitives_rejected: int
    acceptance_rate: float
    coverage_before: float
    coverage_after: float
    
  patterns_observed:
    - pattern: string
      frequency: int
      implications: string
      
  strategy_assessment:
    proposer_effectiveness: 1-5
    critic_calibration: too_strict | balanced | too_lenient
    domain_coverage_balance: string
    
  philosophical_observations:
    assumptions_identified:
      - assumption: string
        problematic: boolean
        mitigation: string | null
    tradition_bias: string
    leibniz_alignment: 1-5
    
  course_corrections:
    strategy_adjustments:
      - component: PROPOSER | CRITIC | REFINER
        adjustment: string
        rationale: string
    domain_priorities: list[string]
    criterion_calibration: string
    
  decision: CONTINUE | PIVOT | CONCLUDE
  
  next_period_predictions:
    - prediction: string
      confidence: float
      
  insights_for_archive:
    - insight: string
      category: philosophical | methodological | substantive
```

#### 2.1.5 ARCHIVIST

**Purpose**: Maintain comprehensive documentation

**Note**: The ARCHIVIST is not a separate LLM call but rather a **structured logging system** that the other agents write through.

**Logging Categories**:

| Category | Location | Format | Purpose |
|----------|----------|--------|---------|
| Deliberation Logs | `reasoning/logs/iteration_XXX/` | YAML + MD | Capture all reasoning |
| Decision Records | `reasoning/decisions/` | Markdown | Explain key decisions |
| Paradox Reports | `reasoning/paradoxes/` | Markdown | Document puzzles |
| Meta Reflections | `reasoning/meta_reflections/` | YAML + MD | Strategy evolution |
| Rejected Concepts | `reasoning/rejected/` | YAML | Why things didn't work |
| Version Snapshots | `alphabet/versions/` | YAML | Alphabet at each version |

---

## 3. State Management

### 3.1 State Files

The system maintains several critical state files that persist across iterations:

#### 3.1.1 Alphabet State (`alphabet/primitives/index.yaml`)

```yaml
alphabet_state:
  version: "0.X.Y"
  last_updated: datetime
  iteration: int
  
  statistics:
    total_primitives: int
    by_domain:
      space: int
      time: int
      causation: int
      # ...
    by_status:
      stable: int      # Unchanged for N iterations
      recent: int      # Added in last M iterations
      contested: int   # Under reconsideration
      
  primitives:
    - id: "PRM_0001"
      label: "existence"
      prime: 2
      domain: "being"
      status: stable
      added_iteration: 1
      last_reviewed: 42
      confidence: 0.95
```

#### 3.1.2 Iteration State (`reasoning/iteration_state.yaml`)

```yaml
iteration_state:
  current_iteration: int
  phase: EXPANSION | CONSOLIDATION | COMPOSITION | META_REFLECTION
  cycle_in_phase: int
  
  current_strategy:
    proposer_mode: string
    proposer_temperature: float
    critic_strictness: float
    domains_priority: list[string]
    
  pending:
    candidates_to_evaluate: list[string]
    conflicts_to_resolve: list[string]
    gaps_to_fill: list[string]
    
  metrics:
    recent_acceptance_rate: float  # Last N candidates
    coverage_score: float
    consistency_score: float
    
  history:
    iterations_since_last_meta: int
    iterations_since_last_primitive: int
    total_proposed: int
    total_accepted: int
    total_rejected: int
```

#### 3.1.3 Relationship State (`alphabet/relationships/graph.yaml`)

```yaml
relationship_graph:
  last_updated: datetime
  
  contrasts:  # Mutually exclusive primitives
    - [PRM_0001, PRM_0002]
    - [PRM_0003, PRM_0004]
    
  presupposes:  # A presupposes B means A requires B
    - source: PRM_0010
      requires: [PRM_0001, PRM_0005]
      
  composes_well:  # Often combined
    - [PRM_0001, PRM_0003]
    - [PRM_0002, PRM_0005, PRM_0007]
```

### 3.2 State Transitions

```
                            ┌─────────────────────┐
                            │   READ FULL STATE   │
                            │                     │
                            │ • alphabet/         │
                            │ • iteration_state   │
                            │ • relationships     │
                            └──────────┬──────────┘
                                       │
                                       ▼
                            ┌─────────────────────┐
                            │  DETERMINE PHASE    │
                            │                     │
                            │ Based on iteration  │
                            │ state and metrics   │
                            └──────────┬──────────┘
                                       │
          ┌────────────────────────────┼────────────────────────────┐
          │                            │                            │
          ▼                            ▼                            ▼
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│   EXPANSION     │         │  CONSOLIDATION  │         │   COMPOSITION   │
│                 │         │                 │         │                 │
│ PROPOSER →      │         │ Review alphabet │         │ Test coverage   │
│ CRITIC →        │         │ Find conflicts  │         │ Identify gaps   │
│ REFINER         │         │ Merge redundant │         │ Refine calculus │
└────────┬────────┘         └────────┬────────┘         └────────┬────────┘
          │                            │                            │
          └────────────────────────────┼────────────────────────────┘
                                       │
                                       ▼
                            ┌─────────────────────┐
                            │  CHECK TRIGGERS     │
                            │                     │
                            │ • Meta reflection?  │
                            │ • Stopping cond?    │
                            │ • Phase complete?   │
                            └──────────┬──────────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    │                  │                  │
                    ▼                  ▼                  ▼
         ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
         │ META-REFLECTION │ │  WRITE STATE    │ │   TERMINATE     │
         │                 │ │                 │ │                 │
         │ Reflect &       │ │ Update all      │ │ Generate final  │
         │ adjust strategy │ │ state files     │ │ report          │
         └────────┬────────┘ └────────┬────────┘ └─────────────────┘
                  │                   │
                  └─────────┬─────────┘
                            │
                            ▼
                   ┌─────────────────┐
                   │ NEXT ITERATION  │
                   └─────────────────┘
```

### 3.3 Atomicity & Recovery

Each iteration must be atomic:

1. **Read Phase**: Load all necessary state into memory
2. **Compute Phase**: Execute reasoning (LLM calls)
3. **Write Phase**: Write all updated state
4. **Commit Phase**: Log completion

If interrupted:
- Check for incomplete iteration markers
- Roll back to last complete iteration
- Resume from that point

```yaml
# .iteration_lock file during processing
iteration_lock:
  iteration: 47
  started: "2024-03-15T14:32:07Z"
  phase: EXPANSION
  status: IN_PROGRESS
  checkpoint: after_critic  # Last completed step
```

---

## 4. LLM Configuration

### 4.1 Model Requirements

**Primary Model**: Claude 3 Opus, GPT-4, or equivalent

Required capabilities:
- Extended context window (>100k tokens preferred)
- Strong philosophical reasoning
- Consistent structured output
- Low hallucination rate

### 4.2 Temperature Settings

| Role | Temperature | Rationale |
|------|-------------|-----------|
| PROPOSER | 0.7 | Creative exploration, novel connections |
| CRITIC | 0.3 | Rigorous, consistent evaluation |
| REFINER | 0.5 | Balanced integration |
| META-REASONER | 0.5 | Reflective but grounded |

### 4.3 Context Management

The full alphabet + all reasoning would exceed context limits. Strategy:

```
CONTEXT COMPOSITION:

1. FIXED CONTEXT (~10k tokens)
   ├── System prompt for current role
   ├── Current iteration state summary
   └── Recent meta-reflection summary

2. ALPHABET CONTEXT (~20k tokens)
   ├── Full index.yaml (compact)
   ├── Detailed entries for:
   │   ├── Primitives relevant to current candidate
   │   ├── Recently added primitives (last 10)
   │   └── Primitives in same domain
   └── Relationship graph (relevant subgraph)

3. REASONING CONTEXT (~30k tokens)
   ├── Last 3-5 iteration logs (summarized)
   ├── Recent rejection patterns
   └── Current gaps/priorities

4. TASK CONTEXT (variable)
   ├── Specific candidates to evaluate
   └── Specific questions to answer
```

### 4.4 Prompt Templates

See [AGENT_LOOP.md](./AGENT_LOOP.md) for full prompt templates.

---

## 5. File System Layout

### 5.1 Directory Structure (Detailed)

```
leibniz-alphabet/
│
├── alphabet/
│   ├── primitives/
│   │   ├── index.yaml              # Master registry (compact)
│   │   │
│   │   ├── by_domain/              # Domain organization
│   │   │   ├── _domain_index.yaml  # Which primitives in each domain
│   │   │   ├── being.yaml          # All being-domain primitives
│   │   │   ├── space.yaml
│   │   │   ├── time.yaml
│   │   │   ├── causation.yaml
│   │   │   ├── mind.yaml
│   │   │   ├── matter.yaml
│   │   │   ├── quantity.yaml
│   │   │   ├── quality.yaml
│   │   │   └── relation.yaml
│   │   │
│   │   └── detailed/               # Full entries (one per primitive)
│   │       ├── PRM_0001_existence.yaml
│   │       ├── PRM_0002_identity.yaml
│   │       └── ...
│   │
│   ├── relationships/
│   │   ├── graph.yaml              # Full relationship graph
│   │   ├── contrasts.yaml          # Mutual exclusions
│   │   ├── presuppositions.yaml    # Dependencies
│   │   └── affinities.yaml         # Composition patterns
│   │
│   └── versions/                   # Snapshots
│       ├── v0.1.0/                 # First stable version
│       │   ├── index.yaml
│       │   ├── primitives/
│       │   └── CHANGELOG.md
│       └── ...
│
├── calculus/
│   ├── operators.yaml              # Composition operators
│   ├── rules.yaml                  # Inference/composition rules
│   │
│   ├── implementations/
│   │   ├── prime_composition.py    # Leibniz's original vision
│   │   ├── set_theoretic.py        # Set-based composition
│   │   ├── type_theoretic.py       # Type-based composition
│   │   └── vector_space.py         # Vector embedding approach
│   │
│   └── examples/
│       ├── basic_compositions.yaml
│       └── complex_derivations.yaml
│
├── reasoning/
│   ├── iteration_state.yaml        # Current iteration state
│   │
│   ├── logs/
│   │   └── iteration_XXX/          # Per-iteration logs
│   │       ├── summary.yaml        # Quick reference
│   │       ├── proposer.yaml       # PROPOSER output
│   │       ├── proposer.md         # PROPOSER reasoning (prose)
│   │       ├── critic.yaml         # CRITIC output
│   │       ├── critic.md           # CRITIC reasoning (prose)
│   │       ├── refiner.yaml        # REFINER output
│   │       ├── refiner.md          # REFINER reasoning (prose)
│   │       └── artifacts.yaml      # What changed this iteration
│   │
│   ├── decisions/                  # Key decision explanations
│   │   ├── _decision_index.yaml    # Index of all decisions
│   │   ├── DEC_0001_existence_is_primitive.md
│   │   └── ...
│   │
│   ├── paradoxes/                  # Problems encountered
│   │   ├── _paradox_index.yaml
│   │   ├── PAR_0001_circularity_of_being.md
│   │   └── ...
│   │
│   ├── rejected/                   # Rejected candidates
│   │   ├── _rejected_index.yaml
│   │   └── rejected_candidates.yaml  # All rejections with reasons
│   │
│   └── meta_reflections/           # Strategy evolution
│       ├── _reflection_index.yaml
│       ├── MR_0001_iteration_005.yaml
│       ├── MR_0001_iteration_005.md
│       └── ...
│
├── validation/
│   ├── benchmarks/
│   │   ├── test_concepts.yaml      # Concepts we should express
│   │   ├── results/
│   │   │   ├── coverage_report.yaml
│   │   │   └── coverage_by_iteration/
│   │   └── decompositions/         # How we decomposed test concepts
│   │
│   ├── comparisons/
│   │   ├── vs_wordnet.md
│   │   ├── vs_cyc.md
│   │   ├── vs_nsm_primes.md
│   │   └── vs_aristotle.md
│   │
│   └── consistency/
│       ├── circularity_check.yaml
│       ├── redundancy_check.yaml
│       └── report.yaml
│
├── sources/
│   ├── leibniz/                    # Leibniz texts
│   ├── philosophical/              # Other sources
│   └── modern_ontologies/          # Contemporary references
│
├── tools/
│   ├── composer.py
│   ├── decomposer.py
│   ├── validator.py
│   └── visualizer.py
│
└── docs/
    ├── TECHNICAL_SPEC.md           # This document
    ├── AGENT_LOOP.md
    ├── REASONING_PROTOCOL.md
    ├── DATA_SCHEMAS.md
    ├── IMPLEMENTATION_GUIDE.md
    ├── CALCULUS_SPEC.md
    └── VALIDATION_FRAMEWORK.md
```

### 5.2 File Naming Conventions

| Type | Pattern | Example |
|------|---------|---------|
| Primitive entries | `PRM_{XXXX}_{label}.yaml` | `PRM_0042_causation.yaml` |
| Decisions | `DEC_{XXXX}_{brief_desc}.md` | `DEC_0015_time_is_primitive.md` |
| Paradoxes | `PAR_{XXXX}_{brief_desc}.md` | `PAR_0003_self_reference.md` |
| Meta reflections | `MR_{XXXX}_iteration_{NNN}.yaml/.md` | `MR_0007_iteration_035.yaml` |
| Iteration logs | `iteration_{NNN}/` | `iteration_042/` |

---

## 6. Execution Environment

### 6.1 Dependencies

```python
# requirements.txt

# LLM interaction
anthropic>=0.25.0        # For Claude
openai>=1.12.0           # For GPT-4
langchain>=0.1.0         # Orchestration (optional)
langgraph>=0.0.26        # State graph (optional)

# Data handling
pyyaml>=6.0              # YAML parsing
pydantic>=2.6.0          # Data validation
networkx>=3.2            # Graph operations

# Utilities
rich>=13.7.0             # Terminal output
typer>=0.9.0             # CLI
python-dotenv>=1.0.0     # Environment variables

# Math (for prime composition)
sympy>=1.12              # Prime number operations

# Optional: visualization
matplotlib>=3.8.0
graphviz>=0.20
```

### 6.2 Configuration

```yaml
# config.yaml

llm:
  provider: anthropic  # or openai
  model: claude-3-opus-20240229
  max_tokens: 4096
  
temperatures:
  proposer: 0.7
  critic: 0.3
  refiner: 0.5
  meta_reasoner: 0.5
  
iteration:
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
  
validation:
  run_consistency_check: true
  run_coverage_check: true
  check_interval: 10
```

### 6.3 Entry Point

```python
# main.py

from alphabetum import AlphabetumAgent
from alphabetum.config import load_config

def main():
    config = load_config("config.yaml")
    agent = AlphabetumAgent(config)
    
    # Resume from last iteration or start fresh
    agent.run()

if __name__ == "__main__":
    main()
```

---

## 7. Error Handling

### 7.1 Error Categories

| Category | Handling | Example |
|----------|----------|---------|
| LLM Failure | Retry with exponential backoff | Rate limit, timeout |
| Parse Failure | Log raw output, attempt recovery | Malformed JSON/YAML |
| State Corruption | Rollback to last checkpoint | Invalid state file |
| Consistency Violation | Halt, require human review | Circular definition detected |
| Stopping Condition | Clean shutdown, generate report | Coverage met |

### 7.2 Recovery Protocol

```python
def recover_from_interruption():
    """
    1. Check for .iteration_lock file
    2. If exists and status == IN_PROGRESS:
       a. Read checkpoint field
       b. Load state from before checkpoint
       c. Resume from checkpoint
    3. If no lock file:
       a. Read iteration_state.yaml
       b. Resume from current_iteration
    """
    pass
```

### 7.3 Consistency Enforcement

Before writing any state change:

```python
def validate_state_change(old_state, new_state):
    """
    Checks:
    1. No primitive ID collisions
    2. No circular presuppositions
    3. No redundant primitives
    4. All references valid
    5. Iteration numbers monotonic
    """
    pass
```

---

## 8. Performance Considerations

### 8.1 Optimization Strategies

| Area | Strategy | Benefit |
|------|----------|---------|
| LLM Calls | Batch candidates for CRITIC | Fewer API calls |
| Context | Use summaries, not full texts | Stay within limits |
| File I/O | Cache frequently-read files | Reduce disk access |
| Validation | Run expensive checks less often | Faster iterations |

### 8.2 Scaling Considerations

For large alphabets (>100 primitives):

1. **Index structures**: Maintain inverted indices for relationship lookups
2. **Graph partitioning**: Divide relationship graph by domain
3. **Incremental validation**: Only re-validate affected portions
4. **Summary generation**: Auto-generate summaries for context

### 8.3 Resource Estimates

| Iteration Count | Primitives | LLM Tokens | Storage |
|-----------------|------------|------------|---------|
| 50 | ~20 | ~5M | ~50MB |
| 100 | ~40 | ~15M | ~150MB |
| 200 | ~70 | ~40M | ~400MB |
| 500 | ~150 | ~150M | ~1.5GB |

---

## Next Steps

1. See [AGENT_LOOP.md](./AGENT_LOOP.md) for the iteration protocol
2. See [REASONING_PROTOCOL.md](./REASONING_PROTOCOL.md) for logging requirements
3. See [DATA_SCHEMAS.md](./DATA_SCHEMAS.md) for complete schema definitions
4. See [IMPLEMENTATION_GUIDE.md](./IMPLEMENTATION_GUIDE.md) for step-by-step instructions
