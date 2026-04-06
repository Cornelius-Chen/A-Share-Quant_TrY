from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134HYCommercialAerospaceEventAttentionRoleCandidateAuditV1Report:
    summary: dict[str, Any]
    candidate_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "candidate_rows": self.candidate_rows,
            "interpretation": self.interpretation,
        }


class V134HYCommercialAerospaceEventAttentionRoleCandidateAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.output_csv = (
            repo_root
            / "data"
            / "training"
            / "commercial_aerospace_event_attention_role_candidates_v1.csv"
        )

    def _load_json(self, relative_path: str) -> dict[str, Any]:
        return json.loads((self.repo_root / relative_path).read_text(encoding="utf-8"))

    def _load_decisive_events(self) -> dict[str, dict[str, Any]]:
        path = (
            self.repo_root
            / "data"
            / "reference"
            / "catalyst_registry"
            / "commercial_aerospace_decisive_event_registry_v1.csv"
        )
        rows: dict[str, dict[str, Any]] = {}
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                rows[row["registry_id"]] = row
        return rows

    def analyze(self) -> V134HYCommercialAerospaceEventAttentionRoleCandidateAuditV1Report:
        events = self._load_decisive_events()
        event_attention = self._load_json(
            "reports/analysis/v134hw_commercial_aerospace_event_attention_supervision_registry_v1.json"
        )
        crowded = self._load_json(
            "reports/analysis/v134hm_commercial_aerospace_crowded_local_rebound_supervision_audit_v1.json"
        )
        named = self._load_json(
            "reports/analysis/v134hk_commercial_aerospace_named_local_rebound_counterexample_audit_v1.json"
        )

        crowded_by_symbol = {row["symbol"]: row for row in crowded["symbol_rows"]}
        named_by_symbol = {row["symbol"]: row for row in named["symbol_rows"]}

        candidate_rows = [
            {
                "symbol": "000547",
                "display_name": "航天发展",
                "candidate_status": "hard_retained",
                "candidate_role": "attention_anchor_and_attention_decoy",
                "source_backing": "ca_source_007 + local_path",
                "evidence_strength": "high",
                "role_reasoning": "explicit turning-point heat naming plus later weak repair makes it the first hard anchor/decoy case",
            },
            {
                "symbol": "603601",
                "display_name": "再升科技",
                "candidate_status": "soft_candidate",
                "candidate_role": "crowded_attention_carrier_candidate",
                "source_backing": "ca_source_010 + crowding_module",
                "evidence_strength": "medium",
                "role_reasoning": "has a real supply-chain validation event and later strong crowded rebound, but no hard local evidence yet that it was the main attention anchor rather than a later crowded beneficiary",
            },
            {
                "symbol": "002361",
                "display_name": "神剑股份",
                "candidate_status": "soft_candidate",
                "candidate_role": "crowding_only_role_candidate",
                "source_backing": "crowding_module_only",
                "evidence_strength": "medium_low",
                "role_reasoning": "shows shelter-like crowding and near-high repair, but lacks a retained event source proving anchor status",
            },
            {
                "symbol": "300342",
                "display_name": "天银机电",
                "candidate_status": "soft_candidate",
                "candidate_role": "outlier_breakout_concentration_candidate",
                "source_backing": "ca_source_004_theme_heat + local_breakout_path",
                "evidence_strength": "medium_low",
                "role_reasoning": "breaks prior highs inside lockout and appears in a theme-heat list, but the event itself was not retained as decisive, so this remains a local concentration candidate rather than a hard anchor",
            },
            {
                "symbol": "301306",
                "display_name": "西测测试",
                "candidate_status": "soft_candidate",
                "candidate_role": "high_beta_attention_follow_candidate",
                "source_backing": "ca_source_011 + raw_only_rebound",
                "evidence_strength": "medium",
                "role_reasoning": "has direct supply-chain validation and strong raw-only rebound, but current evidence fits a high-beta following role more than an attention anchor role",
            },
        ]

        for row in candidate_rows:
            symbol = row["symbol"]
            crowded_row = crowded_by_symbol.get(symbol, {})
            named_row = named_by_symbol.get(symbol, {})
            row["crowded_rebound_family"] = crowded_row.get("crowded_rebound_family", "")
            row["counterexample_family"] = named_row.get("counterexample_family", "")
            row["post_lockout_max_vs_pre_lockout_peak"] = named_row.get("post_lockout_max_vs_pre_lockout_peak", "")
            row["avg_turnover_rate_f"] = crowded_row.get("avg_turnover_rate_f", "")
            row["max_turnover_rate_f"] = crowded_row.get("max_turnover_rate_f", "")
            row["max_date_zone"] = named_row.get("max_date_zone", "")

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(candidate_rows[0].keys()))
            writer.writeheader()
            writer.writerows(candidate_rows)

        summary = {
            "acceptance_posture": "freeze_v134hy_commercial_aerospace_event_attention_role_candidate_audit_v1",
            "existing_hard_role_seed_count": event_attention["summary"]["symbol_role_seed_count"],
            "candidate_symbol_count": len(candidate_rows),
            "hard_retained_count": sum(1 for row in candidate_rows if row["candidate_status"] == "hard_retained"),
            "soft_candidate_count": sum(1 for row in candidate_rows if row["candidate_status"] == "soft_candidate"),
            "attention_anchor_hard_symbol": "000547",
            "candidate_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_rule": "the second event-attention expansion should remain candidate-based: 航天发展 remains the only hard anchor/decoy seed, while 再升科技、神剑股份、天银机电、西测测试 are retained as role candidates with different evidence strengths rather than being prematurely promoted into hard anchor or decoy labels",
        }
        interpretation = [
            "V1.34HY expands the role layer without pretending the evidence is equally strong for every named symbol.",
            "The key discipline is asymmetric promotion: one hard role seed can coexist with several softer role candidates, which is better than flattening everything into the same anchor/decoy confidence level.",
        ]
        return V134HYCommercialAerospaceEventAttentionRoleCandidateAuditV1Report(
            summary=summary,
            candidate_rows=candidate_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134HYCommercialAerospaceEventAttentionRoleCandidateAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134HYCommercialAerospaceEventAttentionRoleCandidateAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134hy_commercial_aerospace_event_attention_role_candidate_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
