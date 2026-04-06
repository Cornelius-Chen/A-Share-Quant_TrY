from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _predict_tier(row: dict[str, Any]) -> str:
    open_to_close_return = float(row["open_to_close_return"])
    ret15 = float(row["ret15"])
    ret60 = float(row["ret60"])
    draw60 = float(row["draw60"])
    close_loc15 = float(row["close_loc15"])
    close_loc60 = float(row["close_loc60"])

    if (
        (ret15 <= -0.05 and close_loc15 <= 0.05 and open_to_close_return <= -0.09)
        or (ret60 <= -0.048 and close_loc60 <= 0.02 and open_to_close_return <= -0.08)
    ):
        return "severe_override_positive"
    if ret60 <= -0.05 and close_loc60 <= 0.20 and open_to_close_return <= -0.06:
        return "reversal_watch"
    if ret60 <= -0.045 and draw60 <= -0.045 and close_loc60 <= 0.05:
        return "mild_override_watch"
    return "unmatched"


@dataclass(slots=True)
class V132GCommercialAerospaceLocal1MinRuleCandidateAuditReport:
    summary: dict[str, Any]
    candidate_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "candidate_rows": self.candidate_rows,
            "interpretation": self.interpretation,
        }


class V132GCommercialAerospaceLocal1MinRuleCandidateAuditAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.registry_report_path = (
            repo_root / "reports" / "analysis" / "v131y_commercial_aerospace_intraday_supervision_registry_v1.json"
        )

    def analyze(self) -> V132GCommercialAerospaceLocal1MinRuleCandidateAuditReport:
        registry = json.loads(self.registry_report_path.read_text(encoding="utf-8"))
        candidate_rows: list[dict[str, Any]] = []
        match_count = 0
        unmatched_count = 0
        for row in registry["registry_rows"]:
            predicted_tier = _predict_tier(row)
            matched = predicted_tier == row["severity_tier"]
            if matched:
                match_count += 1
            if predicted_tier == "unmatched":
                unmatched_count += 1
            candidate_rows.append(
                {
                    "execution_trade_date": row["execution_trade_date"],
                    "symbol": row["symbol"],
                    "severity_tier": row["severity_tier"],
                    "predicted_tier": predicted_tier,
                    "matched": matched,
                }
            )

        summary = {
            "acceptance_posture": "freeze_v132g_commercial_aerospace_local_1min_rule_candidate_audit_v1",
            "registry_row_count": len(candidate_rows),
            "matched_count": match_count,
            "match_rate": round(match_count / len(candidate_rows), 8) if candidate_rows else 0.0,
            "unmatched_count": unmatched_count,
            "authoritative_rule": "the first local 1min candidate rules are acceptable only as supervision-side seed rules if they preserve the severe/reversal/mild tier ordering on the frozen seed registry",
        }
        interpretation = [
            "V1.32G applies the first explicit 1-minute tier rules back onto the frozen six-row intraday seed registry.",
            "This is a seed-side audit only: the question is whether the rule ordering is coherent on the retained seeds, not whether the rules are ready for replay.",
        ]
        return V132GCommercialAerospaceLocal1MinRuleCandidateAuditReport(
            summary=summary,
            candidate_rows=candidate_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V132GCommercialAerospaceLocal1MinRuleCandidateAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V132GCommercialAerospaceLocal1MinRuleCandidateAuditAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v132g_commercial_aerospace_local_1min_rule_candidate_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
