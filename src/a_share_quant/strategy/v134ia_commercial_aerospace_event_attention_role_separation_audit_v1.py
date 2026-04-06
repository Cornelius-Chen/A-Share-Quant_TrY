from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134IACommercialAerospaceEventAttentionRoleSeparationAuditV1Report:
    summary: dict[str, Any]
    separated_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "separated_rows": self.separated_rows,
            "interpretation": self.interpretation,
        }


class V134IACommercialAerospaceEventAttentionRoleSeparationAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.output_csv = (
            repo_root
            / "data"
            / "training"
            / "commercial_aerospace_event_attention_role_separation_v1.csv"
        )

    def _load_json(self, relative_path: str) -> dict[str, Any]:
        return json.loads((self.repo_root / relative_path).read_text(encoding="utf-8"))

    def analyze(self) -> V134IACommercialAerospaceEventAttentionRoleSeparationAuditV1Report:
        candidate_audit = self._load_json(
            "reports/analysis/v134hy_commercial_aerospace_event_attention_role_candidate_audit_v1.json"
        )

        separated_rows: list[dict[str, Any]] = []
        for row in candidate_audit["candidate_rows"]:
            if row["candidate_status"] != "soft_candidate":
                continue

            symbol = row["symbol"]
            if symbol == "603601":
                separated_role = "event_backed_attention_carrier_candidate"
                separation_reading = (
                    "retained supply-chain event plus crowding-like rebound supports a carrier role, "
                    "but not yet a hard anchor or true-selection promotion"
                )
            elif symbol == "002361":
                separated_role = "non_anchor_crowded_concentration_candidate"
                separation_reading = (
                    "crowding and near-high repair exist without retained event backing, so the name is "
                    "better read as concentration without anchor authority"
                )
            elif symbol == "300342":
                separated_role = "non_anchor_outlier_breakout_candidate"
                separation_reading = (
                    "the lockout-window breakout is real, but the supporting event is only discarded theme heat, "
                    "so the name stays a local breakout concentration candidate rather than an anchor"
                )
            elif symbol == "301306":
                separated_role = "event_backed_high_beta_follow_candidate"
                separation_reading = (
                    "retained supply-chain validation exists, but the path still reads more like high-beta followthrough "
                    "than heat-anchor behavior"
                )
            else:
                separated_role = "unclassified_soft_candidate"
                separation_reading = "candidate remains soft and unclassified"

            separated_rows.append(
                {
                    **row,
                    "separated_role": separated_role,
                    "separation_reading": separation_reading,
                }
            )

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(separated_rows[0].keys()))
            writer.writeheader()
            writer.writerows(separated_rows)

        summary = {
            "acceptance_posture": "freeze_v134ia_commercial_aerospace_event_attention_role_separation_audit_v1",
            "soft_candidate_count": len(separated_rows),
            "event_backed_attention_carrier_count": sum(
                1 for row in separated_rows if row["separated_role"] == "event_backed_attention_carrier_candidate"
            ),
            "non_anchor_concentration_count": sum(
                1
                for row in separated_rows
                if row["separated_role"]
                in {"non_anchor_crowded_concentration_candidate", "non_anchor_outlier_breakout_candidate"}
            ),
            "high_beta_follow_count": sum(
                1 for row in separated_rows if row["separated_role"] == "event_backed_high_beta_follow_candidate"
            ),
            "separation_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_rule": "soft role candidates are now better separated: 再升科技 is the strongest event-backed attention-carrier candidate, 神剑股份 and 天银机电 remain non-anchor concentration candidates, and 西测测试 is best read as an event-backed high-beta follow candidate; capital_true_selection stays blocked",
        }
        interpretation = [
            "V1.34IA separates the soft role candidates without collapsing them into a single fuzzy attention bucket.",
            "The goal is not to manufacture a leader yet, but to stop treating every strong local name as the same kind of attention object.",
        ]
        return V134IACommercialAerospaceEventAttentionRoleSeparationAuditV1Report(
            summary=summary,
            separated_rows=separated_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134IACommercialAerospaceEventAttentionRoleSeparationAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134IACommercialAerospaceEventAttentionRoleSeparationAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ia_commercial_aerospace_event_attention_role_separation_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
