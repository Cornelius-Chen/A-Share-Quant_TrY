from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from a_share_quant.strategy.phase_guard import run_phase_guard


def main() -> None:
    result = run_phase_guard(ROOT)
    print(result.headline)
    for bullet in result.bullets:
        print(f"- {bullet}")
    raise SystemExit(result.exit_code)


if __name__ == "__main__":
    main()
