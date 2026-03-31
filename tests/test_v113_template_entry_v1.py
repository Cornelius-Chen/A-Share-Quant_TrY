from pathlib import Path

from a_share_quant.strategy.v113_template_entry_v1 import V113TemplateEntryAnalyzer, load_json_report


def test_v113_template_entry_v1_selects_theme_diffusion_carry() -> None:
    result = V113TemplateEntryAnalyzer().analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v113_phase_charter_v1.json"))
    )
    assert result.summary["selected_template_family"] == "theme_diffusion_carry"
    assert result.summary["seed_archetype_count"] == 3
