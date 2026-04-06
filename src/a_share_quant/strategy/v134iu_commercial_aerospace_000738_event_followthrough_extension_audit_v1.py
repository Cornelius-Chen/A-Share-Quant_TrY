from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134IUCommercialAerospace000738EventFollowthroughExtensionAuditV1Report:
    summary: dict[str, Any]
    extension_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "extension_rows": self.extension_rows,
            "interpretation": self.interpretation,
        }


class V134IUCommercialAerospace000738EventFollowthroughExtensionAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.output_csv = (
            repo_root
            / "data"
            / "training"
            / "commercial_aerospace_000738_event_followthrough_extension_v1.csv"
        )

    def _load_json(self, relative_path: str) -> dict[str, Any]:
        return json.loads((self.repo_root / relative_path).read_text(encoding="utf-8"))

    def analyze(self) -> V134IUCommercialAerospace000738EventFollowthroughExtensionAuditV1Report:
        outside_watch = self._load_json(
            "reports/analysis/v134is_commercial_aerospace_outside_named_second_carrier_supervision_audit_v1.json"
        )
        local_rebound = self._load_json(
            "reports/analysis/v134bk_commercial_aerospace_local_only_rebound_audit_v1.json"
        )
        event_attention = self._load_json(
            "reports/analysis/v134hw_commercial_aerospace_event_attention_supervision_registry_v1.json"
        )
        daily_bars = list(
            csv.DictReader(
                (self.repo_root / "data" / "raw" / "daily_bars" / "tushare_commercial_aerospace_daily_bars_v1.csv").open(
                    encoding="utf-8-sig"
                )
            )
        )

        watch_row = next(row for row in outside_watch["supervision_rows"] if row["symbol"] == "000738")
        local_rows = [row for row in local_rebound["seed_rows"] if row["top_symbol"] == "000738"]
        event_rows = [row for row in event_attention["registry_rows"] if row["symbol"] == "000738"]
        daily_rows = [row for row in daily_bars if row["symbol"] == "000738" and "20260115" <= row["trade_date"] <= "20260403"]
        daily_rows.sort(key=lambda row: row["trade_date"])
        max_row = max(daily_rows, key=lambda row: float(row["close"]))
        end_row = daily_rows[-1]
        drawdown = round(float(end_row["close"]) / float(max_row["close"]) - 1.0, 8)

        extension_rows = [
            {
                "symbol": "000738",
                "display_name": "航发控制",
                "extension_layer": "event_backing_extension",
                "current_status": "still_absent",
                "observed_event_seed_count": len(event_rows),
                "observed_local_top_day_count": "",
                "post_lockout_max_trade_date": "",
                "post_lockout_drawdown_from_max_to_end": "",
                "learning_reading": "no retained event-attention seed currently references 000738 directly, so outside-named promotion still lacks lawful event backing",
            },
            {
                "symbol": "000738",
                "display_name": "航发控制",
                "extension_layer": "local_rebound_leadership_extension",
                "current_status": "explicitly_present",
                "observed_event_seed_count": "",
                "observed_local_top_day_count": len(local_rows),
                "post_lockout_max_trade_date": "",
                "post_lockout_drawdown_from_max_to_end": "",
                "learning_reading": "000738 owns repeated local-only rebound leadership days inside a still-locked board, which is the main reason it remains the best outside-named second-carrier watch",
            },
            {
                "symbol": "000738",
                "display_name": "航发控制",
                "extension_layer": "followthrough_extension",
                "current_status": "moderate_but_not_persistent",
                "observed_event_seed_count": "",
                "observed_local_top_day_count": "",
                "post_lockout_max_trade_date": max_row["trade_date"],
                "post_lockout_drawdown_from_max_to_end": drawdown,
                "learning_reading": "000738 builds meaningful post-lockout continuation and breakout strength, but the later giveback remains too large for persistent followthrough promotion",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(extension_rows[0].keys()))
            writer.writeheader()
            writer.writerows(extension_rows)

        summary = {
            "acceptance_posture": "freeze_v134iu_commercial_aerospace_000738_event_followthrough_extension_audit_v1",
            "symbol": "000738",
            "event_backing_present": False,
            "local_rebound_leadership_day_count": len(local_rows),
            "followthrough_extension_label": "moderate_but_not_persistent",
            "extension_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_rule": "000738 remains a lawful outside-named second-carrier watch because local rebound leadership is real, but promotion is still blocked by absent retained event backing and only moderate, not persistent, followthrough extension",
        }
        interpretation = [
            "V1.34IU extends the outside-named watch into the same two missing evidence layers that blocked premature promotion.",
            "The result is asymmetric and useful: 000738 passes the local leadership extension, but still fails the retained event-backing extension and only reaches moderate followthrough extension.",
        ]
        return V134IUCommercialAerospace000738EventFollowthroughExtensionAuditV1Report(
            summary=summary,
            extension_rows=extension_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134IUCommercialAerospace000738EventFollowthroughExtensionAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134IUCommercialAerospace000738EventFollowthroughExtensionAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134iu_commercial_aerospace_000738_event_followthrough_extension_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
