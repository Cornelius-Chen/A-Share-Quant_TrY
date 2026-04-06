from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V126YCommercialAerospaceShadowStackCompareReport:
    summary: dict[str, Any]
    stack_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "stack_rows": self.stack_rows,
            "interpretation": self.interpretation,
        }


class V126YCommercialAerospaceShadowStackCompareAnalyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.v126o_path = repo_root / "reports" / "analysis" / "v126o_commercial_aerospace_phase_geometry_walk_forward_shadow_replay_v1.json"
        self.v126q_path = repo_root / "reports" / "analysis" / "v126q_commercial_aerospace_pruned_phase_geometry_shadow_replay_v1.json"
        self.v126v_path = repo_root / "reports" / "analysis" / "v126v_commercial_aerospace_preheat_pruned_shadow_replay_v1.json"
        self.v126x_path = repo_root / "reports" / "analysis" / "v126x_commercial_aerospace_conditional_derisk_audit_v1.json"

    @staticmethod
    def _load_summary(path: Path) -> dict[str, Any]:
        return json.loads(path.read_text(encoding="utf-8"))["summary"]

    def analyze(self) -> V126YCommercialAerospaceShadowStackCompareReport:
        v126o = self._load_summary(self.v126o_path)
        v126q = self._load_summary(self.v126q_path)
        v126v = self._load_summary(self.v126v_path)
        v126x = json.loads(self.v126x_path.read_text(encoding="utf-8"))
        x_best_name = v126x["summary"]["best_variant"]
        x_best_row = next(row for row in v126x["variant_rows"] if row["variant"] == x_best_name)

        stack_rows = [
            {
                "variant": "v126o_economic_reference",
                "class": "reference_shadow",
                "final_equity": float(v126o["final_equity"]),
                "max_drawdown": float(v126o["max_drawdown"]),
                "executed_order_count": int(v126o["executed_order_count"]),
            },
            {
                "variant": "v126q_cleaner_reference",
                "class": "cleaner_shadow",
                "final_equity": float(v126q["final_equity"]),
                "max_drawdown": float(v126q["max_drawdown"]),
                "executed_order_count": int(v126q["executed_order_count"]),
            },
            {
                "variant": "v126v_retained_aggressive_shadow",
                "class": "aggressive_shadow",
                "final_equity": float(v126v["final_equity"]),
                "max_drawdown": float(v126v["max_drawdown"]),
                "executed_order_count": int(v126v["executed_order_count"]),
            },
            {
                "variant": f"v126x_{x_best_name}",
                "class": "conditional_derisk_shadow",
                "final_equity": float(x_best_row["final_equity"]),
                "max_drawdown": float(x_best_row["max_drawdown"]),
                "executed_order_count": int(x_best_row["executed_order_count"]),
            },
        ]

        highest_equity = max(stack_rows, key=lambda row: row["final_equity"])
        lowest_drawdown = min(stack_rows, key=lambda row: row["max_drawdown"])
        best_balance = min(
            stack_rows,
            key=lambda row: (
                row["max_drawdown"],
                -row["final_equity"],
            ),
        )

        summary = {
            "acceptance_posture": "freeze_v126y_commercial_aerospace_shadow_stack_compare_v1",
            "highest_equity_variant": highest_equity["variant"],
            "highest_equity_final_equity": highest_equity["final_equity"],
            "lowest_drawdown_variant": lowest_drawdown["variant"],
            "lowest_drawdown": lowest_drawdown["max_drawdown"],
            "best_balance_variant": best_balance["variant"],
            "best_balance_final_equity": best_balance["final_equity"],
            "best_balance_max_drawdown": best_balance["max_drawdown"],
        }
        interpretation = [
            "V1.26Y puts the current commercial-aerospace lawful shadow stack on one plane: economic reference, cleaner reference, aggressive preheat shadow, and the best conditional de-risk variant.",
            "This is a comparison surface only; it does not promote any replay variant by itself.",
        ]
        return V126YCommercialAerospaceShadowStackCompareReport(
            summary=summary,
            stack_rows=stack_rows,
            interpretation=interpretation,
        )


def write_report(*, reports_dir: Path, report_name: str, result: V126YCommercialAerospaceShadowStackCompareReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V126YCommercialAerospaceShadowStackCompareAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v126y_commercial_aerospace_shadow_stack_compare_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
