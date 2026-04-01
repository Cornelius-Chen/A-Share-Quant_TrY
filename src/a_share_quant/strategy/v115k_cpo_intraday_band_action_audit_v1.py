from __future__ import annotations

import csv
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


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def write_csv_rows(*, path: Path, rows: list[dict[str, Any]]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = sorted({key for row in rows for key in row.keys()})
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return path


@dataclass(slots=True)
class V115KCpoIntradayBandActionAuditReport:
    summary: dict[str, Any]
    band_registry_rows: list[dict[str, Any]]
    context_hit_rows: list[dict[str, Any]]
    selected_add_rows: list[dict[str, Any]]
    selected_reduce_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "band_registry_rows": self.band_registry_rows,
            "context_hit_rows": self.context_hit_rows,
            "selected_add_rows": self.selected_add_rows,
            "selected_reduce_rows": self.selected_reduce_rows,
            "interpretation": self.interpretation,
        }


class V115KCpoIntradayBandActionAuditAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    @staticmethod
    def _band_posture(row: dict[str, Any]) -> str:
        increase_rate = _to_float(row.get("increase_rate"))
        decrease_rate = _to_float(row.get("decrease_rate"))
        expectancy = _to_float(row.get("avg_expectancy_proxy_3d"))
        adverse = _to_float(row.get("avg_max_adverse_return_3d"))
        if increase_rate >= 0.20 and expectancy > 0.0 and adverse > -0.08:
            return "candidate_add_band"
        if decrease_rate >= 0.35 and expectancy <= 0.0:
            return "candidate_reduce_band"
        return "hold_band"

    def analyze(
        self,
        *,
        v114w_payload: dict[str, Any],
        v115j_payload: dict[str, Any],
        annotated_rows: list[dict[str, Any]],
    ) -> tuple[V115KCpoIntradayBandActionAuditReport, list[dict[str, Any]]]:
        summary_w = dict(v114w_payload.get("summary", {}))
        summary_j = dict(v115j_payload.get("summary", {}))
        if str(summary_w.get("acceptance_posture")) != "freeze_v114w_cpo_under_exposure_attribution_repaired_v1":
            raise ValueError("V115K expects repaired under-exposure attribution.")
        if str(summary_j.get("acceptance_posture")) != "freeze_v115j_cpo_high_dimensional_intraday_pca_band_audit_v1":
            raise ValueError("V115K expects V115J PCA band audit.")

        top_miss_dates = {str(row["trade_date"]) for row in list(v114w_payload.get("top_opportunity_miss_rows", []))}

        band_registry_rows: list[dict[str, Any]] = []
        for row in list(v115j_payload.get("band_context_rows", [])):
            posture = self._band_posture(row)
            band_registry_rows.append(
                {
                    "state_band": str(row["state_band"]),
                    "row_count": int(row["row_count"]),
                    "increase_rate": _to_float(row.get("increase_rate")),
                    "decrease_rate": _to_float(row.get("decrease_rate")),
                    "hold_rate": _to_float(row.get("hold_rate")),
                    "avg_expectancy_proxy_3d": _to_float(row.get("avg_expectancy_proxy_3d")),
                    "avg_max_adverse_return_3d": _to_float(row.get("avg_max_adverse_return_3d")),
                    "band_posture": posture,
                }
            )

        add_bands = {row["state_band"] for row in band_registry_rows if row["band_posture"] == "candidate_add_band"}
        reduce_bands = {row["state_band"] for row in band_registry_rows if row["band_posture"] == "candidate_reduce_band"}

        for row in annotated_rows:
            row["band_posture"] = (
                "candidate_add_band"
                if str(row.get("state_band")) in add_bands
                else "candidate_reduce_band"
                if str(row.get("state_band")) in reduce_bands
                else "hold_band"
            )
            row["is_top_miss_date"] = str(row.get("signal_trade_date")) in top_miss_dates

        context_hit_rows: list[dict[str, Any]] = []
        contexts = sorted({str(row["action_context"]) for row in annotated_rows})
        for context in contexts:
            rows = [row for row in annotated_rows if str(row["action_context"]) == context]
            context_hit_rows.append(
                {
                    "action_context": context,
                    "row_count": len(rows),
                    "candidate_add_band_rate": round(_mean([1.0 if str(row["band_posture"]) == "candidate_add_band" else 0.0 for row in rows]), 6),
                    "candidate_reduce_band_rate": round(_mean([1.0 if str(row["band_posture"]) == "candidate_reduce_band" else 0.0 for row in rows]), 6),
                    "top_miss_candidate_add_rate": round(
                        _mean(
                            [
                                1.0
                                if bool(row["is_top_miss_date"]) and str(row["band_posture"]) == "candidate_add_band"
                                else 0.0
                                for row in rows
                            ]
                        ),
                        6,
                    ),
                    "avg_expectancy_proxy_3d": round(_mean([_to_float(row.get("expectancy_proxy_3d")) for row in rows]), 6),
                }
            )

        selected_add_rows = sorted(
            [
                {
                    "signal_trade_date": str(row["signal_trade_date"]),
                    "symbol": str(row["symbol"]),
                    "action_context": str(row["action_context"]),
                    "state_band": str(row["state_band"]),
                    "expectancy_proxy_3d": _to_float(row.get("expectancy_proxy_3d")),
                    "max_adverse_return_3d": _to_float(row.get("max_adverse_return_3d")),
                    "is_top_miss_date": bool(row["is_top_miss_date"]),
                }
                for row in annotated_rows
                if str(row["band_posture"]) == "candidate_add_band"
            ],
            key=lambda item: (item["is_top_miss_date"], item["expectancy_proxy_3d"]),
            reverse=True,
        )[:20]

        selected_reduce_rows = sorted(
            [
                {
                    "signal_trade_date": str(row["signal_trade_date"]),
                    "symbol": str(row["symbol"]),
                    "action_context": str(row["action_context"]),
                    "state_band": str(row["state_band"]),
                    "expectancy_proxy_3d": _to_float(row.get("expectancy_proxy_3d")),
                    "max_adverse_return_3d": _to_float(row.get("max_adverse_return_3d")),
                }
                for row in annotated_rows
                if str(row["band_posture"]) == "candidate_reduce_band"
            ],
            key=lambda item: item["max_adverse_return_3d"],
        )[:20]

        summary = {
            "acceptance_posture": "freeze_v115k_cpo_intraday_band_action_audit_v1",
            "band_count": len(band_registry_rows),
            "candidate_add_band_count": len(add_bands),
            "candidate_reduce_band_count": len(reduce_bands),
            "annotated_row_count": len(annotated_rows),
            "top_miss_day_count": len(top_miss_dates),
            "candidate_add_row_count": len([row for row in annotated_rows if str(row["band_posture"]) == "candidate_add_band"]),
            "candidate_reduce_row_count": len([row for row in annotated_rows if str(row["band_posture"]) == "candidate_reduce_band"]),
            "recommended_next_posture": "candidate_only_band_overlay_audit_before_any_replay_binding",
        }
        interpretation = [
            "V1.15K is an action audit on top of V115J bands, not a replay promotion. It asks which continuous-state bands behave like candidate add zones and which behave like reduce zones.",
            "The purpose is to turn PCA band discovery into candidate action semantics without forcing hard clustering or immediate execution-law promotion.",
            "If the same bands repeatedly align with repaired miss days and favorable expectancy, they can later be tested as overlay candidates; until then they remain candidate-only.",
        ]
        report = V115KCpoIntradayBandActionAuditReport(
            summary=summary,
            band_registry_rows=band_registry_rows,
            context_hit_rows=context_hit_rows,
            selected_add_rows=selected_add_rows,
            selected_reduce_rows=selected_reduce_rows,
            interpretation=interpretation,
        )
        return report, annotated_rows


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V115KCpoIntradayBandActionAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    with (repo_root / "data" / "training" / "cpo_midfreq_pca_band_rows_v1.csv").open("r", encoding="utf-8") as handle:
        annotated_rows = list(csv.DictReader(handle))
    analyzer = V115KCpoIntradayBandActionAuditAnalyzer(repo_root=repo_root)
    result, output_rows = analyzer.analyze(
        v114w_payload=json.loads((repo_root / "reports" / "analysis" / "v114w_cpo_under_exposure_attribution_repaired_v1.json").read_text(encoding="utf-8")),
        v115j_payload=json.loads((repo_root / "reports" / "analysis" / "v115j_cpo_high_dimensional_intraday_pca_band_audit_v1.json").read_text(encoding="utf-8")),
        annotated_rows=annotated_rows,
    )
    write_csv_rows(
        path=repo_root / "data" / "training" / "cpo_midfreq_band_action_audit_rows_v1.csv",
        rows=output_rows,
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v115k_cpo_intraday_band_action_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
