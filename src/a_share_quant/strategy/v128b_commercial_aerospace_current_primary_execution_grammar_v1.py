from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V128BCommercialAerospaceCurrentPrimaryExecutionGrammarReport:
    summary: dict[str, Any]
    grammar_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "grammar_rows": self.grammar_rows,
            "interpretation": self.interpretation,
        }


class V128BCommercialAerospaceCurrentPrimaryExecutionGrammarAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.robustness_path = repo_root / "reports" / "analysis" / "v127y_commercial_aerospace_primary_reference_robustness_audit_v1.json"
        self.attribution_path = repo_root / "reports" / "analysis" / "v128a_commercial_aerospace_current_primary_attribution_v1.json"

    def analyze(self) -> V128BCommercialAerospaceCurrentPrimaryExecutionGrammarReport:
        robustness = json.loads(self.robustness_path.read_text(encoding="utf-8"))
        attribution = json.loads(self.attribution_path.read_text(encoding="utf-8"))

        old_variant = attribution["summary"]["old_primary_variant"]
        new_variant = attribution["summary"]["new_primary_variant"]
        reason_rows = attribution["reason_rows"]
        reason_map = {
            (row["variant"], row["action"], row["reason"]): row["count"]
            for row in reason_rows
        }
        drawdown_rows = attribution["drawdown_rows"]
        largest_window = drawdown_rows[0] if drawdown_rows else {}

        grammar_rows = [
            {
                "layer": "entry_surface",
                "current_primary_rule": "retain selective impulse-only drag veto entry surface from prior primary",
                "evidence": "preheat probe/full counts stay unchanged; only a marginal +1 impulse full order appears in the new primary",
            },
            {
                "layer": "window_specific_derisk",
                "current_primary_rule": "inside 20260112->20260212, sell 100% on risk_off_deterioration, sell 75% on weak_drift_chop, and sell 50% on impulse de-risk target",
                "evidence": "new primary variant name encodes full riskoff, weakdrift_075, and impulse_half",
            },
            {
                "layer": "reason_shift",
                "current_primary_rule": "add a narrow impulse-target de-risk reason without broadening entry heat",
                "evidence": (
                    f"impulse-target reduce count rises from {reason_map.get((old_variant, 'reduce', 'window_derisk_impulse_target'), 0)} "
                    f"to {reason_map.get((new_variant, 'reduce', 'window_derisk_impulse_target'), 0)} while preheat probe/full counts stay at "
                    f"{reason_map.get((new_variant, 'open', 'phase_geometry_preheat_probe'), 0)} / "
                    f"{reason_map.get((new_variant, 'open', 'phase_geometry_preheat_full'), 0)}"
                ),
            },
            {
                "layer": "drawdown_control",
                "current_primary_rule": "concentrate extra de-risk in the largest drawdown window rather than sell more everywhere",
                "evidence": (
                    f"largest window {largest_window.get('peak_trade_date','')}->{largest_window.get('trough_trade_date','')}: "
                    f"reduce notional rises from {largest_window.get('old_reduce_notional', 0)} to {largest_window.get('new_reduce_notional', 0)}"
                ),
            },
            {
                "layer": "symbol_beneficiaries",
                "current_primary_rule": "the improved grammar mainly helps 688568, 600118, and 600879 while leaving mild pressure on 300342 and 000738",
                "evidence": (
                    f"top symbol improver = {attribution['summary']['top_symbol_improver']} "
                    f"({attribution['summary']['top_symbol_improver_delta']})"
                ),
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v128b_commercial_aerospace_current_primary_execution_grammar_v1",
            "current_primary_variant": new_variant,
            "prior_primary_variant": old_variant,
            "split_frontier_wins": robustness["summary"]["split_frontier_wins"],
            "suffix_frontier_wins": robustness["summary"]["suffix_frontier_wins"],
            "equity_delta_new_minus_old": attribution["summary"]["equity_delta_new_minus_old"],
            "drawdown_delta_new_minus_old": attribution["summary"]["drawdown_delta_new_minus_old"],
            "execution_grammar_compaction": "entry_surface_stable_plus_window_specific_derisk_intensification",
            "authoritative_next_question": "which part of this grammar is portable versus commercial-aerospace specific",
        }
        interpretation = [
            "V1.28B compresses the current commercial-aerospace primary into an execution grammar rather than another replay comparison table.",
            "The key finding is that the current primary does not win by broadening entry aggression; it wins by keeping the same entry skeleton and intensifying de-risk only in the main drawdown window.",
        ]
        return V128BCommercialAerospaceCurrentPrimaryExecutionGrammarReport(
            summary=summary,
            grammar_rows=grammar_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V128BCommercialAerospaceCurrentPrimaryExecutionGrammarReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V128BCommercialAerospaceCurrentPrimaryExecutionGrammarAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v128b_commercial_aerospace_current_primary_execution_grammar_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
