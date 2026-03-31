from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112CUPackagingAdmissionModePromotionReviewReport:
    summary: dict[str, Any]
    promotion_rows: list[dict[str, Any]]
    boundary_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "promotion_rows": self.promotion_rows,
            "boundary_rows": self.boundary_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112CUPackagingAdmissionModePromotionReviewAnalyzer:
    def analyze(
        self,
        *,
        ch_payload: dict[str, Any],
        cs_payload: dict[str, Any],
        ct_payload: dict[str, Any],
    ) -> V112CUPackagingAdmissionModePromotionReviewReport:
        ch_summary = dict(ch_payload.get("summary", {}))
        cs_summary = dict(cs_payload.get("summary", {}))
        ct_summary = dict(ct_payload.get("summary", {}))
        mode_rows = list(ct_payload.get("mode_rows", []))
        if not mode_rows:
            raise ValueError("V1.12CU requires V1.12CT mode rows.")

        preferred_row = next(
            (row for row in mode_rows if str(row.get("mode_name")) == str(ct_summary.get("preferred_mode"))),
            None,
        )
        if preferred_row is None:
            raise ValueError("V1.12CU requires the preferred V1.12CT mode row.")

        full_row = next((row for row in mode_rows if str(row.get("mode_name")) == "full_20d_admission"), None)
        cut_row = next((row for row in mode_rows if str(row.get("mode_name")) == "cut_at_next_neutral_entry"), None)
        if full_row is None or cut_row is None:
            raise ValueError("V1.12CU requires both packaging admission modes.")

        promotion_ready = bool(full_row.get("beats_neutral_return")) and bool(full_row.get("beats_neutral_drawdown"))

        summary = {
            "acceptance_posture": "freeze_v112cu_packaging_admission_mode_promotion_review_v1",
            "existing_packaging_mainline_asset": bool(ch_summary.get("cluster_mainline_template_asset_count", 0) == 1),
            "joint_promotion_ready": bool(cs_summary.get("joint_promotion_ready", False)),
            "preferred_mode": full_row["mode_name"],
            "promotion_ready": promotion_ready,
            "promotion_posture": (
                "cluster_mainline_admission_extension_candidate"
                if promotion_ready
                else "retain_as_packaging_admission_sidecar_candidate"
            ),
            "recommended_next_posture": (
                "open_controlled_packaging_admission_extension_replay_without_reopening_packaging_template_learning"
                if promotion_ready
                else "retain_packaging_admission_as_sidecar_and_do_not_promote_now"
            ),
        }

        promotion_rows = [
            {
                "promotion_target": "packaging_full_20d_admission_mode",
                "posture": (
                    "cluster_mainline_admission_extension_candidate"
                    if promotion_ready
                    else "packaging_admission_sidecar_candidate"
                ),
                "beats_neutral_return": bool(full_row.get("beats_neutral_return")),
                "beats_neutral_drawdown": bool(full_row.get("beats_neutral_drawdown")),
                "return_delta_vs_neutral": full_row.get("return_delta_vs_neutral"),
                "drawdown_delta_vs_neutral": full_row.get("drawdown_delta_vs_neutral"),
                "skipped_neutral_count": full_row.get("skipped_neutral_count"),
                "admission_count": full_row.get("admission_count"),
            },
            {
                "promotion_target": "packaging_cut_at_next_neutral_entry_mode",
                "posture": "rejected_as_default_promotion_path",
                "beats_neutral_return": bool(cut_row.get("beats_neutral_return")),
                "beats_neutral_drawdown": bool(cut_row.get("beats_neutral_drawdown")),
                "return_delta_vs_neutral": cut_row.get("return_delta_vs_neutral"),
                "drawdown_delta_vs_neutral": cut_row.get("drawdown_delta_vs_neutral"),
                "skipped_neutral_count": cut_row.get("skipped_neutral_count"),
                "admission_count": cut_row.get("admission_count"),
            },
        ]
        boundary_rows = [
            {
                "boundary_name": "template_learning_boundary",
                "reading": "V1.12CU does not reopen packaging template learning. It only decides whether packaging admission deserves promotion from miss-diagnostic into a governed mainline extension candidate.",
            },
            {
                "boundary_name": "core_residual_boundary",
                "reading": "Packaging admission promotion remains separate from the deferred 300308/300502 joint residual stack.",
                "joint_promotion_ready": bool(cs_summary.get("joint_promotion_ready", False)),
            },
            {
                "boundary_name": "mode_selection_boundary",
                "reading": "Only the full 20-day packaging admission mode beats neutral on both return and drawdown. The clipped mode improves return but worsens drawdown and cannot serve as the default promotion path.",
                "full_mode_beats_both": promotion_ready,
                "cut_mode_beats_drawdown": bool(cut_row.get("beats_neutral_drawdown")),
            },
        ]
        interpretation = [
            "V1.12CU turns packaging admission from a residual miss diagnostic into a governed promotion decision.",
            "The review supports promoting full_20d packaging admission into a controlled mainline extension candidate because it improves both neutral return and neutral max drawdown without reopening packaging template learning.",
        ]
        return V112CUPackagingAdmissionModePromotionReviewReport(
            summary=summary,
            promotion_rows=promotion_rows,
            boundary_rows=boundary_rows,
            interpretation=interpretation,
        )


def write_v112cu_packaging_admission_mode_promotion_review_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112CUPackagingAdmissionModePromotionReviewReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
