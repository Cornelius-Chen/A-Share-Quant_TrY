from __future__ import annotations

from pathlib import Path

from a_share_quant.info_center.automation.orchestration.a_share_internal_hot_news_runtime_switch_v1 import (
    HotNewsRuntimeSwitchStoreV1,
)


def test_runtime_switch_defaults_enabled() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    store = HotNewsRuntimeSwitchStoreV1(repo_root)
    state = store.read()

    assert state.enabled in {True, False}
    assert state.row["runtime_id"] == "internal_hot_news_runtime_scheduler"


def test_runtime_switch_write_roundtrip() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    store = HotNewsRuntimeSwitchStoreV1(repo_root)
    original = store.read()
    try:
        written = store.write(
            enabled=False,
            updated_by="pytest_roundtrip",
            notes="temporary disable during switch roundtrip test",
        )
        assert written.enabled is False
        reread = store.read()
        assert reread.enabled is False
        assert reread.row["updated_by"] == "pytest_roundtrip"
    finally:
        store.write(
            enabled=original.enabled,
            updated_by="pytest_restore",
            notes="restore original switch state after roundtrip test",
        )
