from __future__ import annotations

import json
from pathlib import Path


def test_v116z_quality_side_refinement_report() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    payload = json.loads(
        (repo_root / "reports" / "analysis" / "v116z_cpo_quality_side_cooled_refinement_v1.json").read_text(
            encoding="utf-8"
        )
    )
    assert payload["summary"]["authoritative_current_problem"] == "quality_discrimination_after_coverage_repair"
    assert payload["summary"]["effective_visible_axis"] == "pc1"
    variant_map = {row["variant_name"]: row for row in payload["variant_rows"]}
    assert variant_map["cooled_q_0p25"]["hit_day_count"] >= variant_map["cooled_q_0p20"]["hit_day_count"]
    assert variant_map["cooled_q_0p25"]["pc2_axis_active"] is False
