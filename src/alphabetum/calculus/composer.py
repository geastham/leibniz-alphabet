"""
Leibniz's Calculus of Concepts

The core insight: represent primitive concepts as prime numbers.
- Composition is multiplication: HUMAN = ANIMAL * RATIONAL
- Containment checking is divisibility: is ANIMAL in HUMAN? Check if HUMAN % ANIMAL == 0
- Contradiction detection: concepts with overlapping contrasts
"""

from dataclasses import dataclass, field
from typing import Optional
import math
from pathlib import Path
import yaml

from ..state.manager import StateManager
from ..state.models import PrimitiveIndexEntry


@dataclass
class Concept:
    """A composed concept represented as a product of primes."""
    name: str
    number: int  # Product of prime numbers
    components: list[str] = field(default_factory=list)  # Labels of primitives
    negated: list[str] = field(default_factory=list)  # Negated primitives (tracked separately)

    def __repr__(self):
        parts = self.components.copy()
        for neg in self.negated:
            parts.append(f"not-{neg}")
        return f"Concept({self.name} = {' AND '.join(parts)}, n={self.number})"

    def contains(self, other: "Concept") -> bool:
        """Check if this concept contains another (is more specific)."""
        if self.number == 0 or other.number == 0:
            return False
        return self.number % other.number == 0

    def to_expression(self) -> str:
        """Convert to symbolic expression."""
        parts = self.components.copy()
        for neg in self.negated:
            parts.append(f"not({neg})")
        return " AND ".join(parts) if parts else "EMPTY"


class Calculus:
    """
    The calculus of concepts using Leibniz's prime number scheme.

    Each primitive concept is assigned a unique prime number.
    Complex concepts are products of their constituent primes.
    """

    def __init__(self, state_manager: Optional[StateManager] = None, base_path: Optional[Path] = None):
        self.state_manager = state_manager
        if state_manager:
            self._load_primitives()
        else:
            self.primitives: dict[str, int] = {}  # label -> prime
            self.primes_to_labels: dict[int, str] = {}  # prime -> label
            self.contrasts: list[tuple[str, str]] = []

    def _load_primitives(self):
        """Load primitives from state manager."""
        self.primitives = {}
        self.primes_to_labels = {}
        self.contrasts = []

        primitives = self.state_manager.load_alphabet_index()
        for p in primitives:
            self.primitives[p.label] = p.prime
            self.primes_to_labels[p.prime] = p.label

        # Load contrasts
        relationships = self.state_manager.load_relationships()
        for contrast in relationships.contrasts:
            if isinstance(contrast, (list, tuple)) and len(contrast) == 2:
                # Get labels from IDs
                p1_label = self._id_to_label(contrast[0], primitives)
                p2_label = self._id_to_label(contrast[1], primitives)
                if p1_label and p2_label:
                    self.contrasts.append((p1_label, p2_label))

    def _id_to_label(self, primitive_id: str, primitives: list[PrimitiveIndexEntry]) -> Optional[str]:
        """Convert primitive ID to label."""
        for p in primitives:
            if p.id == primitive_id:
                return p.label
        return None

    def register_primitive(self, label: str, prime: int) -> None:
        """Register a primitive concept with its prime number."""
        self.primitives[label] = prime
        self.primes_to_labels[prime] = label

    def register_contrast(self, label1: str, label2: str) -> None:
        """Register that two primitives are contrasting (mutually exclusive)."""
        self.contrasts.append((label1, label2))

    def get_prime(self, label: str) -> Optional[int]:
        """Get the prime number for a primitive label."""
        return self.primitives.get(label)

    def compose(self, *labels: str) -> Concept:
        """
        Compose multiple primitive concepts into a complex concept.

        Example: compose("animal", "rational") -> Concept for HUMAN
        """
        number = 1
        components = []
        missing = []

        for label in labels:
            prime = self.primitives.get(label)
            if prime:
                number *= prime
                components.append(label)
            else:
                missing.append(label)

        # Generate a name for the composition
        if components:
            name = "_".join(sorted(components))
        else:
            name = "EMPTY"

        concept = Concept(
            name=name,
            number=number,
            components=components,
        )

        return concept

    def compose_with_negation(self, positives: list[str], negatives: list[str]) -> Concept:
        """
        Compose with both positive and negative components.

        Example: compose_with_negation(["object"], ["living"]) -> INANIMATE
        """
        concept = self.compose(*positives)
        concept.negated = negatives
        concept.name = f"{concept.name}_not_{'_'.join(negatives)}" if negatives else concept.name
        return concept

    def contains(self, complex_concept: Concept, primitive_label: str) -> bool:
        """
        Check if a complex concept contains a primitive.

        Uses divisibility: HUMAN contains ANIMAL iff HUMAN_number % ANIMAL_prime == 0
        """
        prime = self.primitives.get(primitive_label)
        if not prime:
            return False
        return complex_concept.number % prime == 0

    def extract_components(self, concept: Concept) -> list[str]:
        """Extract all primitive components from a complex concept."""
        components = []
        n = concept.number

        for label, prime in self.primitives.items():
            while n % prime == 0:
                components.append(label)
                n //= prime

        return components

    def is_well_formed(self, concept: Concept) -> tuple[bool, list[str]]:
        """
        Check if a concept is well-formed (no contradictions).

        Returns (is_valid, list_of_violations)
        """
        violations = []
        components = set(concept.components)
        negated = set(concept.negated)

        # Check for P and not-P
        both = components & negated
        if both:
            violations.append(f"Contradiction: both {both} and not-{both}")

        # Check for contrasting primitives
        for label1, label2 in self.contrasts:
            if label1 in components and label2 in components:
                violations.append(f"Contrasting primitives: {label1} and {label2}")

        return len(violations) == 0, violations

    def find_common_components(self, c1: Concept, c2: Concept) -> list[str]:
        """Find primitives shared by two concepts using GCD."""
        gcd = math.gcd(c1.number, c2.number)
        return self.extract_components(Concept(name="gcd", number=gcd))

    def analyze_concept(self, label: str) -> dict:
        """Analyze what primitives would be needed to express a concept."""
        # This is a stub for future LLM-based analysis
        return {
            "label": label,
            "suggested_components": [],
            "confidence": 0.0,
            "notes": "Analysis requires LLM integration"
        }

    def try_express(self, target_label: str, hint_components: list[str]) -> Optional[Concept]:
        """
        Try to express a target concept using given component hints.

        Returns the composition if all components exist, None otherwise.
        """
        available = [h for h in hint_components if h in self.primitives]

        if len(available) == len(hint_components):
            return self.compose(*available)

        return None

    def get_statistics(self) -> dict:
        """Get statistics about the calculus."""
        return {
            "total_primitives": len(self.primitives),
            "total_contrasts": len(self.contrasts),
            "primitives": list(self.primitives.keys()),
            "largest_prime": max(self.primitives.values()) if self.primitives else 0,
        }


def demonstrate_calculus():
    """Demonstrate the calculus with some examples."""
    calc = Calculus()

    # Register some example primitives
    calc.register_primitive("thing", 2)
    calc.register_primitive("living", 3)
    calc.register_primitive("animal", 5)
    calc.register_primitive("rational", 7)
    calc.register_primitive("mortal", 11)

    # Register contrasts
    calc.register_contrast("living", "nonliving")

    # Compose concepts
    human = calc.compose("animal", "rational")
    print(f"HUMAN = {human}")
    print(f"  Number: {human.number}")
    print(f"  Contains ANIMAL? {calc.contains(human, 'animal')}")
    print(f"  Contains RATIONAL? {calc.contains(human, 'rational')}")
    print(f"  Contains LIVING? {calc.contains(human, 'living')}")

    # Compose MORTAL HUMAN
    mortal_human = calc.compose("animal", "rational", "mortal")
    print(f"\nMORTAL HUMAN = {mortal_human}")
    print(f"  Contains HUMAN? {mortal_human.contains(human)}")

    # Well-formedness check
    valid, violations = calc.is_well_formed(human)
    print(f"\n  Is HUMAN well-formed? {valid}")

    return calc


if __name__ == "__main__":
    demonstrate_calculus()
