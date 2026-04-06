from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134IICommercialAerospaceSymbolFollowthroughSupervisionAuditV1Report:
    summary: dict[str, Any]
    followthrough_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "followthrough_rows": self.followthrough_rows,
            "interpretation": self.interpretation,
        }


class V134IICommercialAerospaceSymbolFollowthroughSupervisionAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.output_csv = (
            repo_root
            / "data"
            / "training"
            / "commercial_aerospace_symbol_followthrough_supervision_v1.csv"
        )

    def _load_json(self, relative_path: str) -> dict[str, Any]:
        return json.loads((self.repo_root / relative_path).read_text(encoding="utf-8"))

    def analyze(self) -> V134IICommercialAerospaceSymbolFollowthroughSupervisionAuditV1Report:
        role_separation = self._load_json(
            "reports/analysis/v134ia_commercial_aerospace_event_attention_role_separation_audit_v1.json"
        )
        named_counterexamples = self._load_json(
            "reports/analysis/v134hk_commercial_aerospace_named_local_rebound_counterexample_audit_v1.json"
        )

        separation_by_symbol = {row["symbol"]: row for row in role_separation["separated_rows"]}
        named_rows = [row for row in named_counterexamples["symbol_rows"] if row["symbol"] in separation_by_symbol]

        followthrough_rows: list[dict[str, Any]] = []
        for row in named_rows:
            max_return = float(row["post_lockout_max_return_from_start"])
            drawdown = float(row["post_lockout_drawdown_from_max_to_end"])
            max_zone = row["max_date_zone"]
            role = separation_by_symbol[row["symbol"]]["separated_role"]

            if max_return >= 0.35 and drawdown > -0.12 and max_zone == "post_lockout_raw_only_window":
                follow_label = "persistent_symbol_followthrough_without_board_unlock"
                follow_reading = "symbol carries a durable local followthrough path, but only in raw-only space without legal board unlock"
            elif max_return >= 0.18 and drawdown > -0.12:
                follow_label = "moderate_symbol_followthrough_without_board_unlock"
                follow_reading = "symbol has visible followthrough strength, but it remains symbol-level and does not reopen board participation"
            else:
                follow_label = "weak_or_nonpersistent_followthrough"
                follow_reading = "symbol either fails to build enough followthrough or gives too much back to support stronger role promotion"

            followthrough_rows.append(
                {
                    "symbol": row["symbol"],
                    "display_name": row["display_name"],
                    "separated_role": role,
                    "post_lockout_max_return_from_start": row["post_lockout_max_return_from_start"],
                    "post_lockout_drawdown_from_max_to_end": row["post_lockout_drawdown_from_max_to_end"],
                    "max_date_zone": max_zone,
                    "followthrough_label": follow_label,
                    "followthrough_reading": follow_reading,
                }
            )

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(followthrough_rows[0].keys()))
            writer.writeheader()
            writer.writerows(followthrough_rows)

        summary = {
            "acceptance_posture": "freeze_v134ii_commercial_aerospace_symbol_followthrough_supervision_audit_v1",
            "symbol_count": len(followthrough_rows),
            "persistent_followthrough_count": sum(
                1 for row in followthrough_rows if row["followthrough_label"] == "persistent_symbol_followthrough_without_board_unlock"
            ),
            "moderate_followthrough_count": sum(
                1 for row in followthrough_rows if row["followthrough_label"] == "moderate_symbol_followthrough_without_board_unlock"
            ),
            "weak_followthrough_count": sum(
                1 for row in followthrough_rows if row["followthrough_label"] == "weak_or_nonpersistent_followthrough"
            ),
            "followthrough_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_rule": "a dedicated followthrough surface now exists, but it remains symbol-level: strong followthrough can occur without any legal board unlock, so followthrough alone still cannot promote capital_true_selection",
        }
        interpretation = [
            "V1.34II opens the first dedicated followthrough supervision surface instead of leaving followthrough implicit.",
            "The layer is intentionally conservative: it names symbol-level persistence while keeping board unlock and true selection blocked.",
        ]
        return V134IICommercialAerospaceSymbolFollowthroughSupervisionAuditV1Report(
            summary=summary,
            followthrough_rows=followthrough_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134IICommercialAerospaceSymbolFollowthroughSupervisionAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134IICommercialAerospaceSymbolFollowthroughSupervisionAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ii_commercial_aerospace_symbol_followthrough_supervision_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
