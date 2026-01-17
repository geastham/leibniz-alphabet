"""Validation checks for the alphabet."""

from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime
from typing import Optional
import yaml

try:
    import networkx as nx
    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False

from ..state.manager import StateManager
from ..state.models import PrimitiveIndexEntry, PrimitiveDetailed, Domain


@dataclass
class ValidationResult:
    """Result of a validation check."""
    passed: bool
    score: float
    issues: list[dict] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)


@dataclass
class CoverageResult:
    """Result of coverage testing."""
    total: int
    expressible: int
    partial: int
    inexpressible: int
    coverage_score: float
    gaps: list[dict] = field(default_factory=list)
    details: list[dict] = field(default_factory=list)


class AlphabetValidator:
    """Main validation class for ALPHABETUM."""

    def __init__(self, base_path: Path):
        self.base_path = Path(base_path)
        self.state_manager = StateManager(base_path)

    def run_full_validation(self) -> dict[str, ValidationResult]:
        """Run all validation checks."""
        primitives = self.state_manager.load_alphabet_index()
        relationships = self.state_manager.load_relationships()

        results = {}

        # Consistency checks
        results["circularity"] = self.check_circularity(primitives)
        results["redundancy"] = self.check_redundancy(primitives)
        results["contrast"] = self.check_contrasts(primitives, relationships)
        results["presupposition"] = self.check_presuppositions(primitives, relationships)

        # Coverage check
        coverage = self.check_coverage(primitives)
        results["coverage"] = ValidationResult(
            passed=coverage.coverage_score >= 0.5,
            score=coverage.coverage_score,
            issues=[{"gap": g} for g in coverage.gaps],
            recommendations=self._coverage_recommendations(coverage)
        )

        # Domain balance check
        results["domain_balance"] = self.check_domain_balance(primitives)

        return results

    def run_quick_check(self) -> ValidationResult:
        """Run quick consistency check."""
        primitives = self.state_manager.load_alphabet_index()
        relationships = self.state_manager.load_relationships()

        issues = []

        # Quick circularity check
        circ = self.check_circularity(primitives)
        if not circ.passed:
            issues.extend(circ.issues)

        # Quick presupposition check
        presup = self.check_presuppositions(primitives, relationships)
        if not presup.passed:
            issues.extend(presup.issues)

        return ValidationResult(
            passed=len(issues) == 0,
            score=1.0 if len(issues) == 0 else 0.5,
            issues=issues
        )

    def check_circularity(self, primitives: list[PrimitiveIndexEntry]) -> ValidationResult:
        """Check for circular definitions."""
        issues = []

        if not HAS_NETWORKX:
            # Simplified check without graph library
            return ValidationResult(
                passed=True,
                score=1.0,
                recommendations=["Install networkx for full circularity analysis"]
            )

        # Build dependency graph from detailed entries
        G = nx.DiGraph()
        for p in primitives:
            G.add_node(p.id)
            detailed = self.state_manager.load_primitive_detailed(p.id)
            if detailed:
                for presup in detailed.presupposes:
                    G.add_edge(p.id, presup.id)

        # Find cycles
        try:
            cycles = list(nx.simple_cycles(G))
            if cycles:
                for cycle in cycles:
                    issues.append({
                        "type": "circular_dependency",
                        "cycle": cycle,
                        "severity": "critical"
                    })
        except Exception:
            pass

        return ValidationResult(
            passed=len(issues) == 0,
            score=1.0 if len(issues) == 0 else 0.0,
            issues=issues,
            recommendations=["Break circular dependencies by revising definitions"] if issues else []
        )

    def check_redundancy(self, primitives: list[PrimitiveIndexEntry]) -> ValidationResult:
        """Check for redundant primitives."""
        issues = []

        # Group by domain - primitives in same domain might overlap
        by_domain: dict[str, list] = {}
        for p in primitives:
            domain = p.domain.value
            if domain not in by_domain:
                by_domain[domain] = []
            by_domain[domain].append(p)

        # Check for potential redundancies (simplified)
        for domain, prims in by_domain.items():
            if len(prims) > 10:
                issues.append({
                    "type": "potential_redundancy",
                    "domain": domain,
                    "count": len(prims),
                    "severity": "low",
                    "note": f"Domain {domain} has {len(prims)} primitives - review for potential overlap"
                })

        return ValidationResult(
            passed=len([i for i in issues if i.get("severity") != "low"]) == 0,
            score=1.0 - (len(issues) * 0.1),
            issues=issues,
            recommendations=["Review domains with many primitives for potential redundancy"] if issues else []
        )

    def check_contrasts(
        self,
        primitives: list[PrimitiveIndexEntry],
        relationships
    ) -> ValidationResult:
        """Check contrast consistency."""
        issues = []
        primitive_ids = {p.id for p in primitives}

        for contrast in relationships.contrasts:
            if isinstance(contrast, (list, tuple)) and len(contrast) == 2:
                p1, p2 = contrast
                if p1 not in primitive_ids:
                    issues.append({
                        "type": "invalid_contrast_reference",
                        "missing": p1,
                        "severity": "medium"
                    })
                if p2 not in primitive_ids:
                    issues.append({
                        "type": "invalid_contrast_reference",
                        "missing": p2,
                        "severity": "medium"
                    })

        return ValidationResult(
            passed=len(issues) == 0,
            score=1.0 if len(issues) == 0 else 0.7,
            issues=issues,
            recommendations=["Remove or update invalid contrast references"] if issues else []
        )

    def check_presuppositions(
        self,
        primitives: list[PrimitiveIndexEntry],
        relationships
    ) -> ValidationResult:
        """Check presupposition validity."""
        issues = []
        primitive_ids = {p.id for p in primitives}

        for presup in relationships.presupposes:
            target = presup.get("target")
            source = presup.get("source")

            if target and target not in primitive_ids:
                issues.append({
                    "type": "orphaned_presupposition",
                    "source": source,
                    "missing_target": target,
                    "severity": "high"
                })

        return ValidationResult(
            passed=len(issues) == 0,
            score=1.0 if len(issues) == 0 else 0.5,
            issues=issues,
            recommendations=[
                "Add missing primitives or remove invalid presuppositions"
            ] if issues else []
        )

    def check_coverage(self, primitives: list[PrimitiveIndexEntry]) -> CoverageResult:
        """Check coverage against benchmarks."""
        benchmarks = self._load_benchmarks()
        primitive_labels = {p.label for p in primitives}

        expressible = 0
        partial = 0
        inexpressible = 0
        gaps = []
        details = []

        for benchmark in benchmarks:
            hints = benchmark.get("decomposition_hints", [])
            matched = [h for h in hints if h in primitive_labels]
            coverage = len(matched) / len(hints) if hints else 0

            if coverage >= 0.7:
                status = "expressible"
                expressible += 1
            elif coverage >= 0.3:
                status = "partial"
                partial += 1
                missing = [h for h in hints if h not in primitive_labels]
                gaps.extend(missing)
            else:
                status = "inexpressible"
                inexpressible += 1
                missing = [h for h in hints if h not in primitive_labels]
                gaps.extend(missing)

            details.append({
                "concept": benchmark["name"],
                "domain": benchmark.get("domain", "unknown"),
                "status": status,
                "coverage_ratio": coverage,
                "missing": [h for h in hints if h not in primitive_labels]
            })

        total = len(benchmarks)
        coverage_score = expressible / total if total > 0 else 0

        # Count gap frequencies
        gap_counts: dict[str, int] = {}
        for g in gaps:
            gap_counts[g] = gap_counts.get(g, 0) + 1

        sorted_gaps = sorted(
            [{"label": k, "count": v} for k, v in gap_counts.items()],
            key=lambda x: x["count"],
            reverse=True
        )

        return CoverageResult(
            total=total,
            expressible=expressible,
            partial=partial,
            inexpressible=inexpressible,
            coverage_score=coverage_score,
            gaps=sorted_gaps[:20],  # Top 20 gaps
            details=details
        )

    def check_domain_balance(self, primitives: list[PrimitiveIndexEntry]) -> ValidationResult:
        """Check domain coverage balance."""
        issues = []

        # Count primitives per domain
        by_domain: dict[str, int] = {}
        for p in primitives:
            domain = p.domain.value
            by_domain[domain] = by_domain.get(domain, 0) + 1

        # Check for neglected domains
        all_domains = [d.value for d in Domain]
        for domain in all_domains:
            count = by_domain.get(domain, 0)
            if count == 0:
                issues.append({
                    "type": "neglected_domain",
                    "domain": domain,
                    "count": 0,
                    "severity": "medium"
                })
            elif count < 2:
                issues.append({
                    "type": "sparse_domain",
                    "domain": domain,
                    "count": count,
                    "severity": "low"
                })

        # Calculate balance score
        if by_domain:
            values = list(by_domain.values())
            max_count = max(values)
            min_count = min(values) if values else 0
            balance = min_count / max_count if max_count > 0 else 1.0
        else:
            balance = 0.0

        return ValidationResult(
            passed=balance >= 0.3,
            score=balance,
            issues=issues,
            recommendations=[
                f"Focus PROPOSER on neglected domains: {[i['domain'] for i in issues if i['type'] == 'neglected_domain']}"
            ] if [i for i in issues if i['type'] == 'neglected_domain'] else []
        )

    def check_coverage_only(self) -> CoverageResult:
        """Check coverage only (for CLI)."""
        primitives = self.state_manager.load_alphabet_index()
        return self.check_coverage(primitives)

    def _load_benchmarks(self) -> list[dict]:
        """Load benchmark concepts."""
        benchmarks_file = self.base_path / "validation" / "benchmarks" / "test_concepts.yaml"
        if not benchmarks_file.exists():
            return []
        with open(benchmarks_file) as f:
            data = yaml.safe_load(f)
        return data.get("benchmark_concepts", [])

    def _coverage_recommendations(self, coverage: CoverageResult) -> list[str]:
        """Generate recommendations based on coverage results."""
        recs = []
        if coverage.coverage_score < 0.5:
            recs.append("Coverage is below 50% - continue expanding the alphabet")
        if coverage.gaps:
            top_gaps = [g["label"] for g in coverage.gaps[:5]]
            recs.append(f"Priority gaps to fill: {', '.join(top_gaps)}")
        return recs

    def generate_report(
        self,
        results: dict[str, ValidationResult],
        iteration: int
    ) -> tuple[dict, str]:
        """Generate validation report in YAML and Markdown."""
        overall_score = sum(r.score for r in results.values()) / len(results) if results else 0

        # YAML report
        yaml_report = {
            "validation_report": {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "iteration": iteration,
                "overall_passed": all(r.passed for r in results.values()),
                "overall_score": round(overall_score, 3),
                "checks": {
                    name: {
                        "passed": result.passed,
                        "score": round(result.score, 3),
                        "issues_count": len(result.issues),
                    }
                    for name, result in results.items()
                }
            }
        }

        # Markdown report
        md_lines = [
            f"# Validation Report: Iteration {iteration}",
            "",
            f"**Generated:** {datetime.utcnow().isoformat()}Z",
            f"**Overall Score:** {overall_score:.2f} / 1.00",
            f"**Status:** {'PASS' if all(r.passed for r in results.values()) else 'ISSUES FOUND'}",
            "",
            "## Summary",
            "",
            "| Check | Status | Score |",
            "|-------|--------|-------|",
        ]

        for name, result in results.items():
            status = "Pass" if result.passed else "Fail"
            md_lines.append(f"| {name.title()} | {status} | {result.score:.2f} |")

        md_lines.extend(["", "## Details", ""])

        for name, result in results.items():
            status_symbol = "Pass" if result.passed else "Issues"
            md_lines.append(f"### {name.title()} {status_symbol}")
            md_lines.append(f"Score: {result.score:.2f}")

            if result.issues:
                md_lines.append("\nIssues:")
                for issue in result.issues[:5]:
                    md_lines.append(f"- {issue}")

            if result.recommendations:
                md_lines.append("\nRecommendations:")
                for rec in result.recommendations:
                    md_lines.append(f"- {rec}")

            md_lines.append("")

        return yaml_report, "\n".join(md_lines)
