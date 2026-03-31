from __future__ import annotations

from a_share_quant.strategy.v113f_pilot_object_pool_v1 import V113FPilotObjectPoolAnalyzer


def test_v113f_pilot_object_pool_freezes_three_local_commercial_space_objects() -> None:
    result = V113FPilotObjectPoolAnalyzer().analyze(
        phase_charter_payload={"summary": {"do_open_v113f_now": True}},
        pilot_protocol_payload={"pilot_basis": {"selected_archetype": "commercial_space_mainline"}},
        sector_mapping_rows=[
            {"trade_date": "2024-01-02", "symbol": "002085", "sector_name": "商业航天"},
            {"trade_date": "2024-03-01", "symbol": "002085", "sector_name": "商业航天"},
            {"trade_date": "2024-02-19", "symbol": "000738", "sector_name": "商业航天"},
            {"trade_date": "2024-07-24", "symbol": "600118", "sector_name": "商业航天"},
        ],
        security_master_rows=[
            {"symbol": "002085", "name": "万丰奥威"},
            {"symbol": "000738", "name": "航发控制"},
            {"symbol": "600118", "name": "中国卫星"},
        ],
        mainline_window_rows=[
            {"symbol": "002085"},
            {"symbol": "002085"},
            {"symbol": "000738"},
            {"symbol": "600118"},
        ],
    )

    assert result.summary["pilot_object_count"] == 3
    assert result.object_rows[0]["symbol"] == "002085"
    assert result.summary["ready_for_label_review_sheet_next"] is True
