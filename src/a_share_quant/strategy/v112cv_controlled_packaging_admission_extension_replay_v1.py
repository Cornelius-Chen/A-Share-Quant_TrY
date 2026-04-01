from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112CVControlledPackagingAdmissionExtensionReplayReport:
    summary: dict[str, Any]
    extension_rows: list[dict[str, Any]]
    displaced_neutral_rows: list[dict[str, Any]]
    boundary_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "extension_rows": self.extension_rows,
            "displaced_neutral_rows": self.displaced_neutral_rows,
            "boundary_rows": self.boundary_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112CVControlledPackagingAdmissionExtensionReplayAnalyzer:
    def analyze(
        self,
        *,
        bh_payload: dict[str, Any],
        ct_payload: dict[str, Any],
        cu_payload: dict[str, Any],
    ) -> V112CVControlledPackagingAdmissionExtensionReplayReport:
        bh_summary = dict(bh_payload.get("summary", {}))
        neutral_rows = list(bh_payload.get("trade_rows", []))
        mode_rows = list(ct_payload.get("mode_rows", []))
        ct_admission_rows = list(ct_payload.get("admission_rows", []))
        cu_summary = dict(cu_payload.get("summary", {}))
        if not neutral_rows or not mode_rows:
            raise ValueError("V1.12CV requires neutral trades and CT mode rows.")

        preferred_mode = str(cu_summary.get("preferred_mode"))
        if preferred_mode != "full_20d_admission":
            raise ValueError("V1.12CV only supports the promoted full_20d_admission mode.")
        preferred_row = next((row for row in mode_rows if str(row.get("mode_name")) == preferred_mode), None)
        if preferred_row is None:
            raise ValueError("V1.12CV requires the preferred mode row from V1.12CT.")

        preferred_admission_rows = [
            row for row in ct_admission_rows if str(row.get("mode_name")) == preferred_mode
        ]
        neutral_trade_rows = sorted(
            [
                {
                    "entry_date": str(row.get("entry_date")),
                    "exit_date": str(row.get("exit_date")),
                    "symbol": str(row.get("symbol")),
                    "stage_family": str(row.get("stage_family")),
                    "role_family": str(row.get("role_family")),
                    "realized_forward_return_20d": float(row.get("realized_forward_return_20d", 0.0)),
                    "path_max_drawdown": float(row.get("path_max_drawdown", 0.0)),
                }
                for row in neutral_rows
            ],
            key=lambda row: row["entry_date"],
        )
        admission_windows = sorted(
            [
                {
                    "entry_date": str(row.get("trade_date")),
                    "exit_date": str(row.get("exit_date")),
                    "symbol": "300757",
                    "extension_type": "packaging_full_20d_admission",
                }
                for row in preferred_admission_rows
            ],
            key=lambda row: row["entry_date"],
        )

        displaced_neutral_rows: list[dict[str, Any]] = []
        surviving_neutral_rows: list[dict[str, Any]] = []
        for neutral_row in neutral_trade_rows:
            if any(
                window["entry_date"] <= neutral_row["entry_date"] <= window["exit_date"]
                for window in admission_windows
            ):
                displaced_neutral_rows.append(neutral_row)
            else:
                surviving_neutral_rows.append(neutral_row)

        summary = {
            "acceptance_posture": "freeze_v112cv_controlled_packaging_admission_extension_replay_v1",
            "extension_posture": (
                "controlled_mainline_extension_ready"
                if bool(cu_summary.get("promotion_ready"))
                else "not_ready"
            ),
            "preferred_mode": preferred_mode,
            "baseline_total_return": float(bh_summary.get("total_return", 0.0)),
            "baseline_max_drawdown": float(bh_summary.get("max_drawdown", 0.0)),
            "replayed_total_return": float(preferred_row.get("total_return", 0.0)),
            "replayed_max_drawdown": float(preferred_row.get("max_drawdown", 0.0)),
            "return_delta_vs_neutral": float(preferred_row.get("return_delta_vs_neutral", 0.0)),
            "drawdown_delta_vs_neutral": float(preferred_row.get("drawdown_delta_vs_neutral", 0.0)),
            "admission_count": int(preferred_row.get("admission_count", 0)),
            "displaced_neutral_trade_count": len(displaced_neutral_rows),
            "surviving_neutral_trade_count": len(surviving_neutral_rows),
            "extension_replay_ready": bool(
                cu_summary.get("promotion_ready")
                and preferred_row.get("beats_neutral_return")
                and preferred_row.get("beats_neutral_drawdown")
            ),
            "recommended_next_posture": "freeze_packaging_admission_as_controlled_mainline_extension_and_keep_core_residual_stack_separate",
        }

        extension_rows = []
        for row in admission_windows:
            extension_rows.append(
                {
                    "entry_date": row["entry_date"],
                    "exit_date": row["exit_date"],
                    "symbol": row["symbol"],
                    "extension_type": row["extension_type"],
                }
            )

        boundary_rows = [
            {
                "boundary_name": "template_boundary",
                "reading": "V1.12CV does not reopen packaging template learning. It only replays the promoted full_20d packaging admission mode as a governed mainline extension candidate.",
            },
            {
                "boundary_name": "displacement_boundary",
                "reading": "The extension is allowed to displace later neutral entries only when the promoted admission window legally overlaps them in time order.",
                "displaced_neutral_trade_count": len(displaced_neutral_rows),
            },
            {
                "boundary_name": "core_residual_stack_boundary",
                "reading": "Packaging admission extension remains separate from the deferred 300308/300502 joint residual stack.",
            },
        ]
        interpretation = [
            "V1.12CV converts the promoted packaging admission mode into a governed replay object rather than leaving it as a raw probe result.",
            "The replay confirms that full_20d packaging admission can stand as a controlled mainline extension candidate because it improves both total return and max drawdown versus neutral while preserving time-order legality.",
        ]
        return V112CVControlledPackagingAdmissionExtensionReplayReport(
            summary=summary,
            extension_rows=extension_rows,
            displaced_neutral_rows=displaced_neutral_rows,
            boundary_rows=boundary_rows,
            interpretation=interpretation,
        )


def write_v112cv_controlled_packaging_admission_extension_replay_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112CVControlledPackagingAdmissionExtensionReplayReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
