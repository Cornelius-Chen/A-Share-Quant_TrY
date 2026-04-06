from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


@dataclass(slots=True)
class V116LCpoVisibleOnlyCooledShadowRetentionReport:
    summary: dict[str, Any]
    retained_variant_row: dict[str, Any]
    shadow_variant_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "retained_variant_row": self.retained_variant_row,
            "shadow_variant_rows": self.shadow_variant_rows,
            "interpretation": self.interpretation,
        }


class V116LCpoVisibleOnlyCooledShadowRetentionAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self, *, v116k_payload: dict[str, Any]) -> V116LCpoVisibleOnlyCooledShadowRetentionReport:
        variant_rows = list(v116k_payload.get("variant_rows", []))
        executing_rows = [row for row in variant_rows if int(row.get("executed_order_count", 0)) > 0]

        def score(row: dict[str, Any]) -> tuple[float, float]:
            equity_delta = _to_float(row.get("equity_delta_vs_baseline"))
            drawdown = _to_float(row.get("max_drawdown"))
            return (equity_delta - 3_000_000.0 * max(drawdown - 0.18, 0.0), equity_delta)

        retained = max(executing_rows, key=score)
        shadow_rows = [row for row in executing_rows if str(row["variant_name"]) != str(retained["variant_name"])]
        summary = {
            "acceptance_posture": "freeze_v116l_cpo_visible_only_cooled_shadow_retention_v1",
            "candidate_posture": "cooled_shadow_only_not_promotable",
            "retained_variant_name": str(retained["variant_name"]),
            "retained_final_equity": round(_to_float(retained.get("final_equity")), 4),
            "retained_max_drawdown": round(_to_float(retained.get("max_drawdown")), 6),
            "recommended_next_posture": "carry_retained_cooled_shadow_and_trigger_three_run_adversarial_review_on_v116j_v116k_v116l",
        }
        interpretation = [
            "V1.16L does not create another replay; it freezes one cooled shadow variant out of the V116K heat-trim family.",
            "The retained object remains candidate-only and exists to prevent the project from drifting back to the hottest broader visible-only line by default.",
            "This is a retention step before the mandatory three-run adversarial review over V116J/V116K/V116L.",
        ]
        return V116LCpoVisibleOnlyCooledShadowRetentionReport(
            summary=summary,
            retained_variant_row=retained,
            shadow_variant_rows=shadow_rows,
            interpretation=interpretation,
        )


def write_report(*, reports_dir: Path, report_name: str, result: V116LCpoVisibleOnlyCooledShadowRetentionReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V116LCpoVisibleOnlyCooledShadowRetentionAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v116k_payload=json.loads((repo_root / "reports" / "analysis" / "v116k_cpo_visible_only_shadow_heat_trim_review_v1.json").read_text(encoding="utf-8"))
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v116l_cpo_visible_only_cooled_shadow_retention_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
