from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134IYCommercialAerospaceEventAttentionHeatProxyAuditV1Report:
    summary: dict[str, Any]
    heat_proxy_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "heat_proxy_rows": self.heat_proxy_rows,
            "interpretation": self.interpretation,
        }


class V134IYCommercialAerospaceEventAttentionHeatProxyAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.output_csv = (
            repo_root
            / "data"
            / "training"
            / "commercial_aerospace_event_attention_heat_proxy_v1.csv"
        )

    def _load_json(self, relative_path: str) -> dict[str, Any]:
        return json.loads((self.repo_root / relative_path).read_text(encoding="utf-8"))

    @staticmethod
    def _to_float(value: Any) -> float | None:
        if value in ("", None):
            return None
        return float(value)

    def analyze(self) -> V134IYCommercialAerospaceEventAttentionHeatProxyAuditV1Report:
        role_candidates = self._load_json(
            "reports/analysis/v134hy_commercial_aerospace_event_attention_role_candidate_audit_v1.json"
        )
        role_separation = self._load_json(
            "reports/analysis/v134ia_commercial_aerospace_event_attention_role_separation_audit_v1.json"
        )
        followthrough = self._load_json(
            "reports/analysis/v134ii_commercial_aerospace_symbol_followthrough_supervision_audit_v1.json"
        )

        candidate_by_symbol = {row["symbol"]: row for row in role_candidates["candidate_rows"]}
        separated_by_symbol = {row["symbol"]: row for row in role_separation["separated_rows"]}
        followthrough_by_symbol = {row["symbol"]: row for row in followthrough["followthrough_rows"]}

        symbols = ["000547", "603601", "002361", "300342", "301306"]
        rows: list[dict[str, Any]] = []
        for symbol in symbols:
            candidate_row = candidate_by_symbol[symbol]
            separated_row = separated_by_symbol.get(symbol, {})
            followthrough_row = followthrough_by_symbol.get(symbol, {})

            avg_turnover = self._to_float(candidate_row.get("avg_turnover_rate_f"))
            max_turnover = self._to_float(candidate_row.get("max_turnover_rate_f"))
            peak_gap = self._to_float(candidate_row.get("post_lockout_max_vs_pre_lockout_peak"))
            follow_label = followthrough_row.get("followthrough_label", "not_labeled")

            if symbol == "000547":
                heat_proxy_class = "explicit_heat_anchor_seed"
                heat_proxy_reading = (
                    "anchor authority comes from explicit turning-point heat naming rather than from a pure price-strength proxy"
                )
            elif symbol == "603601":
                heat_proxy_class = "event_backed_heat_carrier_proxy"
                heat_proxy_reading = (
                    "retained event backing plus the strongest turnover concentration and persistent symbol-level followthrough make it the strongest soft heat-carrier proxy"
                )
            elif symbol == "002361":
                heat_proxy_class = "crowded_heat_proxy_without_anchor"
                heat_proxy_reading = (
                    "crowding and high turnover exist, but the symbol lacks retained event backing and persistent followthrough, so it stays a non-anchor heat proxy"
                )
            elif symbol == "300342":
                heat_proxy_class = "breakout_heat_proxy_without_anchor"
                heat_proxy_reading = (
                    "lockout-window breakout and moderate followthrough create visible heat, but retained event support is still too weak for anchor or carrier promotion"
                )
            else:
                heat_proxy_class = "event_backed_follow_heat_proxy"
                heat_proxy_reading = (
                    "event support exists, but the current path still reads like a high-beta follower rather than an attention anchor or carrier"
                )

            rows.append(
                {
                    "symbol": symbol,
                    "display_name": candidate_row["display_name"],
                    "candidate_status": candidate_row["candidate_status"],
                    "candidate_role": candidate_row["candidate_role"],
                    "separated_role": separated_row.get("separated_role", ""),
                    "crowded_rebound_family": candidate_row["crowded_rebound_family"],
                    "avg_turnover_rate_f": avg_turnover,
                    "max_turnover_rate_f": max_turnover,
                    "post_lockout_max_vs_pre_lockout_peak": peak_gap,
                    "followthrough_label": follow_label,
                    "heat_proxy_class": heat_proxy_class,
                    "heat_proxy_reading": heat_proxy_reading,
                }
            )

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

        strongest_soft = max(
            (row for row in rows if row["symbol"] != "000547"),
            key=lambda row: (
                1 if row["heat_proxy_class"] == "event_backed_heat_carrier_proxy" else 0,
                row["max_turnover_rate_f"] or 0.0,
                1 if row["followthrough_label"] == "persistent_symbol_followthrough_without_board_unlock" else 0,
            ),
        )
        summary = {
            "acceptance_posture": "freeze_v134iy_commercial_aerospace_event_attention_heat_proxy_audit_v1",
            "symbol_count": len(rows),
            "explicit_heat_anchor_seed_count": sum(1 for row in rows if row["heat_proxy_class"] == "explicit_heat_anchor_seed"),
            "event_backed_heat_carrier_proxy_count": sum(
                1 for row in rows if row["heat_proxy_class"] == "event_backed_heat_carrier_proxy"
            ),
            "non_anchor_heat_proxy_count": sum(1 for row in rows if "without_anchor" in row["heat_proxy_class"]),
            "strongest_soft_heat_proxy_symbol": strongest_soft["symbol"],
            "counterpanel_thickened": False,
            "heat_proxy_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_rule": "board-local heat proxies can now separate explicit anchor, soft carrier, concentration-only, breakout-only, and follow-only roles, but this still does not create a second hard counterpanel or reopen capital_true_selection",
        }
        interpretation = [
            "V1.34IY adds a board-local heat-proxy layer without pretending the stack has real cross-market heat data.",
            "The gain is local role clarity: who is explicitly named heat, who is the strongest soft carrier proxy, and who is merely concentrated or following heat.",
        ]
        return V134IYCommercialAerospaceEventAttentionHeatProxyAuditV1Report(
            summary=summary,
            heat_proxy_rows=rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134IYCommercialAerospaceEventAttentionHeatProxyAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134IYCommercialAerospaceEventAttentionHeatProxyAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134iy_commercial_aerospace_event_attention_heat_proxy_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
