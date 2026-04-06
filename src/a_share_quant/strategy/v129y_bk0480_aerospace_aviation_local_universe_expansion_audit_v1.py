from __future__ import annotations

import csv
import glob
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


TIMELINE_LAYER_RANK = {"leader": 3, "core": 2, "junk": 1, None: 0}
CURRENT_INTERNAL_OWNERS = {"000738", "600118"}


@dataclass(slots=True)
class V129YBK0480AerospaceAviationLocalUniverseExpansionAuditReport:
    summary: dict[str, Any]
    candidate_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "candidate_rows": self.candidate_rows,
            "interpretation": self.interpretation,
        }


class V129YBK0480AerospaceAviationLocalUniverseExpansionAuditAnalyzer:
    SECTOR_ID = "BK0480"

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.v5_snapshot_path = (
            repo_root
            / "data"
            / "derived"
            / "stock_snapshots"
            / "market_research_stock_snapshots_v5_carry_row_diversity_refresh.csv"
        )
        self.v6_snapshot_path = (
            repo_root
            / "data"
            / "derived"
            / "stock_snapshots"
            / "market_research_stock_snapshots_v6_catalyst_supported_carry_persistence_refresh.csv"
        )
        self.role_grammar_path = (
            repo_root / "reports" / "analysis" / "v129s_bk0480_aerospace_aviation_role_grammar_v1.json"
        )
        self.timeline_glob = str(repo_root / "reports" / "analysis" / "market_v*_symbol_timeline_*_capture_*.json")
        self.output_csv_path = repo_root / "data" / "training" / "bk0480_local_universe_expansion_candidates_v1.csv"

    def _load_snapshot_evidence(self, path: Path) -> dict[str, dict[str, Any]]:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = [row for row in csv.DictReader(handle) if row["sector_id"] == self.SECTOR_ID]
        evidence: dict[str, dict[str, Any]] = {}
        for row in rows:
            bucket = evidence.setdefault(
                row["symbol"],
                {
                    "snapshot_days": 0,
                    "mean_non_junk_parts": [],
                    "mean_expected_parts": [],
                    "mean_drive_parts": [],
                    "mean_resonance_parts": [],
                },
            )
            bucket["snapshot_days"] += 1
            bucket["mean_non_junk_parts"].append(float(row["non_junk_composite_score"]))
            bucket["mean_expected_parts"].append(float(row["expected_upside"]))
            bucket["mean_drive_parts"].append(float(row["drive_strength"]))
            bucket["mean_resonance_parts"].append(float(row["resonance"]))
        for bucket in evidence.values():
            bucket["mean_non_junk"] = round(sum(bucket.pop("mean_non_junk_parts")) / bucket["snapshot_days"], 6)
            bucket["mean_expected_upside"] = round(sum(bucket.pop("mean_expected_parts")) / bucket["snapshot_days"], 6)
            bucket["mean_drive_strength"] = round(sum(bucket.pop("mean_drive_parts")) / bucket["snapshot_days"], 6)
            bucket["mean_resonance"] = round(sum(bucket.pop("mean_resonance_parts")) / bucket["snapshot_days"], 6)
        return evidence

    def _load_timeline_evidence(self) -> dict[str, dict[str, Any]]:
        evidence: dict[str, dict[str, Any]] = {}
        for path_str in glob.glob(self.timeline_glob):
            path = Path(path_str)
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                continue
            symbol = payload.get("summary", {}).get("symbol")
            if not symbol:
                continue
            by_date: dict[str, dict[str, Any]] = {}
            for record in payload.get("candidate_records", []):
                for row in record.get("daily_records", []):
                    if row.get("approved_sector_id") != self.SECTOR_ID:
                        continue
                    trade_date = row["trade_date"]
                    current = {
                        "assignment_layer": row.get("assignment_layer"),
                        "assignment_score": float(row.get("assignment_score") or 0.0),
                        "buy": "buy" in (row.get("emitted_actions") or []),
                        "sell": "sell" in (row.get("emitted_actions") or []),
                    }
                    prior = by_date.get(trade_date)
                    if prior is None or (
                        TIMELINE_LAYER_RANK[current["assignment_layer"]],
                        current["assignment_score"],
                    ) > (
                        TIMELINE_LAYER_RANK[prior["assignment_layer"]],
                        prior["assignment_score"],
                    ):
                        by_date[trade_date] = current
                    elif prior is not None:
                        prior["buy"] = prior["buy"] or current["buy"]
                        prior["sell"] = prior["sell"] or current["sell"]
            if not by_date:
                continue
            dates = sorted(by_date)
            evidence[symbol] = {
                "timeline_approval_days": len(by_date),
                "timeline_leader_core_days": sum(
                    row["assignment_layer"] in {"leader", "core"} for row in by_date.values()
                ),
                "timeline_buy_days": sum(row["buy"] for row in by_date.values()),
                "timeline_sell_days": sum(row["sell"] for row in by_date.values()),
                "timeline_mean_best_score": round(
                    sum(row["assignment_score"] for row in by_date.values()) / len(by_date),
                    6,
                ),
                "timeline_first_date": dates[0],
                "timeline_last_date": dates[-1],
            }
        return evidence

    @staticmethod
    def _status_for_candidate(row: dict[str, Any]) -> tuple[str, str]:
        if row["symbol"] in CURRENT_INTERNAL_OWNERS:
            return "existing_internal_owner", "already_frozen_in_v129s"
        if row["v5_snapshot_days"] >= 20 and row["timeline_leader_core_days"] >= 4 and row["timeline_buy_days"] >= 3:
            return (
                "confirmation_candidate_historical_strong",
                "historical_bk0480_snapshot_support_and_repeated_timeline_buys_make_this_the_best_local_expansion_name",
            )
        if row["timeline_leader_core_days"] >= 4 and row["timeline_sell_days"] <= 1:
            return (
                "quarantine_pending_local_confirmation",
                "timeline_support_exists_but_lacks_native_snapshot_reinforcement_so_this_stays_pending",
            )
        return (
            "reject_or_mirror_pending",
            "evidence_is_too_mixed_or_too_weak_to_admit_even_as_pending_confirmation",
        )

    def analyze(self) -> V129YBK0480AerospaceAviationLocalUniverseExpansionAuditReport:
        role_grammar = json.loads(self.role_grammar_path.read_text(encoding="utf-8"))
        board_name = role_grammar["summary"]["board_name"]
        v5_evidence = self._load_snapshot_evidence(self.v5_snapshot_path)
        v6_evidence = self._load_snapshot_evidence(self.v6_snapshot_path)
        timeline_evidence = self._load_timeline_evidence()

        candidate_rows: list[dict[str, Any]] = []
        for symbol in sorted(set(v5_evidence) | set(v6_evidence) | set(timeline_evidence)):
            v5_row = v5_evidence.get(symbol, {})
            v6_row = v6_evidence.get(symbol, {})
            tl_row = timeline_evidence.get(symbol, {})
            row = {
                "symbol": symbol,
                "v5_snapshot_days": v5_row.get("snapshot_days", 0),
                "v6_snapshot_days": v6_row.get("snapshot_days", 0),
                "v5_mean_non_junk": v5_row.get("mean_non_junk"),
                "v6_mean_non_junk": v6_row.get("mean_non_junk"),
                "v5_mean_expected_upside": v5_row.get("mean_expected_upside"),
                "v6_mean_expected_upside": v6_row.get("mean_expected_upside"),
                "timeline_approval_days": tl_row.get("timeline_approval_days", 0),
                "timeline_leader_core_days": tl_row.get("timeline_leader_core_days", 0),
                "timeline_buy_days": tl_row.get("timeline_buy_days", 0),
                "timeline_sell_days": tl_row.get("timeline_sell_days", 0),
                "timeline_mean_best_score": tl_row.get("timeline_mean_best_score"),
                "timeline_first_date": tl_row.get("timeline_first_date"),
                "timeline_last_date": tl_row.get("timeline_last_date"),
            }
            status, rationale = self._status_for_candidate(row)
            row["recommended_local_status"] = status
            row["rationale"] = rationale
            candidate_rows.append(row)

        candidate_rows.sort(
            key=lambda row: (
                0 if row["recommended_local_status"] == "confirmation_candidate_historical_strong" else
                1 if row["recommended_local_status"] == "quarantine_pending_local_confirmation" else
                2 if row["recommended_local_status"] == "reject_or_mirror_pending" else
                3,
                -row["v6_snapshot_days"],
                -row["v5_snapshot_days"],
                -row["timeline_leader_core_days"],
                row["symbol"],
            )
        )

        confirmation_candidates = [r["symbol"] for r in candidate_rows if r["recommended_local_status"] == "confirmation_candidate_historical_strong"]
        quarantine_candidates = [r["symbol"] for r in candidate_rows if r["recommended_local_status"] == "quarantine_pending_local_confirmation"]
        reject_candidates = [r["symbol"] for r in candidate_rows if r["recommended_local_status"] == "reject_or_mirror_pending"]

        summary = {
            "acceptance_posture": "freeze_v129y_bk0480_aerospace_aviation_local_universe_expansion_audit_v1",
            "board_name": board_name,
            "sector_id": self.SECTOR_ID,
            "current_internal_owner_count": len(CURRENT_INTERNAL_OWNERS),
            "timeline_native_candidate_count": sum(1 for r in candidate_rows if r["timeline_approval_days"] > 0),
            "historical_snapshot_candidate_count": sum(1 for r in candidate_rows if r["v5_snapshot_days"] > 0 or r["v6_snapshot_days"] > 0),
            "confirmation_candidate_count": len(confirmation_candidates),
            "quarantine_candidate_count": len(quarantine_candidates),
            "reject_candidate_count": len(reject_candidates),
            "confirmation_candidates": confirmation_candidates,
            "quarantine_candidates": quarantine_candidates,
            "reject_candidates": reject_candidates,
            "authoritative_rule": "expand_bk0480_locally_only_when_native_snapshot_or_native_timeline_evidence_is_strong_enough_and_keep_cross_version_names_out_of_control_authority_until_harmonized",
            "recommended_next_posture": "refresh_role_surface_with_600760_as_confirmation_only_and_keep_002273_601989_quarantined",
        }
        interpretation = [
            "V1.29Y audits BK0480-native expansion evidence without borrowing commercial-aerospace outer layers.",
            "600760 is the only clear admission candidate because it has both historical BK0480 snapshot support and repeated BK0480-native timeline buys.",
            "002273 and 601989 have enough local timeline evidence to stay under watch, but not enough native snapshot support to enter confirmation today.",
        ]
        return V129YBK0480AerospaceAviationLocalUniverseExpansionAuditReport(summary=summary, candidate_rows=candidate_rows, interpretation=interpretation)

    def write_candidate_csv(self, rows: list[dict[str, Any]]) -> Path:
        self.output_csv_path.parent.mkdir(parents=True, exist_ok=True)
        fieldnames = list(rows[0].keys()) if rows else []
        with self.output_csv_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        return self.output_csv_path


def write_report(*, reports_dir: Path, report_name: str, result: V129YBK0480AerospaceAviationLocalUniverseExpansionAuditReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V129YBK0480AerospaceAviationLocalUniverseExpansionAuditAnalyzer(repo_root)
    result = analyzer.analyze()
    write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v129y_bk0480_aerospace_aviation_local_universe_expansion_audit_v1",
        result=result,
    )
    analyzer.write_candidate_csv(result.candidate_rows)


if __name__ == "__main__":
    main()
