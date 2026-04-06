from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V131YCommercialAerospaceIntradaySupervisionRegistryReport:
    summary: dict[str, Any]
    registry_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "registry_rows": self.registry_rows,
            "interpretation": self.interpretation,
        }


class V131YCommercialAerospaceIntradaySupervisionRegistryAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.supervision_report_path = (
            repo_root / "reports" / "analysis" / "v131d_commercial_aerospace_intraday_override_supervision_table_v1.json"
        )
        self.prototype_report_path = (
            repo_root / "reports" / "analysis" / "v131s_commercial_aerospace_local_5min_override_prototype_audit_v1.json"
        )
        self.mild_watch_report_path = (
            repo_root / "reports" / "analysis" / "v131w_commercial_aerospace_local_5min_ambiguous_case_audit_v1.json"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "commercial_aerospace_intraday_supervision_registry_v1.csv"
        )

    def analyze(self) -> V131YCommercialAerospaceIntradaySupervisionRegistryReport:
        supervision = json.loads(self.supervision_report_path.read_text(encoding="utf-8"))
        prototype = json.loads(self.prototype_report_path.read_text(encoding="utf-8"))
        mild_watch = json.loads(self.mild_watch_report_path.read_text(encoding="utf-8"))

        supervision_map = {
            (row["execution_trade_date"], row["symbol"], row["action"]): row
            for row in supervision["supervision_rows"]
        }
        prototype_map = {
            (row["execution_trade_date"], row["symbol"], row["action"]): row
            for row in prototype["prototype_rows"]
        }
        mild_watch_keys = {
            (row["execution_trade_date"], row["symbol"], row["action"]) for row in mild_watch["retained_rows"]
        }

        registry_rows: list[dict[str, Any]] = []
        for key, supervision_row in supervision_map.items():
            label = supervision_row["supervision_label"]
            if label not in {"override_positive", "reversal_watch"} and key not in mild_watch_keys:
                continue

            if label == "override_positive":
                severity_tier = "severe_override_positive"
            elif label == "reversal_watch":
                severity_tier = "reversal_watch"
            else:
                severity_tier = "mild_override_watch"

            proto = prototype_map.get(key, {})
            registry_rows.append(
                {
                    "signal_trade_date": supervision_row["signal_trade_date"],
                    "execution_trade_date": supervision_row["execution_trade_date"],
                    "symbol": supervision_row["symbol"],
                    "action": supervision_row["action"],
                    "reason": supervision_row["reason"],
                    "signal_label_pg": supervision_row["signal_label_pg"],
                    "phase_window_semantic": supervision_row["phase_window_semantic"],
                    "regime_proxy_semantic": supervision_row["regime_proxy_semantic"],
                    "event_state": supervision_row["event_state"],
                    "pre_open_event_status": supervision_row["pre_open_event_status"],
                    "failure_type": supervision_row["failure_type"],
                    "supervision_label": supervision_row["supervision_label"],
                    "severity_tier": severity_tier,
                    "open_to_close_return": supervision_row["open_to_close_return"],
                    "close_location": supervision_row["close_location"],
                    "forward_return_10": supervision_row["forward_return_10"],
                    "max_adverse_return_10": supervision_row["max_adverse_return_10"],
                    "ret15": proto.get("ret15", ""),
                    "ret30": proto.get("ret30", ""),
                    "ret60": proto.get("ret60", ""),
                    "draw15": proto.get("draw15", ""),
                    "draw60": proto.get("draw60", ""),
                    "close_loc15": proto.get("close_loc15", ""),
                    "close_loc60": proto.get("close_loc60", ""),
                    "prototype_flag": proto.get("prototype_flag", False),
                }
            )

        registry_rows.sort(key=lambda row: (row["execution_trade_date"], row["symbol"], row["severity_tier"]))

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(registry_rows[0].keys()))
            writer.writeheader()
            writer.writerows(registry_rows)

        severe_count = sum(1 for row in registry_rows if row["severity_tier"] == "severe_override_positive")
        reversal_count = sum(1 for row in registry_rows if row["severity_tier"] == "reversal_watch")
        mild_count = sum(1 for row in registry_rows if row["severity_tier"] == "mild_override_watch")

        summary = {
            "acceptance_posture": "freeze_v131y_commercial_aerospace_intraday_supervision_registry_v1",
            "registry_csv": str(self.output_csv.relative_to(self.repo_root)),
            "registry_row_count": len(registry_rows),
            "severe_override_positive_count": severe_count,
            "reversal_watch_count": reversal_count,
            "mild_override_watch_count": mild_count,
            "authoritative_rule": "the minute-level supervision registry should unify severe, reversal, and mild override-watch seeds before any later 1min formalization",
        }
        interpretation = [
            "V1.31Y consolidates the commercial-aerospace intraday supervision stack into a single registry.",
            "The registry is the correct handoff object for future minute-level label specification because it preserves severity tiers instead of collapsing everything into one undifferentiated override class.",
        ]
        return V131YCommercialAerospaceIntradaySupervisionRegistryReport(
            summary=summary,
            registry_rows=registry_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V131YCommercialAerospaceIntradaySupervisionRegistryReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V131YCommercialAerospaceIntradaySupervisionRegistryAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v131y_commercial_aerospace_intraday_supervision_registry_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
