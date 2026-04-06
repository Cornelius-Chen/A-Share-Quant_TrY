import json
from pathlib import Path

from a_share_quant.strategy.v116o_cpo_corrected_cooled_shadow_wider_revalidation_v1 import (
    V116OCpoCorrectedCooledShadowWiderRevalidationAnalyzer,
)


def test_v116o_corrected_cooled_shadow_wider_revalidation_runs() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V116OCpoCorrectedCooledShadowWiderRevalidationAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v114w_payload=json.loads((repo_root / "reports" / "analysis" / "v114w_cpo_under_exposure_attribution_repaired_v1.json").read_text(encoding="utf-8")),
        v116j_payload=json.loads((repo_root / "reports" / "analysis" / "v116j_cpo_visible_only_broader_shadow_replay_v1.json").read_text(encoding="utf-8")),
        v116n_payload=json.loads((repo_root / "reports" / "analysis" / "v116n_cpo_corrected_cooled_shadow_retention_v1.json").read_text(encoding="utf-8")),
    )
    assert result.summary["acceptance_posture"] == "freeze_v116o_cpo_corrected_cooled_shadow_wider_revalidation_v1"
    names = {row["variant_name"] for row in result.variant_rows}
    assert "corrected_cooled_shadow_candidate" in names
    assert "hot_upper_bound_reference" in names
