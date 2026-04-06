from __future__ import annotations

import csv
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any


FEATURE_KEYS = [
    "expected_upside",
    "drive_strength",
    "stability",
    "liquidity",
    "resonance",
    "concept_support",
    "leader_component_score",
    "non_junk_composite_score",
    "context_sector_heat",
    "context_sector_breadth",
]

SUPPORTED_SECTOR_IDS = {"BK0963", "BK0480", "BK0808", "BK0994", "BK0814"}


def _to_float(value: str) -> float:
    return float(value) if value not in ("", None) else 0.0


@dataclass(slots=True)
class V124QCommercialAerospaceUniverseTriageReport:
    summary: dict[str, Any]
    control_eligible_rows: list[dict[str, Any]]
    confirmation_rows: list[dict[str, Any]]
    pending_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "control_eligible_rows": self.control_eligible_rows,
            "confirmation_rows": self.confirmation_rows,
            "pending_rows": self.pending_rows,
            "interpretation": self.interpretation,
        }


class V124QCommercialAerospaceUniverseTriageAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.merged_universe_path = (
            repo_root / "data" / "training" / "commercial_aerospace_merged_universe_v1.csv"
        )
        self.stock_snapshot_path = (
            repo_root
            / "data"
            / "derived"
            / "stock_snapshots"
            / "market_research_stock_snapshots_v6_catalyst_supported_carry_persistence_refresh.csv"
        )

    def _load_csv(self, path: Path) -> list[dict[str, str]]:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            return list(csv.DictReader(handle))

    def _aggregate_supported(self) -> dict[str, dict[str, Any]]:
        rows = self._load_csv(self.stock_snapshot_path)
        grouped: dict[str, dict[str, Any]] = {}
        for row in rows:
            if row["sector_id"] not in SUPPORTED_SECTOR_IDS:
                continue
            symbol = row["symbol"]
            entry = grouped.setdefault(
                symbol,
                {"row_count": 0, "sector_ids": set(), "sector_names": set(), **{k: 0.0 for k in FEATURE_KEYS}},
            )
            entry["row_count"] += 1
            entry["sector_ids"].add(row["sector_id"])
            entry["sector_names"].add(row["sector_name"])
            for key in FEATURE_KEYS:
                entry[key] += _to_float(row[key])

        final: dict[str, dict[str, Any]] = {}
        for symbol, entry in grouped.items():
            count = entry["row_count"]
            final[symbol] = {
                "symbol": symbol,
                "row_count": count,
                "sector_ids": sorted(entry["sector_ids"]),
                "sector_names": sorted(entry["sector_names"]),
                **{key: entry[key] / count for key in FEATURE_KEYS},
            }
        return final

    def _zscore_features(self, rows: list[dict[str, Any]]) -> list[list[float]]:
        means = {k: sum(row[k] for row in rows) / len(rows) for k in FEATURE_KEYS}
        stds = {}
        for key in FEATURE_KEYS:
            var = sum((row[key] - means[key]) ** 2 for row in rows) / max(len(rows), 1)
            stds[key] = math.sqrt(var) or 1.0
        matrix = []
        for row in rows:
            matrix.append([(row[key] - means[key]) / stds[key] for key in FEATURE_KEYS])
        return matrix

    def _kmeans3(self, rows: list[dict[str, Any]]) -> dict[str, int]:
        # Deterministic tiny-kmeans for the 4 snapshot-supported symbols.
        matrix = self._zscore_features(rows)
        symbols = [row["symbol"] for row in rows]
        # seeds: highest liquidity, highest stability, remaining highest sector heat
        liquidity_idx = max(range(len(rows)), key=lambda i: rows[i]["liquidity"])
        stability_idx = max(range(len(rows)), key=lambda i: rows[i]["stability"])
        remaining = [i for i in range(len(rows)) if i not in {liquidity_idx, stability_idx}]
        heat_idx = max(remaining, key=lambda i: rows[i]["context_sector_heat"]) if remaining else liquidity_idx
        seed_ids = [liquidity_idx, stability_idx, heat_idx]
        centroids = [matrix[i][:] for i in seed_ids]

        assignments = [0] * len(rows)
        for _ in range(8):
            changed = False
            for i, vec in enumerate(matrix):
                dists = [
                    sum((vec[j] - centroid[j]) ** 2 for j in range(len(FEATURE_KEYS)))
                    for centroid in centroids
                ]
                best = min(range(len(dists)), key=lambda idx: dists[idx])
                if assignments[i] != best:
                    assignments[i] = best
                    changed = True
            new_centroids = []
            for cid in range(3):
                members = [matrix[i] for i, aid in enumerate(assignments) if aid == cid]
                if not members:
                    new_centroids.append(centroids[cid])
                    continue
                new_centroids.append(
                    [sum(member[j] for member in members) / len(members) for j in range(len(FEATURE_KEYS))]
                )
            centroids = new_centroids
            if not changed:
                break

        # semantic mapping based on raw feature means in each cluster
        cluster_members: dict[int, list[dict[str, Any]]] = {0: [], 1: [], 2: []}
        for row, aid in zip(rows, assignments):
            cluster_members[aid].append(row)

        cluster_semantic: dict[int, str] = {}
        for cid, members in cluster_members.items():
            if not members:
                continue
            avg_liquidity = sum(m["liquidity"] for m in members) / len(members)
            avg_stability = sum(m["stability"] for m in members) / len(members)
            avg_heat = sum(m["context_sector_heat"] for m in members) / len(members)
            if avg_liquidity == max(
                sum(m["liquidity"] for m in ms) / len(ms) if ms else -999 for ms in cluster_members.values()
            ):
                cluster_semantic[cid] = "control_eligible_primary"
            elif avg_stability == max(
                sum(m["stability"] for m in ms) / len(ms) if ms else -999 for ms in cluster_members.values()
            ):
                cluster_semantic[cid] = "control_eligible_support"
            else:
                cluster_semantic[cid] = "confirmation_only_adjacent"

        return {symbol: assignments[i] for i, symbol in enumerate(symbols)}, cluster_semantic, cluster_members

    def analyze(self) -> V124QCommercialAerospaceUniverseTriageReport:
        universe_rows = self._load_csv(self.merged_universe_path)
        supported = self._aggregate_supported()

        supported_rows = [supported[s] for s in sorted(supported) if s in {row["symbol"] for row in universe_rows}]
        assignments, cluster_semantic, cluster_members = self._kmeans3(supported_rows)

        control_eligible_rows: list[dict[str, Any]] = []
        confirmation_rows: list[dict[str, Any]] = []
        pending_rows: list[dict[str, Any]] = []

        universe_map = {row["symbol"]: row for row in universe_rows}

        for symbol, stats in supported.items():
            if symbol not in universe_map:
                continue
            base = universe_map[symbol]
            cluster_id = assignments[symbol]
            semantic = cluster_semantic[cluster_id]
            row = {
                "symbol": symbol,
                "name": base["name"],
                "group": base["group"],
                "subgroup": base["subgroup"],
                "source_layer": base["source_layer"],
                "confidence": base["confidence"],
                "snapshot_row_count": stats["row_count"],
                "snapshot_sector_names": "|".join(stats["sector_names"]),
                "machine_cluster_id": cluster_id,
                "machine_semantic": semantic,
                "avg_liquidity": round(stats["liquidity"], 6),
                "avg_stability": round(stats["stability"], 6),
                "avg_context_heat": round(stats["context_sector_heat"], 6),
                "avg_expected_upside": round(stats["expected_upside"], 6),
            }
            if semantic.startswith("control_eligible"):
                control_eligible_rows.append(row)
            else:
                confirmation_rows.append(row)

        for row in universe_rows:
            if row["symbol"] in supported:
                continue
            pending_rows.append(
                {
                    "symbol": row["symbol"],
                    "name": row["name"],
                    "group": row["group"],
                    "subgroup": row["subgroup"],
                    "source_layer": row["source_layer"],
                    "confidence": row["confidence"],
                    "pending_reason": "web_only_no_snapshot_support_yet",
                }
            )

        control_eligible_rows.sort(key=lambda r: (r["machine_semantic"], r["symbol"]))
        confirmation_rows.sort(key=lambda r: (r["machine_semantic"], r["symbol"]))
        pending_rows.sort(key=lambda r: (r["group"], r["symbol"]))

        summary = {
            "acceptance_posture": "freeze_v124q_commercial_aerospace_universe_triage_v1",
            "merged_universe_count": len(universe_rows),
            "snapshot_supported_count": len(control_eligible_rows) + len(confirmation_rows),
            "control_eligible_count": len(control_eligible_rows),
            "confirmation_count": len(confirmation_rows),
            "pending_count": len(pending_rows),
            "authoritative_rule": "only_snapshot_supported_symbols_may_enter_machine_role_triage_now_and_web_only_symbols_remain_pending_or_confirmation_only",
            "recommended_next_posture": "use_control_eligible_core_for_control_extraction_candidate_surface_and_keep_pending_names_outside_lawful_controls",
        }
        interpretation = [
            "V1.24Q is the first data-driven universe triage for commercial aerospace.",
            "It does not pretend the machine already understands every web-added name; it only lets snapshot-supported names enter machine role triage now.",
            "That preserves the user's broad A-share universe while preventing web-only names from being silently upgraded into lawful control authority.",
        ]
        return V124QCommercialAerospaceUniverseTriageReport(
            summary=summary,
            control_eligible_rows=control_eligible_rows,
            confirmation_rows=confirmation_rows,
            pending_rows=pending_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V124QCommercialAerospaceUniverseTriageReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def write_csv(*, data_dir: Path, result: V124QCommercialAerospaceUniverseTriageReport) -> Path:
    data_dir.mkdir(parents=True, exist_ok=True)
    output_path = data_dir / "commercial_aerospace_universe_triage_v1.csv"
    fieldnames = [
        "symbol",
        "name",
        "group",
        "subgroup",
        "source_layer",
        "confidence",
        "snapshot_row_count",
        "snapshot_sector_names",
        "machine_cluster_id",
        "machine_semantic",
        "avg_liquidity",
        "avg_stability",
        "avg_context_heat",
        "avg_expected_upside",
    ]
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in result.control_eligible_rows + result.confirmation_rows:
            writer.writerow({name: row.get(name) for name in fieldnames})
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V124QCommercialAerospaceUniverseTriageAnalyzer(repo_root)
    result = analyzer.analyze()
    report_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v124q_commercial_aerospace_universe_triage_v1",
        result=result,
    )
    csv_path = write_csv(
        data_dir=repo_root / "data" / "training",
        result=result,
    )
    print(report_path)
    print(csv_path)


if __name__ == "__main__":
    main()
