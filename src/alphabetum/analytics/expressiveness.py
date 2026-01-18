"""
Expressiveness Metrics for ALPHABETUM
=====================================

Information-theoretic measures of alphabet expressiveness and completeness.

Key Metrics:
- Coverage: % of canonical corpus expressible
- Description Length (DL): Average primitives per concept
- Shannon Entropy: Information density of primitive usage
- MDL Score: Minimum description length efficiency
- Expressiveness Index: Composite measure of alphabet power

Based on Leibniz's vision and Shannon's information theory.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import math
import yaml
from collections import Counter

from ..state.manager import StateManager
from ..state.models import PrimitiveIndexEntry


@dataclass
class EncodedConcept:
    """A concept encoded using the alphabet."""
    id: str
    name: str
    source: str
    primitives_used: list[str]
    symbols_used: list[str]
    prime_product: int
    description_length: int  # Number of primitives
    coverage_ratio: float  # What fraction of decomposition is available
    is_fully_expressible: bool
    missing_primitives: list[str]
    formula: str


@dataclass
class CorpusEncodingResult:
    """Results of encoding an entire corpus."""
    corpus_name: str
    total_concepts: int
    fully_expressible: int
    partially_expressible: int
    inexpressible: int
    coverage_score: float
    weighted_coverage: float
    average_description_length: float
    encodings: list[EncodedConcept]
    primitive_usage: dict[str, int]  # How often each primitive is used
    symbol_frequency: dict[str, int]


@dataclass
class ExpressivenessMetrics:
    """Complete expressiveness analysis."""
    # Coverage metrics
    corpus_coverage: float  # % of corpus fully expressible
    weighted_coverage: float  # Weighted by source importance
    partial_coverage: float  # Including partial expressions

    # Information-theoretic metrics
    shannon_entropy: float  # Entropy of primitive usage
    normalized_entropy: float  # Entropy / max possible entropy
    description_length_avg: float  # Mean primitives per concept
    description_length_std: float  # Variance in description length

    # MDL metrics
    mdl_score: float  # Minimum description length efficiency
    compression_ratio: float  # vs naive enumeration
    bits_per_concept: float  # log2(prime_product) average

    # Efficiency metrics
    primitives_count: int
    concepts_expressible: int
    expressiveness_ratio: float  # concepts / primitives
    marginal_value: dict[str, float]  # Value added by each primitive

    # Detailed results
    corpus_results: list[CorpusEncodingResult]
    primitive_importance: dict[str, float]  # Ranked by usage


@dataclass
class IterationExpressivenessReport:
    """Expressiveness report for a single iteration."""
    iteration: int
    timestamp: str
    metrics: ExpressivenessMetrics
    delta_from_previous: Optional[dict]
    recommendations: list[str]


class ExpressivenessAnalyzer:
    """
    Analyzes the expressiveness of the alphabet against canonical corpora.

    Uses information-theoretic measures to quantify how well the alphabet
    captures fundamental concepts from logical treatises.
    """

    def __init__(self, state_manager: StateManager):
        self.state_manager = state_manager
        self.base_path = state_manager.base_path
        self.primitives: list[PrimitiveIndexEntry] = []
        self.primitive_map: dict[str, PrimitiveIndexEntry] = {}
        self.corpus: dict = {}
        self._load_data()

    def _load_data(self):
        """Load primitives and corpus."""
        self.primitives = self.state_manager.load_alphabet_index()
        self.primitive_map = {p.label: p for p in self.primitives}

        corpus_path = self.base_path / "validation" / "corpora" / "logical_treatises.yaml"
        if corpus_path.exists():
            with open(corpus_path) as f:
                self.corpus = yaml.safe_load(f)

    def analyze(self) -> ExpressivenessMetrics:
        """Run complete expressiveness analysis."""
        corpus_results = self._encode_all_corpora()

        # Calculate aggregate metrics
        total_concepts = sum(r.total_concepts for r in corpus_results)
        total_expressible = sum(r.fully_expressible for r in corpus_results)
        total_partial = sum(r.partially_expressible for r in corpus_results)

        # Aggregate primitive usage
        all_usage: Counter = Counter()
        all_descriptions: list[int] = []

        for result in corpus_results:
            all_usage.update(result.primitive_usage)
            for enc in result.encodings:
                if enc.is_fully_expressible:
                    all_descriptions.append(enc.description_length)

        # Shannon entropy of primitive usage
        entropy = self._calculate_entropy(all_usage)
        max_entropy = math.log2(len(self.primitives)) if self.primitives else 0
        normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0

        # Description length statistics
        dl_avg = sum(all_descriptions) / len(all_descriptions) if all_descriptions else 0
        dl_std = self._std_dev(all_descriptions) if all_descriptions else 0

        # MDL score: efficiency of representation
        mdl_score = self._calculate_mdl(corpus_results)

        # Compression ratio vs naive enumeration
        compression = self._calculate_compression(total_concepts)

        # Bits per concept
        bits_per = self._calculate_bits_per_concept(corpus_results)

        # Weighted coverage
        weighted_cov = self._calculate_weighted_coverage(corpus_results)

        # Primitive importance ranking
        importance = self._rank_primitive_importance(corpus_results)

        # Marginal value of each primitive
        marginal = self._calculate_marginal_value(corpus_results)

        return ExpressivenessMetrics(
            corpus_coverage=total_expressible / total_concepts if total_concepts else 0,
            weighted_coverage=weighted_cov,
            partial_coverage=(total_expressible + total_partial) / total_concepts if total_concepts else 0,
            shannon_entropy=entropy,
            normalized_entropy=normalized_entropy,
            description_length_avg=dl_avg,
            description_length_std=dl_std,
            mdl_score=mdl_score,
            compression_ratio=compression,
            bits_per_concept=bits_per,
            primitives_count=len(self.primitives),
            concepts_expressible=total_expressible,
            expressiveness_ratio=total_expressible / len(self.primitives) if self.primitives else 0,
            marginal_value=marginal,
            corpus_results=corpus_results,
            primitive_importance=importance
        )

    def _encode_all_corpora(self) -> list[CorpusEncodingResult]:
        """Encode all sections of the corpus."""
        results = []

        corpus_data = self.corpus.get("corpus", {})
        for section_name, section in corpus_data.items():
            if isinstance(section, dict) and "concepts" in section:
                result = self._encode_corpus_section(
                    section_name,
                    section.get("source", section_name),
                    section.get("weight", 1.0),
                    section["concepts"]
                )
                results.append(result)

        return results

    def _encode_corpus_section(
        self,
        name: str,
        source: str,
        weight: float,
        concepts: list[dict]
    ) -> CorpusEncodingResult:
        """Encode a single corpus section."""
        encodings = []
        primitive_usage: Counter = Counter()
        symbol_usage: Counter = Counter()
        fully_expr = 0
        partial_expr = 0
        inexpressible = 0

        primitive_labels = set(self.primitive_map.keys())

        for concept in concepts:
            encoding = self._encode_concept(concept, primitive_labels)
            encodings.append(encoding)

            if encoding.is_fully_expressible:
                fully_expr += 1
                primitive_usage.update(encoding.primitives_used)
                symbol_usage.update(encoding.symbols_used)
            elif encoding.coverage_ratio > 0:
                partial_expr += 1
                primitive_usage.update(encoding.primitives_used)
                symbol_usage.update(encoding.symbols_used)
            else:
                inexpressible += 1

        total = len(concepts)
        coverage = fully_expr / total if total > 0 else 0

        avg_dl = sum(e.description_length for e in encodings if e.is_fully_expressible)
        count = sum(1 for e in encodings if e.is_fully_expressible)
        avg_dl = avg_dl / count if count > 0 else 0

        return CorpusEncodingResult(
            corpus_name=name,
            total_concepts=total,
            fully_expressible=fully_expr,
            partially_expressible=partial_expr,
            inexpressible=inexpressible,
            coverage_score=coverage,
            weighted_coverage=coverage * weight,
            average_description_length=avg_dl,
            encodings=encodings,
            primitive_usage=dict(primitive_usage),
            symbol_frequency=dict(symbol_usage)
        )

    def _encode_concept(
        self,
        concept: dict,
        available_primitives: set[str]
    ) -> EncodedConcept:
        """Encode a single concept using available primitives."""
        decomp = concept.get("decomposition", {})
        required_primitives = decomp.get("primitives", [])
        formula = decomp.get("formula", "")
        confidence = decomp.get("confidence", 0.5)

        # Find which primitives we have
        have = [p for p in required_primitives if p in available_primitives]
        missing = [p for p in required_primitives if p not in available_primitives]

        # Calculate coverage ratio
        coverage = len(have) / len(required_primitives) if required_primitives else 0
        is_full = coverage >= 0.7 and confidence >= 0.6  # Threshold for "expressible"

        # Get symbols and calculate prime product
        symbols = []
        prime_product = 1
        for prim_label in have:
            prim = self.primitive_map.get(prim_label)
            if prim:
                symbols.append(prim.symbol)
                prime_product *= prim.prime

        return EncodedConcept(
            id=concept.get("id", ""),
            name=concept.get("name", ""),
            source=concept.get("source", ""),
            primitives_used=have,
            symbols_used=symbols,
            prime_product=prime_product,
            description_length=len(have),
            coverage_ratio=coverage,
            is_fully_expressible=is_full,
            missing_primitives=missing,
            formula=formula
        )

    def _calculate_entropy(self, usage: Counter) -> float:
        """Calculate Shannon entropy of primitive usage distribution."""
        if not usage:
            return 0.0

        total = sum(usage.values())
        if total == 0:
            return 0.0

        entropy = 0.0
        for count in usage.values():
            if count > 0:
                p = count / total
                entropy -= p * math.log2(p)

        return entropy

    def _std_dev(self, values: list) -> float:
        """Calculate standard deviation."""
        if len(values) < 2:
            return 0.0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return math.sqrt(variance)

    def _calculate_mdl(self, corpus_results: list[CorpusEncodingResult]) -> float:
        """
        Calculate Minimum Description Length score.

        MDL = (description of data using model) + (description of model)
        Lower is better, we invert for "score" interpretation.
        """
        # Model complexity: number of primitives
        model_bits = len(self.primitives) * math.log2(len(self.primitives) + 1) if self.primitives else 0

        # Data description: sum of log2(prime_products) for encoded concepts
        data_bits = 0
        count = 0
        for result in corpus_results:
            for enc in result.encodings:
                if enc.is_fully_expressible and enc.prime_product > 0:
                    data_bits += math.log2(enc.prime_product)
                    count += 1

        if count == 0:
            return 0.0

        avg_data_bits = data_bits / count

        # MDL score: inverse of (model + data) cost, normalized
        total_cost = model_bits + avg_data_bits
        if total_cost == 0:
            return 0.0

        # Score: higher is better (more efficient encoding)
        return 1.0 / (1.0 + total_cost / 100)

    def _calculate_compression(self, total_concepts: int) -> float:
        """
        Calculate compression ratio vs naive enumeration.

        Naive: each concept is a unique symbol (total_concepts bits per concept)
        Our encoding: log2(prime_product) bits per concept
        """
        if not self.primitives or total_concepts == 0:
            return 1.0

        # Naive encoding: enumerate all concepts
        naive_bits = math.log2(total_concepts) if total_concepts > 0 else 0

        # Our encoding: average log2(prime_product)
        max_prime = max(p.prime for p in self.primitives)
        avg_composition_size = len(self.primitives) / 2  # Estimate
        our_bits = avg_composition_size * math.log2(max_prime)

        if our_bits == 0:
            return 1.0

        return naive_bits / our_bits

    def _calculate_bits_per_concept(self, corpus_results: list[CorpusEncodingResult]) -> float:
        """Calculate average bits needed per concept."""
        total_bits = 0
        count = 0

        for result in corpus_results:
            for enc in result.encodings:
                if enc.is_fully_expressible and enc.prime_product > 1:
                    total_bits += math.log2(enc.prime_product)
                    count += 1

        return total_bits / count if count > 0 else 0

    def _calculate_weighted_coverage(self, corpus_results: list[CorpusEncodingResult]) -> float:
        """Calculate coverage weighted by corpus importance."""
        weights = self.corpus.get("metadata", {}).get("coverage_weights", {})

        total_weight = 0
        weighted_sum = 0

        for result in corpus_results:
            weight = weights.get(result.corpus_name, 1.0)
            total_weight += weight
            weighted_sum += result.coverage_score * weight

        return weighted_sum / total_weight if total_weight > 0 else 0

    def _rank_primitive_importance(
        self,
        corpus_results: list[CorpusEncodingResult]
    ) -> dict[str, float]:
        """Rank primitives by their importance in encoding the corpus."""
        total_usage: Counter = Counter()

        for result in corpus_results:
            total_usage.update(result.primitive_usage)

        total = sum(total_usage.values())
        if total == 0:
            return {}

        return {k: v / total for k, v in total_usage.most_common()}

    def _calculate_marginal_value(self, corpus_results: list[CorpusEncodingResult]) -> dict[str, float]:
        """
        Calculate the marginal value of each primitive.

        This estimates how much coverage we'd lose if we removed each primitive.
        Uses pre-computed corpus results to avoid recursion.
        """
        marginal = {}

        if not corpus_results:
            return marginal

        total = sum(r.total_concepts for r in corpus_results)
        if total == 0:
            return marginal

        # For each primitive, estimate its contribution
        for prim in self.primitives:
            # Count concepts that depend on this primitive
            dependent_concepts = 0
            for result in corpus_results:
                for enc in result.encodings:
                    if prim.label in enc.primitives_used:
                        dependent_concepts += 1

            marginal[prim.label] = dependent_concepts / total

        return marginal

    def generate_report(self, iteration: int) -> dict:
        """Generate a YAML-serializable expressiveness report."""
        metrics = self.analyze()

        # Find challenge corpus coverage specifically
        challenge_coverage = 0.0
        for r in metrics.corpus_results:
            if r.corpus_name == "challenge_concepts":
                challenge_coverage = r.coverage_score

        report = {
            "expressiveness_report": {
                "iteration": iteration,
                "summary": {
                    "primitives": metrics.primitives_count,
                    "corpus_coverage": f"{metrics.corpus_coverage:.1%}",
                    "weighted_coverage": f"{metrics.weighted_coverage:.1%}",
                    "concepts_expressible": metrics.concepts_expressible,
                    "expressiveness_ratio": round(metrics.expressiveness_ratio, 2),
                },
                "information_theory": {
                    "shannon_entropy": round(metrics.shannon_entropy, 3),
                    "normalized_entropy": round(metrics.normalized_entropy, 3),
                    "bits_per_concept": round(metrics.bits_per_concept, 2),
                    "mdl_score": round(metrics.mdl_score, 4),
                    "compression_ratio": round(metrics.compression_ratio, 3),
                },
                "description_length": {
                    "average": round(metrics.description_length_avg, 2),
                    "std_dev": round(metrics.description_length_std, 2),
                },
                "primitive_importance": {
                    k: round(v, 3) for k, v in list(metrics.primitive_importance.items())[:11]
                },
                "corpus_breakdown": [
                    {
                        "name": r.corpus_name,
                        "total": r.total_concepts,
                        "expressible": r.fully_expressible,
                        "partial": r.partially_expressible,
                        "coverage": f"{r.coverage_score:.1%}",
                    }
                    for r in metrics.corpus_results
                ]
            }
        }

        return report

    def append_to_history(self, iteration: int, notes: str = "") -> None:
        """Append current metrics to the history file."""
        from datetime import datetime

        metrics = self.analyze()

        # Find challenge corpus coverage
        challenge_coverage = 0.0
        for r in metrics.corpus_results:
            if r.corpus_name == "challenge_concepts":
                challenge_coverage = r.coverage_score

        history_path = self.base_path / "reports" / "expressiveness" / "history.yaml"

        # Load existing history
        if history_path.exists():
            with open(history_path) as f:
                history_data = yaml.safe_load(f) or {}
        else:
            history_data = {"history": []}

        history = history_data.get("history", [])

        # Check if this iteration already exists
        existing_idx = None
        for i, entry in enumerate(history):
            if entry.get("iteration") == iteration:
                existing_idx = i
                break

        new_entry = {
            "iteration": iteration,
            "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "primitives": metrics.primitives_count,
            "corpus_coverage": round(metrics.corpus_coverage, 3),
            "weighted_coverage": round(metrics.weighted_coverage, 3),
            "concepts_expressible": metrics.concepts_expressible,
            "shannon_entropy": round(metrics.shannon_entropy, 3),
            "normalized_entropy": round(metrics.normalized_entropy, 3),
            "bits_per_concept": round(metrics.bits_per_concept, 2),
            "mdl_score": round(metrics.mdl_score, 4),
            "expressiveness_ratio": round(metrics.expressiveness_ratio, 2),
            "challenge_coverage": round(challenge_coverage, 3),
        }
        if notes:
            new_entry["notes"] = notes

        if existing_idx is not None:
            history[existing_idx] = new_entry
        else:
            history.append(new_entry)

        # Sort by iteration
        history.sort(key=lambda x: x.get("iteration", 0))

        history_data["history"] = history

        # Write back
        history_path.parent.mkdir(parents=True, exist_ok=True)
        with open(history_path, "w") as f:
            yaml.dump(history_data, f, default_flow_style=False, sort_keys=False)

    def generate_encoding_table(self) -> str:
        """Generate a markdown table showing concept encodings with symbols."""
        metrics = self.analyze()

        lines = [
            "# Corpus Encoding Analysis",
            "",
            "Concepts from canonical logical treatises encoded using the ALPHABETUM.",
            "",
        ]

        for result in metrics.corpus_results:
            lines.extend([
                f"## {result.corpus_name.replace('_', ' ').title()}",
                "",
                f"Coverage: {result.coverage_score:.1%} ({result.fully_expressible}/{result.total_concepts})",
                "",
                "| Concept | Primitives | Symbols | Prime | Status |",
                "|---------|------------|---------|-------|--------|",
            ])

            for enc in result.encodings:
                status = "Full" if enc.is_fully_expressible else f"Partial ({enc.coverage_ratio:.0%})"
                prims = ", ".join(enc.primitives_used) if enc.primitives_used else "-"
                syms = " ".join(enc.symbols_used) if enc.symbols_used else "-"
                prime = enc.prime_product if enc.prime_product > 1 else "-"

                lines.append(f"| {enc.name} | {prims} | {syms} | {prime} | {status} |")

            if result.encodings:
                # Show missing primitives summary
                all_missing: Counter = Counter()
                for enc in result.encodings:
                    all_missing.update(enc.missing_primitives)

                if all_missing:
                    lines.extend([
                        "",
                        "**Missing primitives needed:**",
                    ])
                    for prim, count in all_missing.most_common(5):
                        lines.append(f"- `{prim}` ({count} concepts)")

            lines.append("")

        # Summary statistics
        lines.extend([
            "## Summary Statistics",
            "",
            "| Metric | Value |",
            "|--------|-------|",
            f"| Total Primitives | {metrics.primitives_count} |",
            f"| Corpus Coverage | {metrics.corpus_coverage:.1%} |",
            f"| Weighted Coverage | {metrics.weighted_coverage:.1%} |",
            f"| Shannon Entropy | {metrics.shannon_entropy:.3f} |",
            f"| Bits per Concept | {metrics.bits_per_concept:.2f} |",
            f"| MDL Score | {metrics.mdl_score:.4f} |",
            f"| Avg Description Length | {metrics.description_length_avg:.2f} primitives |",
            "",
        ])

        return "\n".join(lines)


def run_expressiveness_analysis(base_path: Path) -> ExpressivenessMetrics:
    """Convenience function to run expressiveness analysis."""
    state_manager = StateManager(base_path)
    analyzer = ExpressivenessAnalyzer(state_manager)
    return analyzer.analyze()
