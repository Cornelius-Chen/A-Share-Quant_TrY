from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv


def load_tushare_token(*, repo_root: Path | None = None) -> str:
    """Load a Tushare token from env or local dotenv without committing secrets."""
    if repo_root is None:
        repo_root = Path(__file__).resolve().parents[3]
    dotenv_path = repo_root / ".env.local"
    if dotenv_path.exists():
        load_dotenv(dotenv_path=dotenv_path, override=False)
        token = os.getenv("TUSHARE_TOKEN", "").strip()
        if not token:
            for raw_line in dotenv_path.read_text(encoding="utf-8-sig").splitlines():
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                if key.strip() == "TUSHARE_TOKEN":
                    token = value.strip()
                    os.environ["TUSHARE_TOKEN"] = token
                    break
    else:
        token = ""
    token = token or os.getenv("TUSHARE_TOKEN", "").strip()
    if not token:
        raise RuntimeError(
            "TUSHARE_TOKEN is not configured. Put it in .env.local or your user environment."
        )
    return token


def require_tushare() -> Any:
    try:
        import tushare as ts
    except ImportError as exc:
        raise RuntimeError(
            "Tushare is not installed. Install it first, for example: python -m pip install tushare"
        ) from exc
    return ts


def build_tushare_pro(*, repo_root: Path | None = None) -> Any:
    ts = require_tushare()
    token = load_tushare_token(repo_root=repo_root)
    ts.set_token(token)
    return ts.pro_api(token)
