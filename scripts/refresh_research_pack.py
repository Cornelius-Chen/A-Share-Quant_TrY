from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


PACK_CONFIGS: dict[str, dict[str, str]] = {
    "baseline_research_v1": {
        "sector_mapping": "config/baseline_research_sector_mapping.yaml",
        "derived": "config/baseline_research_derived_data.yaml",
        "suite": "config/baseline_research_strategy_suite.yaml",
        "audit": "config/baseline_research_data_audit.yaml",
    },
    "theme_research_v1": {
        "sector_mapping": "config/theme_research_sector_mapping.yaml",
        "derived": "config/theme_research_derived_data.yaml",
        "suite": "config/theme_research_strategy_suite.yaml",
        "audit": "config/theme_research_data_audit.yaml",
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Refresh a research pack sequentially to avoid stale intermediate outputs."
    )
    parser.add_argument(
        "--pack",
        required=True,
        choices=sorted(PACK_CONFIGS),
        help="Named research pack to refresh.",
    )
    parser.add_argument(
        "--skip-suite",
        action="store_true",
        help="Skip the strategy-suite step.",
    )
    return parser.parse_args()


def _run_step(label: str, command: list[str]) -> None:
    print(f"[refresh] {label}: {' '.join(command)}")
    completed = subprocess.run(command, cwd=ROOT, check=False)
    if completed.returncode != 0:
        raise SystemExit(f"{label} failed with exit code {completed.returncode}")


def main() -> None:
    args = parse_args()
    pack = PACK_CONFIGS[args.pack]

    _run_step(
        "sector_mapping",
        [sys.executable, "scripts/bootstrap_sector_mapping.py", "--config", pack["sector_mapping"]],
    )
    _run_step(
        "derived",
        [sys.executable, "scripts/generate_bootstrap_derived_data.py", "--config", pack["derived"]],
    )
    if not args.skip_suite:
        _run_step(
            "suite",
            [sys.executable, "scripts/run_strategy_suite.py", "--config", pack["suite"]],
        )
    _run_step(
        "audit",
        [sys.executable, "scripts/audit_data_pack.py", "--config", pack["audit"]],
    )
    print(f"[refresh] completed: {args.pack}")


if __name__ == "__main__":
    main()
