from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V122ICpo1MinProxyLabelBaseReadinessAuditReport:
    summary: dict[str, Any]
    symbol_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "symbol_rows": self.symbol_rows,
            "interpretation": self.interpretation,
        }


class V122ICpo1MinProxyLabelBaseReadinessAuditAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V122ICpo1MinProxyLabelBaseReadinessAuditReport:
        path = self.repo_root / "data" / "training" / "cpo_recent_1min_proxy_action_timepoint_label_base_v1.csv"
        with path.open("r", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))

        by_symbol: dict[str, dict[str, int]] = {}
        for row in rows:
            symbol = row["symbol"]
            label = row["proxy_action_label"]
            symbol_counts = by_symbol.setdefault(symbol, {})
            symbol_counts[label] = symbol_counts.get(label, 0) + 1

        symbol_rows = []
        for symbol, counts in sorted(by_symbol.items()):
            symbol_rows.append(
                {
                    "symbol": symbol,
                    "row_count": sum(counts.values()),
                    "add_probe_count": counts.get("add_probe", 0),
                    "reduce_probe_count": counts.get("reduce_probe", 0),
                    "close_probe_count": counts.get("close_probe", 0),
                    "hold_probe_count": counts.get("hold_probe", 0),
                }
            )

        summary = {
            "acceptance_posture": "freeze_v122i_cpo_1min_proxy_label_base_readiness_audit_v1",
            "symbol_count": len(symbol_rows),
            "row_count": len(rows),
            "label_plane_status": "recent_1min_proxy_action_timepoint_label_base_ready",
            "recommended_next_posture": "re_audit_surviving_1min_family_against_proxy_labels",
        }
        interpretation = [
            "V1.22I confirms the recent 1-minute plane now has a concrete proxy action-timepoint label base.",
            "This is still only a recent local label plane, but it is strong enough to replace unlabeled geometric family tuning.",
            "The next step is to re-audit surviving 1-minute families against these proxy labels.",
        ]
        return V122ICpo1MinProxyLabelBaseReadinessAuditReport(
            summary=summary,
            symbol_rows=symbol_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V122ICpo1MinProxyLabelBaseReadinessAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V122ICpo1MinProxyLabelBaseReadinessAuditAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v122i_cpo_1min_proxy_label_base_readiness_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
