# Validation Framework

## Testing and Validating the Alphabet of Human Thought

**Version:** 1.0.0  
**Last Updated:** 2024-03-15  
**Status:** Canonical Reference

---

## Table of Contents

1. [Validation Philosophy](#1-validation-philosophy)
2. [Internal Consistency Checks](#2-internal-consistency-checks)
3. [Coverage Testing](#3-coverage-testing)
4. [Comparative Validation](#4-comparative-validation)
5. [Continuous Validation](#5-continuous-validation)
6. [Benchmark Concepts](#6-benchmark-concepts)
7. [Evaluation Rubrics](#7-evaluation-rubrics)
8. [Implementation](#8-implementation)

---

## 1. Validation Philosophy

### 1.1 What Are We Validating?

The alphabet must be validated on multiple dimensions:

| Dimension | Question | Validation Approach |
|-----------|----------|---------------------|
| **Primitiveness** | Are the primitives truly irreducible? | Decomposition attacks |
| **Consistency** | Is the alphabet internally coherent? | Circularity & contrast checks |
| **Coverage** | Can we express complex concepts? | Benchmark testing |
| **Completeness** | Are there major gaps? | Domain coverage analysis |
| **Composability** | Does the calculus work? | Composition validation |

### 1.2 Validation Is Ongoing

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    VALIDATION INTEGRATION                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  EVERY ITERATION:                                                       │
│  ├── CRITIC validates each candidate                                    │
│  └── Quick consistency check on alphabet                                │
│                                                                         │
│  EVERY N ITERATIONS:                                                    │
│  ├── Full consistency suite                                             │
│  ├── Coverage testing against benchmarks                                │
│  └── Domain balance analysis                                            │
│                                                                         │
│  EVERY META-REFLECTION:                                                 │
│  ├── Comparative analysis (vs. other ontologies)                        │
│  ├── Progress toward goals                                              │
│  └── Methodology assessment                                             │
│                                                                         │
│  ON TERMINATION:                                                        │
│  ├── Full validation suite                                              │
│  ├── Final report with all metrics                                      │
│  └── Recommendations for future work                                    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 1.3 Validation Outputs

All validation produces:

1. **Structured reports** (YAML) for automated processing
2. **Narrative reports** (Markdown) for human review
3. **Metrics** for tracking progress
4. **Issues** flagged for resolution

---

## 2. Internal Consistency Checks

### 2.1 Circularity Detection

**Goal**: Ensure no primitive is defined in terms of itself.

**Method**: Build a dependency graph and check for cycles.

```python
def check_circularity(alphabet: list[PrimitiveDetailed]) -> CircularityReport:
    """
    Check for circular definitions.
    
    A definition is circular if:
    - It directly uses the term being defined
    - It uses a term that eventually depends on the defined term
    """
    import networkx as nx
    
    # Build dependency graph
    G = nx.DiGraph()
    for primitive in alphabet:
        G.add_node(primitive.id)
        # Add edges for concepts used in definition
        for dep in extract_dependencies(primitive.definition.informal):
            if dep in [p.id for p in alphabet]:
                G.add_edge(primitive.id, dep)
    
    # Find cycles
    cycles = list(nx.simple_cycles(G))
    
    return CircularityReport(
        has_cycles=len(cycles) > 0,
        cycles=cycles,
        graph=G
    )
```

**Report format**:

```yaml
# validation/consistency/circularity_report.yaml

circularity_report:
  timestamp: datetime
  iteration: int
  
  status: pass | warning | fail
  
  cycles_found:
    - cycle: [PRM_0012, PRM_0015, PRM_0012]
      severity: critical
      description: "CAUSATION defined using EFFECT, which uses CAUSATION"
      
  dependency_depth:
    max: 5
    average: 2.3
    
  recommendations:
    - "Review PRM_0012 definition to break circular dependency"
```

### 2.2 Redundancy Detection

**Goal**: Ensure no primitive can be expressed as a composition of others.

**Method**: For each primitive, attempt to express it using all other primitives.

```python
def check_redundancy(alphabet: list[PrimitiveDetailed], calculus: Calculus) -> RedundancyReport:
    """
    Check for redundant primitives.
    
    A primitive is redundant if it can be expressed as a composition
    of other primitives in the alphabet.
    """
    redundancies = []
    
    for primitive in alphabet:
        # Try to express this primitive using others
        others = [p for p in alphabet if p.id != primitive.id]
        
        for subset in powerset(others):
            if len(subset) < 2:
                continue
            
            composition = calculus.compose(*[p.label for p in subset])
            
            if is_equivalent(primitive, composition):
                redundancies.append({
                    "primitive": primitive.id,
                    "expressible_as": [p.id for p in subset],
                    "confidence": calculate_equivalence_confidence(primitive, composition)
                })
                break
    
    return RedundancyReport(
        has_redundancies=len(redundancies) > 0,
        redundancies=redundancies
    )
```

### 2.3 Contrast Consistency

**Goal**: Ensure contrasting primitives are truly mutually exclusive.

```python
def check_contrast_consistency(
    alphabet: list[PrimitiveDetailed], 
    contrasts: list[tuple[str, str]]
) -> ContrastReport:
    """
    Verify that declared contrasts are valid.
    
    Two primitives P and Q are validly contrasted if:
    - No entity can be both P and Q
    - There's no context where both apply
    """
    issues = []
    
    for p1_id, p2_id in contrasts:
        p1 = get_primitive(p1_id, alphabet)
        p2 = get_primitive(p2_id, alphabet)
        
        # Check if there's any overlap in ostensive examples
        overlap = set(p1.definition.ostensive) & set(p2.definition.ostensive)
        if overlap:
            issues.append({
                "primitives": [p1_id, p2_id],
                "issue": "overlapping_examples",
                "overlap": list(overlap)
            })
        
        # Check if definitions allow coexistence
        if not are_mutually_exclusive(p1.definition.informal, p2.definition.informal):
            issues.append({
                "primitives": [p1_id, p2_id],
                "issue": "definitions_not_exclusive",
                "note": "Definitions may allow coexistence"
            })
    
    return ContrastReport(issues=issues)
```

### 2.4 Presupposition Validity

**Goal**: Ensure presupposition chains are valid.

```python
def check_presuppositions(
    alphabet: list[PrimitiveDetailed],
    presuppositions: list[dict]
) -> PresuppositionReport:
    """
    Verify presupposition relationships.
    
    If P presupposes Q, then:
    - Q must exist in the alphabet
    - Q must be "more fundamental" than P
    - There should be no cycles
    """
    issues = []
    
    for presup in presuppositions:
        source = presup["source"]
        targets = presup.get("requires", [])
        
        for target in targets:
            # Check target exists
            if target not in [p.id for p in alphabet]:
                issues.append({
                    "source": source,
                    "target": target,
                    "issue": "missing_target",
                    "description": f"{source} presupposes {target}, but {target} not in alphabet"
                })
            
            # Check no reverse presupposition (would create cycle)
            if has_presupposition(target, source, presuppositions):
                issues.append({
                    "source": source,
                    "target": target,
                    "issue": "circular_presupposition"
                })
    
    return PresuppositionReport(issues=issues)
```

### 2.5 Consolidated Consistency Check

```yaml
# validation/consistency/report.yaml

consistency_report:
  timestamp: datetime
  iteration: int
  
  overall_score: 0.95  # 0-1
  status: pass | warning | fail
  
  checks:
    circularity:
      status: pass
      cycles_found: 0
      
    redundancy:
      status: warning
      redundancies_found: 1
      details:
        - primitive: PRM_0045
          might_be_expressible_as: [PRM_0012, PRM_0023]
          confidence: 0.7
          
    contrast:
      status: pass
      issues_found: 0
      
    presupposition:
      status: pass
      missing_targets: 0
      
  recommendations:
    - "Review PRM_0045 for potential redundancy"
```

---

## 3. Coverage Testing

### 3.1 Benchmark Concept Decomposition

**Goal**: Test if the alphabet can express complex concepts.

**Method**: Take benchmark concepts and attempt to decompose them.

```python
def test_coverage(
    alphabet: list[PrimitiveDetailed],
    calculus: Calculus,
    benchmarks: list[BenchmarkConcept]
) -> CoverageReport:
    """
    Test coverage against benchmark concepts.
    """
    results = []
    
    for benchmark in benchmarks:
        result = attempt_decomposition(benchmark, alphabet, calculus)
        results.append({
            "concept": benchmark.name,
            "domain": benchmark.domain,
            "status": result.status,  # expressible | partial | inexpressible
            "decomposition": result.decomposition,
            "missing_primitives": result.missing,
            "confidence": result.confidence
        })
    
    # Calculate metrics
    expressible = sum(1 for r in results if r["status"] == "expressible")
    partial = sum(1 for r in results if r["status"] == "partial")
    inexpressible = sum(1 for r in results if r["status"] == "inexpressible")
    
    return CoverageReport(
        total=len(benchmarks),
        expressible=expressible,
        partial=partial,
        inexpressible=inexpressible,
        coverage_score=expressible / len(benchmarks),
        details=results
    )
```

### 3.2 Domain Coverage Analysis

**Goal**: Ensure all conceptual domains are represented.

```python
def analyze_domain_coverage(
    alphabet: list[PrimitiveDetailed],
    expected_domains: list[str]
) -> DomainCoverageReport:
    """
    Analyze how well each domain is covered.
    """
    coverage = {}
    
    for domain in expected_domains:
        primitives_in_domain = [p for p in alphabet if p.domain_primary.value == domain]
        coverage[domain] = {
            "count": len(primitives_in_domain),
            "primitives": [p.id for p in primitives_in_domain],
            "status": "adequate" if len(primitives_in_domain) >= 3 else "sparse"
        }
    
    # Identify neglected domains
    neglected = [d for d, v in coverage.items() if v["count"] == 0]
    sparse = [d for d, v in coverage.items() if 0 < v["count"] < 3]
    
    return DomainCoverageReport(
        coverage=coverage,
        neglected_domains=neglected,
        sparse_domains=sparse
    )
```

### 3.3 Gap Identification

**Goal**: Identify what primitives are missing.

```python
def identify_gaps(
    coverage_results: list[dict],
    alphabet: list[PrimitiveDetailed]
) -> list[Gap]:
    """
    Identify primitives that would help express inexpressible concepts.
    """
    # Collect all missing primitives across failed decompositions
    missing_counts = {}
    
    for result in coverage_results:
        if result["status"] != "expressible":
            for missing in result["missing_primitives"]:
                if missing not in missing_counts:
                    missing_counts[missing] = {
                        "label": missing,
                        "count": 0,
                        "concepts_needing": []
                    }
                missing_counts[missing]["count"] += 1
                missing_counts[missing]["concepts_needing"].append(result["concept"])
    
    # Sort by frequency
    gaps = sorted(missing_counts.values(), key=lambda x: x["count"], reverse=True)
    
    return [Gap(**g) for g in gaps]
```

---

## 4. Comparative Validation

### 4.1 Comparison with Other Ontologies

**Goal**: See how our alphabet relates to established ontologies.

#### 4.1.1 vs. Anna Wierzbicka's Semantic Primes (NSM)

```yaml
# validation/comparisons/vs_nsm_primes.yaml

comparison:
  source: "Natural Semantic Metalanguage (NSM)"
  author: "Wierzbicka et al."
  nsm_primes_count: 65
  
  mappings:
    exact_match:
      - nsm: "I"
        our: "self"
        notes: "Direct correspondence"
        
      - nsm: "SOMETHING"
        our: "thing"
        notes: "Direct correspondence"
        
    partial_match:
      - nsm: "GOOD"
        our: "value_positive"
        notes: "Our concept is more abstract"
        
    no_match_nsm_has:
      - nsm: "WORDS"
        notes: "We treat language as derived, not primitive"
        
    no_match_we_have:
      - our: "causation"
        notes: "NSM doesn't have explicit causation primitive"
        
  summary:
    exact_matches: 23
    partial_matches: 18
    only_in_nsm: 24
    only_in_ours: 35
    
  analysis: |
    Our alphabet is more metaphysical/philosophical, while NSM
    is more linguistic/practical. NSM includes more social/
    communicative primitives; we include more abstract metaphysical
    ones.
```

#### 4.1.2 vs. Aristotle's Categories

```yaml
comparison:
  source: "Aristotle's Categories"
  
  aristotle_categories:
    - substance
    - quantity
    - quality
    - relation
    - place
    - time
    - position
    - state
    - action
    - passion
    
  mappings:
    - aristotle: "substance"
      our: ["thing", "existence"]
      
    - aristotle: "quantity"
      our: ["number", "magnitude", "plurality"]
      
    # ... etc
```

#### 4.1.3 vs. Cyc Upper Ontology

Compare against the Cyc project's upper-level concepts.

#### 4.1.4 vs. WordNet Top Synsets

Compare against WordNet's highest-level synsets.

### 4.2 Comparison Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| **Coverage overlap** | What % of our primitives map to theirs? | >60% |
| **Unique primitives** | What do we have that they don't? | Document |
| **Missing primitives** | What do they have that we don't? | Investigate |
| **Structural similarity** | How similar are the relationship structures? | Qualitative |

---

## 5. Continuous Validation

### 5.1 Validation Triggers

| Trigger | Validation Actions |
|---------|-------------------|
| Primitive added | Quick consistency check, update coverage estimate |
| Primitive revised | Re-check affected relationships |
| Every 10 iterations | Full consistency suite, coverage testing |
| Meta-reflection | Comparative analysis, methodology review |
| Termination | Complete validation, final report |

### 5.2 Automated Validation Pipeline

```python
class ValidationPipeline:
    """Automated validation for ALPHABETUM."""
    
    def __init__(self, base_path: Path, config: dict):
        self.base_path = base_path
        self.config = config
        self.state_manager = StateManager(base_path)
    
    def run_quick_check(self) -> QuickCheckResult:
        """Run after each primitive change."""
        alphabet = self.state_manager.load_alphabet_index()
        
        # Fast circularity check (just new additions)
        circularity = quick_circularity_check(alphabet[-5:], alphabet)
        
        # Fast redundancy check
        redundancy = quick_redundancy_check(alphabet[-5:], alphabet)
        
        return QuickCheckResult(
            circularity=circularity,
            redundancy=redundancy,
            passed=circularity.passed and redundancy.passed
        )
    
    def run_full_suite(self) -> FullValidationResult:
        """Run full validation suite."""
        alphabet = self.state_manager.load_full_alphabet()
        relationships = self.state_manager.load_relationships()
        benchmarks = self.load_benchmarks()
        
        results = {
            "circularity": check_circularity(alphabet),
            "redundancy": check_redundancy(alphabet, self.calculus),
            "contrast": check_contrast_consistency(alphabet, relationships.contrasts),
            "presupposition": check_presuppositions(alphabet, relationships.presupposes),
            "coverage": test_coverage(alphabet, self.calculus, benchmarks),
            "domain_coverage": analyze_domain_coverage(alphabet, EXPECTED_DOMAINS),
        }
        
        # Calculate overall score
        scores = [
            1.0 if results["circularity"].passed else 0.0,
            1.0 if results["redundancy"].passed else 0.5,
            1.0 if results["contrast"].passed else 0.5,
            1.0 if results["presupposition"].passed else 0.5,
            results["coverage"].coverage_score,
        ]
        
        overall_score = sum(scores) / len(scores)
        
        return FullValidationResult(
            results=results,
            overall_score=overall_score,
            passed=overall_score >= 0.7
        )
```

### 5.3 Validation Reports

Generate reports in both YAML (for automation) and Markdown (for humans):

```markdown
<!-- validation/consistency/report.md -->

# Validation Report: Iteration 42

**Generated:** 2024-03-15T14:32:07Z  
**Overall Score:** 0.87 / 1.00  
**Status:** ✅ PASS

## Summary

| Check | Status | Score |
|-------|--------|-------|
| Circularity | ✅ Pass | 1.00 |
| Redundancy | ⚠️ Warning | 0.85 |
| Contrast Consistency | ✅ Pass | 1.00 |
| Presuppositions | ✅ Pass | 1.00 |
| Coverage | ℹ️ Progress | 0.72 |

## Details

### Circularity Check ✅

No circular definitions detected in the alphabet.

Dependency graph depth:
- Maximum: 4 levels
- Average: 2.1 levels

### Redundancy Check ⚠️

One potential redundancy flagged:

- **PRM_0045 (succession)** might be expressible as:
  - `TIME ∧ ORDER`
  - Confidence: 70%
  - Recommendation: Review during next CONSOLIDATION phase

### Coverage Testing

- **Total benchmarks:** 100
- **Expressible:** 72
- **Partial:** 18
- **Inexpressible:** 10

Top gaps identified:
1. `desert` - needed by 5 concepts
2. `social_contract` - needed by 4 concepts
3. `intentionality` - needed by 3 concepts

## Recommendations

1. Investigate PRM_0045 redundancy claim
2. Prioritize `desert` as next primitive candidate
3. Focus PROPOSER on ethics/social domains

---
*Report generated by ALPHABETUM Validation Pipeline*
```

---

## 6. Benchmark Concepts

### 6.1 Benchmark Selection Criteria

Benchmarks should be:

| Criterion | Description |
|-----------|-------------|
| **Diverse** | Cover all major domains |
| **Varied complexity** | Simple to highly complex |
| **Well-defined** | Clear meaning |
| **Philosophically interesting** | Represent important concepts |
| **Cross-cultural** | Not culturally specific |

### 6.2 Benchmark Set

```yaml
# validation/benchmarks/test_concepts.yaml

benchmark_concepts:
  version: "1.0.0"
  
  # === METAPHYSICS ===
  - id: BM_001
    name: "change"
    domain: metaphysics
    complexity: medium
    decomposition_hints: [thing, time, state, difference]
    
  - id: BM_002
    name: "identity"
    domain: metaphysics
    complexity: simple
    decomposition_hints: [same, one]
    note: "May be primitive itself"
    
  - id: BM_003
    name: "possibility"
    domain: metaphysics
    complexity: high
    decomposition_hints: [existence, negation, world]
    
  # === EPISTEMOLOGY ===
  - id: BM_010
    name: "knowledge"
    domain: epistemology
    complexity: high
    decomposition_hints: [belief, truth, justification]
    
  - id: BM_011
    name: "belief"
    domain: epistemology
    complexity: medium
    decomposition_hints: [mind, proposition, attitude]
    
  - id: BM_012
    name: "truth"
    domain: epistemology
    complexity: high
    decomposition_hints: [proposition, correspondence, reality]
    
  # === ETHICS ===
  - id: BM_020
    name: "justice"
    domain: ethics
    complexity: high
    decomposition_hints: [fairness, desert, rights, social]
    
  - id: BM_021
    name: "duty"
    domain: ethics
    complexity: medium
    decomposition_hints: [obligation, action, moral]
    
  - id: BM_022
    name: "virtue"
    domain: ethics
    complexity: high
    decomposition_hints: [character, good, disposition]
    
  # === MIND ===
  - id: BM_030
    name: "consciousness"
    domain: mind
    complexity: high
    decomposition_hints: [awareness, experience, self]
    note: "May be primitive itself"
    
  - id: BM_031
    name: "intention"
    domain: mind
    complexity: medium
    decomposition_hints: [mind, goal, action, future]
    
  - id: BM_032
    name: "emotion"
    domain: mind
    complexity: medium
    decomposition_hints: [feeling, body, evaluation]
    
  # === SOCIAL ===
  - id: BM_040
    name: "promise"
    domain: social
    complexity: medium
    decomposition_hints: [speech, future, obligation]
    
  - id: BM_041
    name: "institution"
    domain: social
    complexity: high
    decomposition_hints: [group, rules, persistent, social]
    
  # === PHYSICAL ===
  - id: BM_050
    name: "motion"
    domain: physical
    complexity: simple
    decomposition_hints: [space, time, change, thing]
    
  - id: BM_051
    name: "force"
    domain: physical
    complexity: medium
    decomposition_hints: [causation, motion, interaction]
    
  # === EVERYDAY ===
  - id: BM_060
    name: "tool"
    domain: everyday
    complexity: simple
    decomposition_hints: [thing, purpose, use]
    
  - id: BM_061
    name: "gift"
    domain: everyday
    complexity: medium
    decomposition_hints: [thing, transfer, voluntary, social]
    
  - id: BM_062
    name: "game"
    domain: everyday
    complexity: medium
    decomposition_hints: [activity, rules, play, competition]
```

### 6.3 Decomposition Protocol

When testing if a benchmark is expressible:

```python
def attempt_decomposition(
    benchmark: BenchmarkConcept,
    alphabet: list[PrimitiveDetailed],
    calculus: Calculus
) -> DecompositionResult:
    """
    Attempt to decompose a benchmark concept.
    
    Protocol:
    1. Try systematic decomposition using calculus
    2. If that fails, try heuristic decomposition
    3. If that fails, identify what's missing
    """
    # Step 1: Direct composition attempt
    if benchmark.decomposition_hints:
        try:
            result = calculus.compose(*benchmark.decomposition_hints)
            if validate_composition(result, benchmark):
                return DecompositionResult(
                    status="expressible",
                    decomposition=benchmark.decomposition_hints,
                    confidence=0.9
                )
        except:
            pass
    
    # Step 2: Search for composition
    for subset in powerset(alphabet, max_size=6):
        composition = calculus.compose(*[p.label for p in subset])
        if matches_benchmark(composition, benchmark):
            return DecompositionResult(
                status="expressible",
                decomposition=[p.label for p in subset],
                confidence=0.8
            )
    
    # Step 3: Partial match
    partial_components = find_partial_components(benchmark, alphabet)
    if partial_components:
        missing = identify_missing(benchmark, partial_components)
        return DecompositionResult(
            status="partial",
            decomposition=partial_components,
            missing=missing,
            confidence=0.5
        )
    
    # Step 4: Cannot express
    return DecompositionResult(
        status="inexpressible",
        missing=benchmark.decomposition_hints or ["unknown"],
        confidence=0.9
    )
```

---

## 7. Evaluation Rubrics

### 7.1 Alphabet Quality Rubric

For human evaluators assessing the final alphabet:

| Dimension | 1 (Poor) | 3 (Adequate) | 5 (Excellent) |
|-----------|----------|--------------|---------------|
| **Primitiveness** | Many can be decomposed | Some questionable | All resist decomposition |
| **Coverage** | Major gaps in important domains | Most domains covered | Comprehensive coverage |
| **Consistency** | Circular definitions present | Minor inconsistencies | Fully coherent |
| **Composability** | Composition rules unclear | Works for simple cases | Elegant, general calculus |
| **Documentation** | Sparse reasoning logs | Adequate documentation | Exceptional reasoning archive |
| **Novelty** | Merely rehashes existing work | Some new insights | Genuine philosophical contributions |
| **Leibniz Alignment** | Diverges from original vision | Generally aligned | True to spirit with improvements |

### 7.2 Primitive Quality Rubric

For evaluating individual primitives:

| Criterion | Weight | 1 (Weak) | 3 (Moderate) | 5 (Strong) |
|-----------|--------|----------|--------------|------------|
| **Decomposition resistance** | 30% | Easily decomposed | Resists some attacks | Resists all attacks |
| **Universality** | 20% | Culture-specific | Near-universal | Truly universal |
| **Clarity** | 15% | Vague, ambiguous | Reasonably clear | Precisely defined |
| **Usefulness** | 15% | Rarely needed | Sometimes needed | Essential for many concepts |
| **Independence** | 10% | Overlaps with others | Minor overlap | Fully independent |
| **Justification** | 10% | Weak argument | Reasonable support | Compelling case |

### 7.3 Calculus Quality Rubric

| Criterion | 1 (Poor) | 3 (Adequate) | 5 (Excellent) |
|-----------|----------|--------------|---------------|
| **Expressiveness** | Can't compose many concepts | Most concepts expressible | Arbitrary concepts expressible |
| **Precision** | Ambiguous compositions | Mostly unambiguous | Fully deterministic |
| **Parsimony** | Many redundant operators | Some redundancy | Minimal, elegant |
| **Reversibility** | Can't reliably decompose | Decomposition mostly works | Perfect decomposition |
| **Validation** | No well-formedness checks | Basic checks | Comprehensive validation |

---

## 8. Implementation

### 8.1 Validation Module

**`src/alphabetum/validation/checker.py`**:

```python
"""Validation checks for the alphabet."""

from dataclasses import dataclass
from pathlib import Path
import yaml

from ..state.manager import StateManager
from ..state.models import PrimitiveDetailed


@dataclass
class ValidationResult:
    passed: bool
    score: float
    issues: list[dict]
    recommendations: list[str]


class AlphabetValidator:
    """Main validation class for ALPHABETUM."""
    
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.state_manager = StateManager(base_path)
    
    def run_full_validation(self) -> dict[str, ValidationResult]:
        """Run all validation checks."""
        alphabet = self.state_manager.load_full_alphabet()
        relationships = self.state_manager.load_relationships()
        
        results = {}
        
        # Consistency checks
        results["circularity"] = self.check_circularity(alphabet)
        results["redundancy"] = self.check_redundancy(alphabet)
        results["contrast"] = self.check_contrasts(alphabet, relationships)
        results["presupposition"] = self.check_presuppositions(alphabet, relationships)
        
        # Coverage checks
        benchmarks = self.load_benchmarks()
        results["coverage"] = self.check_coverage(alphabet, benchmarks)
        results["domain_balance"] = self.check_domain_balance(alphabet)
        
        return results
    
    def check_circularity(self, alphabet: list[PrimitiveDetailed]) -> ValidationResult:
        """Check for circular definitions."""
        # Implementation as shown earlier
        pass
    
    def check_redundancy(self, alphabet: list[PrimitiveDetailed]) -> ValidationResult:
        """Check for redundant primitives."""
        pass
    
    def check_contrasts(self, alphabet, relationships) -> ValidationResult:
        """Check contrast consistency."""
        pass
    
    def check_presuppositions(self, alphabet, relationships) -> ValidationResult:
        """Check presupposition validity."""
        pass
    
    def check_coverage(self, alphabet, benchmarks) -> ValidationResult:
        """Check coverage against benchmarks."""
        pass
    
    def check_domain_balance(self, alphabet) -> ValidationResult:
        """Check domain coverage balance."""
        pass
    
    def load_benchmarks(self) -> list:
        """Load benchmark concepts."""
        benchmarks_file = self.base_path / "validation" / "benchmarks" / "test_concepts.yaml"
        with open(benchmarks_file) as f:
            data = yaml.safe_load(f)
        return data["benchmark_concepts"]
    
    def generate_report(
        self, 
        results: dict[str, ValidationResult],
        iteration: int
    ) -> tuple[dict, str]:
        """Generate validation report in YAML and Markdown."""
        # Generate YAML report
        yaml_report = {
            "validation_report": {
                "iteration": iteration,
                "overall_passed": all(r.passed for r in results.values()),
                "overall_score": sum(r.score for r in results.values()) / len(results),
                "checks": {
                    name: {
                        "passed": result.passed,
                        "score": result.score,
                        "issues_count": len(result.issues),
                    }
                    for name, result in results.items()
                }
            }
        }
        
        # Generate Markdown report
        md_lines = [
            f"# Validation Report: Iteration {iteration}",
            "",
            f"**Overall Score:** {yaml_report['validation_report']['overall_score']:.2f}",
            "",
            "## Results",
            "",
        ]
        
        for name, result in results.items():
            status = "✅" if result.passed else "❌"
            md_lines.append(f"### {name.title()} {status}")
            md_lines.append(f"Score: {result.score:.2f}")
            if result.issues:
                md_lines.append("Issues:")
                for issue in result.issues[:3]:  # Top 3
                    md_lines.append(f"- {issue}")
            md_lines.append("")
        
        return yaml_report, "\n".join(md_lines)
```

### 8.2 CLI Interface

**`tools/validate.py`**:

```python
"""CLI for running validation."""

import typer
from pathlib import Path

from src.alphabetum.validation.checker import AlphabetValidator


app = typer.Typer()


@app.command()
def full(
    path: Path = typer.Option(".", help="Path to alphabet repository")
):
    """Run full validation suite."""
    validator = AlphabetValidator(path)
    results = validator.run_full_validation()
    
    yaml_report, md_report = validator.generate_report(
        results,
        iteration=validator.state_manager.load_iteration_state().current_iteration
    )
    
    # Print Markdown report
    print(md_report)
    
    # Save reports
    # ...


@app.command()
def quick(
    path: Path = typer.Option(".", help="Path to alphabet repository")
):
    """Run quick consistency check."""
    validator = AlphabetValidator(path)
    result = validator.run_quick_check()
    
    if result.passed:
        print("✅ Quick check passed")
    else:
        print("❌ Issues found:")
        for issue in result.issues:
            print(f"  - {issue}")


@app.command()
def coverage(
    path: Path = typer.Option(".", help="Path to alphabet repository")
):
    """Check coverage against benchmarks."""
    validator = AlphabetValidator(path)
    result = validator.check_coverage_only()
    
    print(f"Coverage: {result.coverage_score:.1%}")
    print(f"Expressible: {result.expressible}/{result.total}")
    
    if result.gaps:
        print("\nTop gaps:")
        for gap in result.gaps[:5]:
            print(f"  - {gap.label} (needed by {gap.count} concepts)")


if __name__ == "__main__":
    app()
```

---

## Summary

The Validation Framework ensures that the alphabet is:

1. **Internally consistent**: No circularity, redundancy, or invalid relationships
2. **Externally valid**: Can express complex concepts from benchmarks
3. **Comprehensively documented**: All validation produces detailed reports
4. **Continuously monitored**: Validation runs at appropriate intervals
5. **Comparable**: Maps to other established ontologies

Validation is not a one-time check but an **ongoing process** integrated into every phase of the ALPHABETUM loop.

> *"The true test of an alphabet is not its elegance, but whether it can spell the words of human thought."*
