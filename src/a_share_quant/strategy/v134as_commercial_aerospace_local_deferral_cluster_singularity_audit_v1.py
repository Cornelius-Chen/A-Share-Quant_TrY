from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134ASCommercialAerospaceLocalDeferralClusterSingularityAuditV1Report:
    summary: dict[str, Any]
    cluster_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "cluster_rows": self.cluster_rows,
            "interpretation": self.interpretation,
        }


class V134ASCommercialAerospaceLocalDeferralClusterSingularityAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.horizon_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_reversal_full_horizon_sanity_audit_v1.csv"
        )
        self.deferral_audit_path = (
            repo_root / "reports" / "analysis" / "v134ao_commercial_aerospace_local_reversal_deferral_audit_v1.json"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_local_deferral_cluster_singularity_audit_v1.csv"
        )

    def analyze(self) -> V134ASCommercialAerospaceLocalDeferralClusterSingularityAuditV1Report:
        with self.horizon_csv.open("r", encoding="utf-8-sig", newline="") as handle:
            horizon_rows = list(csv.DictReader(handle))
        audit = json.loads(self.deferral_audit_path.read_text(encoding="utf-8"))
        impacted_keys = {(row["trade_date"], row["symbol"]) for row in audit["impacted_rows"]}

        cluster_rows: list[dict[str, Any]] = []
        rebound_cost_count = 0
        matched_rebound_count = 0
        for row in horizon_rows:
            horizon_5d_raw = row["horizon_pnl_5d"]
            if horizon_5d_raw == "":
                continue
            horizon_5d = float(horizon_5d_raw)
            regime_label = "rebound_cost_case" if horizon_5d > 0 else "followthrough_benefit_case"
            if regime_label == "rebound_cost_case":
                rebound_cost_count += 1
            matched = (row["trade_date"], row["symbol"]) in impacted_keys
            if matched and regime_label == "rebound_cost_case":
                matched_rebound_count += 1
            cluster_rows.append(
                {
                    "trade_date": row["trade_date"],
                    "symbol": row["symbol"],
                    "month_bucket": row["month_bucket"],
                    "regime_label": regime_label,
                    "horizon_pnl_5d": horizon_5d,
                    "matched_local_deferral": matched,
                }
            )

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(cluster_rows[0].keys()))
            writer.writeheader()
            writer.writerows(cluster_rows)

        total_reversal_sessions = len(cluster_rows)
        matched_total = len(impacted_keys)
        summary = {
            "acceptance_posture": "freeze_v134as_commercial_aerospace_local_deferral_cluster_singularity_audit_v1",
            "reversal_session_count": total_reversal_sessions,
            "rebound_cost_case_count": rebound_cost_count,
            "matched_local_deferral_count": matched_total,
            "matched_local_deferral_share_of_reversal": round(matched_total / total_reversal_sessions, 8),
            "matched_local_deferral_share_of_rebound_cost": round(
                matched_rebound_count / rebound_cost_count, 8
            ) if rebound_cost_count else 0.0,
            "cluster_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "commercial_aerospace_local_deferral_cluster_singularity_audit_ready_for_direction_triage",
        }
        interpretation = [
            "V1.34AS checks whether the promoted local reversal-deferral expression is a broad failure cluster or only a single narrow residue.",
            "If the hit share is tiny, the right posture is to freeze the local expression and stop searching the same family for more refinements.",
        ]
        return V134ASCommercialAerospaceLocalDeferralClusterSingularityAuditV1Report(
            summary=summary,
            cluster_rows=cluster_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134ASCommercialAerospaceLocalDeferralClusterSingularityAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134ASCommercialAerospaceLocalDeferralClusterSingularityAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134as_commercial_aerospace_local_deferral_cluster_singularity_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
