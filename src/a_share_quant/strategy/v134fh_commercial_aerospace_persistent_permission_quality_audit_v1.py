from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134FHCommercialAerospacePersistentPermissionQualityAuditV1Report:
    summary: dict[str, Any]
    quality_rows: list[dict[str, Any]]
    session_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "quality_rows": self.quality_rows,
            "session_rows": self.session_rows,
            "interpretation": self.interpretation,
        }


class V134FHCommercialAerospacePersistentPermissionQualityAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.family_csv_path = (
            repo_root / "data" / "training" / "commercial_aerospace_add_permission_family_sessions_v1.csv"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_persistent_permission_quality_sessions_v1.csv"
        )

    def analyze(self) -> V134FHCommercialAerospacePersistentPermissionQualityAuditV1Report:
        with self.family_csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))

        session_rows: list[dict[str, Any]] = []
        for row in rows:
            if row["permission_family"] != "persistent_permission_candidate":
                continue
            close_loc_15m = float(row["close_loc_15m"]) if row["close_loc_15m"] not in ("", None) else None
            open_to_60m = float(row["open_to_60m"])
            continuation_15_to_60m = float(row["continuation_15_to_60m"])

            if close_loc_15m is not None and close_loc_15m >= 0.62:
                quality_tier = "full_quality_persistent_permission"
            elif close_loc_15m is not None and close_loc_15m >= 0.60:
                quality_tier = "bridge_quality_persistent_permission"
            else:
                quality_tier = "probe_quality_persistent_permission"

            session_rows.append(
                {
                    "trade_date": row["trade_date"],
                    "month_bucket": row["month_bucket"],
                    "symbol": row["symbol"],
                    "predicted_label": row["predicted_label"],
                    "is_seed_allowed": row["is_seed_allowed"] == "True",
                    "quality_tier": quality_tier,
                    "open_to_15m": float(row["open_to_15m"]),
                    "open_to_60m": open_to_60m,
                    "continuation_15_to_60m": continuation_15_to_60m,
                    "close_loc_15m": close_loc_15m,
                    "burst_amount_share_15": float(row["burst_amount_share_15"]),
                }
            )

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(session_rows[0].keys()))
            writer.writeheader()
            writer.writerows(session_rows)

        quality_rows: list[dict[str, Any]] = []
        for quality_tier in (
            "full_quality_persistent_permission",
            "bridge_quality_persistent_permission",
            "probe_quality_persistent_permission",
        ):
            quality_sessions = [row for row in session_rows if row["quality_tier"] == quality_tier]
            quality_rows.append(
                {
                    "quality_tier": quality_tier,
                    "session_count": len(quality_sessions),
                    "seed_allowed_count": sum(1 for row in quality_sessions if row["is_seed_allowed"]),
                    "predicted_full_count": sum(1 for row in quality_sessions if row["predicted_label"] == "allowed_preheat_full_add"),
                    "predicted_probe_count": sum(1 for row in quality_sessions if row["predicted_label"] == "allowed_preheat_probe_add"),
                    "mean_open_to_60m": round(sum(row["open_to_60m"] for row in quality_sessions) / len(quality_sessions), 8)
                    if quality_sessions
                    else 0.0,
                    "mean_close_loc_15m": round(sum(row["close_loc_15m"] for row in quality_sessions) / len(quality_sessions), 8)
                    if quality_sessions
                    else 0.0,
                }
            )

        summary = {
            "acceptance_posture": "freeze_v134fh_commercial_aerospace_persistent_permission_quality_audit_v1",
            "persistent_session_count": len(session_rows),
            "full_quality_count": next(row["session_count"] for row in quality_rows if row["quality_tier"] == "full_quality_persistent_permission"),
            "bridge_quality_count": next(row["session_count"] for row in quality_rows if row["quality_tier"] == "bridge_quality_persistent_permission"),
            "probe_quality_count": next(row["session_count"] for row in quality_rows if row["quality_tier"] == "probe_quality_persistent_permission"),
            "session_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_rule": (
                "persistent permission candidates are not flat; they split into full-quality, bridge-quality, and probe-quality tiers that should remain local supervision strata"
            ),
        }
        interpretation = [
            "V1.34FH refines the persistent permission family into internal quality tiers.",
            "The goal is not to authorize execution, only to stop treating all persistent permission candidates as equally strong add objects.",
        ]
        return V134FHCommercialAerospacePersistentPermissionQualityAuditV1Report(
            summary=summary,
            quality_rows=quality_rows,
            session_rows=session_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134FHCommercialAerospacePersistentPermissionQualityAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134FHCommercialAerospacePersistentPermissionQualityAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134fh_commercial_aerospace_persistent_permission_quality_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
