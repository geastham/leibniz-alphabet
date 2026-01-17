"""Unit tests for state models."""

import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from alphabetum.state.models import (
    Phase, Verdict, PrimitiveStatus, Domain,
    PrimitiveIndexEntry, Definition, Candidate, Evaluation, AttackResult
)


class TestEnums:
    """Test enum definitions."""

    def test_phase_values(self):
        assert Phase.EXPANSION.value == "EXPANSION"
        assert Phase.CONSOLIDATION.value == "CONSOLIDATION"
        assert Phase.COMPOSITION.value == "COMPOSITION"
        assert Phase.META_REFLECTION.value == "META_REFLECTION"

    def test_verdict_values(self):
        assert Verdict.ACCEPT.value == "ACCEPT"
        assert Verdict.REJECT.value == "REJECT"
        assert Verdict.REFINE.value == "REFINE"
        assert Verdict.DEFER.value == "DEFER"

    def test_domain_values(self):
        assert Domain.BEING.value == "being"
        assert Domain.SPACE.value == "space"
        assert Domain.TIME.value == "time"
        assert len(Domain) == 15  # All domains


class TestPrimitiveIndexEntry:
    """Test PrimitiveIndexEntry model."""

    def test_create_valid_entry(self):
        entry = PrimitiveIndexEntry(
            id="PRM_0001",
            label="existence",
            prime=2,
            domain=Domain.BEING,
            status=PrimitiveStatus.STABLE,
            added_iteration=1,
            last_reviewed=5,
            confidence=0.9,
        )
        assert entry.id == "PRM_0001"
        assert entry.label == "existence"
        assert entry.prime == 2
        assert entry.domain == Domain.BEING
        assert entry.confidence == 0.9

    def test_confidence_bounds(self):
        with pytest.raises(ValueError):
            PrimitiveIndexEntry(
                id="PRM_0001",
                label="test",
                prime=2,
                domain=Domain.BEING,
                status=PrimitiveStatus.STABLE,
                added_iteration=1,
                last_reviewed=1,
                confidence=1.5,  # Out of bounds
            )


class TestCandidate:
    """Test Candidate model."""

    def test_create_candidate(self):
        candidate = Candidate(
            id="CAND_001_001",
            label="existence",
            domain=Domain.BEING,
            proposed_symbol="E",
            informal_definition="The quality of being or existing",
            ostensive_examples=["A rock exists", "Numbers exist abstractly"],
            negative_examples=["Square circles do not exist"],
            primitiveness_argument="Cannot be defined without circularity",
            decomposition_resistance="All attempts lead back to existence itself",
            confidence=0.8,
        )
        assert candidate.label == "existence"
        assert candidate.domain == Domain.BEING
        assert len(candidate.ostensive_examples) == 2


class TestEvaluation:
    """Test Evaluation model."""

    def test_create_accept_evaluation(self):
        evaluation = Evaluation(
            candidate_id="CAND_001_001",
            decomposition_attacks=[
                AttackResult(
                    approach="analytic",
                    attempt="Define existence as...",
                    result="Circular - used 'is' which presupposes existence",
                    survived=True,
                )
            ],
            decomposition_survived=True,
            circularity_survived=True,
            verdict=Verdict.ACCEPT,
            confidence=0.85,
            reasoning_summary="Concept survives all attacks",
            key_insight="Existence is truly primitive",
        )
        assert evaluation.verdict == Verdict.ACCEPT
        assert len(evaluation.decomposition_attacks) == 1

    def test_create_reject_evaluation(self):
        evaluation = Evaluation(
            candidate_id="CAND_001_002",
            redundancy_can_be_expressed=True,
            redundancy_using=["time", "before"],
            verdict=Verdict.REJECT,
            confidence=0.9,
            reasoning_summary="Can be expressed as time + before relation",
        )
        assert evaluation.verdict == Verdict.REJECT
        assert evaluation.redundancy_can_be_expressed is True


class TestDefinition:
    """Test Definition model."""

    def test_create_definition(self):
        definition = Definition(
            informal="The quality of being or existing",
            formal="E(x) iff x is in the domain",
            ostensive=["Rocks", "Numbers", "Thoughts"],
            negative=["Nothing", "Non-existence"],
        )
        assert definition.informal
        assert len(definition.ostensive) == 3
