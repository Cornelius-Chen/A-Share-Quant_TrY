from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.strategy.phase_status_refresh import build_phase_status_refresh_plan


def main() -> None:
    plan = build_phase_status_refresh_plan(ROOT)
    for step in plan.steps:
        print(f"[{step.step}/{len(plan.steps)}] {step.name}: {' '.join(step.command)}")
        subprocess.run(step.command, cwd=ROOT, check=True)

    with plan.final_report_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    print(f"Phase status refresh complete: {plan.final_report_path}")
    print(f"Summary: {payload.get('summary', {})}")


if __name__ == "__main__":
    main()
