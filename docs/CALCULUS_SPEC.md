# The Calculus Ratiocinator

## Specification for Composing Complex Concepts from Primitives

**Version:** 1.0.0  
**Last Updated:** 2024-03-15  
**Status:** Canonical Reference

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Leibniz's Original Vision](#2-leibnizs-original-vision)
3. [The Prime Number System](#3-the-prime-number-system)
4. [Composition Operators](#4-composition-operators)
5. [Alternative Formal Systems](#5-alternative-formal-systems)
6. [Composition Rules](#6-composition-rules)
7. [Decomposition Algorithms](#7-decomposition-algorithms)
8. [Implementation](#8-implementation)
9. [Examples](#9-examples)

---

## 1. Introduction

### 1.1 What Is the Calculus?

The **Calculus Ratiocinator** is the system by which primitive concepts are combined to form complex concepts. If the alphabet provides the letters, the calculus provides the grammar and syntax.

Leibniz envisioned a system where:

> "If controversies were to arise, there would be no more need of disputation between two philosophers than between two accountants. For it would suffice to take their pencils in their hands, to sit down to their slates, and to say to each other: **Let us calculate.**"

### 1.2 Goals

The calculus must:

1. **Compose**: Build complex concepts from primitives
2. **Decompose**: Factor complex concepts into constituent primitives
3. **Validate**: Check if compositions are well-formed
4. **Compare**: Determine if two concepts are equivalent
5. **Query**: Check if a concept contains a given primitive

### 1.3 Design Constraints

| Constraint | Rationale |
|------------|-----------|
| **Deterministic** | Same inputs → same outputs |
| **Reversible** | Composition ↔ decomposition |
| **Transparent** | Steps can be inspected |
| **Multiple Representations** | Support different formal systems |

---

## 2. Leibniz's Original Vision

### 2.1 The Characteristic Universalis

Leibniz proposed assigning each primitive concept a **prime number**. Complex concepts would be represented as **products** of these primes.

**Key insight**: Prime factorization is unique. Every composite number has exactly one factorization into primes.

```
PRIMITIVE: ANIMAL = 2
PRIMITIVE: RATIONAL = 3

COMPLEX: HUMAN = ANIMAL × RATIONAL = 2 × 3 = 6

CHECK: Does HUMAN contain ANIMAL?
       6 mod 2 = 0  ✓ Yes
       
CHECK: Does HUMAN contain IMMORTAL (= 5)?
       6 mod 5 = 1  ✗ No
```

### 2.2 Advantages

| Advantage | Explanation |
|-----------|-------------|
| **Containment checking** | Divisibility test |
| **Unique representation** | Fundamental theorem of arithmetic |
| **Composition** | Multiplication |
| **Decomposition** | Prime factorization |
| **Compatibility** | LCM of concepts |

### 2.3 Limitations

| Limitation | Our Approach |
|------------|--------------|
| **Large numbers** | Use symbolic representation alongside numeric |
| **Order doesn't matter** | For ordered composition, use sequences |
| **No negation** | Extend with signed primes or separate negation track |
| **No quantification** | Layer predicate logic on top |

---

## 3. The Prime Number System

### 3.1 Prime Assignment

Each primitive in the alphabet is assigned the **next available prime number** in sequence.

```yaml
# alphabet/primitives/index.yaml (excerpt)
primitives:
  - id: PRM_0001
    label: existence
    prime: 2
    
  - id: PRM_0002  
    label: identity
    prime: 3
    
  - id: PRM_0003
    label: difference
    prime: 5
    
  - id: PRM_0004
    label: unity
    prime: 7
    
  - id: PRM_0005
    label: plurality
    prime: 11
    
  # ... etc
```

### 3.2 Composition

To compose primitives into a complex concept:

```python
def compose(*primitive_primes: list[int]) -> int:
    """
    Compose primitives by multiplying their primes.
    
    Example:
        HUMAN = ANIMAL(2) × RATIONAL(3) = 6
    """
    result = 1
    for prime in primitive_primes:
        result *= prime
    return result
```

### 3.3 Decomposition

To decompose a complex concept into its primitives:

```python
def decompose(complex_concept: int) -> list[int]:
    """
    Decompose by prime factorization.
    
    Example:
        6 → [2, 3] → [ANIMAL, RATIONAL]
    """
    factors = []
    n = complex_concept
    divisor = 2
    
    while n > 1:
        while n % divisor == 0:
            factors.append(divisor)
            n //= divisor
        divisor += 1
    
    return factors
```

### 3.4 Containment Check

To check if a complex concept contains a primitive:

```python
def contains(complex_concept: int, primitive_prime: int) -> bool:
    """
    Check containment via divisibility.
    
    Example:
        HUMAN(6) contains ANIMAL(2)? → 6 % 2 == 0 → True
    """
    return complex_concept % primitive_prime == 0
```

### 3.5 Handling Negation

For negation, we use a **dual representation**:

```python
@dataclass
class Concept:
    positive: int  # Product of positive primitives
    negative: int  # Product of negated primitives
    
    def __repr__(self):
        pos = decompose(self.positive)
        neg = decompose(self.negative)
        return f"Concept(+{pos}, -{neg})"
```

Example:

```python
# INANIMATE = THING ∧ ¬LIVING
INANIMATE = Concept(
    positive=THING,      # 13
    negative=LIVING      # 17
)

# Check: Is something INANIMATE and LIVING?
# This is a contradiction: INANIMATE requires ¬LIVING
def is_consistent(concept: Concept) -> bool:
    from math import gcd
    return gcd(concept.positive, concept.negative) == 1
```

---

## 4. Composition Operators

### 4.1 Core Operators

| Operator | Symbol | Arity | Description |
|----------|--------|-------|-------------|
| **Conjunction** | ∧ | 2+ | Both/all concepts apply |
| **Negation** | ¬ | 1 | Concept does not apply |
| **Disjunction** | ∨ | 2+ | At least one applies |
| **Implication** | → | 2 | If first, then second |
| **Predication** | () | 2 | Apply predicate to subject |
| **Relation** | R() | 3 | Relate two concepts |

### 4.2 Operator Semantics

#### 4.2.1 Conjunction (∧)

The fundamental composition operator.

```
SEMANTICS:
    A ∧ B applies to X iff A applies to X AND B applies to X
    
PRIME REPRESENTATION:
    A ∧ B = A × B
    
EXAMPLE:
    LIVING(17) ∧ RATIONAL(3) = 51 = RATIONAL_BEING
```

#### 4.2.2 Negation (¬)

Exclusion of a concept.

```
SEMANTICS:
    ¬A applies to X iff A does NOT apply to X
    
REPRESENTATION:
    Use dual representation: Concept(positive, negative)
    ¬A shifts A from positive to negative track
    
EXAMPLE:
    ¬LIVING with THING:
    Concept(positive=THING, negative=LIVING)
```

#### 4.2.3 Disjunction (∨)

At least one of several concepts.

```
SEMANTICS:
    A ∨ B applies to X iff A applies to X OR B applies to X
    
REPRESENTATION:
    Cannot directly represent in prime system
    Use set of possible concepts: {A, B}
    
EXAMPLE:
    VERTEBRATE ∨ INVERTEBRATE = {VERTEBRATE, INVERTEBRATE}
    Both are types of ANIMAL
```

#### 4.2.4 Implication (→)

Conditional composition.

```
SEMANTICS:
    A → B means: if A applies to X, then B applies to X
    
REPRESENTATION:
    Store as rule: (A, B) ∈ ImplicationRules
    
EXAMPLE:
    HUMAN → MORTAL
    If something is HUMAN(6), it must be MORTAL(19)
```

### 4.3 Operator Table

```yaml
# calculus/operators.yaml

operators:
  - id: OP_CONJ
    symbol: "∧"
    name: conjunction
    arity: 2
    variadic: true
    semantics:
      informal: "Both concepts apply"
      formal: "∀x: (A∧B)(x) ↔ A(x) ∧ B(x)"
    prime_operation: "multiplication"
    
  - id: OP_NEG
    symbol: "¬"
    name: negation
    arity: 1
    semantics:
      informal: "Concept does not apply"
      formal: "∀x: (¬A)(x) ↔ ¬A(x)"
    prime_operation: "shift to negative track"
    
  - id: OP_DISJ
    symbol: "∨"
    name: disjunction
    arity: 2
    variadic: true
    semantics:
      informal: "At least one concept applies"
      formal: "∀x: (A∨B)(x) ↔ A(x) ∨ B(x)"
    prime_operation: "set union of possibilities"
    
  - id: OP_IMPL
    symbol: "→"
    name: implication
    arity: 2
    semantics:
      informal: "If first applies, second must apply"
      formal: "∀x: (A→B) means A(x) → B(x)"
    prime_operation: "rule storage"
```

---

## 5. Alternative Formal Systems

The prime number system is primary, but we implement alternatives for comparison and specific use cases.

### 5.1 Set-Theoretic Representation

Concepts as **sets of primitives**.

```python
class SetTheoreticConcept:
    """Concept as a set of primitive labels."""
    
    def __init__(self, primitives: set[str]):
        self.primitives = primitives
    
    def compose_with(self, other: 'SetTheoreticConcept') -> 'SetTheoreticConcept':
        """Conjunction = set union"""
        return SetTheoreticConcept(self.primitives | other.primitives)
    
    def contains(self, primitive: str) -> bool:
        """Containment = set membership"""
        return primitive in self.primitives
    
    def is_subtype_of(self, other: 'SetTheoreticConcept') -> bool:
        """Subtype = superset of primitives"""
        return self.primitives >= other.primitives
```

**Advantages**: Intuitive, easy to visualize  
**Disadvantages**: Less compact, harder to compare

### 5.2 Type-Theoretic Representation

Concepts as **types** with composition via **product types**.

```python
from typing import TypeVar, Generic

class PrimitiveType:
    """A primitive concept as a type."""
    name: str

class CompositeType:
    """A composite concept as a product type."""
    components: tuple[PrimitiveType | 'CompositeType', ...]
    
    def __init__(self, *components):
        self.components = components
```

**Advantages**: Type checking, formal verification possible  
**Disadvantages**: More complex machinery

### 5.3 Vector Space Representation

Primitives as **basis vectors**, concepts as **linear combinations**.

```python
import numpy as np

class VectorConcept:
    """Concept as a vector in primitive-space."""
    
    def __init__(self, n_primitives: int):
        self.vector = np.zeros(n_primitives)
    
    @classmethod
    def from_primitives(cls, primitive_indices: list[int], n_total: int):
        """Create concept from primitive indices."""
        concept = cls(n_total)
        for idx in primitive_indices:
            concept.vector[idx] = 1.0
        return concept
    
    def similarity(self, other: 'VectorConcept') -> float:
        """Cosine similarity between concepts."""
        dot = np.dot(self.vector, other.vector)
        norm = np.linalg.norm(self.vector) * np.linalg.norm(other.vector)
        return dot / norm if norm > 0 else 0
```

**Advantages**: Supports "approximate" matching, gradual containment  
**Disadvantages**: Loses discreteness of primitives

### 5.4 Graph-Based Representation

Concepts as **subgraphs** in the primitive relationship graph.

```python
import networkx as nx

class GraphConcept:
    """Concept as a subgraph of the primitive graph."""
    
    def __init__(self, full_graph: nx.DiGraph):
        self.full_graph = full_graph
        self.active_nodes: set[str] = set()
    
    def add_primitive(self, primitive_id: str):
        """Add primitive and its presuppositions."""
        self.active_nodes.add(primitive_id)
        # Also add presupposed primitives
        for pred in self.full_graph.predecessors(primitive_id):
            if self.full_graph[pred][primitive_id].get('type') == 'presupposes':
                self.add_primitive(pred)
```

**Advantages**: Captures relationships naturally  
**Disadvantages**: Complex operations

---

## 6. Composition Rules

### 6.1 Well-Formedness Rules

A composition is **well-formed** if:

```yaml
well_formedness_rules:
  
  - id: WF_NO_CONTRADICTION
    description: "A concept cannot contain both P and ¬P"
    check: "gcd(positive_track, negative_track) == 1"
    violation_type: contradiction
    
  - id: WF_PRESUPPOSITIONS_MET
    description: "All presupposed primitives must be present"
    check: "for each P in concept: all presuppositions of P are in concept"
    violation_type: incomplete
    
  - id: WF_NO_CONTRASTS
    description: "Contrasting primitives cannot coexist"
    check: "for each pair (P, Q) in concept: (P, Q) not in contrasts"
    violation_type: incompatible
```

### 6.2 Inference Rules

Rules for deriving new facts:

```yaml
inference_rules:
  
  - id: INF_CONTAINMENT
    name: "Containment Inference"
    premises:
      - "X is A∧B"
    conclusion: "X is A AND X is B"
    
  - id: INF_TRANSITIVITY
    name: "Transitivity of Implication"
    premises:
      - "A → B"
      - "B → C"
    conclusion: "A → C"
    
  - id: INF_PRESUPPOSITION
    name: "Presupposition Inheritance"
    premises:
      - "X is A"
      - "A presupposes B"
    conclusion: "X is B"
```

### 6.3 Composition Patterns

Common composition patterns:

```yaml
composition_patterns:
  
  - name: "Differentiation"
    pattern: "GENUS ∧ DIFFERENTIA → SPECIES"
    example: "ANIMAL ∧ RATIONAL → HUMAN"
    
  - name: "Negation Specialization"
    pattern: "GENUS ∧ ¬PROPERTY → SUBSPECIES"
    example: "OBJECT ∧ ¬LIVING → INANIMATE"
    
  - name: "Relational Composition"
    pattern: "RELATION(A, B)"
    example: "CAUSE(EVENT_A, EVENT_B)"
    
  - name: "Property Attribution"
    pattern: "THING ∧ PROPERTY"
    example: "OBJECT ∧ RED → RED_OBJECT"
```

---

## 7. Decomposition Algorithms

### 7.1 Prime Decomposition

For the prime number system:

```python
def prime_decompose(concept: int, alphabet: dict[int, str]) -> list[str]:
    """
    Decompose a prime product into primitive labels.
    
    Args:
        concept: Product of primes
        alphabet: Map from prime to primitive label
        
    Returns:
        List of primitive labels
    """
    factors = prime_factorization(concept)
    return [alphabet[p] for p in factors if p in alphabet]


def prime_factorization(n: int) -> list[int]:
    """Return prime factors of n."""
    factors = []
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1
    if n > 1:
        factors.append(n)
    return factors
```

### 7.2 Semantic Decomposition

When given a natural language concept to decompose:

```
ALGORITHM: SemanticDecomposition

INPUT: concept_description (string)
OUTPUT: list of primitives, or indication of gaps

1. PARSE concept description into features
2. FOR each feature:
   a. SEARCH alphabet for matching primitive
   b. IF found: add to result
   c. ELSE: add to gaps list
3. CHECK well-formedness of result
4. RETURN (result, gaps)
```

### 7.3 Recursive Decomposition

When a "primitive" might actually be composite:

```python
def recursive_decompose(concept_id: str, alphabet: Alphabet) -> DecompositionTree:
    """
    Recursively decompose until reaching true primitives.
    
    Returns a tree showing the decomposition structure.
    """
    concept = alphabet.get(concept_id)
    
    if concept.is_primitive:
        return DecompositionTree(concept_id, is_leaf=True)
    
    children = []
    for component_id in concept.components:
        child_tree = recursive_decompose(component_id, alphabet)
        children.append(child_tree)
    
    return DecompositionTree(concept_id, children=children)
```

---

## 8. Implementation

### 8.1 Core Classes

**`calculus/implementations/prime_composition.py`**:

```python
"""Leibniz's prime number composition system."""

from dataclasses import dataclass
from typing import Optional
from functools import reduce
from math import gcd


@dataclass
class PrimeConcept:
    """A concept represented via prime numbers."""
    positive: int = 1  # Product of positive primitives
    negative: int = 1  # Product of negated primitives
    
    def __mul__(self, other: 'PrimeConcept') -> 'PrimeConcept':
        """Conjunction via multiplication."""
        return PrimeConcept(
            positive=self.positive * other.positive,
            negative=self.negative * other.negative
        )
    
    def __neg__(self) -> 'PrimeConcept':
        """Negation swaps positive and negative."""
        return PrimeConcept(
            positive=self.negative,
            negative=self.positive
        )
    
    def contains(self, primitive_prime: int) -> bool:
        """Check if concept contains primitive."""
        return self.positive % primitive_prime == 0
    
    def excludes(self, primitive_prime: int) -> bool:
        """Check if concept excludes primitive."""
        return self.negative % primitive_prime == 0
    
    def is_consistent(self) -> bool:
        """Check for no contradictions."""
        return gcd(self.positive, self.negative) == 1
    
    def decompose(self) -> tuple[list[int], list[int]]:
        """Return (positive primes, negative primes)."""
        return (
            prime_factorization(self.positive),
            prime_factorization(self.negative)
        )


class PrimeCalculus:
    """The Leibnizian calculus for composing concepts."""
    
    def __init__(self, alphabet: dict[str, int]):
        """
        Args:
            alphabet: Map from primitive label to prime number
        """
        self.alphabet = alphabet
        self.reverse_alphabet = {v: k for k, v in alphabet.items()}
    
    def primitive(self, label: str) -> PrimeConcept:
        """Create a concept from a single primitive."""
        if label not in self.alphabet:
            raise ValueError(f"Unknown primitive: {label}")
        return PrimeConcept(positive=self.alphabet[label])
    
    def compose(self, *labels: str) -> PrimeConcept:
        """Compose multiple primitives."""
        concepts = [self.primitive(label) for label in labels]
        return reduce(lambda a, b: a * b, concepts)
    
    def negate(self, label: str) -> PrimeConcept:
        """Create a negated primitive."""
        if label not in self.alphabet:
            raise ValueError(f"Unknown primitive: {label}")
        return PrimeConcept(negative=self.alphabet[label])
    
    def decompose(self, concept: PrimeConcept) -> dict[str, list[str]]:
        """Decompose concept into labeled primitives."""
        pos_primes, neg_primes = concept.decompose()
        return {
            "positive": [self.reverse_alphabet[p] for p in pos_primes if p in self.reverse_alphabet],
            "negative": [self.reverse_alphabet[p] for p in neg_primes if p in self.reverse_alphabet],
        }
    
    def contains(self, concept: PrimeConcept, label: str) -> bool:
        """Check if concept contains primitive."""
        if label not in self.alphabet:
            return False
        return concept.contains(self.alphabet[label])
    
    def is_subtype(self, specific: PrimeConcept, general: PrimeConcept) -> bool:
        """Check if specific is a subtype of general.
        
        A is subtype of B if A contains all primitives of B
        (and possibly more).
        """
        return specific.positive % general.positive == 0


def prime_factorization(n: int) -> list[int]:
    """Compute prime factorization."""
    if n <= 1:
        return []
    factors = []
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1
    if n > 1:
        factors.append(n)
    return factors
```

### 8.2 Validation

**`calculus/implementations/validator.py`**:

```python
"""Validate concept compositions."""

from dataclasses import dataclass
from typing import Optional

from .prime_composition import PrimeConcept


@dataclass
class ValidationResult:
    valid: bool
    issues: list[str]
    
    def __bool__(self):
        return self.valid


class ConceptValidator:
    """Validates concept well-formedness."""
    
    def __init__(self, contrasts: list[tuple[int, int]], presuppositions: dict[int, list[int]]):
        """
        Args:
            contrasts: List of (prime1, prime2) pairs that cannot coexist
            presuppositions: Map from prime to list of presupposed primes
        """
        self.contrasts = set(contrasts)
        self.presuppositions = presuppositions
    
    def validate(self, concept: PrimeConcept) -> ValidationResult:
        """Validate a concept for well-formedness."""
        issues = []
        
        # Check consistency (no P and ¬P)
        if not concept.is_consistent():
            issues.append("Concept contains contradictory primitives")
        
        # Check contrasts
        pos_primes = set(prime_factorization(concept.positive))
        for p1, p2 in self.contrasts:
            if p1 in pos_primes and p2 in pos_primes:
                issues.append(f"Concept contains contrasting primitives: {p1}, {p2}")
        
        # Check presuppositions
        for prime in pos_primes:
            if prime in self.presuppositions:
                for required in self.presuppositions[prime]:
                    if required not in pos_primes:
                        issues.append(f"Primitive {prime} requires {required}")
        
        return ValidationResult(valid=len(issues) == 0, issues=issues)
```

---

## 9. Examples

### 9.1 Basic Composition

```python
# Setup
alphabet = {
    "existence": 2,
    "thing": 3,
    "living": 5,
    "animal": 7,
    "rational": 11,
    "mortal": 13,
}

calculus = PrimeCalculus(alphabet)

# Compose HUMAN
human = calculus.compose("thing", "living", "animal", "rational")
print(human)  # PrimeConcept(positive=1155, negative=1)

# Decompose
print(calculus.decompose(human))
# {'positive': ['thing', 'living', 'animal', 'rational'], 'negative': []}

# Check containment
print(calculus.contains(human, "rational"))  # True
print(calculus.contains(human, "mortal"))    # False (not yet composed in)
```

### 9.2 Working with Negation

```python
# INANIMATE = THING ∧ ¬LIVING
thing = calculus.primitive("thing")
not_living = calculus.negate("living")
inanimate = thing * not_living

print(inanimate)  # PrimeConcept(positive=3, negative=5)
print(calculus.decompose(inanimate))
# {'positive': ['thing'], 'negative': ['living']}

# Consistency check
print(inanimate.is_consistent())  # True

# Now try to add LIVING (should fail)
living = calculus.primitive("living")
contradiction = inanimate * living
print(contradiction.is_consistent())  # False!
```

### 9.3 Subtype Checking

```python
# HUMAN is a subtype of ANIMAL
human = calculus.compose("thing", "living", "animal", "rational")
animal = calculus.compose("thing", "living", "animal")

print(calculus.is_subtype(human, animal))  # True
print(calculus.is_subtype(animal, human))  # False
```

### 9.4 Complex Derivation: JUSTICE

```yaml
# calculus/examples/derive_justice.yaml

derivation:
  name: "Deriving JUSTICE"
  target: "justice"
  
  steps:
    - step: 1
      operation: "primitive"
      input: "fairness"
      result: "fairness"
      prime: 17
      explanation: "Start with the primitive of equal treatment"
      
    - step: 2
      operation: "compose"
      inputs: ["fairness", "desert"]
      result: "fair_desert"
      prime: "17 × 19 = 323"
      explanation: "Add the concept of deserving outcomes"
      
    - step: 3
      operation: "compose"
      inputs: ["fair_desert", "rights"]
      result: "just_rights"
      prime: "323 × 23 = 7429"
      explanation: "Include the concept of entitlements"
      
    - step: 4
      operation: "compose"
      inputs: ["just_rights", "social_order"]
      result: "justice"
      prime: "7429 × 29 = 215441"
      explanation: "Ground in social context"
      
  final:
    concept: "justice"
    prime: 215441
    decomposition: ["fairness", "desert", "rights", "social_order"]
    
  verification:
    - check: "contains fairness"
      result: "215441 % 17 = 0 ✓"
    - check: "contains desert"  
      result: "215441 % 19 = 0 ✓"
    - check: "contains punishment"
      result: "215441 % 31 = 16 ✗ (not present)"
```

---

## Summary

The Calculus Ratiocinator provides:

1. **Prime Number System**: Core representation, efficient containment checking
2. **Composition Operators**: ∧, ¬, ∨, → for building complex concepts
3. **Alternative Systems**: Set-theoretic, type-theoretic, vector-space, graph-based
4. **Validation**: Well-formedness checking, consistency enforcement
5. **Decomposition**: Factor complex concepts into primitives
6. **Implementation**: Ready-to-use Python classes

The calculus transforms the alphabet from a static list into a **dynamic generative system** capable of expressing arbitrarily complex concepts.

> *"Calculemus!"* — Let us calculate.
