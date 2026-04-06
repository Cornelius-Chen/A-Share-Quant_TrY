from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v122_supportive_continuation_utils import load_supportive_continuation_rows


@dataclass(slots=True)
class V122JCpo1MinSupportiveFamilyProxyLabelAuditReport:
    summary: dict[str, Any]
    label_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "label_rows": self.label_rows,
            "interpretation": self.interpretation,
        }


class V122JCpo1MinSupportiveFamilyProxyLabelAuditAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V122JCpo1MinSupportiveFamilyProxyLabelAuditReport:
        supportive_rows = load_supportive_continuation_rows(self.repo_root)
        label_path = self.repo_root / "data" / "training" / "cpo_recent_1min_proxy_action_timepoint_label_base_v1.csv"
        with label_path.open("r", encoding="utf-8") as handle:
            label_rows = list(csv.DictReader(handle))

        supportive_keys = {(row["symbol"], row["trade_date"], row["clock_time"]) for row in supportive_rows}
        supportive_label_counts: dict[str, int] = {}
        total_supportive = 0
        for row in label_rows:
            key = (row["symbol"], row["trade_date"], row["clock_time"])
            if key not in supportive_keys:
                continue
            total_supportive += 1
            label = row["proxy_action_label"]
            supportive_label_counts[label] = supportive_label_counts.get(label, 0) + 1

        overall_label_counts: dict[str, int] = {}
        for row in label_rows:
            label = row["proxy_action_label"]
            overall_label_counts[label] = overall_label_counts.get(label, 0) + 1

        labels = sorted(set(overall_label_counts) | set(supportive_label_counts))
        comparison_rows = []
        for label in labels:
            supportive_count = supportive_label_counts.get(label, 0)
            overall_count = overall_label_counts.get(label, 0)
            supportive_rate = supportive_count / total_supportive if total_supportive else 0.0
            overall_rate = overall_count / len(label_rows) if label_rows else 0.0
            comparison_rows.append(
                {
                    "label": label,
                    "supportive_count": supportive_count,
                    "supportive_rate": round(supportive_rate, 8),
                    "overall_count": overall_count,
                    "overall_rate": round(overall_rate, 8),
                    "enrichment_vs_overall": round(supportive_rate - overall_rate, 8),
                }
            )

        add_row = next((row for row in comparison_rows if row["label"] == "add_probe"), None)
        reduce_row = next((row for row in comparison_rows if row["label"] == "reduce_probe"), None)
        close_row = next((row for row in comparison_rows if row["label"] == "close_probe"), None)
        summary = {
            "acceptance_posture": "freeze_v122j_cpo_1min_supportive_family_proxy_label_audit_v1",
            "supportive_row_count": total_supportive,
            "base_row_count": len(label_rows),
            "supportive_add_enrichment": add_row["enrichment_vs_overall"] if add_row else 0.0,
            "supportive_reduce_enrichment": reduce_row["enrichment_vs_overall"] if reduce_row else 0.0,
            "supportive_close_enrichment": close_row["enrichment_vs_overall"] if close_row else 0.0,
            "recommended_next_posture": "triage_supportive_family_against_proxy_label_plane",
        }
        interpretation = [
            "V1.22J checks whether the surviving supportive 1-minute family actually concentrates in add-probe rows rather than just looking directionally positive in aggregate.",
            "This is the first direct bridge between the surviving 1-minute family and the stricter proxy action-timepoint label base.",
            "The next step is to triage whether this enrichment is enough to keep the family alive under the new label plane.",
        ]
        return V122JCpo1MinSupportiveFamilyProxyLabelAuditReport(
            summary=summary,
            label_rows=comparison_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V122JCpo1MinSupportiveFamilyProxyLabelAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V122JCpo1MinSupportiveFamilyProxyLabelAuditAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v122j_cpo_1min_supportive_family_proxy_label_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
