from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134FDCommercialAerospaceAddPermissionFamilyAuditV1Report:
    summary: dict[str, Any]
    family_rows: list[dict[str, Any]]
    session_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "family_rows": self.family_rows,
            "session_rows": self.session_rows,
            "interpretation": self.interpretation,
        }


class V134FDCommercialAerospaceAddPermissionFamilyAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.context_csv_path = (
            repo_root / "data" / "training" / "commercial_aerospace_add_permission_context_sessions_v1.csv"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_add_permission_family_sessions_v1.csv"
        )

    def analyze(self) -> V134FDCommercialAerospaceAddPermissionFamilyAuditV1Report:
        with self.context_csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))

        session_rows: list[dict[str, Any]] = []
        for row in rows:
            if not (
                row["unlock_worthy"] == "True"
                and row["high_role_symbol"] == "True"
                and float(row["burst_amount_share_15"]) <= 0.40
            ):
                continue

            open_to_15m = float(row["open_to_15m"])
            open_to_60m = float(row["open_to_60m"])
            continuation_15_to_60m = open_to_60m - open_to_15m

            if open_to_60m <= -0.01:
                permission_family = "failed_permission_watch"
            elif open_to_60m >= 0.01 and continuation_15_to_60m > 0:
                permission_family = "persistent_permission_candidate"
            else:
                permission_family = "fragile_permission_watch"

            session_rows.append(
                {
                    "trade_date": row["trade_date"],
                    "month_bucket": row["month_bucket"],
                    "symbol": row["symbol"],
                    "predicted_label": row["predicted_label"],
                    "is_seed_allowed": row["is_seed_allowed"] == "True",
                    "permission_family": permission_family,
                    "open_to_15m": round(open_to_15m, 8),
                    "open_to_60m": round(open_to_60m, 8),
                    "continuation_15_to_60m": round(continuation_15_to_60m, 8),
                    "close_loc_15m": float(row["close_loc_15m"]) if row["close_loc_15m"] else None,
                    "burst_amount_share_15": float(row["burst_amount_share_15"]),
                }
            )

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(session_rows[0].keys()))
            writer.writeheader()
            writer.writerows(session_rows)

        family_rows: list[dict[str, Any]] = []
        for family_name in (
            "persistent_permission_candidate",
            "fragile_permission_watch",
            "failed_permission_watch",
        ):
            family_sessions = [row for row in session_rows if row["permission_family"] == family_name]
            family_rows.append(
                {
                    "permission_family": family_name,
                    "session_count": len(family_sessions),
                    "seed_allowed_count": sum(1 for row in family_sessions if row["is_seed_allowed"]),
                    "non_seed_count": sum(1 for row in family_sessions if not row["is_seed_allowed"]),
                    "mean_open_to_60m": round(
                        sum(row["open_to_60m"] for row in family_sessions) / len(family_sessions), 8
                    )
                    if family_sessions
                    else 0.0,
                    "mean_continuation_15_to_60m": round(
                        sum(row["continuation_15_to_60m"] for row in family_sessions) / len(family_sessions),
                        8,
                    )
                    if family_sessions
                    else 0.0,
                }
            )

        summary = {
            "acceptance_posture": "freeze_v134fd_commercial_aerospace_add_permission_family_audit_v1",
            "high_confidence_session_count": len(session_rows),
            "persistent_permission_candidate_count": next(
                row["session_count"] for row in family_rows if row["permission_family"] == "persistent_permission_candidate"
            ),
            "fragile_permission_watch_count": next(
                row["session_count"] for row in family_rows if row["permission_family"] == "fragile_permission_watch"
            ),
            "failed_permission_watch_count": next(
                row["session_count"] for row in family_rows if row["permission_family"] == "failed_permission_watch"
            ),
            "session_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_rule": (
                "the narrow add-permission clue is not monolithic; it splits into persistent, fragile, and failed families that should stay in local supervision rather than collapse into a single positive permission claim"
            ),
        }
        interpretation = [
            "V1.34FD decomposes the narrow quantity-price add-permission clue into local supervision families.",
            "This shows whether the new clue is finding a coherent persistent-permission pocket or just a smaller mixed bag of early rebounds.",
        ]
        return V134FDCommercialAerospaceAddPermissionFamilyAuditV1Report(
            summary=summary,
            family_rows=family_rows,
            session_rows=session_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134FDCommercialAerospaceAddPermissionFamilyAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134FDCommercialAerospaceAddPermissionFamilyAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134fd_commercial_aerospace_add_permission_family_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
