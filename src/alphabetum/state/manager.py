"""State management for the alphabet and reasoning logs."""

import yaml
from pathlib import Path
from datetime import datetime
from typing import Optional

from .models import (
    IterationState, PrimitiveIndexEntry, PrimitiveDetailed,
    Phase, Domain, PrimitiveStatus, Definition, RelationshipGraph
)


def _represent_domain(dumper, domain):
    """Custom YAML representer for Domain enum."""
    return dumper.represent_scalar('tag:yaml.org,2002:str', domain.value)


def _represent_phase(dumper, phase):
    """Custom YAML representer for Phase enum."""
    return dumper.represent_scalar('tag:yaml.org,2002:str', phase.value)


def _represent_status(dumper, status):
    """Custom YAML representer for PrimitiveStatus enum."""
    return dumper.represent_scalar('tag:yaml.org,2002:str', status.value)


# Register custom representers
yaml.add_representer(Domain, _represent_domain)
yaml.add_representer(Phase, _represent_phase)
yaml.add_representer(PrimitiveStatus, _represent_status)


class StateManager:
    """Manages all persistent state for ALPHABETUM."""

    def __init__(self, base_path: Path):
        self.base_path = Path(base_path)
        self.alphabet_path = self.base_path / "alphabet"
        self.reasoning_path = self.base_path / "reasoning"
        self.calculus_path = self.base_path / "calculus"
        self.validation_path = self.base_path / "validation"

    # === ITERATION STATE ===

    def load_iteration_state(self) -> IterationState:
        """Load current iteration state from YAML."""
        state_file = self.reasoning_path / "iteration_state.yaml"
        with open(state_file) as f:
            data = yaml.safe_load(f)
        return self._parse_iteration_state(data["iteration_state"])

    def save_iteration_state(self, state: IterationState) -> None:
        """Save iteration state to YAML."""
        state_file = self.reasoning_path / "iteration_state.yaml"
        state.last_updated = datetime.utcnow()
        data = {"iteration_state": self._serialize_iteration_state(state)}
        with open(state_file, "w") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    # === ALPHABET ===

    def load_alphabet_index(self) -> list[PrimitiveIndexEntry]:
        """Load the alphabet index."""
        index_file = self.alphabet_path / "primitives" / "index.yaml"
        with open(index_file) as f:
            data = yaml.safe_load(f)
        return [
            PrimitiveIndexEntry(**self._parse_primitive_entry(p))
            for p in data["alphabet_index"].get("primitives", [])
        ]

    def _parse_primitive_entry(self, p: dict) -> dict:
        """Parse a primitive entry, converting string enums."""
        return {
            **p,
            "domain": Domain(p["domain"]) if isinstance(p["domain"], str) else p["domain"],
            "status": PrimitiveStatus(p["status"]) if isinstance(p["status"], str) else p["status"],
        }

    def save_alphabet_index(
        self,
        primitives: list[PrimitiveIndexEntry],
        iteration: int
    ) -> None:
        """Save the alphabet index."""
        index_file = self.alphabet_path / "primitives" / "index.yaml"

        # Compute statistics
        by_domain: dict[str, int] = {}
        by_status = {"stable": 0, "recent": 0, "contested": 0}

        for p in primitives:
            domain = p.domain.value
            by_domain[domain] = by_domain.get(domain, 0) + 1
            if p.status.value in by_status:
                by_status[p.status.value] = by_status.get(p.status.value, 0) + 1

        data = {
            "alphabet_index": {
                "version": "1.0.0",
                "last_updated": datetime.utcnow().isoformat() + "Z",
                "iteration": iteration,
                "statistics": {
                    "total_primitives": len(primitives),
                    "by_domain": by_domain,
                    "by_status": by_status,
                },
                "primitives": [
                    {
                        "id": p.id,
                        "label": p.label,
                        "prime": p.prime,
                        "domain": p.domain.value,
                        "status": p.status.value,
                        "added_iteration": p.added_iteration,
                        "last_reviewed": p.last_reviewed,
                        "confidence": p.confidence,
                    }
                    for p in primitives
                ]
            }
        }

        with open(index_file, "w") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    def load_primitive_detailed(self, primitive_id: str) -> Optional[PrimitiveDetailed]:
        """Load a detailed primitive entry."""
        detailed_dir = self.alphabet_path / "primitives" / "detailed"
        for f in detailed_dir.glob(f"{primitive_id}_*.yaml"):
            with open(f) as file:
                data = yaml.safe_load(file)
            prim_data = data["primitive"]
            # Parse definition
            if isinstance(prim_data.get("definition"), dict):
                prim_data["definition"] = Definition(**prim_data["definition"])
            # Parse domain
            if isinstance(prim_data.get("domain_primary"), str):
                prim_data["domain_primary"] = Domain(prim_data["domain_primary"])
            if prim_data.get("domains_secondary"):
                prim_data["domains_secondary"] = [
                    Domain(d) if isinstance(d, str) else d
                    for d in prim_data["domains_secondary"]
                ]
            return PrimitiveDetailed(**prim_data)
        return None

    def save_primitive_detailed(self, primitive: PrimitiveDetailed) -> Path:
        """Save a detailed primitive entry."""
        filename = f"{primitive.id}_{primitive.label}.yaml"
        filepath = self.alphabet_path / "primitives" / "detailed" / filename

        data = {
            "primitive": {
                "id": primitive.id,
                "symbol": primitive.symbol,
                "label": primitive.label,
                "definition": {
                    "informal": primitive.definition.informal,
                    "formal": primitive.definition.formal,
                    "ostensive": primitive.definition.ostensive,
                    "negative": primitive.definition.negative,
                },
                "domain_primary": primitive.domain_primary.value,
                "domains_secondary": [d.value for d in primitive.domains_secondary],
                "contrasts_with": [
                    {"id": r.id, "label": r.label, "reason": r.reason}
                    for r in primitive.contrasts_with
                ],
                "presupposes": [
                    {"id": r.id, "label": r.label, "reason": r.reason}
                    for r in primitive.presupposes
                ],
                "often_combined_with": [
                    {"id": r.id, "label": r.label, "reason": r.reason}
                    for r in primitive.often_combined_with
                ],
                "proposed_iteration": primitive.proposed_iteration,
                "accepted_iteration": primitive.accepted_iteration,
                "prime_number": primitive.prime_number,
                "confidence": primitive.confidence,
                "version": primitive.version,
            }
        }

        with open(filepath, "w") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

        return filepath

    # === RELATIONSHIPS ===

    def load_relationships(self) -> RelationshipGraph:
        """Load the relationship graph."""
        graph_file = self.alphabet_path / "relationships" / "graph.yaml"
        with open(graph_file) as f:
            data = yaml.safe_load(f)
        graph_data = data.get("relationship_graph", {})
        return RelationshipGraph(
            version=graph_data.get("version", "1.0.0"),
            iteration=graph_data.get("iteration", 0),
            contrasts=graph_data.get("contrasts", []),
            presupposes=graph_data.get("presupposes", []),
            composes_well=graph_data.get("composes_well", []),
        )

    def save_relationships(self, graph: RelationshipGraph, iteration: int) -> None:
        """Save the relationship graph."""
        graph_file = self.alphabet_path / "relationships" / "graph.yaml"
        data = {
            "relationship_graph": {
                "version": graph.version,
                "last_updated": datetime.utcnow().isoformat() + "Z",
                "iteration": iteration,
                "contrasts": graph.contrasts,
                "presupposes": graph.presupposes,
                "composes_well": graph.composes_well,
            }
        }
        with open(graph_file, "w") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    # === PRIMES ===

    def get_next_prime(self) -> int:
        """Get the next available prime number for a new primitive."""
        primitives = self.load_alphabet_index()
        if not primitives:
            return 2  # First prime

        used_primes = {p.prime for p in primitives}
        candidate = max(used_primes) + 1

        while not self._is_prime(candidate):
            candidate += 1

        return candidate

    def _is_prime(self, n: int) -> bool:
        """Check if n is prime."""
        if n < 2:
            return False
        if n == 2:
            return True
        if n % 2 == 0:
            return False
        for i in range(3, int(n**0.5) + 1, 2):
            if n % i == 0:
                return False
        return True

    # === ITERATION LOGS ===

    def ensure_iteration_log_dir(self, iteration: int) -> Path:
        """Create iteration log directory if needed."""
        log_dir = self.reasoning_path / "logs" / f"iteration_{iteration:03d}"
        log_dir.mkdir(parents=True, exist_ok=True)
        return log_dir

    def save_log(
        self,
        iteration: int,
        filename: str,
        content: dict | str
    ) -> Path:
        """Save a log file for an iteration."""
        log_dir = self.ensure_iteration_log_dir(iteration)
        filepath = log_dir / filename

        with open(filepath, "w") as f:
            if isinstance(content, dict):
                yaml.dump(content, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
            else:
                f.write(content)

        return filepath

    def load_log(self, iteration: int, filename: str) -> Optional[dict | str]:
        """Load a log file from an iteration."""
        log_dir = self.reasoning_path / "logs" / f"iteration_{iteration:03d}"
        filepath = log_dir / filename

        if not filepath.exists():
            return None

        with open(filepath) as f:
            if filename.endswith(".yaml"):
                return yaml.safe_load(f)
            else:
                return f.read()

    # === HELPERS ===

    def _parse_iteration_state(self, data: dict) -> IterationState:
        """Parse iteration state from YAML data."""
        strategy = data.get("current_strategy", {})
        pending = data.get("pending", {})
        metrics = data.get("metrics", {})
        history = data.get("history", {})

        return IterationState(
            current_iteration=data.get("current_iteration", 0),
            phase=Phase(data.get("phase", "EXPANSION")),
            cycle_in_phase=data.get("cycle_in_phase", 0),
            proposer_mode=strategy.get("proposer_mode", "DOMAIN_SWEEP"),
            proposer_temperature=strategy.get("proposer_temperature", 0.7),
            critic_strictness=strategy.get("critic_strictness", 0.5),
            domains_priority=[Domain(d) for d in strategy.get("domains_priority", ["being"])],
            candidates_to_evaluate=pending.get("candidates_to_evaluate", []),
            gaps_to_fill=pending.get("gaps_to_fill", []),
            coverage_score=metrics.get("coverage_score", 0.0),
            consistency_score=metrics.get("consistency_score", 1.0),
            recent_acceptance_rate=metrics.get("recent_acceptance_rate"),
            total_proposed=history.get("total_proposed", 0),
            total_accepted=history.get("total_accepted", 0),
            total_rejected=history.get("total_rejected", 0),
        )

    def _serialize_iteration_state(self, state: IterationState) -> dict:
        """Serialize iteration state to YAML format."""
        return {
            "current_iteration": state.current_iteration,
            "phase": state.phase.value,
            "cycle_in_phase": state.cycle_in_phase,
            "last_updated": state.last_updated.isoformat() + "Z" if state.last_updated else None,
            "current_strategy": {
                "proposer_mode": state.proposer_mode,
                "proposer_temperature": state.proposer_temperature,
                "critic_strictness": state.critic_strictness,
                "domains_priority": [d.value for d in state.domains_priority],
            },
            "pending": {
                "candidates_to_evaluate": state.candidates_to_evaluate,
                "candidates_to_revise": [],
                "conflicts_to_resolve": [],
                "gaps_to_fill": state.gaps_to_fill,
            },
            "metrics": {
                "recent_acceptance_rate": state.recent_acceptance_rate,
                "coverage_score": state.coverage_score,
                "consistency_score": state.consistency_score,
            },
            "triggers": {
                "meta_reflection_due": state.current_iteration > 0 and state.current_iteration % 5 == 0,
                "iterations_since_meta": state.current_iteration % 5,
                "iterations_since_primitive": 0,
            },
            "history": {
                "total_proposed": state.total_proposed,
                "total_accepted": state.total_accepted,
                "total_rejected": state.total_rejected,
            },
        }

    def load_config(self) -> dict:
        """Load the main configuration file."""
        config_file = self.base_path / "config.yaml"
        with open(config_file) as f:
            return yaml.safe_load(f)
