from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112BDPhaseCharterReport:
    summary: dict[str, Any]
    charter: dict[str, Any]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "charter": self.charter,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112BDPhaseCharterAnalyzer:
    def analyze(self, *, v112bb_phase_closure_payload: dict[str, Any]) -> V112BDPhaseCharterReport:
        closure_summary = dict(v112bb_phase_closure_payload.get("summary", {}))
        if not bool(closure_summary.get("v112bb_success_criteria_met")):
            raise ValueError("V1.12BD requires the completed V1.12BB closure check.")

        charter = {
            "phase_name": "V1.12BD Market Regime Overlay Feature Review",
            "mission": (
                "Freeze the market-regime overlay family for CPO so that broad-index trend, liquidity, board style, "
                "risk appetite, and sector ETF context can be used as lawful overlay inputs in later experiments."
            ),
            "in_scope": [
                "broad-index trend and liquidity factors",
                "ChiNext and STAR board relative-strength factors",
                "AI hardware / optics sector ETF proxies",
                "market emotion and turnover pressure overlays",
            ],
            "out_of_scope": [
                "promotion into core truth labels",
                "replacement of stock-level role logic",
                "formal signal generation",
            ],
            "success_criteria": [
                "the project has an explicit market-regime overlay family",
                "overlay factors are separated from core role and phase truth",
                "the allowed usage boundary is frozen before model-zoo expansion",
            ],
        }
        summary = {
            "acceptance_posture": "open_v112bd_market_regime_overlay_feature_review",
            "do_open_v112bd_now": True,
            "recommended_first_action": "freeze_v112bd_market_regime_overlay_feature_review_v1",
        }
        interpretation = [
            "V1.12BD exists because broad market regime, board style, and sector liquidity can influence CPO without replacing the cycle grammar itself.",
            "The phase freezes them as overlay candidates first, not as truth labels.",
        ]
        return V112BDPhaseCharterReport(summary=summary, charter=charter, interpretation=interpretation)


def write_v112bd_phase_charter_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112BDPhaseCharterReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
