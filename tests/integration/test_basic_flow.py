"""Integration test for basic ALPHABETUM flow."""

import pytest
import tempfile
import shutil
from pathlib import Path
import sys
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


def create_test_project(base: Path):
    """Create a minimal test project structure."""
    # Create directories
    (base / "alphabet" / "primitives" / "detailed").mkdir(parents=True)
    (base / "alphabet" / "relationships").mkdir(parents=True)
    (base / "reasoning" / "logs").mkdir(parents=True)
    (base / "reasoning" / "rejected").mkdir(parents=True)
    (base / "reasoning" / "meta_reflections").mkdir(parents=True)
    (base / "validation" / "benchmarks").mkdir(parents=True)
    (base / "calculus").mkdir(parents=True)

    # Config
    config = {
        "llm": {
            "provider": "anthropic",
            "model": "claude-3-opus-20240229",
            "max_tokens": 4096,
            "timeout_seconds": 120,
            "retry_attempts": 3,
        },
        "temperatures": {
            "proposer": 0.7,
            "critic": 0.3,
            "refiner": 0.5,
            "meta_reasoner": 0.5,
        },
        "iteration": {
            "candidates_per_cycle": 2,
            "expansion_cycles": 2,
            "consolidation_cycles": 1,
            "composition_cycles": 1,
            "meta_reflection_interval": 5,
        },
        "stopping": {
            "coverage_threshold": 0.90,
            "diminishing_returns_window": 10,
            "diminishing_returns_threshold": 2,
            "max_iterations": 100,
            "stability_window": 10,
        },
    }
    with open(base / "config.yaml", "w") as f:
        yaml.dump(config, f)

    # Iteration state
    state = {
        "iteration_state": {
            "current_iteration": 0,
            "phase": "EXPANSION",
            "cycle_in_phase": 0,
            "current_strategy": {
                "proposer_mode": "DOMAIN_SWEEP",
                "proposer_temperature": 0.7,
                "critic_strictness": 0.5,
                "domains_priority": ["being", "space", "time"],
            },
            "pending": {
                "candidates_to_evaluate": [],
                "gaps_to_fill": [],
            },
            "metrics": {
                "coverage_score": 0.0,
                "consistency_score": 1.0,
            },
            "history": {
                "total_proposed": 0,
                "total_accepted": 0,
                "total_rejected": 0,
            },
        }
    }
    with open(base / "reasoning" / "iteration_state.yaml", "w") as f:
        yaml.dump(state, f)

    # Alphabet index
    index = {
        "alphabet_index": {
            "version": "1.0.0",
            "iteration": 0,
            "statistics": {"total_primitives": 0, "by_domain": {}, "by_status": {}},
            "primitives": [],
        }
    }
    with open(base / "alphabet" / "primitives" / "index.yaml", "w") as f:
        yaml.dump(index, f)

    # Relationships
    graph = {
        "relationship_graph": {
            "version": "1.0.0",
            "iteration": 0,
            "contrasts": [],
            "presupposes": [],
            "composes_well": [],
        }
    }
    with open(base / "alphabet" / "relationships" / "graph.yaml", "w") as f:
        yaml.dump(graph, f)

    # Benchmarks
    benchmarks = {
        "benchmark_concepts": [
            {
                "id": "BM_001",
                "name": "change",
                "domain": "metaphysics",
                "complexity": "medium",
                "decomposition_hints": ["thing", "time", "state"],
            },
            {
                "id": "BM_002",
                "name": "motion",
                "domain": "physical",
                "complexity": "simple",
                "decomposition_hints": ["space", "time", "thing"],
            },
        ]
    }
    with open(base / "validation" / "benchmarks" / "test_concepts.yaml", "w") as f:
        yaml.dump(benchmarks, f)


class TestStateManagerIntegration:
    """Test state manager with real file operations."""

    @pytest.fixture
    def temp_project(self):
        tmpdir = tempfile.mkdtemp()
        base = Path(tmpdir)
        create_test_project(base)
        yield base
        shutil.rmtree(tmpdir)

    def test_full_state_cycle(self, temp_project):
        """Test loading, modifying, and saving state."""
        from alphabetum.state.manager import StateManager
        from alphabetum.state.models import Phase, Domain, PrimitiveStatus, PrimitiveIndexEntry

        manager = StateManager(temp_project)

        # Load initial state
        state = manager.load_iteration_state()
        assert state.current_iteration == 0

        # Modify state
        state.current_iteration = 1
        state.phase = Phase.CONSOLIDATION
        state.total_proposed = 5
        state.total_accepted = 2

        # Save state
        manager.save_iteration_state(state)

        # Reload and verify
        reloaded = manager.load_iteration_state()
        assert reloaded.current_iteration == 1
        assert reloaded.phase == Phase.CONSOLIDATION
        assert reloaded.total_proposed == 5
        assert reloaded.total_accepted == 2

    def test_primitive_lifecycle(self, temp_project):
        """Test creating and loading primitives."""
        from alphabetum.state.manager import StateManager
        from alphabetum.state.models import (
            PrimitiveIndexEntry, PrimitiveDetailed, Definition,
            Domain, PrimitiveStatus
        )

        manager = StateManager(temp_project)

        # Create a primitive
        index_entry = PrimitiveIndexEntry(
            id="PRM_0001",
            label="existence",
            prime=2,
            domain=Domain.BEING,
            status=PrimitiveStatus.RECENT,
            added_iteration=1,
            last_reviewed=1,
            confidence=0.9,
        )

        detailed = PrimitiveDetailed(
            id="PRM_0001",
            symbol="E",
            label="existence",
            definition=Definition(
                informal="The quality of being or existing",
                ostensive=["A rock exists", "Numbers exist"],
                negative=["Nothing does not exist"],
            ),
            domain_primary=Domain.BEING,
            proposed_iteration=1,
            accepted_iteration=1,
            prime_number=2,
            confidence=0.9,
        )

        # Save
        manager.save_alphabet_index([index_entry], 1)
        manager.save_primitive_detailed(detailed)

        # Reload and verify
        loaded_index = manager.load_alphabet_index()
        assert len(loaded_index) == 1
        assert loaded_index[0].label == "existence"

        loaded_detailed = manager.load_primitive_detailed("PRM_0001")
        assert loaded_detailed is not None
        assert loaded_detailed.label == "existence"
        assert "rock" in loaded_detailed.definition.ostensive[0].lower()


class TestValidationIntegration:
    """Test validation with real project."""

    @pytest.fixture
    def temp_project(self):
        tmpdir = tempfile.mkdtemp()
        base = Path(tmpdir)
        create_test_project(base)
        yield base
        shutil.rmtree(tmpdir)

    def test_empty_alphabet_validation(self, temp_project):
        """Test validation with empty alphabet."""
        from alphabetum.validation.checker import AlphabetValidator

        validator = AlphabetValidator(temp_project)
        results = validator.run_full_validation()

        # Should pass with empty alphabet
        assert "circularity" in results
        assert "redundancy" in results
        assert results["circularity"].passed

    def test_coverage_with_empty_alphabet(self, temp_project):
        """Test coverage check with empty alphabet."""
        from alphabetum.validation.checker import AlphabetValidator

        validator = AlphabetValidator(temp_project)
        coverage = validator.check_coverage_only()

        assert coverage.total == 2  # Two benchmarks
        assert coverage.expressible == 0  # Nothing expressible
        assert coverage.coverage_score == 0.0


class TestCalculusIntegration:
    """Test calculus with loaded primitives."""

    @pytest.fixture
    def temp_project(self):
        tmpdir = tempfile.mkdtemp()
        base = Path(tmpdir)
        create_test_project(base)

        # Add some primitives
        from alphabetum.state.manager import StateManager
        from alphabetum.state.models import PrimitiveIndexEntry, Domain, PrimitiveStatus

        manager = StateManager(base)
        primitives = [
            PrimitiveIndexEntry(
                id="PRM_0001", label="thing", prime=2, domain=Domain.BEING,
                status=PrimitiveStatus.STABLE, added_iteration=1, last_reviewed=1, confidence=0.9,
            ),
            PrimitiveIndexEntry(
                id="PRM_0002", label="space", prime=3, domain=Domain.SPACE,
                status=PrimitiveStatus.STABLE, added_iteration=1, last_reviewed=1, confidence=0.9,
            ),
            PrimitiveIndexEntry(
                id="PRM_0003", label="time", prime=5, domain=Domain.TIME,
                status=PrimitiveStatus.STABLE, added_iteration=1, last_reviewed=1, confidence=0.9,
            ),
        ]
        manager.save_alphabet_index(primitives, 1)

        yield base
        shutil.rmtree(tmpdir)

    def test_calculus_with_loaded_primitives(self, temp_project):
        """Test calculus loading from state manager."""
        from alphabetum.state.manager import StateManager
        from alphabetum.calculus.composer import Calculus

        state_manager = StateManager(temp_project)
        calc = Calculus(state_manager)

        # Verify primitives loaded
        assert calc.get_prime("thing") == 2
        assert calc.get_prime("space") == 3
        assert calc.get_prime("time") == 5

        # Test composition
        motion = calc.compose("thing", "space", "time")
        assert motion.number == 30  # 2 * 3 * 5
        assert calc.contains(motion, "thing")
        assert calc.contains(motion, "space")
        assert calc.contains(motion, "time")
