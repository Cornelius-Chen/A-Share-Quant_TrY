from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _to_float(value: Any, default: float = 0.0) -> float:
    text = str(value).strip()
    if text == "":
        return default
    try:
        return float(text)
    except (TypeError, ValueError):
        return default


@dataclass(slots=True)
class V115LCpoIntradayStrictBandRefinementReport:
    summary: dict[str, Any]
    candidate_band_rows: list[dict[str, Any]]
    strict_registry_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "candidate_band_rows": self.candidate_band_rows,
            "strict_registry_rows": self.strict_registry_rows,
            "interpretation": self.interpretation,
        }


class V115LCpoIntradayStrictBandRefinementAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self, *, v115k_payload: dict[str, Any]) -> V115LCpoIntradayStrictBandRefinementReport:
        summary_k = dict(v115k_payload.get("summary", {}))
        if str(summary_k.get("acceptance_posture")) != "freeze_v115k_cpo_intraday_band_action_audit_v1":
            raise ValueError("V115L expects V115K band action audit.")

        candidate_band_rows = [
            dict(row)
            for row in list(v115k_payload.get("band_registry_rows", []))
            if str(row.get("band_posture")) == "candidate_add_band"
        ]
        strict_registry_rows: list[dict[str, Any]] = []
        for row in candidate_band_rows:
            increase_rate = _to_float(row.get("increase_rate"))
            expectancy = _to_float(row.get("avg_expectancy_proxy_3d"))
            adverse = _to_float(row.get("avg_max_adverse_return_3d"))
            row_count = int(row.get("row_count", 0))
            strict_posture = (
                "strict_candidate_add_band"
                if increase_rate >= 0.25 and expectancy >= 0.05 and adverse > -0.06 and row_count >= 4
                else "soft_candidate_add_band"
            )
            strict_registry_rows.append(
                {
                    "state_band": str(row["state_band"]),
                    "row_count": row_count,
                    "increase_rate": increase_rate,
                    "avg_expectancy_proxy_3d": expectancy,
                    "avg_max_adverse_return_3d": adverse,
                    "strict_posture": strict_posture,
                }
            )

        strict_add_band_count = sum(1 for row in strict_registry_rows if str(row["strict_posture"]) == "strict_candidate_add_band")
        strict_band_names = [str(row["state_band"]) for row in strict_registry_rows if str(row["strict_posture"]) == "strict_candidate_add_band"]
        summary = {
            "acceptance_posture": "freeze_v115l_cpo_intraday_strict_band_refinement_v1",
            "candidate_add_band_count_before_refinement": len(candidate_band_rows),
            "strict_candidate_add_band_count": strict_add_band_count,
            "strict_candidate_add_band_names": strict_band_names,
            "recommended_next_posture": "only_strict_candidate_add_bands_should_be_tested_in_overlay_audit_next",
        }
        interpretation = [
            "V1.15L accepts that the first band audit is too permissive if every positive-looking band is treated equally.",
            "The refinement step narrows add-band candidates using expectancy, adverse path quality, and minimum support count.",
            "This keeps the next overlay test focused on the cleanest bands instead of letting all positive-looking regions leak into action logic at once.",
        ]
        return V115LCpoIntradayStrictBandRefinementReport(
            summary=summary,
            candidate_band_rows=candidate_band_rows,
            strict_registry_rows=strict_registry_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V115LCpoIntradayStrictBandRefinementReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V115LCpoIntradayStrictBandRefinementAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v115k_payload=json.loads((repo_root / "reports" / "analysis" / "v115k_cpo_intraday_band_action_audit_v1.json").read_text(encoding="utf-8")),
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v115l_cpo_intraday_strict_band_refinement_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
