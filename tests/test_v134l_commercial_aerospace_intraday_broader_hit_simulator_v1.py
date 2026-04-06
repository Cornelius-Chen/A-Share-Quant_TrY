from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_v134l_commercial_aerospace_intraday_broader_hit_simulator_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    script_path = repo_root / "scripts" / "run_v134l_commercial_aerospace_intraday_broader_hit_simulator_v1.py"

    subprocess.run([sys.executable, str(script_path)], check=True, cwd=repo_root)

    report_path = repo_root / "reports" / "analysis" / "v134l_commercial_aerospace_intraday_broader_hit_simulator_v1.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))

    assert report["summary"]["broader_hit_session_count"] == 24
    assert report["summary"]["reference_notional_per_session"] == 100000.0
    assert report["summary"]["pending_out_of_window_count"] == 0
    assert report["summary"]["simulated_order_count"] > 0
    assert report["summary"]["reversal_execution_count"] > 0
    assert report["summary"]["severe_execution_count"] > 0
