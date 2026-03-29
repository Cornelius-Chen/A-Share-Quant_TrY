from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class PromotionGateResult:
    incumbent_name: str
    challenger_name: str
    passed: bool
    summary: dict[str, Any]
    checks: list[dict[str, Any]]
    incumbent_metrics: dict[str, Any]
    challenger_metrics: dict[str, Any]
    dataset_deltas: list[dict[str, Any]]
    row_win_counts: dict[str, dict[str, int]]

    def as_dict(self) -> dict[str, Any]:
        return {
            "incumbent_name": self.incumbent_name,
            "challenger_name": self.challenger_name,
            "passed": self.passed,
            "summary": self.summary,
            "checks": self.checks,
            "incumbent_metrics": self.incumbent_metrics,
            "challenger_metrics": self.challenger_metrics,
            "dataset_deltas": self.dataset_deltas,
            "row_win_counts": self.row_win_counts,
        }


def load_comparison_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Comparison report at {path} must decode to a mapping.")
    return payload


class PromotionGateEvaluator:
    """Evaluate whether a challenger has enough evidence to challenge a default."""

    def evaluate(
        self,
        *,
        payload: dict[str, Any],
        incumbent_name: str,
        challenger_name: str,
        gate_config: dict[str, Any],
    ) -> PromotionGateResult:
        leaderboard = payload.get("extras", {}).get("candidate_leaderboard", [])
        if not isinstance(leaderboard, list):
            raise ValueError("Comparison report is missing a valid candidate leaderboard.")
        candidate_metrics = {
            str(item["candidate_name"]): item
            for item in leaderboard
            if isinstance(item, dict) and item.get("candidate_name") is not None
        }
        incumbent_metrics = candidate_metrics.get(incumbent_name)
        challenger_metrics = candidate_metrics.get(challenger_name)
        if incumbent_metrics is None:
            raise ValueError(f"Incumbent candidate '{incumbent_name}' not found in leaderboard.")
        if challenger_metrics is None:
            raise ValueError(f"Challenger candidate '{challenger_name}' not found in leaderboard.")

        comparisons = payload.get("comparisons", [])
        if not isinstance(comparisons, list):
            raise ValueError("Comparison report is missing valid comparison rows.")
        row_win_counts = self._compute_row_win_counts(comparisons)
        dataset_deltas = self._compute_dataset_deltas(
            comparisons=comparisons,
            incumbent_name=incumbent_name,
            challenger_name=challenger_name,
        )

        composite_improvement = round(
            float(incumbent_metrics["composite_rank_score"])
            - float(challenger_metrics["composite_rank_score"]),
            6,
        )
        total_return_delta = round(
            float(challenger_metrics["mean_total_return"])
            - float(incumbent_metrics["mean_total_return"]),
            6,
        )
        capture_delta = round(
            float(challenger_metrics["mean_mainline_capture_ratio"])
            - float(incumbent_metrics["mean_mainline_capture_ratio"]),
            6,
        )
        drawdown_improvement = round(
            float(incumbent_metrics["mean_max_drawdown"])
            - float(challenger_metrics["mean_max_drawdown"]),
            6,
        )

        checks = [
            self._check_minimum(
                name="composite_rank_improvement",
                actual=composite_improvement,
                threshold=float(gate_config.get("min_composite_rank_improvement", 0.0)),
                description="Challenger must improve the cross-pack composite rank score enough to justify further promotion discussion.",
            ),
            self._check_minimum(
                name="mean_total_return_delta",
                actual=total_return_delta,
                threshold=float(gate_config.get("min_mean_total_return_delta", 0.0)),
                description="Challenger must improve mean total return versus the incumbent.",
            ),
            self._check_minimum(
                name="mean_max_drawdown_improvement",
                actual=drawdown_improvement,
                threshold=float(gate_config.get("min_mean_max_drawdown_improvement", 0.0)),
                description="Challenger must improve mean max drawdown versus the incumbent.",
            ),
            self._check_maximum(
                name="mean_capture_regression",
                actual=round(-capture_delta, 6) if capture_delta < 0 else 0.0,
                threshold=float(gate_config.get("max_mean_capture_regression", 1.0)),
                description="Challenger may give back some capture, but only within the configured tolerance.",
            ),
            self._check_minimum(
                name="total_return_row_wins",
                actual=float(row_win_counts.get(challenger_name, {}).get("total_return", 0)),
                threshold=float(gate_config.get("min_total_return_row_wins", 0)),
                description="Challenger must still own at least a minimum number of row-level total-return wins.",
            ),
            self._check_minimum(
                name="min_dataset_mean_total_return_delta",
                actual=min(item["mean_total_return_delta"] for item in dataset_deltas),
                threshold=float(gate_config.get("min_dataset_mean_total_return_delta", float("-inf"))),
                description="Challenger must improve mean total return by at least the configured amount on every dataset pack.",
            ),
            self._check_minimum(
                name="min_dataset_mean_max_drawdown_improvement",
                actual=min(item["mean_max_drawdown_improvement"] for item in dataset_deltas),
                threshold=float(gate_config.get("min_dataset_mean_max_drawdown_improvement", float("-inf"))),
                description="Challenger must improve mean max drawdown by at least the configured amount on every dataset pack.",
            ),
            self._check_maximum(
                name="max_dataset_mean_capture_regression",
                actual=max(item["mean_capture_regression"] for item in dataset_deltas),
                threshold=float(gate_config.get("max_dataset_mean_capture_regression", float("inf"))),
                description="No single dataset pack may suffer capture regression beyond the configured tolerance.",
            ),
        ]

        passed = all(bool(check["passed"]) for check in checks)
        summary = {
            "composite_rank_improvement": composite_improvement,
            "mean_total_return_delta": total_return_delta,
            "mean_capture_delta": capture_delta,
            "mean_max_drawdown_improvement": drawdown_improvement,
            "challenger_total_return_row_wins": row_win_counts.get(challenger_name, {}).get(
                "total_return",
                0,
            ),
            "incumbent_total_return_row_wins": row_win_counts.get(incumbent_name, {}).get(
                "total_return",
                0,
            ),
        }
        return PromotionGateResult(
            incumbent_name=incumbent_name,
            challenger_name=challenger_name,
            passed=passed,
            summary=summary,
            checks=checks,
            incumbent_metrics=incumbent_metrics,
            challenger_metrics=challenger_metrics,
            dataset_deltas=dataset_deltas,
            row_win_counts=row_win_counts,
        )

    def _compute_row_win_counts(
        self,
        comparisons: list[dict[str, Any]],
    ) -> dict[str, dict[str, int]]:
        grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
        for row in comparisons:
            if not isinstance(row, dict):
                continue
            key = (str(row["dataset_name"]), str(row["strategy_name"]))
            grouped.setdefault(key, []).append(row)

        row_wins: dict[str, dict[str, int]] = {}
        for rows in grouped.values():
            total_return_winner = max(rows, key=lambda item: float(item["summary"]["total_return"]))
            capture_winner = max(
                rows,
                key=lambda item: float(item["summary"]["mainline_capture_ratio"]),
            )
            drawdown_winner = min(rows, key=lambda item: float(item["summary"]["max_drawdown"]))
            for metric_name, winner in (
                ("total_return", total_return_winner),
                ("mainline_capture_ratio", capture_winner),
                ("max_drawdown", drawdown_winner),
            ):
                candidate_name = str(winner["candidate_name"])
                row_wins.setdefault(
                    candidate_name,
                    {
                        "total_return": 0,
                        "mainline_capture_ratio": 0,
                        "max_drawdown": 0,
                    },
                )
                row_wins[candidate_name][metric_name] += 1
        return row_wins

    def _compute_dataset_deltas(
        self,
        *,
        comparisons: list[dict[str, Any]],
        incumbent_name: str,
        challenger_name: str,
    ) -> list[dict[str, Any]]:
        grouped: dict[str, dict[str, list[dict[str, Any]]]] = {}
        for row in comparisons:
            if not isinstance(row, dict):
                continue
            dataset_name = str(row["dataset_name"])
            candidate_name = str(row["candidate_name"])
            grouped.setdefault(dataset_name, {}).setdefault(candidate_name, []).append(row)

        deltas: list[dict[str, Any]] = []
        for dataset_name, candidate_rows in sorted(grouped.items()):
            incumbent_rows = candidate_rows.get(incumbent_name, [])
            challenger_rows = candidate_rows.get(challenger_name, [])
            if not incumbent_rows or not challenger_rows:
                continue
            incumbent_mean_return = sum(
                float(row["summary"]["total_return"]) for row in incumbent_rows
            ) / len(incumbent_rows)
            challenger_mean_return = sum(
                float(row["summary"]["total_return"]) for row in challenger_rows
            ) / len(challenger_rows)
            incumbent_mean_capture = sum(
                float(row["summary"]["mainline_capture_ratio"]) for row in incumbent_rows
            ) / len(incumbent_rows)
            challenger_mean_capture = sum(
                float(row["summary"]["mainline_capture_ratio"]) for row in challenger_rows
            ) / len(challenger_rows)
            incumbent_mean_drawdown = sum(
                float(row["summary"]["max_drawdown"]) for row in incumbent_rows
            ) / len(incumbent_rows)
            challenger_mean_drawdown = sum(
                float(row["summary"]["max_drawdown"]) for row in challenger_rows
            ) / len(challenger_rows)
            capture_regression = max(
                0.0,
                incumbent_mean_capture - challenger_mean_capture,
            )
            deltas.append(
                {
                    "dataset_name": dataset_name,
                    "mean_total_return_delta": round(
                        challenger_mean_return - incumbent_mean_return,
                        6,
                    ),
                    "mean_capture_delta": round(
                        challenger_mean_capture - incumbent_mean_capture,
                        6,
                    ),
                    "mean_capture_regression": round(capture_regression, 6),
                    "mean_max_drawdown_improvement": round(
                        incumbent_mean_drawdown - challenger_mean_drawdown,
                        6,
                    ),
                }
            )
        return deltas

    def _check_minimum(
        self,
        *,
        name: str,
        actual: float,
        threshold: float,
        description: str,
    ) -> dict[str, Any]:
        return {
            "name": name,
            "actual": round(actual, 6),
            "threshold": round(threshold, 6),
            "operator": ">=",
            "passed": actual >= threshold,
            "description": description,
        }

    def _check_maximum(
        self,
        *,
        name: str,
        actual: float,
        threshold: float,
        description: str,
    ) -> dict[str, Any]:
        return {
            "name": name,
            "actual": round(actual, 6),
            "threshold": round(threshold, 6),
            "operator": "<=",
            "passed": actual <= threshold,
            "description": description,
        }


def write_promotion_gate_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: PromotionGateResult,
    extras: dict[str, Any] | None = None,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    payload = result.as_dict()
    if extras:
        payload["extras"] = extras
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
    return output_path
