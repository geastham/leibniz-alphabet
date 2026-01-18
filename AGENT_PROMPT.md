# Leibniz Alphabet: Agent Iteration Prompt

You are executing an iteration of **Project Alphabetum** - an attempt to reconstruct Leibniz's Alphabet of Human Thought using AI-assisted philosophical reasoning.

## Quick Start

Run one complete iteration by acting as all four roles in sequence:

```bash
# 1. Check current state
python tools/session_runner.py --status

# 2. Generate PROPOSER prompt (read it, then act as PROPOSER)
python tools/session_runner.py --phase proposer --output-prompt -n 3
```

## Project Overview

The goal is to discover **primitive concepts** - irreducible, simple ideas that cannot be broken down further and from which ALL complex concepts can be composed.

### The Framework

Each iteration cycles through **four phases**:

1. **PROPOSER**: Generate 3 candidate primitive concepts
2. **CRITIC**: Rigorously evaluate each candidate (ACCEPT/REJECT/REFINE)
3. **REFINER**: Integrate accepted primitives into the alphabet
4. **Update State**: Save all results and advance iteration

### Current Alphabet

Read the current state:
```bash
cat alphabet/primitives/index.yaml
cat reasoning/iteration_state.yaml
```

## Your Task: Execute One Iteration

### Phase 1: PROPOSER

Generate 3 candidate primitives. Output valid YAML:

```yaml
candidates:
  - label: "concept_name"
    domain: "being|relation|time|space|mind|quality|quantity|ethics|..."
    proposed_symbol: "unicode symbol"
    informal_definition: "what this concept means"
    ostensive_examples:
      - "example 1"
      - "example 2"
    negative_examples:
      - "what this is NOT"
    primitiveness_argument: "why this cannot be decomposed"
    decomposition_resistance: "what happens when you try to break it down"
    relevance_to_gaps: "what expressiveness this adds"
    confidence: 0.7
```

Save with:
```bash
python tools/session_runner.py --save-candidates "YOUR_YAML_HERE"
```

### Phase 2: CRITIC

For each candidate, apply the **six attacks**:

1. **DECOMPOSITION**: Can it be broken into simpler parts?
2. **CIRCULARITY**: Does the definition presuppose itself?
3. **REDUNDANCY**: Can it be expressed from existing primitives?
4. **EDGE CASES**: Where does the meaning shift or fail?
5. **CULTURAL VARIANCE**: Is it truly universal?
6. **PARSIMONY**: Do we really need it?

Output valid YAML with verdict (ACCEPT/REJECT/REFINE):

```yaml
evaluation:
  candidate_label: "name"
  decomposition:
    attempts:
      - approach: "analytic"
        attempt: "what you tried"
        result: "outcome"
        survived: true/false
    survived: true/false
    notes: "summary"
  circularity:
    concepts_traced: ["concept1", "concept2"]
    survived: true
    notes: "summary"
  redundancy:
    can_be_expressed: false
    using_primitives: null
    notes: "summary"
  edge_cases:
    cases_found:
      - case: "description"
        severity: "low/medium/high"
    overall_severity: "low"
  cultural_variance:
    evidence_for_universality: ["evidence"]
    assessment: "universal"
  parsimony:
    expressiveness_value: "essential/high/medium/low"
    necessary: true/false
  verdict: "ACCEPT"
  confidence: 0.8
  reasoning_summary: "overall reasoning"
  key_insight: "what we learned"
```

Save each evaluation:
```bash
python tools/session_runner.py --save-evaluation "YOUR_YAML" --candidate-id "CAND_XXX_YY"
```

### Phase 3: REFINER

For each ACCEPTED candidate, create a primitive entry:

```yaml
primitive:
  id: "P0XX"
  label: "concept_name"
  domain: "domain"
  symbol: "symbol"
  prime_number: NEXT_PRIME
  definition:
    informal: "refined definition"
    formal: null
  examples:
    ostensive: ["example1", "example2"]
    negative: ["not this"]
  relationships:
    contrasts_with: []
    presupposes: ["P001"]
    composes_well_with: []
  confidence: 0.85
  status: "stable"
  notes: "observations"
```

Save with:
```bash
python tools/session_runner.py --save-primitive "YOUR_YAML"
```

### Phase 4: Finalize

1. Fix the index file if needed (it may have duplicate sections)
2. Update `reasoning/iteration_state.yaml` with:
   - Increment `current_iteration`
   - Clear `pending.candidates_to_evaluate`
   - Add any new `derived_concepts` discovered
   - Update `gaps_to_fill` based on insights
   - Update `history` counts

3. Write narrative log to `reasoning/logs/iteration_XXX/narrative.md`

4. Commit and push:
```bash
git add -A
git commit -m "Execute iteration X: [summary of what was added/rejected]"
git push
```

## Key Principles

### What Makes a Good Primitive

1. **Irreducible**: Cannot be defined without circularity
2. **Universal**: Applies across all cultures and contexts
3. **Necessary**: Required to express important concepts
4. **Independent**: Not redundant with existing primitives

### Productive Rejections

When a candidate is REJECTED because it's **derivable**, that's a SUCCESS! It shows:
- Our existing primitives are powerful
- We've identified a derived concept
- Add it to the `derived_concepts` list

Examples of derived concepts:
- Difference = negation(identity)
- Necessity = negation(possibility(negation))
- Causation = succession + counterfactual
- Agency = intentionality + causation
- Truth = intentionality + existence
- Valence = quality + normativity

### Signs of Approaching Completeness

- Declining acceptance rate (more candidates derivable)
- Fewer genuine gaps identified
- New candidates reduce to existing primitives

## Prime Number Assignment

Each primitive gets a unique prime:
- P001: 2, P002: 3, P003: 5, P004: 7, P005: 11
- P006: 13, P007: 17, P008: 19, P009: 23, P010: 29
- P011: 31, P012: 37, P013: 41, ...

Complex concepts = products of constituent primes.

## Domains Reference

- **being**: existence, actuality, possibility
- **relation**: identity, negation, composition
- **time**: succession, duration
- **space**: adjacency, location
- **mind**: intentionality, consciousness
- **quality**: properties, characteristics
- **quantity**: magnitude, number
- **ethics**: normativity, obligation
- **knowledge**: truth, justification
- **action**: agency, doing
- **emotion**: valence, affect
- **social**: collective, shared
- **language**: meaning, reference

---

## Example Iteration Flow

```
1. Read state → "Iteration 5, 11 primitives, gaps: social, phenomenality"

2. PROPOSER generates:
   - "phenomenality" (mind domain)
   - "collectivity" (social domain)
   - "reference" (language domain)

3. CRITIC evaluates:
   - phenomenality: ACCEPT (irreducible qualia)
   - collectivity: REJECT (= composition + intentionality)
   - reference: REJECT (= intentionality toward language)

4. REFINER integrates:
   - P012: phenomenality (prime 37)

5. Update state:
   - iteration: 6
   - primitives: 12
   - new derived: collectivity, reference

6. Commit: "Execute iteration 6: Add phenomenality; derive collectivity, reference"
```

---

**Begin by checking the current state and running the PROPOSER phase.**
