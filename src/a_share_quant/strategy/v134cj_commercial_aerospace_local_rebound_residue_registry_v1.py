from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134CJCommercialAerospaceLocalReboundResidueRegistryV1Report:
    summary: dict[str, Any]
    registry_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "registry_rows": self.registry_rows,
            "interpretation": self.interpretation,
        }


class V134CJCommercialAerospaceLocalReboundResidueRegistryV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.horizon_audit_path = (
            repo_root
            / "reports"
            / "analysis"
            / "v134cf_commercial_aerospace_isolated_sell_side_horizon_quality_audit_v1.json"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_local_rebound_residue_registry_v1.csv"
        )

    def analyze(self) -> V134CJCommercialAerospaceLocalReboundResidueRegistryV1Report:
        audit = json.loads(self.horizon_audit_path.read_text(encoding="utf-8"))
        registry_rows: list[dict[str, Any]] = []
        for row in audit["session_rows"]:
            pnl_3d = float(row["horizon_pnl_if_held_3d"]) if row["horizon_pnl_if_held_3d"] != "" else 0.0
            if pnl_3d <= 0:
                continue
            pnl_5d = float(row["horizon_pnl_if_held_5d"]) if row["horizon_pnl_if_held_5d"] != "" else 0.0
            residue_type = (
                "persistent_rebound_residue_watch" if pnl_5d > 0 else "transient_rebound_residue_watch"
            )
            registry_rows.append(
                {
                    "trade_date": row["trade_date"],
                    "symbol": row["symbol"],
                    "predicted_tier": row["predicted_tier"],
                    "same_day_protected_mark_to_close": round(float(row["same_day_protected_mark_to_close"]), 4),
                    "horizon_pnl_if_held_3d": round(pnl_3d, 4),
                    "horizon_pnl_if_held_5d": round(pnl_5d, 4),
                    "residue_type": residue_type,
                }
            )

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(registry_rows[0].keys()))
            writer.writeheader()
            writer.writerows(registry_rows)

        persistent_count = sum(1 for row in registry_rows if row["residue_type"] == "persistent_rebound_residue_watch")
        transient_count = sum(1 for row in registry_rows if row["residue_type"] == "transient_rebound_residue_watch")
        top_case = max(registry_rows, key=lambda row: float(row["horizon_pnl_if_held_3d"]))
        summary = {
            "acceptance_posture": "freeze_v134cj_commercial_aerospace_local_rebound_residue_registry_v1",
            "residue_seed_count": len(registry_rows),
            "persistent_rebound_residue_count": persistent_count,
            "transient_rebound_residue_count": transient_count,
            "top_residue_case": f"{top_case['trade_date']} {top_case['symbol']}",
            "registry_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "commercial_aerospace_local_rebound_residue_registry_ready_for_direction_triage",
        }
        interpretation = [
            "V1.34CJ freezes the remaining 3-day rebound-cost residues from the first real sell binding surface into explicit local supervision seeds.",
            "The split between persistent and transient residue prevents the branch from treating all rebound-cost cases as one family when some simply fade again by 5 days.",
        ]
        return V134CJCommercialAerospaceLocalReboundResidueRegistryV1Report(
            summary=summary,
            registry_rows=registry_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134CJCommercialAerospaceLocalReboundResidueRegistryV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134CJCommercialAerospaceLocalReboundResidueRegistryV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134cj_commercial_aerospace_local_rebound_residue_registry_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
