from __future__ import annotations

from datetime import date
from pathlib import Path

from a_share_quant.data.sector_mapper import AkshareCninfoSectorMapper, SectorMapperConfig


def test_expand_history_backfills_earliest_known_sector() -> None:
    mapper = object.__new__(AkshareCninfoSectorMapper)
    mapper.config = SectorMapperConfig(
        mapping_source="test",
        mapping_version="v1",
        classification_field="行业大类",
        fallback_sector_name="UNKNOWN",
        fallback_sector_id="UNKNOWN",
        backfill_earliest_known=True,
        output_csv=Path("dummy.csv"),
    )

    records = mapper._expand_history(
        symbol="000001",
        trade_dates=[
            date(2024, 1, 2),
            date(2024, 1, 3),
            date(2024, 2, 8),
        ],
        history=[
            {
                "change_date": date(2024, 2, 8),
                "sector_name": "货币金融服务",
                "sector_id": "货币金融服务".upper(),
            }
        ],
    )

    assert all(record.sector_name == "货币金融服务" for record in records)
