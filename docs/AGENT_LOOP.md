# The Agent Loop

## Iterative Refinement Protocol for ALPHABETUM

**Version:** 1.0.0  
**Last Updated:** 2024-03-15  
**Status:** Canonical Reference

---

## Table of Contents

1. [Core Philosophy](#1-core-philosophy)
2. [The Master Loop](#2-the-master-loop)
3. [Phase Specifications](#3-phase-specifications)
4. [Stopping Conditions](#4-stopping-conditions)
5. [Self-Continuation Protocol](#5-self-continuation-protocol)
6. [Prompt Templates](#6-prompt-templates)
7. [Iteration Handoff Protocol](#7-iteration-handoff-protocol)

---

## 1. Core Philosophy

### 1.1 The Central Insight

> **The agent must be told how to keep going until it's done.**

This is not a one-shot task. This is an **open-ended reasoning journey** that could span hundreds of iterations. The agent must:

1. **Know what "done" looks like** (stopping conditions)
2. **Know how to make progress** (iteration protocol)
3. **Know when to step back** (meta-reflection triggers)
4. **Know how to escape local optima** (strategy pivots)
5. **Know what to record** (the reasoning is the artifact)

### 1.2 The Fundamental Tension

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    THE REFINEMENT PARADOX                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  The agent must be:                                                     │
│                                                                         │
│    PERSISTENT       but not      STUBBORN                               │
│    (keep trying)                 (recognize dead ends)                  │
│                                                                         │
│    RIGOROUS         but not      PARALYZED                              │
│    (validate claims)             (accept imperfection)                  │
│                                                                         │
│    CREATIVE         but not      UNDISCIPLINED                          │
│    (explore widely)              (maintain coherence)                   │
│                                                                         │
│    SELF-CRITICAL    but not      SELF-DEFEATING                         │
│    (question assumptions)        (trust the process)                    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 1.3 Progress Model

Progress is measured on multiple dimensions:

| Dimension | Metric | Target |
|-----------|--------|--------|
| **Coverage** | % of benchmark concepts expressible | 90%+ |
| **Primitives** | Number of validated primitives | 50-200 |
| **Consistency** | Circularity-free, non-redundant | 100% |
| **Stability** | Primitives unchanged over iterations | High for core |
| **Documentation** | Reasoning logged per decision | 100% |

---

## 2. The Master Loop

### 2.1 High-Level Structure

```
╔═══════════════════════════════════════════════════════════════════════════╗
║                           THE MASTER LOOP                                  ║
╠═══════════════════════════════════════════════════════════════════════════╣
║                                                                           ║
║  INITIALIZE                                                               ║
║  ├── Load or create initial state                                         ║
║  ├── Load seed primitives (if iteration 0)                               ║
║  └── Verify consistency                                                   ║
║                                                                           ║
║  ┌─────────────────────────────────────────────────────────────────────┐  ║
║  │                                                                     │  ║
║  │  WHILE not stopping_condition():                                    │  ║
║  │                                                                     │  ║
║  │      PHASE 1: EXPANSION (3-5 cycles)                               │  ║
║  │      ├── PROPOSER generates candidates                             │  ║
║  │      ├── CRITIC evaluates each candidate                           │  ║
║  │      ├── REFINER integrates accepted candidates                    │  ║
║  │      └── ARCHIVIST logs everything                                 │  ║
║  │                                                                     │  ║
║  │      PHASE 2: CONSOLIDATION (1-2 cycles)                           │  ║
║  │      ├── CRITIC reviews alphabet for new issues                    │  ║
║  │      ├── REFINER resolves conflicts and redundancies               │  ║
║  │      └── ARCHIVIST logs everything                                 │  ║
║  │                                                                     │  ║
║  │      PHASE 3: COMPOSITION (2-3 cycles)                             │  ║
║  │      ├── Attempt to express benchmark concepts                     │  ║
║  │      ├── Identify expressiveness gaps                              │  ║
║  │      ├── Feed gaps to next PROPOSER cycle                          │  ║
║  │      └── ARCHIVIST logs everything                                 │  ║
║  │                                                                     │  ║
║  │      PHASE 4: META-REFLECTION (1 cycle)                            │  ║
║  │      ├── META-REASONER evaluates progress                          │  ║
║  │      ├── Adjust strategy parameters                                │  ║
║  │      ├── Document insights and paradoxes                           │  ║
║  │      └── Decide: CONTINUE | PIVOT | CONCLUDE                       │  ║
║  │                                                                     │  ║
║  │      INCREMENT iteration                                            │  ║
║  │                                                                     │  ║
║  └─────────────────────────────────────────────────────────────────────┘  ║
║                                                                           ║
║  TERMINATE                                                                ║
║  ├── Generate FINAL_REPORT.md                                            ║
║  ├── Create final version snapshot                                       ║
║  └── Archive all state                                                    ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
```

### 2.2 Iteration Flow Diagram

```
ITERATION N
│
├── 1. READ STATE
│   ├── Load alphabet/primitives/index.yaml
│   ├── Load reasoning/iteration_state.yaml
│   ├── Load recent logs (last 3-5 iterations)
│   └── Summarize for context
│
├── 2. DETERMINE PHASE
│   ├── Check phase in iteration_state
│   ├── Check cycle counter
│   └── Determine which phase to execute
│
├── 3. EXECUTE PHASE
│   │
│   ├── [IF EXPANSION]
│   │   ├── Generate N candidates (PROPOSER)
│   │   ├── For each candidate:
│   │   │   ├── Evaluate (CRITIC)
│   │   │   ├── If ACCEPT: integrate (REFINER)
│   │   │   └── If REJECT: archive rejection
│   │   └── Log all reasoning
│   │
│   ├── [IF CONSOLIDATION]
│   │   ├── Check for emergent conflicts
│   │   ├── Check for newly-apparent redundancies
│   │   ├── Propose resolutions
│   │   └── Apply resolutions (REFINER)
│   │
│   ├── [IF COMPOSITION]
│   │   ├── Select benchmark concepts to test
│   │   ├── Attempt decomposition into primitives
│   │   ├── Record expressible vs inexpressible
│   │   └── Extract gap information
│   │
│   └── [IF META-REFLECTION]
│       ├── Aggregate metrics from period
│       ├── Identify patterns
│       ├── Propose strategy adjustments
│       └── Record insights
│
├── 4. UPDATE STATE
│   ├── Write updated alphabet index
│   ├── Write new primitive files (if any)
│   ├── Update relationships
│   ├── Write iteration log
│   └── Update iteration_state
│
├── 5. CHECK TRANSITIONS
│   ├── Phase complete? → Next phase
│   ├── Meta-reflection trigger? → Phase 4
│   └── Stopping condition? → TERMINATE
│
└── 6. CONTINUE or TERMINATE
```

### 2.3 Cycle Management

Within each iteration, phases are cycled:

```
EXPANSION     ████████████████░░░░░░░░░░░░░░░░░░░░░░░░  40%
CONSOLIDATION ░░░░░░░░░░░░░░░░████████░░░░░░░░░░░░░░░░  20%
COMPOSITION   ░░░░░░░░░░░░░░░░░░░░░░░░████████████░░░░  30%
META          ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░████  10%
```

**Cycle counts per iteration** (configurable):

| Phase | Cycles | Purpose |
|-------|--------|---------|
| EXPANSION | 3-5 | Generate and evaluate new candidates |
| CONSOLIDATION | 1-2 | Maintain alphabet consistency |
| COMPOSITION | 2-3 | Test expressiveness, find gaps |
| META-REFLECTION | 1 | Step back, adjust strategy |

---

## 3. Phase Specifications

### 3.1 EXPANSION Phase

**Goal**: Add new validated primitives to the alphabet

**Cycle structure**:

```python
def expansion_cycle(state):
    # 1. PROPOSER generates candidates
    candidates = proposer.generate(
        n=3,  # Candidates per cycle
        strategy=state.current_strategy.proposer_mode,
        gaps=state.pending.gaps_to_fill,
        domains_priority=state.current_strategy.domains_priority
    )
    
    # 2. CRITIC evaluates each
    for candidate in candidates:
        evaluation = critic.evaluate(candidate, state.alphabet)
        
        # 3. Log the evaluation
        archivist.log_evaluation(candidate, evaluation)
        
        # 4. Handle verdict
        if evaluation.verdict == "ACCEPT":
            state = refiner.integrate(candidate, evaluation, state)
        elif evaluation.verdict == "REJECT":
            archivist.archive_rejection(candidate, evaluation)
        elif evaluation.verdict == "REFINE":
            state.pending.candidates_to_revise.append(candidate)
    
    return state
```

**PROPOSER instructions per cycle**:

| Cycle | Mode | Instructions |
|-------|------|--------------|
| 1 | DOMAIN_SWEEP | "Focus on the highest-priority domain. Propose 3 candidates from that domain." |
| 2 | DECOMPOSITION_MINING | "Take 2 complex concepts, decompose as far as possible. What resists decomposition?" |
| 3 | GAP_FILLING | "Review the current gaps. Propose candidates that would help express inexpressible concepts." |
| 4 | CROSS_REFERENCE | "Look at recent decomposition chains. What concepts appear repeatedly?" |
| 5 | THOUGHT_EXPERIMENT | "What concepts would you need to explain human experience to an alien?" |

### 3.2 CONSOLIDATION Phase

**Goal**: Ensure alphabet remains consistent as it grows

**Checks to perform**:

```yaml
consolidation_checks:
  
  circularity_check:
    description: "Ensure no primitive's definition depends on itself"
    action: "Trace dependency chains for all recent additions"
    on_violation: "Flag for revision or removal"
    
  redundancy_check:
    description: "Ensure no primitive is expressible via others"
    action: "For each primitive, attempt to express using all others"
    on_violation: "Merge or remove redundant primitive"
    
  contrast_consistency:
    description: "Ensure contrasting primitives are truly exclusive"
    action: "Check all contrast relationships still hold"
    on_violation: "Revise relationship or primitive definitions"
    
  presupposition_validity:
    description: "Ensure presupposed primitives exist"
    action: "Check all presupposition targets are valid"
    on_violation: "Add missing primitive or revise relationship"
```

**Cycle structure**:

```python
def consolidation_cycle(state):
    issues = []
    
    # 1. Run checks
    issues.extend(check_circularity(state.alphabet))
    issues.extend(check_redundancy(state.alphabet))
    issues.extend(check_contrast_consistency(state.alphabet))
    issues.extend(check_presuppositions(state.alphabet))
    
    # 2. Prioritize issues
    issues = prioritize_by_severity(issues)
    
    # 3. Resolve issues
    for issue in issues[:3]:  # Handle top 3 per cycle
        resolution = propose_resolution(issue, state)
        if resolution.requires_removal:
            state = remove_primitive(resolution.primitive_id, state)
        elif resolution.requires_revision:
            state = revise_primitive(resolution.primitive_id, resolution.changes, state)
        elif resolution.requires_merge:
            state = merge_primitives(resolution.source, resolution.target, state)
        
        archivist.log_resolution(issue, resolution)
    
    return state
```

### 3.3 COMPOSITION Phase

**Goal**: Test expressiveness, identify gaps

**Process**:

```python
def composition_cycle(state):
    # 1. Select test concepts
    test_concepts = select_benchmark_concepts(
        n=5,
        prioritize_uncovered=True,
        current_coverage=state.metrics.coverage_score
    )
    
    # 2. Attempt decomposition
    results = []
    for concept in test_concepts:
        attempt = decompose_concept(concept, state.alphabet, state.calculus)
        results.append({
            "concept": concept,
            "expressible": attempt.success,
            "decomposition": attempt.decomposition if attempt.success else None,
            "missing_primitives": attempt.gaps if not attempt.success else [],
            "confidence": attempt.confidence
        })
    
    # 3. Update coverage metrics
    state.metrics.coverage_score = calculate_coverage(state)
    
    # 4. Extract gaps for next EXPANSION
    gaps = extract_gaps(results)
    state.pending.gaps_to_fill = prioritize_gaps(gaps)
    
    # 5. Log everything
    archivist.log_composition_attempt(results)
    
    return state
```

**Gap extraction**:

```yaml
gap_analysis:
  concept_attempted: "justice"
  expressible: false
  
  decomposition_attempt:
    - "fairness" → EXISTS (PRM_0042)
    - "desert" → MISSING
    - "rights" → PARTIALLY (PRM_0038 covers some aspects)
    - "social_contract" → MISSING
    
  gaps_identified:
    - label: "desert"
      domain: "ethics"
      description: "The concept that people should get what they deserve"
      priority: high
      
    - label: "social_contract"
      domain: "political_philosophy"
      description: "The implicit agreement underlying society"
      priority: medium
```

### 3.4 META-REFLECTION Phase

**Goal**: Step back, assess progress, adjust strategy

**Triggers** (any of these):
- End of iteration cycle (every N iterations)
- Acceptance rate below threshold
- Coverage plateau detected
- Consistency violation detected
- Explicit request from previous reflection

**Reflection protocol**:

```markdown
## META-REFLECTION FRAMEWORK

### 1. QUANTITATIVE ASSESSMENT

| Metric | Last Period | Current | Trend |
|--------|-------------|---------|-------|
| Primitives added | X | Y | ↑/↓/→ |
| Acceptance rate | X% | Y% | ↑/↓/→ |
| Coverage score | X% | Y% | ↑/↓/→ |
| Consistency score | X% | Y% | ↑/↓/→ |

### 2. QUALITATIVE ASSESSMENT

**What's working well?**
- [Observations about effective strategies]

**What's not working?**
- [Patterns in rejections]
- [Persistent gaps]
- [Recurring issues]

### 3. PATTERN ANALYSIS

**Rejection patterns:**
- Most common rejection reason: [X]
- Domain most rejected from: [Y]
- Implication: [Z]

**Success patterns:**
- What do accepted primitives have in common?
- Which strategies yield most acceptances?

### 4. PHILOSOPHICAL AUDIT

**Assumptions we're making:**
1. [Assumption 1] - Problematic? How to mitigate?
2. [Assumption 2] - Problematic? How to mitigate?

**Leibniz alignment:**
- How well does our alphabet match Leibniz's vision?
- Are we being true to the original project?
- Where are we diverging, and should we?

### 5. STRATEGY ADJUSTMENTS

| Component | Current | Proposed | Rationale |
|-----------|---------|----------|-----------|
| PROPOSER mode | [X] | [Y] | [Why] |
| CRITIC strictness | [X] | [Y] | [Why] |
| Domain priority | [X] | [Y] | [Why] |

### 6. DECISION

[ ] CONTINUE - Keep current course with minor adjustments
[ ] PIVOT - Major strategy change required
[ ] CONCLUDE - We've gone as far as we can

**Justification:**
[Explanation of decision]

### 7. PREDICTIONS

For next period, I predict:
1. [Prediction 1] (confidence: X%)
2. [Prediction 2] (confidence: Y%)

### 8. INSIGHTS TO ARCHIVE

**Worth preserving for blog/documentation:**
- [Insight 1]
- [Insight 2]
```

---

## 4. Stopping Conditions

### 4.1 Success Conditions

The agent should CONTINUE running until ANY of these are met:

```yaml
stopping_conditions:
  
  coverage_threshold:
    description: "Sufficient expressiveness achieved"
    condition: "coverage_score >= 0.90"
    action: "TERMINATE with success"
    
  stability_achieved:
    description: "Alphabet has stabilized"
    condition: "no primitives added or changed in last 10 iterations"
    action: "TERMINATE with success (local optimum)"
    
  diminishing_returns:
    description: "Progress has slowed beyond recovery"
    condition: "less than 2 primitives added in last 10 iterations AND no strategy pivot available"
    action: "TERMINATE with partial success"
```

### 4.2 Failure Conditions

```yaml
failure_conditions:
  
  fundamental_limit:
    description: "Agent determines the task is impossible"
    condition: "META-REASONER concludes with strong justification that further progress requires solving unsolvable philosophical problems"
    action: "TERMINATE with documented failure"
    
  resource_exhaustion:
    description: "Maximum iterations reached"
    condition: "iteration >= max_iterations"
    action: "TERMINATE with timeout"
    
  irrecoverable_inconsistency:
    description: "Alphabet has become fundamentally corrupted"
    condition: "CONSOLIDATION cannot resolve circular dependencies"
    action: "ROLLBACK to last stable version or TERMINATE"
```

### 4.3 The Stopping Decision

The META-REASONER makes the final call:

```python
def should_continue(state, metrics, reflection):
    # Check hard stops
    if metrics.iteration >= config.max_iterations:
        return False, "MAX_ITERATIONS_REACHED"
    
    if metrics.coverage_score >= config.coverage_threshold:
        return False, "COVERAGE_ACHIEVED"
    
    # Check soft stops
    if reflection.decision == "CONCLUDE":
        return False, reflection.justification
    
    # Check diminishing returns
    recent_additions = count_additions(state, window=10)
    if recent_additions < config.diminishing_returns_threshold:
        if not reflection.has_pivot_strategy:
            return False, "DIMINISHING_RETURNS_NO_PIVOT"
    
    # Check stability
    if is_stable(state, window=10):
        return False, "STABILITY_ACHIEVED"
    
    # Default: continue
    return True, "PROGRESS_POSSIBLE"
```

---

## 5. Self-Continuation Protocol

### 5.1 The Continuation Imperative

> **CRITICAL**: The agent must understand that this task is not complete after one response. It must actively continue until stopping conditions are met.

**Instructions for the agent**:

```markdown
## CONTINUATION PROTOCOL

You are engaged in a multi-iteration reasoning task. After each action:

1. CHECK: Have you hit a stopping condition?
   - If YES: Generate FINAL_REPORT.md and terminate
   - If NO: Continue to step 2

2. CHECK: Have you completed the current phase?
   - If YES: Transition to next phase
   - If NO: Continue current phase

3. CHECK: Is it time for meta-reflection?
   - If YES: Execute META-REFLECTION phase
   - If NO: Continue with current phase

4. EXECUTE: Perform the next step in the current phase

5. LOG: Record all reasoning, decisions, and outputs

6. REPEAT: Return to step 1

YOU ARE NOT DONE UNTIL A STOPPING CONDITION IS MET.
```

### 5.2 Context Persistence

Since LLMs are stateless, the agent must:

1. **Read state from files** at the start of each continuation
2. **Write state to files** at the end of each step
3. **Use files as memory** between invocations

**Critical state files**:

```yaml
must_read_on_resume:
  - alphabet/primitives/index.yaml       # Current alphabet
  - reasoning/iteration_state.yaml       # Where we are
  - reasoning/logs/iteration_XXX/        # Recent reasoning
  - reasoning/meta_reflections/latest    # Current strategy

must_write_on_pause:
  - reasoning/iteration_state.yaml       # Updated state
  - reasoning/logs/iteration_XXX/        # All new reasoning
  - alphabet/primitives/index.yaml       # If changed
  - Any new primitive files              # If created
```

### 5.3 Handoff Format

When the agent needs to continue (e.g., new chat session), it should be able to resume from:

```yaml
# handoff_state.yaml

handoff:
  timestamp: datetime
  iteration: int
  phase: EXPANSION | CONSOLIDATION | COMPOSITION | META_REFLECTION
  cycle_in_phase: int
  
  immediate_context:
    what_was_i_doing: "string description"
    what_should_i_do_next: "string description"
    pending_candidates: list[CandidateID]
    pending_issues: list[IssueID]
    
  key_metrics:
    primitives_count: int
    coverage_score: float
    recent_acceptance_rate: float
    
  files_to_read:
    - path: "alphabet/primitives/index.yaml"
      purpose: "Current alphabet state"
    - path: "reasoning/logs/iteration_XXX/"
      purpose: "Recent deliberation"
    # ... etc
```

---

## 6. Prompt Templates

### 6.1 PROPOSER System Prompt

```markdown
# ROLE: PROPOSER

You are the PROPOSER in Project Alphabetum, an attempt to reconstruct Leibniz's Alphabet of Human Thought.

## Your Mission

Generate candidate **primitive concepts**—irreducible, simple ideas that cannot be broken down further and from which complex concepts can be composed.

## Current State

- **Iteration**: {iteration}
- **Alphabet size**: {alphabet_size} primitives
- **Recent acceptance rate**: {acceptance_rate}%
- **Coverage score**: {coverage_score}%
- **Priority domains**: {domains_priority}
- **Current strategy**: {proposer_mode}

## Current Gaps

The following concepts cannot yet be expressed:
{gaps_list}

## Generation Instructions

Using the **{proposer_mode}** strategy, generate **{n}** candidate primitives.

For each candidate, provide:

1. **Label**: A clear, concise name
2. **Informal definition**: What this concept means (some circularity is acceptable for primitives)
3. **Domain**: Primary domain (space, time, causation, mind, matter, quantity, quality, relation, etc.)
4. **Ostensive examples**: 3-5 examples that point to this concept
5. **Negative examples**: What this concept is NOT (to clarify boundaries)
6. **Primitiveness argument**: Why can't this be decomposed?
7. **Decomposition resistance**: What happens when you try to break it down?
8. **Relevance**: How does this help express currently-inexpressible concepts?

## Quality Criteria

Good candidates:
- Resist decomposition from multiple angles
- Apply across multiple contexts
- Are necessary for expressing important concepts
- Don't overlap with existing primitives

## Current Alphabet Summary

{alphabet_summary}

## Output Format

```yaml
candidates:
  - label: "..."
    informal_definition: "..."
    domain: "..."
    proposed_symbol: "..."
    ostensive_examples: [...]
    negative_examples: [...]
    primitiveness_argument: "..."
    decomposition_resistance: "..."
    relevance_to_gaps: "..."
```

Generate candidates now.
```

### 6.2 CRITIC System Prompt

```markdown
# ROLE: CRITIC

You are the CRITIC in Project Alphabetum. Your mission: rigorously test whether proposed concepts are truly primitive.

## Your Mindset

Be adversarial but fair. Your job is to find weaknesses. Apply every attack with genuine effort to falsify the claim of primitiveness. But also acknowledge when a concept survives your attacks.

## Candidate to Evaluate

{candidate_yaml}

## Attack Protocol

Apply these attacks in order:

### 1. DECOMPOSITION ATTACK

Try to break this concept into simpler parts:
- **Analytic**: Can you define it in terms of more basic concepts?
- **Synthetic**: Can you identify constituent parts or aspects?
- **Functional**: Can you describe what it does in terms of simpler operations?

Record each attempt and its result.

### 2. CIRCULARITY CHECK

- Trace every concept used in the definition
- Do any of them presuppose the candidate itself?
- Do any of them rely on concepts not yet in our alphabet?
- Draw the dependency graph

### 3. REDUNDANCY TEST

Given our current alphabet:
{alphabet_summary}

Can this candidate be expressed as a composition of existing primitives?
- If yes: it's not primitive
- If no: what's missing that prevents expression?

### 4. EDGE CASES

Find contexts where:
- The concept's meaning shifts
- The concept doesn't apply cleanly
- The concept behaves unexpectedly

What do these edge cases tell us?

### 5. CULTURAL VARIANCE

- Is this concept truly universal across cultures?
- Evidence from linguistics? Developmental psychology?
- Could an alien civilization lack this concept?

### 6. PARSIMONY CHECK

- Do we really need this primitive?
- What expressiveness do we lose without it?
- Is there a more economical alternative?

## Verdict

After applying all attacks, render one of:

- **ACCEPT**: Candidate survived all attacks. Recommend for alphabet.
- **REJECT**: Candidate failed critical attack. Specify which and why.
- **REFINE**: Core intuition is valid, but formulation needs work. Suggest improvements.

## Output Format

```yaml
evaluation:
  candidate_id: "..."
  
  attacks:
    decomposition:
      attempts:
        - approach: "analytic"
          attempt: "..."
          result: "..."
        - approach: "synthetic"
          attempt: "..."
          result: "..."
      survived: true/false
      notes: "..."
      
    circularity:
      concepts_traced: [...]
      circular_paths: [...]
      external_dependencies: [...]
      survived: true/false
      notes: "..."
      
    redundancy:
      expression_attempt: "..."
      can_be_expressed: true/false
      using_primitives: [...] or null
      notes: "..."
      
    edge_cases:
      cases_found:
        - case: "..."
          issue: "..."
      severity: low/medium/high
      notes: "..."
      
    cultural_variance:
      evidence_for_universality: [...]
      evidence_against: [...]
      assessment: universal/near_universal/culturally_bound
      notes: "..."
      
    parsimony:
      expressiveness_value: high/medium/low
      alternatives: [...]
      necessary: true/false
      notes: "..."
  
  verdict: ACCEPT/REJECT/REFINE
  confidence: 0.0-1.0
  
  reasoning_summary: "..."
  key_insight: "..." # Something learned regardless of verdict
```

Evaluate the candidate now.
```

### 6.3 META-REASONER System Prompt

```markdown
# ROLE: META-REASONER

You are the META-REASONER in Project Alphabetum. Your mission: step back from the work and reflect on the process itself.

## Current State

- **Iteration range under review**: {start_iteration} - {end_iteration}
- **Primitives at start**: {primitives_start}
- **Primitives now**: {primitives_now}
- **Primitives added**: {primitives_added}
- **Candidates proposed**: {candidates_proposed}
- **Candidates rejected**: {candidates_rejected}
- **Acceptance rate**: {acceptance_rate}%
- **Coverage at start**: {coverage_start}%
- **Coverage now**: {coverage_now}%

## Recent Logs Summary

{recent_logs_summary}

## Rejection Patterns

{rejection_patterns}

## Current Gaps

{current_gaps}

## Reflection Framework

### 1. Progress Assessment

Evaluate quantitative and qualitative progress:
- Are we moving toward our goals?
- Is the rate of progress acceptable?
- What trends do you see?

### 2. Strategy Evaluation

- Is the PROPOSER generating good candidates?
- Is the CRITIC appropriately calibrated (too strict? too lenient?)?
- Are we neglecting certain domains?
- What patterns do rejections show?

### 3. Philosophical Audit

- What assumptions are we making implicitly?
- Which philosophical traditions are we leaning toward?
- Are we being true to Leibniz's original vision?
- What would critics of this project say?

### 4. Course Correction

If adjustments are needed:
- What specific changes would help?
- Which domains should we prioritize?
- Should we calibrate the primitiveness criterion?
- Are there new strategies to try?

### 5. Decision

You must decide:
- **CONTINUE**: Keep current course with minor adjustments
- **PIVOT**: Make major strategy change (explain what and why)
- **CONCLUDE**: We've gone as far as we can (justify thoroughly)

### 6. Predictions and Insights

- What do you predict for the next period?
- What insights are worth archiving for blog content?
- Have we encountered any paradoxes worth documenting?

## Output Format

```yaml
meta_reflection:
  iteration_range: [{start}, {end}]
  timestamp: "..."
  
  progress:
    primitives_added: X
    primitives_rejected: Y
    acceptance_rate: Z%
    coverage_before: A%
    coverage_after: B%
    assessment: "..."
    
  patterns_observed:
    - pattern: "..."
      frequency: N
      implications: "..."
      
  strategy_assessment:
    proposer_effectiveness: 1-5
    proposer_notes: "..."
    critic_calibration: too_strict/balanced/too_lenient
    critic_notes: "..."
    domain_coverage_balance: "..."
    
  philosophical_observations:
    assumptions_identified:
      - assumption: "..."
        problematic: true/false
        mitigation: "..."
    tradition_bias: "..."
    leibniz_alignment: 1-5
    leibniz_notes: "..."
    
  course_corrections:
    strategy_adjustments:
      - component: PROPOSER/CRITIC/REFINER
        adjustment: "..."
        rationale: "..."
    domain_priorities: [...]
    criterion_calibration: "..."
    new_approaches: [...]
    
  decision: CONTINUE/PIVOT/CONCLUDE
  decision_justification: "..."
  
  predictions:
    - prediction: "..."
      confidence: 0.0-1.0
      
  insights_for_archive:
    - insight: "..."
      category: philosophical/methodological/substantive
      
  paradoxes_encountered:
    - paradox: "..."
      status: open/resolved
      notes: "..."
```

Reflect now.
```

---

## 7. Iteration Handoff Protocol

### 7.1 End of Session Handoff

When the agent must pause (context limits, user intervention, etc.):

```yaml
# Generate this at end of session
session_handoff:
  session_id: "..."
  ended_at: datetime
  
  state_snapshot:
    iteration: N
    phase: "..."
    cycle: M
    
  in_progress:
    current_task: "..."
    current_candidate: "..." or null
    pending_evaluations: [...]
    
  must_do_next:
    - "Read reasoning/iteration_state.yaml"
    - "Read last 3 iteration logs"
    - "Continue with {specific_task}"
    
  context_critical:
    - "We're in the middle of evaluating CAUSATION"
    - "Recent rejections suggest we're being too strict"
    - "META-REASONER suggested focusing on mind domain"
```

### 7.2 Session Resume Protocol

When starting a new session:

```markdown
## RESUME PROTOCOL

1. Read `reasoning/iteration_state.yaml`
2. Check for `session_handoff.yaml` - if exists, read it
3. Read last 3 iteration logs
4. Read latest meta-reflection
5. Read alphabet index
6. Summarize current state
7. Determine next action
8. Continue the loop
```

### 7.3 Checkpoint Frequency

Create checkpoints:
- After each complete iteration
- After each phase transition
- Before and after META-REFLECTION
- When significant changes occur (>3 primitives added)

---

## Summary

The Agent Loop is designed to:

1. **Keep the agent going** until meaningful stopping conditions are met
2. **Structure progress** through well-defined phases
3. **Enable reflection** at regular intervals
4. **Persist everything** for transparency and recovery
5. **Support resumption** after any interruption

The agent is not done until:
- Coverage reaches 90%+, OR
- The alphabet stabilizes, OR
- Diminishing returns with no pivot available, OR
- A fundamental limit is reached

**The reasoning is the artifact. Log everything.**
