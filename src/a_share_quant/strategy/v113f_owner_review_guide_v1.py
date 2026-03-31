from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V113FOwnerReviewGuideReport:
    summary: dict[str, Any]
    guide_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "guide_rows": self.guide_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V113FOwnerReviewGuideAnalyzer:
    """Translate the first theme-diffusion pilot draft into a compact owner review guide."""

    NAME_OVERRIDES = {
        "002085": "万丰奥威",
        "000738": "航发控制",
        "600118": "中国卫星",
    }

    ROLE_CN = {
        "leader": "龙头",
        "mid_core": "中军",
        "mapping_activation": "映射激活",
    }

    EVIDENCE_CN = {
        "dense_local_commercial_space_mapping": "本地证据最强",
        "sparse_cross_theme_mapping": "跨题材映射偏多",
        "sparse_policy_anchor_mapping": "政策锚点较强但直连证据偏弱",
    }

    def analyze(
        self,
        *,
        pilot_object_pool_payload: dict[str, Any],
        review_sheet_payload: dict[str, Any],
    ) -> V113FOwnerReviewGuideReport:
        object_rows = list(pilot_object_pool_payload.get("object_rows", []))
        review_rows = {str(row.get("symbol", "")): row for row in review_sheet_payload.get("review_rows", [])}
        if not object_rows:
            raise ValueError("V1.13F owner review guide requires a non-empty pilot object pool.")

        guide_rows: list[dict[str, Any]] = []
        for object_row in object_rows:
            symbol = str(object_row.get("symbol", ""))
            review_row = dict(review_rows.get(symbol, {}))
            guide_rows.append(
                {
                    "symbol": symbol,
                    "display_name": self.NAME_OVERRIDES.get(symbol, str(object_row.get("name") or "")),
                    "current_role_guess_cn": self.ROLE_CN.get(str(object_row.get("pool_role_guess", "")), "待审"),
                    "evidence_strength_reading_cn": self.EVIDENCE_CN.get(
                        str(object_row.get("local_evidence_status", "")),
                        "证据层级待审",
                    ),
                    "current_window_guess": {
                        "start": review_row.get("cycle_window_start_guess"),
                        "end": review_row.get("cycle_window_end_guess"),
                    },
                    "owner_should_review": [
                        "是否保留在第一版 pilot",
                        "角色是否要改",
                        "周期起止是否要改",
                        "是否需要补充同层级对象",
                    ],
                    "current_reading": object_row.get("role_guess_reason"),
                }
            )

        summary = {
            "acceptance_posture": "freeze_v113f_owner_review_guide_v1",
            "guide_row_count": len(guide_rows),
            "ready_for_owner_review_now": True,
        }
        interpretation = [
            "This guide converts the raw draft object pool into a compact owner-facing review surface.",
            "It does not change the pilot itself; it only lowers the friction of correcting roles and windows.",
            "The next useful move remains owner review of the three draft objects.",
        ]
        return V113FOwnerReviewGuideReport(summary=summary, guide_rows=guide_rows, interpretation=interpretation)


def write_v113f_owner_review_guide_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V113FOwnerReviewGuideReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
