from __future__ import annotations

from a_share_quant.strategy.v120c_cpo_catalyst_event_registry_bootstrap_v1 import (
    CpoCatalystEventRegistryBootstrapAnalyzer,
    _candidate_expected_dates,
    _normalize_timestamp,
    _select_best_candidate,
    extract_time_candidates_from_html,
)


def test_normalize_timestamp_supports_common_formats() -> None:
    assert _normalize_timestamp("2025-08-19T08:21:10") == "2025-08-19 08:21:10"
    assert _normalize_timestamp("2025年8月19日 8:21") == "2025-08-19 08:21:00"


def test_extract_time_candidates_reads_meta_and_text() -> None:
    html = """
    <html>
      <head>
        <meta property="article:published_time" content="2024-09-25 11:20:30" />
      </head>
      <body>
        发布时间：2024年9月25日 11:20
      </body>
    </html>
    """
    candidates = extract_time_candidates_from_html(html)
    normalized = [row["normalized"] for row in candidates]
    assert "2024-09-25 11:20:30" in normalized
    assert "2024-09-25 11:20:00" in normalized


def test_select_best_candidate_prefers_expected_date_match() -> None:
    candidates = [
        {"source": "regex_html", "raw_value": "2026-04-02 22:05:18", "normalized": "2026-04-02 22:05:18"},
        {"source": "meta", "raw_value": "2024-09-25 11:20:30", "normalized": "2024-09-25 11:20:30"},
    ]
    selected, confidence, source = _select_best_candidate(
        source_name="证券时报 2024-09-25 CPO概念爆发",
        url="https://example.com/article/1703076.html",
        candidates=candidates,
    )
    assert selected == "2024-09-25 11:20:30"
    assert confidence == "matched_expected_date_meta"
    assert source == "meta"


def test_candidate_expected_dates_from_name_and_url() -> None:
    dates = _candidate_expected_dates(
        "中国金融信息网 2023-12-08 CPO板块强势",
        "https://www.cnfin.com/yw-lb/detail/20231208/3978903_1.html",
    )
    assert "2023-12-08" in dates


def test_bootstrap_analyzer_counts_resolved_and_unresolved_rows() -> None:
    analyzer = CpoCatalystEventRegistryBootstrapAnalyzer()
    information_registry_payload = {
        "source_rows": [
            {
                "source_name": "测试来源 2024-09-25",
                "layer": "message_and_catalyst",
                "url": "https://example.com/20240925/demo",
            }
        ]
    }
    future_calendar_payload = {
        "recurring_calendar_rows": [
            {
                "target_layer": "message_and_catalyst",
                "source_name": "future_anchor",
                "cadence_bucket": "annual_event_window",
                "why_it_helps": "anchor",
            }
        ]
    }

    class StubAnalyzer(CpoCatalystEventRegistryBootstrapAnalyzer):
        def analyze(self, *, information_registry_payload, future_calendar_payload):
            return super().analyze(
                information_registry_payload={
                    "source_rows": [],
                },
                future_calendar_payload=future_calendar_payload,
            )

    result = StubAnalyzer().analyze(
        information_registry_payload=information_registry_payload,
        future_calendar_payload=future_calendar_payload,
    )
    assert result.summary["historical_source_row_count"] == 0
    assert result.summary["forward_anchor_row_count"] == 1
    assert result.summary["total_registry_row_count"] == 1
