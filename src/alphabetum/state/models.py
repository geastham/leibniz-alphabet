"""Pydantic models for all data structures in ALPHABETUM."""

from datetime import datetime
from enum import Enum
from typing import Optional, Any
from pydantic import BaseModel, Field


class Phase(str, Enum):
    """The current phase of the iteration loop."""
    EXPANSION = "EXPANSION"
    CONSOLIDATION = "CONSOLIDATION"
    COMPOSITION = "COMPOSITION"
    META_REFLECTION = "META_REFLECTION"


class Verdict(str, Enum):
    """CRITIC's verdict on a candidate primitive."""
    ACCEPT = "ACCEPT"
    REJECT = "REJECT"
    REFINE = "REFINE"
    DEFER = "DEFER"


class PrimitiveStatus(str, Enum):
    """Status of a primitive in the alphabet."""
    STABLE = "stable"
    RECENT = "recent"
    CONTESTED = "contested"
    DEPRECATED = "deprecated"


class Domain(str, Enum):
    """Conceptual domains for organizing primitives."""
    BEING = "being"
    SPACE = "space"
    TIME = "time"
    CAUSATION = "causation"
    MIND = "mind"
    MATTER = "matter"
    QUANTITY = "quantity"
    QUALITY = "quality"
    RELATION = "relation"
    ETHICS = "ethics"
    EMOTION = "emotion"
    ACTION = "action"
    KNOWLEDGE = "knowledge"
    SOCIAL = "social"
    LANGUAGE = "language"


class PrimitiveIndexEntry(BaseModel):
    """Compact entry in the alphabet index."""
    id: str
    label: str
    prime: int
    domain: Domain
    status: PrimitiveStatus
    added_iteration: int
    last_reviewed: int
    confidence: float = Field(ge=0.0, le=1.0)


class Definition(BaseModel):
    """Definition structure for a primitive."""
    informal: str
    formal: Optional[str] = None
    ostensive: list[str] = Field(default_factory=list)
    negative: list[str] = Field(default_factory=list)


class Relationship(BaseModel):
    """A relationship to another primitive."""
    id: str
    label: str
    reason: str


class PrimitiveDetailed(BaseModel):
    """Full primitive specification."""
    id: str
    symbol: str
    label: str
    definition: Definition
    domain_primary: Domain
    domains_secondary: list[Domain] = Field(default_factory=list)

    contrasts_with: list[Relationship] = Field(default_factory=list)
    presupposes: list[Relationship] = Field(default_factory=list)
    often_combined_with: list[Relationship] = Field(default_factory=list)

    proposed_iteration: int
    accepted_iteration: Optional[int] = None
    prime_number: int
    confidence: float = Field(ge=0.0, le=1.0)
    version: int = 1


class IterationState(BaseModel):
    """Current iteration state."""
    current_iteration: int
    phase: Phase
    cycle_in_phase: int
    last_updated: Optional[datetime] = None

    proposer_mode: str
    proposer_temperature: float
    critic_strictness: float
    domains_priority: list[Domain]

    candidates_to_evaluate: list[str] = Field(default_factory=list)
    gaps_to_fill: list[str] = Field(default_factory=list)

    coverage_score: float = 0.0
    consistency_score: float = 1.0
    recent_acceptance_rate: Optional[float] = None

    total_proposed: int = 0
    total_accepted: int = 0
    total_rejected: int = 0


class Candidate(BaseModel):
    """A candidate primitive proposed by PROPOSER."""
    id: str
    label: str
    domain: Domain
    proposed_symbol: str
    informal_definition: str
    ostensive_examples: list[str] = Field(default_factory=list)
    negative_examples: list[str] = Field(default_factory=list)
    primitiveness_argument: str
    decomposition_resistance: str
    relevance_to_gaps: str = ""
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)


class AttackResult(BaseModel):
    """Result of a CRITIC attack."""
    approach: str
    attempt: str
    result: str
    survived: bool


class Evaluation(BaseModel):
    """CRITIC's evaluation of a candidate."""
    candidate_id: str

    decomposition_attacks: list[AttackResult] = Field(default_factory=list)
    decomposition_survived: bool = True

    circularity_survived: bool = True
    circularity_notes: str = ""

    redundancy_can_be_expressed: bool = False
    redundancy_using: Optional[list[str]] = None

    edge_cases_severity: str = "low"  # low, medium, high

    cultural_assessment: str = "universal"  # universal, near_universal, culturally_bound

    parsimony_necessary: bool = True

    verdict: Verdict
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning_summary: str = ""
    key_insight: Optional[str] = None


class RelationshipGraph(BaseModel):
    """The relationship graph between primitives."""
    version: str = "1.0.0"
    last_updated: Optional[datetime] = None
    iteration: int = 0

    contrasts: list[tuple[str, str]] = Field(default_factory=list)
    presupposes: list[dict[str, Any]] = Field(default_factory=list)
    composes_well: list[list[str]] = Field(default_factory=list)


class MetaReflection(BaseModel):
    """META-REASONER's reflection output."""
    id: str
    iteration_range: tuple[int, int]
    timestamp: datetime

    primitives_added: int = 0
    primitives_rejected: int = 0
    acceptance_rate: float = 0.0
    coverage_before: float = 0.0
    coverage_after: float = 0.0

    patterns_observed: list[dict[str, Any]] = Field(default_factory=list)

    proposer_effectiveness: int = Field(ge=1, le=5, default=3)
    critic_calibration: str = "balanced"  # too_strict, balanced, too_lenient

    strategy_adjustments: list[dict[str, str]] = Field(default_factory=list)
    domain_priorities: list[str] = Field(default_factory=list)

    decision: str = "CONTINUE"  # CONTINUE, PIVOT, CONCLUDE
    decision_justification: str = ""

    predictions: list[dict[str, Any]] = Field(default_factory=list)
    insights: list[dict[str, str]] = Field(default_factory=list)
