#!/usr/bin/env python3
"""
Generate sample evolution data for demonstration and testing.

Creates realistic-looking history data showing how an alphabet might evolve
over multiple iterations.
"""

import sys
from pathlib import Path
import random
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import yaml


def generate_sample_history(iterations: int = 25) -> dict:
    """
    Generate sample history data simulating alphabet evolution.

    Creates data showing:
    - Initial rapid growth phase
    - Gradual convergence toward coverage threshold
    - Realistic fluctuations in acceptance rate
    - Domain expansion over time
    """
    random.seed(42)  # Reproducible results

    snapshots = []
    base_time = datetime.utcnow() - timedelta(hours=iterations)

    # Track cumulative state
    total_primitives = 0
    total_proposed = 0
    coverage = 0.0

    # Domain growth simulation
    domains = [
        "being", "space", "time", "causation", "mind", "matter",
        "quantity", "quality", "relation", "ethics", "emotion",
        "action", "knowledge", "social", "language"
    ]
    domain_counts = {d: 0 for d in domains}

    # Phase simulation parameters
    for i in range(iterations):
        # Simulate different phases
        if i < 5:
            # Early phase: high growth, exploring
            proposed = random.randint(4, 6)
            acceptance_rate = random.uniform(0.4, 0.7)
            coverage_gain = random.uniform(0.03, 0.06)
        elif i < 15:
            # Middle phase: steady growth
            proposed = random.randint(3, 5)
            acceptance_rate = random.uniform(0.3, 0.5)
            coverage_gain = random.uniform(0.02, 0.04)
        else:
            # Late phase: diminishing returns
            proposed = random.randint(2, 4)
            acceptance_rate = random.uniform(0.2, 0.4)
            coverage_gain = random.uniform(0.01, 0.025)

        accepted = int(proposed * acceptance_rate)
        rejected = proposed - accepted

        total_proposed += proposed
        total_primitives += accepted
        prev_coverage = coverage
        coverage = min(0.95, coverage + coverage_gain)

        # Distribute new primitives to domains (weighted by current gaps)
        for _ in range(accepted):
            # Prefer domains with fewer primitives
            weights = [1.0 / (domain_counts[d] + 1) for d in domains]
            total_weight = sum(weights)
            weights = [w / total_weight for w in weights]

            chosen = random.choices(domains, weights=weights)[0]
            domain_counts[chosen] += 1

        # Calculate domain ratios
        total_in_domains = sum(domain_counts.values())
        domain_ratios = {
            d: c / total_in_domains if total_in_domains > 0 else 0
            for d, c in domain_counts.items()
        }

        snapshot = {
            "iteration": i,
            "timestamp": (base_time + timedelta(hours=i)).isoformat() + "Z",
            "counts": {
                "total_primitives": total_primitives,
                "primitives_added": accepted,
                "primitives_rejected": rejected,
                "candidates_proposed": total_proposed,
            },
            "rates": {
                "acceptance_rate": round(accepted / proposed if proposed > 0 else 0, 4),
                "cumulative_acceptance_rate": round(total_primitives / total_proposed if total_proposed > 0 else 0, 4),
            },
            "coverage": {
                "score": round(coverage, 4),
                "delta": round(coverage - prev_coverage, 4),
            },
            "domains": {
                "counts": dict(domain_counts),
                "ratios": {k: round(v, 4) for k, v in domain_ratios.items()},
            },
            "quality": {
                "avg_confidence": round(random.uniform(0.7, 0.9), 4),
                "consistency_score": round(random.uniform(0.85, 1.0), 4),
            },
            "strategy": {
                "phase": "EXPANSION" if i % 4 < 2 else "CONSOLIDATION" if i % 4 == 2 else "COMPOSITION",
                "proposer_mode": random.choice(["DOMAIN_SWEEP", "GAP_FILLING", "DECOMPOSITION_MINING"]),
                "priority_domains": random.sample(domains, 3),
            },
            "gaps": {
                "count": max(0, 20 - int(coverage * 25)),
                "top": random.sample(["intentionality", "causation", "desert", "rights", "obligation"], 3),
            },
        }

        snapshots.append(snapshot)

    return {
        "version": "1.0.0",
        "last_updated": datetime.utcnow().isoformat() + "Z",
        "total_snapshots": len(snapshots),
        "snapshots": snapshots,
    }


def generate_sample_primitives(history: dict) -> list:
    """Generate sample primitive entries matching history."""
    primitives = []
    prime = 2

    # Get final domain counts from history
    final_snapshot = history["snapshots"][-1]
    domain_counts = final_snapshot["domains"]["counts"]

    id_counter = 1
    for domain, count in domain_counts.items():
        for j in range(count):
            # Generate a plausible label
            labels = {
                "being": ["existence", "thing", "identity", "unity", "essence", "substance"],
                "space": ["extension", "location", "boundary", "inside", "outside", "distance"],
                "time": ["duration", "succession", "simultaneity", "before", "after", "now"],
                "causation": ["cause", "effect", "influence", "power", "change", "process"],
                "mind": ["thought", "perception", "consciousness", "intention", "belief", "desire"],
                "matter": ["body", "mass", "force", "motion", "energy", "resistance"],
                "quantity": ["one", "many", "all", "some", "none", "number"],
                "quality": ["property", "degree", "kind", "similar", "different", "same"],
                "relation": ["between", "with", "towards", "from", "to", "connection"],
                "ethics": ["good", "bad", "ought", "right", "wrong", "value"],
                "emotion": ["pleasure", "pain", "fear", "desire", "love", "anger"],
                "action": ["do", "make", "act", "move", "change", "create"],
                "knowledge": ["know", "believe", "true", "false", "certain", "possible"],
                "social": ["person", "group", "rule", "agreement", "promise", "obligation"],
                "language": ["meaning", "reference", "sign", "symbol", "express", "communicate"],
            }

            available = labels.get(domain, [f"{domain}_{j}"])
            label = available[j % len(available)]

            # Find next prime
            while not is_prime(prime):
                prime += 1

            primitives.append({
                "id": f"PRM_{id_counter:04d}",
                "label": label,
                "prime": prime,
                "domain": domain,
                "status": "stable" if id_counter < len(primitives) * 0.8 else "recent",
                "added_iteration": min(id_counter // 2, len(history["snapshots"]) - 1),
                "last_reviewed": len(history["snapshots"]) - 1,
                "confidence": round(random.uniform(0.7, 0.95), 2),
            })

            prime += 1
            id_counter += 1

    return primitives


def is_prime(n: int) -> bool:
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


def main():
    """Generate and save sample data."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate sample evolution data")
    parser.add_argument("--path", "-p", type=Path, default=Path("."),
                       help="Path to alphabet repository")
    parser.add_argument("--iterations", "-n", type=int, default=25,
                       help="Number of iterations to simulate")

    args = parser.parse_args()
    base_path = args.path

    print(f"Generating sample data for {args.iterations} iterations...")

    # Generate history
    history = generate_sample_history(args.iterations)

    # Save history
    analytics_dir = base_path / "analytics"
    analytics_dir.mkdir(parents=True, exist_ok=True)

    history_path = analytics_dir / "history.yaml"
    with open(history_path, "w") as f:
        yaml.dump(history, f, default_flow_style=False, sort_keys=False)
    print(f"  Saved history to {history_path}")

    # Generate primitives
    primitives = generate_sample_primitives(history)

    # Update alphabet index
    final_snapshot = history["snapshots"][-1]

    index = {
        "alphabet_index": {
            "version": "1.0.0",
            "last_updated": datetime.utcnow().isoformat() + "Z",
            "iteration": len(history["snapshots"]) - 1,
            "statistics": {
                "total_primitives": len(primitives),
                "by_domain": final_snapshot["domains"]["counts"],
                "by_status": {"stable": int(len(primitives) * 0.8), "recent": len(primitives) - int(len(primitives) * 0.8)},
            },
            "primitives": primitives,
        }
    }

    index_path = base_path / "alphabet" / "primitives" / "index.yaml"
    with open(index_path, "w") as f:
        yaml.dump(index, f, default_flow_style=False, sort_keys=False)
    print(f"  Updated alphabet index at {index_path}")

    # Update iteration state
    state = {
        "iteration_state": {
            "current_iteration": len(history["snapshots"]) - 1,
            "phase": final_snapshot["strategy"]["phase"],
            "cycle_in_phase": 0,
            "current_strategy": {
                "proposer_mode": final_snapshot["strategy"]["proposer_mode"],
                "proposer_temperature": 0.7,
                "critic_strictness": 0.5,
                "domains_priority": final_snapshot["strategy"]["priority_domains"],
            },
            "pending": {
                "candidates_to_evaluate": [],
                "gaps_to_fill": final_snapshot["gaps"]["top"],
            },
            "metrics": {
                "coverage_score": final_snapshot["coverage"]["score"],
                "consistency_score": final_snapshot["quality"]["consistency_score"],
                "recent_acceptance_rate": final_snapshot["rates"]["cumulative_acceptance_rate"],
            },
            "history": {
                "total_proposed": final_snapshot["counts"]["candidates_proposed"],
                "total_accepted": final_snapshot["counts"]["total_primitives"],
                "total_rejected": final_snapshot["counts"]["candidates_proposed"] - final_snapshot["counts"]["total_primitives"],
            },
        }
    }

    state_path = base_path / "reasoning" / "iteration_state.yaml"
    with open(state_path, "w") as f:
        yaml.dump(state, f, default_flow_style=False, sort_keys=False)
    print(f"  Updated iteration state at {state_path}")

    print("\nSample data generation complete!")
    print(f"  • {len(history['snapshots'])} iteration snapshots")
    print(f"  • {len(primitives)} primitives")
    print(f"  • Coverage: {final_snapshot['coverage']['score']:.1%}")

    print("\nYou can now run:")
    print("  python tools/analytics.py status")
    print("  python tools/analytics.py convergence --detailed")
    print("  python tools/analytics.py figures")
    print("  python tools/analytics.py report")


if __name__ == "__main__":
    main()
