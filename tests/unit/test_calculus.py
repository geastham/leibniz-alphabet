"""Unit tests for the calculus of concepts."""

import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from alphabetum.calculus.composer import Calculus, Concept


class TestConcept:
    """Test Concept dataclass."""

    def test_create_concept(self):
        concept = Concept(
            name="test",
            number=30,
            components=["animal", "rational"],
        )
        assert concept.name == "test"
        assert concept.number == 30
        assert len(concept.components) == 2

    def test_concept_contains(self):
        # HUMAN = 5 * 7 = 35 (animal * rational)
        human = Concept(name="human", number=35, components=["animal", "rational"])
        # ANIMAL = 5
        animal = Concept(name="animal", number=5, components=["animal"])

        assert human.contains(animal)  # Human contains animal
        assert not animal.contains(human)  # Animal doesn't contain human

    def test_concept_to_expression(self):
        concept = Concept(
            name="human",
            number=35,
            components=["animal", "rational"],
            negated=["immortal"],
        )
        expr = concept.to_expression()
        assert "animal" in expr
        assert "rational" in expr
        assert "not(immortal)" in expr


class TestCalculus:
    """Test Calculus class."""

    @pytest.fixture
    def calculus(self):
        calc = Calculus()
        calc.register_primitive("thing", 2)
        calc.register_primitive("living", 3)
        calc.register_primitive("animal", 5)
        calc.register_primitive("rational", 7)
        calc.register_primitive("mortal", 11)
        calc.register_contrast("living", "nonliving")
        return calc

    def test_register_primitive(self, calculus):
        assert calculus.get_prime("thing") == 2
        assert calculus.get_prime("animal") == 5
        assert calculus.get_prime("unknown") is None

    def test_compose_two_primitives(self, calculus):
        # HUMAN = ANIMAL * RATIONAL = 5 * 7 = 35
        human = calculus.compose("animal", "rational")
        assert human.number == 35
        assert "animal" in human.components
        assert "rational" in human.components

    def test_compose_three_primitives(self, calculus):
        # MORTAL_HUMAN = ANIMAL * RATIONAL * MORTAL = 5 * 7 * 11 = 385
        mortal_human = calculus.compose("animal", "rational", "mortal")
        assert mortal_human.number == 385
        assert len(mortal_human.components) == 3

    def test_compose_handles_missing(self, calculus):
        # Composing with unknown primitive
        concept = calculus.compose("animal", "unknown")
        assert concept.number == 5  # Only animal included
        assert "animal" in concept.components
        assert "unknown" not in concept.components

    def test_contains_check(self, calculus):
        human = calculus.compose("animal", "rational")
        assert calculus.contains(human, "animal")
        assert calculus.contains(human, "rational")
        assert not calculus.contains(human, "mortal")

    def test_extract_components(self, calculus):
        human = calculus.compose("animal", "rational")
        components = calculus.extract_components(human)
        assert "animal" in components
        assert "rational" in components
        assert len(components) == 2

    def test_well_formed_valid(self, calculus):
        human = calculus.compose("animal", "rational")
        valid, violations = calculus.is_well_formed(human)
        assert valid
        assert len(violations) == 0

    def test_well_formed_contradiction(self, calculus):
        concept = calculus.compose_with_negation(["animal"], ["animal"])
        valid, violations = calculus.is_well_formed(concept)
        assert not valid
        assert len(violations) > 0

    def test_find_common_components(self, calculus):
        human = calculus.compose("animal", "rational")
        mortal_animal = calculus.compose("animal", "mortal")
        common = calculus.find_common_components(human, mortal_animal)
        assert "animal" in common

    def test_get_statistics(self, calculus):
        stats = calculus.get_statistics()
        assert stats["total_primitives"] == 5
        assert stats["total_contrasts"] == 1
        assert stats["largest_prime"] == 11


class TestCalculusEdgeCases:
    """Test edge cases for the calculus."""

    def test_empty_composition(self):
        calc = Calculus()
        concept = calc.compose()  # No primitives
        assert concept.number == 1
        assert concept.components == []

    def test_duplicate_composition(self):
        calc = Calculus()
        calc.register_primitive("animal", 5)
        concept = calc.compose("animal", "animal")
        # Should have animal twice in components
        assert concept.number == 25  # 5 * 5

    def test_large_composition(self):
        calc = Calculus()
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
        for i, p in enumerate(primes):
            calc.register_primitive(f"prim_{i}", p)

        concept = calc.compose(*[f"prim_{i}" for i in range(10)])
        expected = 1
        for p in primes:
            expected *= p
        assert concept.number == expected
