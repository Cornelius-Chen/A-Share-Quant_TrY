from __future__ import annotations

import csv
import glob
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


TIMELINE_LAYER_RANK = {"leader": 3, "core": 2, "junk": 1, None: 0}
CURRENT_INTERNAL_OWNERS = {"300474"}


@dataclass(slots=True)
class V130NBK0808MilitaryCivilFusionLocalEmergenceWatchAuditReport:
    summary: dict[str, Any]
    candidate_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "candidate_rows": self.candidate_rows,
            "interpretation": self.interpretation,
        }


class V130NBK0808MilitaryCivilFusionLocalEmergenceWatchAuditAnalyzer:
    SECTOR_ID = "BK0808"

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
        self.timeline_glob = str(repo_root / "reports" / "analysis" / "market_v*_symbol_timeline_*_capture_*.json")
        self.output_csv_path = repo_root / "data" / "training" / "bk0808_local_emergence_watch_candidates_v1.csv"

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
    def _watch_status_for_candidate(row: dict[str, Any]) -> tuple[str, str]:
        if row["symbol"] in CURRENT_INTERNAL_OWNERS:
            return "existing_internal_owner", "already_the_only_v6_same_plane_owner"
        if row["v6_snapshot_days"] == 0 and row["timeline_leader_core_days"] >= 8 and row["timeline_buy_days"] == 0:
            return (
                "nearest_same_plane_watch",
                "timeline-native bk0808 support is already strong enough that this should be watched as the most plausible second same-plane symbol if native snapshot support appears",
            )
        if row["v5_snapshot_days"] >= 10:
            return (
                "historical_bridge_watch",
                "historical bk0808 snapshot support exists, but this remains bridge-only until v6 same-plane support appears",
            )
        if row["timeline_leader_core_days"] >= 4:
            return (
                "timeline_only_quarantine",
                "timeline support exists but is not yet enough to make this the nearest reopen watch",
            )
        return (
            "reject_or_mirror_pending",
            "evidence is too thin or too mixed to keep near the reopen watch",
        )

    def analyze(self) -> V130NBK0808MilitaryCivilFusionLocalEmergenceWatchAuditReport:
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
                "timeline_approval_days": tl_row.get("timeline_approval_days", 0),
                "timeline_leader_core_days": tl_row.get("timeline_leader_core_days", 0),
                "timeline_buy_days": tl_row.get("timeline_buy_days", 0),
                "timeline_sell_days": tl_row.get("timeline_sell_days", 0),
                "timeline_mean_best_score": tl_row.get("timeline_mean_best_score"),
                "timeline_first_date": tl_row.get("timeline_first_date"),
                "timeline_last_date": tl_row.get("timeline_last_date"),
            }
            status, rationale = self._watch_status_for_candidate(row)
            row["recommended_watch_status"] = status
            row["rationale"] = rationale
            candidate_rows.append(row)

        priority_order = {
            "existing_internal_owner": 0,
            "nearest_same_plane_watch": 1,
            "historical_bridge_watch": 2,
            "timeline_only_quarantine": 3,
            "reject_or_mirror_pending": 4,
        }
        candidate_rows.sort(
            key=lambda row: (
                priority_order[row["recommended_watch_status"]],
                -row["v6_snapshot_days"],
                -row["timeline_leader_core_days"],
                -row["v5_snapshot_days"],
                row["symbol"],
            )
        )

        nearest_same_plane_watch = [
            row["symbol"] for row in candidate_rows if row["recommended_watch_status"] == "nearest_same_plane_watch"
        ]
        historical_bridge_watch = [
            row["symbol"] for row in candidate_rows if row["recommended_watch_status"] == "historical_bridge_watch"
        ]

        summary = {
            "acceptance_posture": "freeze_v130n_bk0808_military_civil_fusion_local_emergence_watch_audit_v1",
            "sector_id": self.SECTOR_ID,
            "current_internal_owner_count": len(CURRENT_INTERNAL_OWNERS),
            "nearest_same_plane_watch_count": len(nearest_same_plane_watch),
            "historical_bridge_watch_count": len(historical_bridge_watch),
            "nearest_same_plane_watch": nearest_same_plane_watch,
            "historical_bridge_watch": historical_bridge_watch,
            "authoritative_status": "watch_bk0808_for_second_same_plane_symbol_but_do_not_unlock_worker",
            "authoritative_rule": "the watchlist may identify likely emergence candidates but cannot be treated as same-plane support until v6 native snapshot evidence appears",
        }
        interpretation = [
            "V1.30N keeps the transfer program frozen while making BK0808 monitoring less blind.",
            "600118 is the most important near-surface watch because it already has strong BK0808 timeline-native support, even though it still lacks v6 same-plane snapshot support.",
            "600760 remains useful only as a bridge watch, not as proof that BK0808 can reopen today.",
        ]
        return V130NBK0808MilitaryCivilFusionLocalEmergenceWatchAuditReport(
            summary=summary,
            candidate_rows=candidate_rows,
            interpretation=interpretation,
        )

    def write_candidate_csv(self, rows: list[dict[str, Any]]) -> Path:
        self.output_csv_path.parent.mkdir(parents=True, exist_ok=True)
        fieldnames = list(rows[0].keys()) if rows else []
        with self.output_csv_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        return self.output_csv_path


def write_report(*, reports_dir: Path, report_name: str, result: V130NBK0808MilitaryCivilFusionLocalEmergenceWatchAuditReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V130NBK0808MilitaryCivilFusionLocalEmergenceWatchAuditAnalyzer(repo_root)
    result = analyzer.analyze()
    write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v130n_bk0808_military_civil_fusion_local_emergence_watch_audit_v1",
        result=result,
    )
    analyzer.write_candidate_csv(result.candidate_rows)


if __name__ == "__main__":
    main()
