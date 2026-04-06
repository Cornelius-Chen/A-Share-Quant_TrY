from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from a_share_quant.strategy.v123_1min_orthogonal_downside_utils import (
    POSITIVE_LABELS,
    balanced_accuracy,
    load_recent_1min_downside_rows,
    zscore,
)


@dataclass(slots=True)
class V123ECpo1MinDownsideSamePlaneIntegrationAuditReport:
    summary: dict[str, Any]
    variant_rows: list[dict[str, Any]]
    time_split_rows: list[dict[str, Any]]
    symbol_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "variant_rows": self.variant_rows,
            "time_split_rows": self.time_split_rows,
            "symbol_rows": self.symbol_rows,
            "interpretation": self.interpretation,
        }


class V123ECpo1MinDownsideSamePlaneIntegrationAuditAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V123ECpo1MinDownsideSamePlaneIntegrationAuditReport:
        rows = load_recent_1min_downside_rows(self.repo_root)
        y_true = np.asarray([row["proxy_action_label"] in POSITIVE_LABELS for row in rows], dtype=bool)

        downside = np.asarray([float(row["downside_failure_score"]) for row in rows], dtype=float)
        orth = np.asarray([float(row["gap_exhaustion_stall_score"]) for row in rows], dtype=float)
        downside_z = zscore(list(downside))
        orth_z = zscore(list(orth))

        variants: dict[str, np.ndarray] = {
            "downside_failure_reference": downside,
            "gap_exhaustion_stall_reference": orth,
            "equal_blend_score": 0.5 * downside_z + 0.5 * orth_z,
            "downside_heavy_blend_score": 0.67 * downside_z + 0.33 * orth_z,
            "orthogonal_heavy_blend_score": 0.33 * downside_z + 0.67 * orth_z,
            "dual_confirm_min_score": np.minimum(downside_z, orth_z),
        }

        variant_rows: list[dict[str, Any]] = []
        variant_metrics: dict[str, dict[str, float]] = {}
        for name, values in variants.items():
            threshold = float(np.quantile(values, 0.75))
            y_pred = values >= threshold
            positives = values[y_true]
            negatives = values[~y_true]
            gap = float(positives.mean() - negatives.mean()) if len(positives) and len(negatives) else 0.0
            ba = balanced_accuracy(list(y_true), list(y_pred))
            corr_vs_downside = float(np.corrcoef(downside, values)[0, 1])
            corr_vs_orth = float(np.corrcoef(orth, values)[0, 1])
            variant_metrics[name] = {
                "gap": gap,
                "q75_ba": ba,
                "threshold": threshold,
            }
            variant_rows.append(
                {
                    "variant_name": name,
                    "mean_gap_positive_minus_negative": round(float(gap), 8),
                    "q75_threshold": round(float(threshold), 8),
                    "q75_balanced_accuracy": round(float(ba), 8),
                    "corr_vs_downside_failure": round(float(corr_vs_downside), 8),
                    "corr_vs_gap_exhaustion_stall": round(float(corr_vs_orth), 8),
                }
            )

        unique_dates = sorted({row["trade_date"] for row in rows})
        time_metrics: dict[str, dict[str, float]] = {}
        time_split_rows: list[dict[str, Any]] = []
        for name, values in variants.items():
            split_scores: list[float] = []
            for split_index in range(1, len(unique_dates)):
                train_dates = set(unique_dates[:split_index])
                test_dates = set(unique_dates[split_index:])
                train_indices = [i for i, row in enumerate(rows) if row["trade_date"] in train_dates]
                test_indices = [i for i, row in enumerate(rows) if row["trade_date"] in test_dates]
                if not train_indices or not test_indices:
                    continue
                threshold = float(np.quantile(values[train_indices], 0.75))
                split_scores.append(
                    balanced_accuracy(
                        list(y_true[test_indices]),
                        list(values[test_indices] >= threshold),
                    )
                )
            time_mean = float(np.mean(split_scores)) if split_scores else 0.0
            time_min = float(np.min(split_scores)) if split_scores else 0.0
            time_metrics[name] = {"mean": time_mean, "min": time_min}
            time_split_rows.append(
                {
                    "variant_name": name,
                    "mean_test_balanced_accuracy": round(float(time_mean), 8),
                    "min_test_balanced_accuracy": round(float(time_min), 8),
                }
            )

        symbols = sorted({row["symbol"] for row in rows})
        symbol_metrics: dict[str, dict[str, float]] = {}
        symbol_rows: list[dict[str, Any]] = []
        for name, values in variants.items():
            holdout_scores: list[float] = []
            for holdout_symbol in symbols:
                train_indices = [i for i, row in enumerate(rows) if row["symbol"] != holdout_symbol]
                test_indices = [i for i, row in enumerate(rows) if row["symbol"] == holdout_symbol]
                threshold = float(np.quantile(values[train_indices], 0.75))
                holdout_scores.append(
                    balanced_accuracy(
                        list(y_true[test_indices]),
                        list(values[test_indices] >= threshold),
                    )
                )
            symbol_mean = float(np.mean(holdout_scores))
            symbol_min = float(np.min(holdout_scores))
            symbol_metrics[name] = {"mean": symbol_mean, "min": symbol_min}
            symbol_rows.append(
                {
                    "variant_name": name,
                    "mean_test_balanced_accuracy": round(float(symbol_mean), 8),
                    "min_test_balanced_accuracy": round(float(symbol_min), 8),
                }
            )

        best_variant_name = max(
            variants,
            key=lambda name: (
                time_metrics[name]["mean"],
                symbol_metrics[name]["mean"],
                variant_metrics[name]["q75_ba"],
            ),
        )
        best_variant_row = next(row for row in variant_rows if row["variant_name"] == best_variant_name)
        best_standalone_name = max(
            ["downside_failure_reference", "gap_exhaustion_stall_reference"],
            key=lambda name: (
                time_metrics[name]["mean"],
                symbol_metrics[name]["mean"],
                variant_metrics[name]["q75_ba"],
            ),
        )
        best_standalone_q75 = variant_metrics[best_standalone_name]["q75_ba"]
        best_standalone_time_mean = time_metrics[best_standalone_name]["mean"]
        best_standalone_symbol_mean = symbol_metrics[best_standalone_name]["mean"]
        best_standalone_time_min = time_metrics[best_standalone_name]["min"]
        best_standalone_symbol_min = symbol_metrics[best_standalone_name]["min"]
        material_increment = bool(
            best_variant_name not in {"downside_failure_reference", "gap_exhaustion_stall_reference"}
            and time_metrics[best_variant_name]["mean"] > best_standalone_time_mean + 0.003
            and symbol_metrics[best_variant_name]["mean"] > best_standalone_symbol_mean + 0.003
            and time_metrics[best_variant_name]["min"] >= best_standalone_time_min - 0.002
            and symbol_metrics[best_variant_name]["min"] >= best_standalone_symbol_min - 0.002
            and variant_metrics[best_variant_name]["q75_ba"] >= best_standalone_q75
        )

        summary = {
            "acceptance_posture": "freeze_v123e_cpo_1min_downside_same_plane_integration_audit_v1",
            "variant_count": len(variant_rows),
            "best_variant_name": best_variant_name,
            "best_standalone_name": best_standalone_name,
            "best_q75_balanced_accuracy": float(best_variant_row["q75_balanced_accuracy"]),
            "best_standalone_q75_balanced_accuracy": round(best_standalone_q75, 8),
            "material_increment_over_downside_failure": material_increment,
            "recommended_next_posture": (
                "three_agent_triage_same_plane_integration"
                if material_increment
                else "treat_same_plane_integration_as_non_increment_and_stop"
            ),
        }
        interpretation = [
            "V1.23E compares simple same-plane blends between downside_failure and the new orthogonal gap_exhaustion_stall branch.",
            "The question is not whether a blend can look slightly better in-sample, but whether it creates material non-replay increment over the standalone reference.",
            "The next step is triage on whether the best blend is real increment or just same-plane decoration.",
        ]
        return V123ECpo1MinDownsideSamePlaneIntegrationAuditReport(
            summary=summary,
            variant_rows=variant_rows,
            time_split_rows=time_split_rows,
            symbol_rows=symbol_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V123ECpo1MinDownsideSamePlaneIntegrationAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V123ECpo1MinDownsideSamePlaneIntegrationAuditAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v123e_cpo_1min_downside_same_plane_integration_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
