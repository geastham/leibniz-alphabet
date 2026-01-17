# Data Schemas

## Complete Schema Definitions for ALPHABETUM

**Version:** 1.0.0  
**Last Updated:** 2024-03-15  
**Status:** Canonical Reference

---

## Table of Contents

1. [Schema Overview](#1-schema-overview)
2. [Primitive Schemas](#2-primitive-schemas)
3. [Relationship Schemas](#3-relationship-schemas)
4. [Reasoning Schemas](#4-reasoning-schemas)
5. [Calculus Schemas](#5-calculus-schemas)
6. [Validation Schemas](#6-validation-schemas)
7. [State Management Schemas](#7-state-management-schemas)
8. [Enumerations](#8-enumerations)

---

## 1. Schema Overview

### 1.1 Design Principles

All schemas follow these principles:

| Principle | Description |
|-----------|-------------|
| **YAML-First** | All data stored as YAML for human readability and version control |
| **Self-Documenting** | Field names are descriptive; comments explain purpose |
| **Evolvable** | Version fields enable schema migration |
| **Cross-Referenced** | IDs link entities across files |
| **Timestamped** | All entities track creation and modification times |

### 1.2 ID Conventions

| Entity Type | Pattern | Example |
|-------------|---------|---------|
| Primitive | `PRM_{XXXX}` | `PRM_0042` |
| Candidate | `CAND_{iteration}_{seq}` | `CAND_042_003` |
| Decision | `DEC_{XXXX}` | `DEC_0015` |
| Paradox | `PAR_{XXXX}` | `PAR_0007` |
| Meta-Reflection | `MR_{XXXX}` | `MR_0012` |
| Domain | Lowercase snake_case | `space`, `mind`, `causation` |

### 1.3 Timestamp Format

All timestamps use ISO 8601 format:
```
YYYY-MM-DDTHH:MM:SSZ
Example: 2024-03-15T14:32:07Z
```

---

## 2. Primitive Schemas

### 2.1 Primitive Index Entry (Compact)

Location: `alphabet/primitives/index.yaml`

```yaml
# Schema for index.yaml
alphabet_index:
  version: string         # Schema version: "1.0.0"
  last_updated: datetime  # When last modified
  iteration: int          # Current iteration number
  
  statistics:
    total_primitives: int
    by_domain:            # Count per domain
      space: int
      time: int
      causation: int
      mind: int
      matter: int
      quantity: int
      quality: int
      relation: int
      being: int
      ethics: int
      emotion: int
      # ... extensible
    by_status:
      stable: int         # Unchanged for N iterations
      recent: int         # Added in last M iterations
      contested: int      # Under reconsideration
      
  primitives:             # Array of compact entries
    - id: string          # "PRM_0001"
      label: string       # "existence"
      prime: int          # Assigned prime number: 2, 3, 5, ...
      domain: string      # Primary domain
      status: enum        # stable | recent | contested
      added_iteration: int
      last_reviewed: int
      confidence: float   # 0.0-1.0
```

### 2.2 Primitive Detailed Entry

Location: `alphabet/primitives/detailed/PRM_XXXX_{label}.yaml`

```yaml
# Full primitive specification
primitive:
  # === IDENTITY ===
  id: string              # "PRM_0042"
  symbol: string          # Proposed symbolic representation: "∃", "→", etc.
  label: string           # Human-readable: "existence"
  
  # === DEFINITION ===
  definition:
    informal: string      # Natural language definition
    formal: string | null # Formal logical definition if expressible
    ostensive:            # Examples pointing to the concept
      - string
      - string
    negative:             # What this concept is NOT
      - string
      - string
    boundary_cases:       # Edge cases where application is unclear
      - case: string
        resolution: string
        
  # === JUSTIFICATION ===
  justification:
    primitiveness_argument: string  # Why this can't be decomposed
    
    decomposition_attempts:  # Record of decomposition attacks
      - approach: string     # "analytic", "synthetic", "functional"
        attempt: string      # What was tried
        result: string       # Why it failed
        iteration: int       # When attempted
        
    linguistic_evidence: string     # Cross-linguistic support
    developmental_evidence: string  # How children acquire this
    philosophical_precedent:
      - thinker: string      # "Aristotle"
        work: string         # "Categories"
        treatment: string    # How they treated this concept
        
  # === RELATIONSHIPS ===
  relationships:
    contrasts_with:          # Mutually exclusive primitives
      - id: string           # "PRM_0043"
        label: string        # For quick reference
        reason: string       # Why they contrast
        
    presupposes:             # Required for this concept to apply
      - id: string
        label: string
        reason: string
        
    presupposed_by:          # Primitives that require this one
      - id: string
        label: string
        
    often_combined_with:     # Frequent composition partners
      - id: string
        label: string
        example_composition: string
        
    domain_primary: string   # Main domain
    domains_secondary:       # Also applicable to
      - string
      
  # === METADATA ===
  metadata:
    proposed_iteration: int
    accepted_iteration: int
    prime_number: int        # For Leibniz composition
    
    confidence:
      current: float         # 0.0-1.0
      history:               # How confidence evolved
        - iteration: int
          value: float
          reason: string
          
    stability:
      last_changed: int      # Iteration of last change
      change_count: int      # How many times revised
      
    version: int             # Entry version for tracking revisions
    
  # === LEIBNIZ CONNECTION ===
  leibniz_correspondence:
    mentioned_by_leibniz: boolean
    citations:
      - work: string
        passage: string
        interpretation: string
    alignment: string        # How well this matches Leibniz's vision
    
  # === HISTORY ===
  history:
    proposed:
      iteration: int
      strategy: string       # How it was generated
      original_form: string  # Initial definition
      
    evaluations:             # CRITIC evaluations
      - iteration: int
        verdict: string      # ACCEPT, REJECT, REFINE
        key_points: string
        
    revisions:
      - iteration: int
        field: string
        old_value: any
        new_value: any
        reason: string
```

### 2.3 Domain Index

Location: `alphabet/primitives/by_domain/_domain_index.yaml`

```yaml
domain_index:
  version: string
  last_updated: datetime
  
  domains:
    - name: string           # "space"
      description: string    # "Primitives relating to spatial extension..."
      primitive_count: int
      primitives:
        - id: string
          label: string
          confidence: float
```

---

## 3. Relationship Schemas

### 3.1 Relationship Graph

Location: `alphabet/relationships/graph.yaml`

```yaml
relationship_graph:
  version: string
  last_updated: datetime
  iteration: int
  
  # === CONTRAST RELATIONSHIPS ===
  contrasts:                  # Mutually exclusive pairs
    - pair: [string, string]  # [PRM_0001, PRM_0002]
      symmetric: boolean      # Usually true
      reason: string
      established_iteration: int
      
  # === PRESUPPOSITION RELATIONSHIPS ===
  presupposes:                # A requires B
    - source: string          # PRM_0010
      target: string          # PRM_0001
      reason: string
      established_iteration: int
      
  # === COMPOSITION AFFINITIES ===
  composes_well:              # Often combined
    - set: [string, ...]      # [PRM_0001, PRM_0003]
      example: string         # What they compose into
      frequency: int          # How often combined in compositions
      
  # === DERIVED VIEWS ===
  # (Computed from above, cached for efficiency)
  contrast_clusters:          # Groups of mutually contrasting primitives
    - cluster_id: string
      members: [string, ...]
      
  presupposition_chains:      # Transitive closure of presupposes
    - root: string
      chain: [string, ...]
      depth: int
```

### 3.2 Contrast Details

Location: `alphabet/relationships/contrasts.yaml`

```yaml
contrast_details:
  version: string
  
  contrasts:
    - id: string              # "CTR_0001"
      primitives: [string, string]
      
      relationship:
        type: enum            # contradictory | contrary | complementary
        explanation: string
        
      examples:
        - context: string
          why_exclusive: string
          
      exceptions:             # Edge cases where both might apply
        - case: string
          resolution: string
```

---

## 4. Reasoning Schemas

### 4.1 Iteration Summary

Location: `reasoning/logs/iteration_XXX/summary.yaml`

```yaml
iteration_summary:
  iteration: int
  timestamp: datetime
  duration_minutes: int
  
  phases_executed:
    - phase: string           # EXPANSION, CONSOLIDATION, etc.
      cycles: int
      
  candidates:
    proposed: int
    accepted: int
    rejected: int
    deferred: int
    
  primitives:
    added: [string, ...]      # IDs of added primitives
    revised: [string, ...]
    removed: [string, ...]
    
  metrics:
    alphabet_size: int
    coverage_before: float
    coverage_after: float
    acceptance_rate: float
    
  highlights:
    - string
    
  blog_markers: int           # Count of [BLOG_MARKER] tags
  
  next_actions:
    - string
```

### 4.2 PROPOSER Output

Location: `reasoning/logs/iteration_XXX/proposer.yaml`

```yaml
proposer_output:
  timestamp: datetime
  iteration: int
  cycle: int
  strategy: string            # DOMAIN_SWEEP, DECOMPOSITION_MINING, etc.
  
  context:
    alphabet_size: int
    gaps_provided: [string, ...]
    domains_priority: [string, ...]
    
  candidates:
    - id: string              # CAND_042_001
      label: string
      domain: string
      proposed_symbol: string
      
      definition:
        informal: string
        ostensive_examples: [string, ...]
        negative_examples: [string, ...]
        
      generation_trace:
        source: string        # How this was generated
        inspirations: [string, ...]
        decomposition_chain: string  # If from decomposition mining
        
      primitiveness_argument: string
      decomposition_resistance: string
      relevance_to_gaps: string
      
      confidence: float
      
  meta_observations:
    - string
    
  self_assessment:
    novelty: int              # 1-5
    relevance_to_gaps: int    # 1-5
    decomposition_depth: int  # 1-5
```

### 4.3 CRITIC Output

Location: `reasoning/logs/iteration_XXX/critic.yaml`

```yaml
critic_output:
  timestamp: datetime
  iteration: int
  
  evaluations:
    - candidate_id: string
      
      attacks:
        decomposition:
          attempts:
            - approach: string    # analytic, synthetic, functional
              attempt: string
              result: string
              success: boolean    # Did decomposition succeed?
          survived: boolean
          notes: string
          
        circularity:
          concepts_traced: [string, ...]
          dependency_graph:
            - from: string
              to: string
          circular_paths: [[string, ...], ...]
          external_dependencies: [string, ...]
          survived: boolean
          notes: string
          
        redundancy:
          expression_attempts:
            - using: [string, ...]    # Primitives used
              expression: string      # Attempted expression
              success: boolean
          can_be_expressed: boolean
          using_primitives: [string, ...] | null
          notes: string
          
        edge_cases:
          cases_found:
            - case: string
              issue: string
              severity: string    # low, medium, high
          overall_severity: string
          notes: string
          
        cultural_variance:
          evidence_for_universality: [string, ...]
          evidence_against: [string, ...]
          assessment: string      # universal, near_universal, culturally_bound
          notes: string
          
        parsimony:
          expressiveness_value: string  # high, medium, low
          alternatives_considered: [string, ...]
          necessary: boolean
          notes: string
          
      verdict: string             # ACCEPT, REJECT, REFINE
      confidence: float
      
      reasoning_summary: string
      key_insight: string | null
      
  meta_observations:
    - string
```

### 4.4 REFINER Output

Location: `reasoning/logs/iteration_XXX/refiner.yaml`

```yaml
refiner_output:
  timestamp: datetime
  iteration: int
  
  integrations:
    - candidate_id: string
      action: string              # INTEGRATE, REVISE, MERGE, SPLIT
      
      # For INTEGRATE:
      primitive_id: string        # Assigned ID: PRM_0088
      assigned_prime: int
      file_created: string        # Path to new file
      
      relationships_added:
        - type: string            # contrasts_with, presupposes, composes_with
          target: string          # PRM_XXXX
          justification: string
          
  revisions:                      # Changes to existing primitives
    - primitive_id: string
      field: string
      old_value: any
      new_value: any
      reason: string
      
  conflicts:
    detected:
      - type: string              # circularity, redundancy, contrast_violation
        involved: [string, ...]
        description: string
        
    resolved:
      - conflict_type: string
        resolution: string
        actions_taken: [string, ...]
        
  alphabet_state:
    total_primitives: int
    by_domain:
      # domain: count
    consistency_score: float
```

### 4.5 Meta-Reflection

Location: `reasoning/meta_reflections/MR_XXXX_iteration_NNN.yaml`

```yaml
meta_reflection:
  id: string                  # MR_0012
  iteration_range: [int, int] # [40, 45]
  timestamp: datetime
  
  # === PROGRESS ===
  progress:
    primitives_start: int
    primitives_end: int
    primitives_added: int
    primitives_rejected: int
    acceptance_rate: float
    coverage_before: float
    coverage_after: float
    trend: string             # improving, stable, declining
    
  # === PATTERNS ===
  patterns_observed:
    - pattern: string
      frequency: int
      domain: string | null
      implications: string
      
  rejection_patterns:
    by_reason:
      decomposable: int
      redundant: int
      circular: int
      culturally_bound: int
      unnecessary: int
    by_domain:
      # domain: count
      
  # === STRATEGY ===
  strategy_assessment:
    proposer:
      effectiveness: int      # 1-5
      current_mode: string
      notes: string
      
    critic:
      calibration: string     # too_strict, balanced, too_lenient
      notes: string
      
    domain_balance:
      well_covered: [string, ...]
      neglected: [string, ...]
      
  # === PHILOSOPHY ===
  philosophical_observations:
    assumptions:
      - assumption: string
        problematic: boolean
        mitigation: string | null
        
    tradition_bias: string
    leibniz_alignment: int    # 1-5
    leibniz_notes: string
    
  # === COURSE CORRECTION ===
  course_corrections:
    strategy_adjustments:
      - component: string     # PROPOSER, CRITIC, REFINER
        adjustment: string
        rationale: string
        
    domain_priorities: [string, ...]
    criterion_calibration: string
    new_approaches: [string, ...]
    
  # === DECISION ===
  decision: string            # CONTINUE, PIVOT, CONCLUDE
  decision_justification: string
  
  # === PREDICTIONS ===
  predictions:
    - prediction: string
      confidence: float
      
  # === CONTENT ===
  insights_for_archive:
    - insight: string
      category: string        # philosophical, methodological, substantive
      
  paradoxes_encountered:
    - id: string              # PAR_XXXX if new
      description: string
      status: string          # open, resolved
      resolution: string | null
```

### 4.6 Decision Record

Location: `reasoning/decisions/DEC_XXXX_{brief_desc}.yaml`

```yaml
decision_record:
  id: string
  title: string
  date: datetime
  iteration: int
  status: string              # ACCEPTED, PENDING, REVERSED
  
  question: string            # The question being decided
  
  background: string          # Context for the decision
  
  options:
    - option: string
      arguments_for: [string, ...]
      arguments_against: [string, ...]
      
  considerations:
    - claim: string
      analysis: string
      weight: float           # How much this influenced decision
      
  decision: string            # Which option was chosen
  
  justification: string
  confidence: float
  
  implications:
    - string
    
  future_considerations:
    - string
    
  blog_markers:
    - marker_type: string
      description: string
```

### 4.7 Paradox Record

Location: `reasoning/paradoxes/PAR_XXXX_{brief_desc}.yaml`

```yaml
paradox_record:
  id: string
  title: string
  discovered_iteration: int
  timestamp: datetime
  status: string              # open, resolved, accepted_as_limit
  
  description: string         # What the paradox is
  
  context: string             # How we encountered it
  
  analysis:
    nature: string            # circularity, regress, contradiction, etc.
    severity: string          # blocking, significant, minor
    affected_primitives: [string, ...]
    
  resolution_attempts:
    - attempt: string
      result: string
      iteration: int
      
  current_stance: string      # How we're currently handling it
  
  resolution:                 # If resolved
    approach: string
    explanation: string
    iteration: int
    
  insights: [string, ...]
  
  blog_potential: string
```

---

## 5. Calculus Schemas

### 5.1 Operator Definition

Location: `calculus/operators.yaml`

```yaml
operators:
  version: string
  
  composition_operators:
    - id: string              # OP_001
      symbol: string          # "∧"
      name: string            # "conjunction"
      arity: int              # Number of operands
      
      description: string
      
      semantics:
        informal: string
        formal: string        # In chosen formal language
        
      signature:
        inputs: [string, ...]   # Concept types accepted
        output: string          # Concept type produced
        
      examples:
        - inputs: [string, ...]
          output: string
          explanation: string
          
      constraints:
        preconditions: [string, ...]
        postconditions: [string, ...]
        
      implemented_in: [string, ...]  # Which implementations support this
```

### 5.2 Composition Rule

Location: `calculus/rules.yaml`

```yaml
rules:
  version: string
  
  composition_rules:
    - id: string
      name: string
      description: string
      
      pattern:
        lhs: string           # Left-hand side pattern
        rhs: string           # Right-hand side result
        
      conditions: [string, ...] # When rule applies
      
      examples:
        - before: string
          after: string
          
  inference_rules:
    - id: string
      name: string
      description: string
      
      premises: [string, ...]
      conclusion: string
      
      justification: string
```

### 5.3 Composition Example

Location: `calculus/examples/`

```yaml
composition_example:
  id: string
  name: string                # "Deriving JUSTICE"
  complexity: string          # simple, medium, complex
  
  target_concept: string      # The concept being composed
  
  derivation:
    - step: int
      operation: string       # Operator used
      operands: [string, ...] # Primitive IDs or intermediate results
      result: string
      explanation: string
      
  final_expression: string    # The complete composition
  
  validation:
    covers_intuitive_meaning: boolean
    edge_cases_handled: [string, ...]
    limitations: [string, ...]
    
  notes: string
```

---

## 6. Validation Schemas

### 6.1 Benchmark Concept

Location: `validation/benchmarks/test_concepts.yaml`

```yaml
benchmark_concepts:
  version: string
  
  concepts:
    - id: string
      name: string            # "justice"
      domain: string          # "ethics"
      
      expected_complexity: string  # simple, medium, complex
      
      decomposition_hints:    # Suspected constituent primitives
        - string
        
      definition: string      # What this concept means
      
      test_cases:             # Specific instances to check
        - case: string
          should_satisfy: boolean
          
      sources:                # Where this benchmark comes from
        - string
```

### 6.2 Coverage Report

Location: `validation/benchmarks/results/coverage_report.yaml`

```yaml
coverage_report:
  timestamp: datetime
  iteration: int
  
  overall:
    total_concepts: int
    expressible: int
    partially_expressible: int
    inexpressible: int
    coverage_score: float     # 0.0-1.0
    
  by_domain:
    - domain: string
      total: int
      expressible: int
      coverage: float
      
  by_complexity:
    - complexity: string
      total: int
      expressible: int
      coverage: float
      
  details:
    - concept_id: string
      status: string          # expressible, partial, inexpressible
      decomposition: string | null
      missing_primitives: [string, ...] | null
      confidence: float
```

### 6.3 Consistency Report

Location: `validation/consistency/report.yaml`

```yaml
consistency_report:
  timestamp: datetime
  iteration: int
  
  overall_score: float        # 0.0-1.0
  status: string              # consistent, warnings, violations
  
  circularity_check:
    status: string            # pass, fail
    violations:
      - path: [string, ...]   # Circular dependency chain
        severity: string
        
  redundancy_check:
    status: string
    violations:
      - primitive: string
        can_be_expressed_as: string
        using: [string, ...]
        
  contrast_check:
    status: string
    violations:
      - primitives: [string, string]
        violation: string     # What makes them non-exclusive
        
  presupposition_check:
    status: string
    violations:
      - source: string
        missing_target: string
```

---

## 7. State Management Schemas

### 7.1 Iteration State

Location: `reasoning/iteration_state.yaml`

```yaml
iteration_state:
  current_iteration: int
  phase: string               # EXPANSION, CONSOLIDATION, COMPOSITION, META_REFLECTION
  cycle_in_phase: int
  last_updated: datetime
  
  current_strategy:
    proposer_mode: string
    proposer_temperature: float
    critic_strictness: float  # 0.0-1.0
    domains_priority: [string, ...]
    
  pending:
    candidates_to_evaluate: [string, ...]
    candidates_to_revise: [string, ...]
    conflicts_to_resolve: [string, ...]
    gaps_to_fill: [string, ...]
    
  metrics:
    recent_acceptance_rate: float
    coverage_score: float
    consistency_score: float
    
  triggers:
    meta_reflection_due: boolean
    iterations_since_meta: int
    iterations_since_primitive: int
    
  history:
    total_proposed: int
    total_accepted: int
    total_rejected: int
```

### 7.2 Session Handoff

Location: `reasoning/session_handoff.yaml`

```yaml
session_handoff:
  session_id: string
  ended_at: datetime
  reason: string              # context_limit, user_pause, error, etc.
  
  state_snapshot:
    iteration: int
    phase: string
    cycle: int
    
  in_progress:
    current_task: string
    current_candidate: string | null
    pending_evaluations: [string, ...]
    partial_results: any      # Task-specific partial state
    
  must_do_next:
    - action: string
      priority: int
      
  context_critical:
    - string                  # Important context to re-establish
    
  files_to_read:
    - path: string
      purpose: string
```

### 7.3 Iteration Lock

Location: `.iteration_lock` (during processing)

```yaml
iteration_lock:
  iteration: int
  started: datetime
  phase: string
  status: string              # IN_PROGRESS, COMPLETING, FAILED
  checkpoint: string          # Last completed step
  pid: int                    # Process ID (if applicable)
```

---

## 8. Enumerations

### 8.1 Domains

```yaml
domains:
  - being          # Existence, identity, essence
  - space          # Extension, location, shape
  - time           # Duration, succession, simultaneity
  - causation      # Cause, effect, influence
  - mind           # Consciousness, thought, perception
  - matter         # Physical substance, properties
  - quantity       # Number, magnitude, degree
  - quality        # Properties, attributes
  - relation       # Between, with, towards
  - ethics         # Good, bad, ought
  - emotion        # Feeling, affect
  - action         # Doing, agency
  - knowledge      # Belief, truth, justification
  - social         # Person, group, institution
  - language       # Meaning, reference, expression
```

### 8.2 Phases

```yaml
phases:
  - EXPANSION      # Generate and evaluate new candidates
  - CONSOLIDATION  # Review and maintain consistency
  - COMPOSITION    # Test expressiveness
  - META_REFLECTION # Strategy review
```

### 8.3 Verdicts

```yaml
verdicts:
  - ACCEPT         # Candidate survives all attacks
  - REJECT         # Candidate fails critical attack
  - REFINE         # Core valid, formulation needs work
  - DEFER          # Need more information
```

### 8.4 Primitive Status

```yaml
primitive_status:
  - stable         # Unchanged for N iterations
  - recent         # Added in last M iterations
  - contested      # Under reconsideration
  - deprecated     # Marked for removal
```

### 8.5 Relationship Types

```yaml
relationship_types:
  - contrasts_with   # Mutually exclusive
  - presupposes      # Requires for application
  - composes_well    # Often combined
  - specializes      # More specific version
  - generalizes      # More abstract version
```

### 8.6 Attack Types

```yaml
attack_types:
  - decomposition    # Break into simpler parts
  - circularity      # Check for self-reference
  - redundancy       # Check if expressible via others
  - edge_cases       # Find boundary conditions
  - cultural_variance # Check universality
  - parsimony        # Check necessity
```

### 8.7 Blog Marker Categories

```yaml
blog_marker_categories:
  - NARRATIVE_ARC           # A complete reasoning journey
  - PHILOSOPHICAL_INSIGHT   # Interesting observation
  - METHODOLOGY_ILLUSTRATION # Shows method in action
  - PARADOX_ENCOUNTER       # Hit a contradiction
  - BREAKTHROUGH_MOMENT     # Sudden insight
  - FAILURE_ANALYSIS        # What didn't work
  - HISTORICAL_CONNECTION   # Link to Leibniz/others
  - META_INSIGHT            # Self-observation
```

---

## Validation

All YAML files should validate against these schemas. Use tools like:

```bash
# Example validation command
python tools/validate_schema.py alphabet/primitives/detailed/PRM_0042_causation.yaml --schema primitive_detailed
```

Schema validation ensures:
1. Required fields present
2. Types correct
3. Enums valid
4. Cross-references resolvable
5. Timestamps parseable
