from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.strategy.phase_status_console import PhaseStatusConsoleFormatter


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} did not decode to a mapping.")
    return payload


def main() -> None:
    snapshot_path = ROOT / "reports" / "analysis" / "phase_status_snapshot_v1.json"
    action_plan_path = ROOT / "reports" / "analysis" / "refresh_trigger_action_plan_v1.json"
    view = PhaseStatusConsoleFormatter().build_view(
        snapshot_payload=load_json(snapshot_path),
        action_plan_payload=load_json(action_plan_path),
    )
    print(view.headline)
    for bullet in view.bullets:
        print(f"- {bullet}")
    raise SystemExit(view.exit_code)


if __name__ == "__main__":
    main()
