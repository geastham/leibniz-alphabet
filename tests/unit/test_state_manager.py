"""Unit tests for state manager."""

import pytest
import tempfile
from pathlib import Path
import sys
import shutil

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from alphabetum.state.manager import StateManager
from alphabetum.state.models import (
    IterationState, Phase, Domain, PrimitiveStatus,
    PrimitiveIndexEntry, PrimitiveDetailed, Definition
)


class TestStateManager:
    """Test StateManager class."""

    @pytest.fixture
    def temp_project(self):
        """Create a temporary project structure."""
        tmpdir = tempfile.mkdtemp()
        base = Path(tmpdir)

        # Create directory structure
        (base / "alphabet" / "primitives" / "detailed").mkdir(parents=True)
        (base / "alphabet" / "relationships").mkdir(parents=True)
        (base / "reasoning" / "logs").mkdir(parents=True)
        (base / "validation" / "benchmarks").mkdir(parents=True)

        # Create initial files
        import yaml

        # Config
        config = {
            "llm": {"provider": "anthropic", "model": "test", "max_tokens": 1000},
            "temperatures": {"proposer": 0.7, "critic": 0.3, "refiner": 0.5, "meta_reasoner": 0.5},
            "iteration": {
                "candidates_per_cycle": 3,
                "expansion_cycles": 2,
                "consolidation_cycles": 1,
                "composition_cycles": 1,
            },
            "stopping": {"coverage_threshold": 0.9, "max_iterations": 100},
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
                    "domains_priority": ["being", "space"],
                },
                "pending": {},
                "metrics": {},
                "history": {},
            }
        }
        with open(base / "reasoning" / "iteration_state.yaml", "w") as f:
            yaml.dump(state, f)

        # Alphabet index
        index = {
            "alphabet_index": {
                "version": "1.0.0",
                "iteration": 0,
                "statistics": {"total_primitives": 0},
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

        yield base

        # Cleanup
        shutil.rmtree(tmpdir)

    def test_load_iteration_state(self, temp_project):
        manager = StateManager(temp_project)
        state = manager.load_iteration_state()

        assert state.current_iteration == 0
        assert state.phase == Phase.EXPANSION
        assert state.proposer_mode == "DOMAIN_SWEEP"

    def test_save_iteration_state(self, temp_project):
        manager = StateManager(temp_project)
        state = manager.load_iteration_state()

        state.current_iteration = 5
        state.phase = Phase.CONSOLIDATION
        manager.save_iteration_state(state)

        # Reload and verify
        reloaded = manager.load_iteration_state()
        assert reloaded.current_iteration == 5
        assert reloaded.phase == Phase.CONSOLIDATION

    def test_load_empty_alphabet(self, temp_project):
        manager = StateManager(temp_project)
        primitives = manager.load_alphabet_index()
        assert len(primitives) == 0

    def test_save_and_load_primitives(self, temp_project):
        manager = StateManager(temp_project)

        primitives = [
            PrimitiveIndexEntry(
                id="PRM_0001",
                label="existence",
                prime=2,
                domain=Domain.BEING,
                status=PrimitiveStatus.RECENT,
                added_iteration=1,
                last_reviewed=1,
                confidence=0.9,
            ),
            PrimitiveIndexEntry(
                id="PRM_0002",
                label="space",
                prime=3,
                domain=Domain.SPACE,
                status=PrimitiveStatus.RECENT,
                added_iteration=1,
                last_reviewed=1,
                confidence=0.85,
            ),
        ]

        manager.save_alphabet_index(primitives, iteration=1)

        # Reload
        loaded = manager.load_alphabet_index()
        assert len(loaded) == 2
        assert loaded[0].label == "existence"
        assert loaded[1].label == "space"

    def test_save_detailed_primitive(self, temp_project):
        manager = StateManager(temp_project)

        detailed = PrimitiveDetailed(
            id="PRM_0001",
            symbol="E",
            label="existence",
            definition=Definition(
                informal="The quality of being or existing",
                formal=None,
                ostensive=["A rock exists"],
                negative=["Nothing"],
            ),
            domain_primary=Domain.BEING,
            proposed_iteration=1,
            accepted_iteration=1,
            prime_number=2,
            confidence=0.9,
        )

        filepath = manager.save_primitive_detailed(detailed)
        assert filepath.exists()

        # Reload
        loaded = manager.load_primitive_detailed("PRM_0001")
        assert loaded is not None
        assert loaded.label == "existence"
        assert loaded.definition.informal == "The quality of being or existing"

    def test_get_next_prime(self, temp_project):
        manager = StateManager(temp_project)

        # Empty alphabet - should return 2
        assert manager.get_next_prime() == 2

        # Add some primitives
        primitives = [
            PrimitiveIndexEntry(
                id="PRM_0001", label="test1", prime=2, domain=Domain.BEING,
                status=PrimitiveStatus.RECENT, added_iteration=1, last_reviewed=1, confidence=0.9,
            ),
            PrimitiveIndexEntry(
                id="PRM_0002", label="test2", prime=3, domain=Domain.BEING,
                status=PrimitiveStatus.RECENT, added_iteration=1, last_reviewed=1, confidence=0.9,
            ),
        ]
        manager.save_alphabet_index(primitives, 1)

        # Next prime after 3 is 5
        assert manager.get_next_prime() == 5

    def test_is_prime(self, temp_project):
        manager = StateManager(temp_project)

        assert manager._is_prime(2)
        assert manager._is_prime(3)
        assert manager._is_prime(5)
        assert manager._is_prime(7)
        assert manager._is_prime(11)
        assert not manager._is_prime(4)
        assert not manager._is_prime(6)
        assert not manager._is_prime(9)
        assert not manager._is_prime(1)
        assert not manager._is_prime(0)

    def test_load_relationships(self, temp_project):
        manager = StateManager(temp_project)
        graph = manager.load_relationships()

        assert graph.version == "1.0.0"
        assert len(graph.contrasts) == 0

    def test_save_log(self, temp_project):
        manager = StateManager(temp_project)

        log_content = {"test": "data", "iteration": 1}
        filepath = manager.save_log(1, "test.yaml", log_content)

        assert filepath.exists()

        # Reload
        loaded = manager.load_log(1, "test.yaml")
        assert loaded["test"] == "data"
