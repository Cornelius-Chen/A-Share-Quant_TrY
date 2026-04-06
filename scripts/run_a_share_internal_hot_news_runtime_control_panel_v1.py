from __future__ import annotations

import csv
import json
import locale
import os
import subprocess
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk
from datetime import datetime, timedelta, timezone


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = str(REPO_ROOT / "src")
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

from a_share_quant.info_center.automation.orchestration.a_share_internal_hot_news_runtime_switch_v1 import (  # noqa: E402
    HotNewsRuntimeSwitchStoreV1,
)


REGISTRY_PATH = (
    REPO_ROOT
    / "data"
    / "reference"
    / "info_center"
    / "automation_registry"
    / "a_share_internal_hot_news_runtime_scheduler_registry_v1.csv"
)
MANIFEST_PATH = (
    REPO_ROOT
    / "data"
    / "reference"
    / "info_center"
    / "automation_registry"
    / "a_share_internal_hot_news_runtime_scheduler_manifest_v1.json"
)
SCHEDULER_SCRIPT = (
    REPO_ROOT
    / "src"
    / "a_share_quant"
    / "info_center"
    / "automation"
    / "orchestration"
    / "materialize_a_share_internal_hot_news_runtime_scheduler_v1.py"
)
TIME_SLICES_DIR = REPO_ROOT / "data" / "derived" / "info_center" / "time_slices"
CONTROL_PACKET_PATH = TIME_SLICES_DIR / "a_share_internal_hot_news_program_control_packet_v1.csv"
OPPORTUNITY_FEED_PATH = TIME_SLICES_DIR / "a_share_internal_hot_news_program_opportunity_feed_v1.csv"
RISK_FEED_PATH = TIME_SLICES_DIR / "a_share_internal_hot_news_program_risk_feed_v1.csv"
WATCHLIST_PACKET_PATH = TIME_SLICES_DIR / "a_share_internal_hot_news_program_symbol_watchlist_packet_v1.csv"
GUIDANCE_PATH = TIME_SLICES_DIR / "a_share_internal_hot_news_trading_guidance_surface_v1.csv"
EVENT_CLUSTER_PATH = TIME_SLICES_DIR / "a_share_internal_hot_news_event_cluster_surface_v1.csv"
SNAPSHOT_PATH = TIME_SLICES_DIR / "a_share_internal_hot_news_program_snapshot_v1.csv"
TASK_NAME = "A_Share_Internal_Hot_News_Runtime_Scheduler"
UTC = timezone.utc
BJ_TZ = timezone(timedelta(hours=8))


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _safe_value(row: dict[str, str], key: str, default: str = "") -> str:
    return row.get(key, default) if row else default


def _short_module_name(module_name: str) -> str:
    return module_name.rsplit(".", 1)[-1]


def _format_utc_as_bj(value: str) -> str:
    raw = (value or "").strip()
    if not raw:
        return "n/a"
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M:%S.%f"):
        try:
            parsed = datetime.strptime(raw, fmt).replace(tzinfo=UTC)
            return parsed.astimezone(BJ_TZ).strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue
    return raw


def _cn_theme(value: str) -> str:
    mapping = {
        "ai": "人工智能",
        "bank": "银行",
        "brokerage": "券商",
        "chemical_materials": "化工材料",
        "coal": "煤炭",
        "commercial_aerospace": "商业航天",
        "consumer_electronics": "消费电子",
        "consumer_staples": "消费",
        "defense_industry": "军工",
        "energy_storage": "储能",
        "gold": "黄金",
        "home_appliances": "家电",
        "innovative_drug": "创新药",
        "liquor": "白酒",
        "lithium_battery": "锂电",
        "medicine_devices": "医疗器械",
        "military_electronics": "军工电子",
        "new_energy_vehicle": "新能源车",
        "nonferrous_metals": "有色金属",
        "nuclear_power": "核电",
        "oil_gas": "油气",
        "optical_communication": "光通信",
        "pharmaceutical": "医药",
        "power_equipment": "电力设备",
        "pv_solar": "光伏",
        "rare_earth": "稀土",
        "robotics": "机器人",
        "semiconductor": "半导体",
        "shipping": "航运",
        "telecom": "通信",
        "broad_market": "全市场",
        "market_or_macro": "市场/宏观",
        "none": "无",
        "": "无",
    }
    return mapping.get((value or "").strip(), value or "无")


def _stage_name(module_name: str) -> str:
    short = _short_module_name(module_name)
    if short.startswith("fetch_"):
        return "fetch"
    if "controlled_merge" in short:
        return "merge"
    if "retention" in short:
        return "retention"
    if any(
        token in short
        for token in (
            "guidance",
            "event_cluster",
            "important",
            "signal_enrichment",
            "rolling_context",
            "focus_scoring",
        )
    ):
        return "transform"
    if any(
        token in short
        for token in ("ingress", "minimal_view", "split_feeds", "watch", "snapshot", "status", "control_packet")
    ):
        return "serving"
    return "other"


class HotNewsRuntimeControlPanelV1:
    AUTO_REFRESH_MS = 5000
    STAGE_DISPLAY = {
        "fetch": {"icon": "🐣", "title": "Fetch", "bg": "#FFE8D6"},
        "merge": {"icon": "🧃", "title": "Merge", "bg": "#FFF1B8"},
        "transform": {"icon": "🫧", "title": "Clean + Classify", "bg": "#D9F7BE"},
        "serving": {"icon": "🎀", "title": "Ready To Use", "bg": "#D6E4FF"},
        "retention": {"icon": "🧺", "title": "Retention", "bg": "#F4D9FF"},
        "other": {"icon": "🌱", "title": "Other", "bg": "#F5F5F5"},
    }

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.switch_store = HotNewsRuntimeSwitchStoreV1(REPO_ROOT)
        self.manual_output_message = ""
        self.auto_cycle_message = ""
        self.last_seen_cycle_completed_at_utc = ""
        self.refresh_job: str | None = None
        self.tech_details_visible = False

        self.status_var = tk.StringVar(value="loading")
        self.runtime_var = tk.StringVar(value="")
        self.focus_var = tk.StringVar(value="")
        self.retention_var = tk.StringVar(value="")
        self.final_var = tk.StringVar(value="")

        self.stage_vars = {
            stage: tk.StringVar(value=f"{meta['icon']} {meta['title']}\nwaiting")
            for stage, meta in self.STAGE_DISPLAY.items()
        }
        self.cls_card_var = tk.StringVar(value="📡 CLS\nwaiting")
        self.sina_card_var = tk.StringVar(value="📰 Sina\nwaiting")
        self.focus_card_var = tk.StringVar(value="🎯 Focus\nwaiting")
        self.challenger_card_var = tk.StringVar(value="⚔ Challenger\nwaiting")

        self.root.title("A股新闻中控")
        self.root.geometry("1460x900")
        self.root.minsize(1240, 760)
        self.root.configure(bg="#FFF9FB")
        self.root.protocol("WM_DELETE_WINDOW", self._close)
        self.root.after(80, self._bring_window_front)

        self._build()
        self.refresh()
        self._schedule_refresh()

    def _build(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Soft.TLabelframe", background="#FFF9FB")
        style.configure("Soft.TLabelframe.Label", background="#FFF9FB", font=("Segoe UI", 10, "bold"))

        outer = ttk.Frame(self.root, padding=12)
        outer.pack(fill="both", expand=True)

        banner = tk.Frame(outer, bg="#FFE3EC", bd=0, highlightthickness=0)
        banner.pack(fill="x")
        tk.Label(
            banner,
            text="🧁 A-Share Hot News Mini Factory",
            font=("Segoe UI", 18, "bold"),
            bg="#FFE3EC",
            fg="#5C385C",
            padx=14,
            pady=12,
        ).pack(anchor="w")
        tk.Label(
            banner,
            text="Every 3 minutes the pipeline fetches, cleans, classifies, clusters, scores, and refreshes final outputs.",
            font=("Segoe UI", 10),
            bg="#FFE3EC",
            fg="#7A517A",
            padx=14,
            pady=0,
        ).pack(anchor="w")

        summary = ttk.LabelFrame(outer, text="运行概况", padding=10, style="Soft.TLabelframe")
        summary.pack(fill="x", pady=(10, 8))
        ttk.Label(summary, textvariable=self.status_var).pack(anchor="w", pady=2)
        ttk.Label(summary, textvariable=self.runtime_var).pack(anchor="w", pady=2)
        ttk.Label(summary, textvariable=self.focus_var).pack(anchor="w", pady=2)
        ttk.Label(summary, textvariable=self.retention_var).pack(anchor="w", pady=2)
        ttk.Label(summary, textvariable=self.final_var).pack(anchor="w", pady=2)

        buttons = ttk.Frame(outer)
        buttons.pack(fill="x", pady=(0, 8))
        ttk.Button(buttons, text="整体启动", command=self.enable_runtime).pack(side="left", padx=(0, 8))
        ttk.Button(buttons, text="整体禁用", command=self.disable_runtime).pack(side="left", padx=(0, 8))
        ttk.Button(buttons, text="立即跑一轮", command=self.run_once).pack(side="left", padx=(0, 8))
        ttk.Button(buttons, text="刷新状态", command=self.refresh).pack(side="left", padx=(0, 8))
        ttk.Button(buttons, text="技术细节开/关", command=self.toggle_tech_details).pack(side="left", padx=(0, 8))
        ttk.Button(buttons, text="打开最终结果文件", command=lambda: self._open_path(CONTROL_PACKET_PATH)).pack(
            side="left",
            padx=(0, 8),
        )
        ttk.Button(buttons, text="打开机会结果文件", command=lambda: self._open_path(OPPORTUNITY_FEED_PATH)).pack(
            side="left",
            padx=(0, 8),
        )
        ttk.Button(buttons, text="打开结果目录", command=lambda: self._open_path(TIME_SLICES_DIR)).pack(
            side="left",
        )

        source_row = tk.Frame(outer, bg="#FFF9FB")
        source_row.pack(fill="x", pady=(0, 10))
        for index, (var, bg) in enumerate(
            [
                (self.cls_card_var, "#E6F4FF"),
                (self.sina_card_var, "#FFF7E6"),
                (self.focus_card_var, "#E8FFE8"),
                (self.challenger_card_var, "#FFF0F6"),
            ]
        ):
            card = tk.Frame(source_row, bg=bg, bd=0, highlightthickness=0)
            card.pack(side="left", fill="x", expand=True, padx=(0 if index == 0 else 8, 0))
            tk.Label(
                card,
                textvariable=var,
                justify="center",
                font=("Segoe UI Emoji", 11, "bold"),
                bg=bg,
                fg="#4A3A4A",
                padx=8,
                pady=12,
            ).pack(fill="both", expand=True)

        self.stage_row = tk.Frame(outer, bg="#FFF9FB")
        self.stage_row.pack(fill="x", pady=(0, 10))
        ordered_stages = ["fetch", "merge", "transform", "serving", "retention"]
        for index, stage in enumerate(ordered_stages):
            meta = self.STAGE_DISPLAY[stage]
            card = tk.Frame(self.stage_row, bg=meta["bg"], bd=0, highlightthickness=0)
            card.pack(side="left", fill="x", expand=True, padx=(0 if index == 0 else 6, 0))
            tk.Label(
                card,
                textvariable=self.stage_vars[stage],
                justify="center",
                font=("Segoe UI Emoji", 11, "bold"),
                bg=meta["bg"],
                fg="#4A3A4A",
                padx=8,
                pady=12,
            ).pack(fill="both", expand=True)
            if index < len(ordered_stages) - 1:
                tk.Label(
                    self.stage_row,
                    text="➜",
                    font=("Segoe UI Emoji", 16, "bold"),
                    bg="#FFF9FB",
                    fg="#C08AB7",
                    padx=6,
                ).pack(side="left")

        main_pane = ttk.PanedWindow(outer, orient="horizontal")
        main_pane.pack(fill="both", expand=True)

        left_frame = ttk.Frame(main_pane)
        right_frame = ttk.Frame(main_pane)
        main_pane.add(left_frame, weight=3)
        main_pane.add(right_frame, weight=2)

        self.pipeline_group = ttk.LabelFrame(left_frame, text="技术细节：处理步骤", padding=8, style="Soft.TLabelframe")
        self.pipeline_group.pack(fill="both", expand=True)

        columns = ("stage", "module", "state", "completed", "output")
        self.step_tree = ttk.Treeview(self.pipeline_group, columns=columns, show="headings", height=22)
        self.step_tree.heading("stage", text="Stage")
        self.step_tree.heading("module", text="Module")
        self.step_tree.heading("state", text="State")
        self.step_tree.heading("completed", text="Completed UTC")
        self.step_tree.heading("output", text="Output")
        self.step_tree.column("stage", width=90, anchor="center")
        self.step_tree.column("module", width=320, anchor="w")
        self.step_tree.column("state", width=150, anchor="center")
        self.step_tree.column("completed", width=150, anchor="center")
        self.step_tree.column("output", width=390, anchor="w")
        step_scroll = ttk.Scrollbar(self.pipeline_group, orient="vertical", command=self.step_tree.yview)
        self.step_tree.configure(yscrollcommand=step_scroll.set)
        self.step_tree.pack(side="left", fill="both", expand=True)
        step_scroll.pack(side="right", fill="y")

        digest_group = ttk.LabelFrame(left_frame, text="本轮摘要", padding=8, style="Soft.TLabelframe")
        digest_group.pack(fill="both", expand=False, pady=(8, 0))
        self.digest_text = tk.Text(digest_group, height=11, wrap="word")
        self.digest_text.pack(fill="both", expand=True)
        self.digest_text.configure(state="disabled")

        final_group = ttk.LabelFrame(right_frame, text="当前结论", padding=8, style="Soft.TLabelframe")
        final_group.pack(fill="both", expand=True)
        self.final_text = tk.Text(final_group, height=20, wrap="word")
        self.final_text.pack(fill="both", expand=True)
        self.final_text.configure(state="disabled")

        self.path_group = ttk.LabelFrame(right_frame, text="技术细节：结果路径", padding=8, style="Soft.TLabelframe")
        self.path_group.pack(fill="both", expand=True, pady=(8, 0))
        self.path_text = tk.Text(self.path_group, height=16, wrap="none")
        self.path_text.pack(fill="both", expand=True)
        self.path_text.configure(state="disabled")
        self.pipeline_group.pack_forget()
        self.path_group.pack_forget()
        self.stage_row.pack_forget()

    def _close(self) -> None:
        if self.refresh_job is not None:
            self.root.after_cancel(self.refresh_job)
            self.refresh_job = None
        self.root.destroy()

    def _bring_window_front(self) -> None:
        self.root.update_idletasks()
        width = max(self.root.winfo_width(), 1460)
        height = max(self.root.winfo_height(), 900)
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        pos_x = max((screen_width - width) // 2, 20)
        pos_y = max((screen_height - height) // 2, 20)
        self.root.geometry(f"{width}x{height}+{pos_x}+{pos_y}")
        self.root.deiconify()
        self.root.lift()
        self.root.attributes("-topmost", True)
        self.root.after(1200, lambda: self.root.attributes("-topmost", False))
        try:
            self.root.focus_force()
        except tk.TclError:
            pass

    def _schedule_refresh(self) -> None:
        self.refresh_job = self.root.after(self.AUTO_REFRESH_MS, self._refresh_tick)

    def toggle_tech_details(self) -> None:
        self.tech_details_visible = not self.tech_details_visible
        if self.tech_details_visible:
            self.stage_row.pack(fill="x", pady=(0, 10))
            self.pipeline_group.pack(fill="both", expand=True, before=self.digest_text.master, pady=(0, 0))
            self.path_group.pack(fill="both", expand=True, pady=(8, 0))
        else:
            self.stage_row.pack_forget()
            self.pipeline_group.pack_forget()
            self.path_group.pack_forget()

    def _refresh_tick(self) -> None:
        self.refresh()
        self._schedule_refresh()

    def _set_text(self, widget: tk.Text, content: str) -> None:
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", content)
        widget.configure(state="disabled")

    def _run_schtasks(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["schtasks.exe", *args],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            encoding=locale.getpreferredencoding(False),
            errors="replace",
        )

    def _task_status(self) -> str:
        result = self._run_schtasks("/Query", "/TN", TASK_NAME, "/FO", "LIST")
        if result.returncode != 0:
            return "task_missing"
        stdout = result.stdout or ""
        for line in stdout.splitlines():
            if line.strip().startswith("Status:"):
                return line.split(":", 1)[1].strip() or "unknown"
        return "unknown"

    def _open_path(self, path: Path) -> None:
        if not path.exists():
            messagebox.showwarning("Path Missing", str(path))
            return
        os.startfile(path)  # type: ignore[attr-defined]

    def _compose_digest(self, registry: dict[str, str], manifest: dict) -> str:
        cycle_steps = manifest.get("cycle_steps", [])
        materialized_count = sum(step.get("step_state") == "materialized" for step in cycle_steps)
        fallback_count = sum(step.get("step_state") == "fallback_existing_artifact" for step in cycle_steps)
        first_step = cycle_steps[0] if cycle_steps else {}
        last_step = cycle_steps[-1] if cycle_steps else {}
        lines = [
            "这一轮自动更新已经完成。",
            f"开始时间：{_format_utc_as_bj(_safe_value(registry, 'last_cycle_started_at_utc', ''))}",
            f"完成时间：{_format_utc_as_bj(_safe_value(registry, 'last_cycle_completed_at_utc', ''))}",
            f"总步骤：{_safe_value(registry, 'executed_step_count', '0')}",
            f"成功写出：{materialized_count} 步",
            f"沿用旧结果：{fallback_count} 步",
            f"开头步骤：{_short_module_name(first_step.get('module_name', 'none'))}",
            f"最后步骤：{_short_module_name(last_step.get('module_name', 'none'))}",
            "",
            "怎么看",
            "- 这里显示的是最近一轮自动运行的摘要，不需要手动点“立即跑一轮”才会更新。",
            "- 上面的卡片如果条数不变，也会通过更新时间告诉你这一轮确实跑过了。",
        ]
        if self.auto_cycle_message:
            lines.extend(["", "最近自动更新提示", self.auto_cycle_message])
        elif self.manual_output_message:
            lines.extend(["", "最近手动运行提示", self.manual_output_message])
        return "\n".join(lines)

    def _build_auto_cycle_message(self, registry: dict[str, str], manifest: dict) -> str:
        cycle_steps = manifest.get("cycle_steps", [])
        materialized_count = sum(step.get("step_state") == "materialized" for step in cycle_steps)
        fallback_count = sum(step.get("step_state") == "fallback_existing_artifact" for step in cycle_steps)
        return (
            "自动更新已完成\n"
            f"完成时间：{_format_utc_as_bj(_safe_value(registry, 'last_cycle_completed_at_utc', ''))}\n"
            f"运行状态：{_safe_value(registry, 'runtime_state', 'none')}\n"
            f"步骤：{_safe_value(registry, 'executed_step_count', '0')} "
            f"(成功写出={materialized_count}，沿用旧结果={fallback_count})\n"
            f"当前主方向：{_cn_theme(_safe_value(registry, 'top_opportunity_theme', 'none'))}\n"
            f"当前盯盘股票：{_safe_value(registry, 'top_watch_symbol', '')}"
        )

    def _compose_final_result(
        self,
        control: dict[str, str],
        opportunity_rows: list[dict[str, str]],
        risk_rows: list[dict[str, str]],
        watchlist_rows: list[dict[str, str]],
    ) -> str:
        top_opportunity = opportunity_rows[0] if opportunity_rows else {}
        top_risk = risk_rows[0] if risk_rows else {}
        top_watch = watchlist_rows[0] if watchlist_rows else {}
        risk_titles = [row.get("title", "") for row in risk_rows[:3] if row.get("title", "")]
        lines = [
            "当前系统结论",
            "",
            f"当前主方向：{_cn_theme(_safe_value(control, 'top_opportunity_theme', 'none'))}",
            f"当前盯盘股票：{_safe_value(control, 'top_watch_symbol', '')}",
            f"当前挑战方向：{_cn_theme(_safe_value(control, 'top_challenger_theme_slug', 'none'))} / {_safe_value(control, 'top_challenger_symbol', '')}",
            f"当前结论：{_safe_value(control, 'focus_rotation_readiness_state', 'unknown')}",
            "",
            "方向梗概",
            f"- 机会方向：{_cn_theme(_safe_value(top_opportunity, 'primary_theme_slug', _safe_value(control, 'top_opportunity_theme', 'none')))}",
            f"  候选股票：{_safe_value(top_watch, 'beneficiary_symbol', _safe_value(control, 'top_watch_symbol', ''))}",
            f"  映射把握：{_safe_value(top_watch, 'beneficiary_mapping_confidence', _safe_value(control, 'top_opportunity_mapping_confidence', ''))}",
            f"  关联强度：{_safe_value(top_watch, 'beneficiary_linkage_class', _safe_value(control, 'top_opportunity_linkage_class', ''))}",
            f"  当前动作：{_safe_value(top_opportunity, 'opportunity_action_bias', '')}",
            "",
            "风险梗概",
            f"- 当前风险主轴：{_cn_theme(_safe_value(top_risk, 'primary_theme_slug', 'broad_market'))}",
            f"- 风险处理动作：{_safe_value(top_risk, 'risk_action_bias', '')}",
        ]
        if risk_titles:
            lines.append("- 最近风险摘取：")
            for title in risk_titles:
                lines.append(f"  {title}")
        lines.extend(
            [
                "",
                "为什么现在选这只票",
                f"- 先从新闻里识别出主方向：{_cn_theme(_safe_value(control, 'top_opportunity_theme', 'none'))}",
                f"- 再从这个方向映射到受益股：{_safe_value(control, 'top_watch_symbol', '')}",
                f"- 当前这只票和主题的关系是：{_safe_value(control, 'top_watch_linkage_class', 'unknown')}",
                f"- 映射可信度是：{_safe_value(control, 'top_watch_mapping_confidence', 'unknown')}",
                "- 如果挑战方向继续明显走强，系统后面才会考虑轮换。",
                "",
                "补充状态",
                f"- 系统健康：{_safe_value(control, 'program_health_state', 'unknown')}",
                f"- 数据新鲜度：{_safe_value(control, 'freshness_state', 'unknown')}",
                f"- 挑战者审查：{_safe_value(control, 'challenger_review_state', 'unknown')}",
            ]
        )
        return "\n".join(lines)

    def _compose_paths(self) -> str:
        return "\n".join(
            [
                f"Scheduler registry: {REGISTRY_PATH}",
                f"Scheduler manifest: {MANIFEST_PATH}",
                f"Trading guidance: {GUIDANCE_PATH}",
                f"Event cluster: {EVENT_CLUSTER_PATH}",
                f"Opportunity feed: {OPPORTUNITY_FEED_PATH}",
                f"Program snapshot: {SNAPSHOT_PATH}",
                f"Program control packet: {CONTROL_PACKET_PATH}",
                f"Time slices folder: {TIME_SLICES_DIR}",
            ]
        )

    def _refresh_step_tree(self, manifest: dict) -> None:
        for item_id in self.step_tree.get_children():
            self.step_tree.delete(item_id)
        for step in manifest.get("cycle_steps", []):
            self.step_tree.insert(
                "",
                "end",
                values=(
                    _stage_name(step.get("module_name", "")),
                    _short_module_name(step.get("module_name", "")),
                    step.get("step_state", ""),
                    step.get("completed_at_utc", ""),
                    step.get("authoritative_output", ""),
                ),
            )

    def _find_step(self, manifest: dict, suffix: str) -> dict[str, str]:
        for step in manifest.get("cycle_steps", []):
            if step.get("module_name", "").endswith(suffix):
                return step
        return {}

    def _refresh_stage_cards(self, manifest: dict) -> None:
        stats = {
            stage: {"materialized": 0, "fallback": 0, "other": 0}
            for stage in self.STAGE_DISPLAY
        }
        for step in manifest.get("cycle_steps", []):
            stage = _stage_name(step.get("module_name", ""))
            if stage not in stats:
                stage = "other"
            step_state = step.get("step_state", "")
            if step_state == "materialized":
                stats[stage]["materialized"] += 1
            elif step_state == "fallback_existing_artifact":
                stats[stage]["fallback"] += 1
            else:
                stats[stage]["other"] += 1

        for stage, meta in self.STAGE_DISPLAY.items():
            ok_count = stats[stage]["materialized"]
            fallback_count = stats[stage]["fallback"]
            other_count = stats[stage]["other"]
            detail = f"{ok_count} ok"
            if fallback_count:
                detail += f" | {fallback_count} fallback"
            if other_count:
                detail += f" | {other_count} other"
            self.stage_vars[stage].set(f"{meta['icon']} {meta['title']}\n{detail}")

    def refresh(self) -> None:
        switch_state = self.switch_store.read()
        task_status = self._task_status()
        registry_rows = _read_csv(REGISTRY_PATH)
        registry = registry_rows[0] if registry_rows else {}
        manifest = _read_json(MANIFEST_PATH)
        control_rows = _read_csv(CONTROL_PACKET_PATH)
        control = control_rows[0] if control_rows else {}
        opportunity_rows = _read_csv(OPPORTUNITY_FEED_PATH)
        risk_rows = _read_csv(RISK_FEED_PATH)
        watchlist_rows = _read_csv(WATCHLIST_PACKET_PATH)
        current_cycle_completed_at_utc = _safe_value(registry, "last_cycle_completed_at_utc", "")

        if current_cycle_completed_at_utc:
            if not self.last_seen_cycle_completed_at_utc:
                self.last_seen_cycle_completed_at_utc = current_cycle_completed_at_utc
                self.auto_cycle_message = self._build_auto_cycle_message(registry, manifest)
            elif current_cycle_completed_at_utc != self.last_seen_cycle_completed_at_utc:
                self.last_seen_cycle_completed_at_utc = current_cycle_completed_at_utc
                self.auto_cycle_message = self._build_auto_cycle_message(registry, manifest)

        self.status_var.set(
            "switch="
            f"{'enabled' if switch_state.enabled else 'disabled'} | "
            f"task={task_status} | "
            f"runtime_state={_safe_value(registry, 'runtime_state', 'none')} | "
            f"last_cycle_bj={_format_utc_as_bj(_safe_value(registry, 'last_cycle_completed_at_utc', ''))}"
        )
        self.runtime_var.set(
            "runtime: "
            f"health={_safe_value(registry, 'program_health_state', 'unknown')} "
            f"freshness={_safe_value(registry, 'freshness_state', 'unknown')} "
            f"steps={_safe_value(registry, 'executed_step_count', '0')} "
            f"CLS={_safe_value(registry, 'cls_fetch_row_count', '0')} "
            f"Sina={_safe_value(registry, 'sina_fetch_row_count', '0')}"
        )
        self.focus_var.set(
            "focus: "
            f"theme={_safe_value(registry, 'top_opportunity_theme', 'none')} "
            f"symbol={_safe_value(registry, 'top_watch_symbol', '')} "
            f"readiness={_safe_value(registry, 'focus_rotation_readiness_state', 'unknown')}"
        )
        self.retention_var.set(
            "retention: "
            f"active_queue={_safe_value(registry, 'retention_active_queue_count', '0')} "
            f"expired_cleanup={_safe_value(registry, 'retention_expired_cleanup_count', '0')} "
            f"cap_pruned_files={_safe_value(registry, 'retention_cap_pruned_file_count', '0')} "
            f"cap_removed_rows={_safe_value(registry, 'retention_cap_removed_row_count', '0')}"
        )
        self.final_var.set(
            "final: "
            f"top_opportunity={_safe_value(control, 'top_opportunity_theme', 'none')} "
            f"top_watch={_safe_value(control, 'top_watch_symbol', '')} "
            f"challenger={_safe_value(control, 'top_challenger_theme_slug', 'none')}/"
            f"{_safe_value(control, 'top_challenger_symbol', '')}"
        )

        cls_step = self._find_step(manifest, "fetch_a_share_internal_hot_news_cls_telegraph_v1")
        sina_step = self._find_step(manifest, "fetch_a_share_internal_hot_news_sina_7x24_v1")
        cycle_bj = _format_utc_as_bj(_safe_value(registry, "last_cycle_completed_at_utc", ""))
        cycle_clock = cycle_bj[-8:] if cycle_bj != "n/a" else "n/a"
        self.cls_card_var.set(
            "\n".join(
                [
                    "📡 CLS",
                    f"rows {_safe_value(registry, 'cls_fetch_row_count', '0')}",
                    f"state {cls_step.get('step_state', 'unknown')}",
                    f"updated {cycle_clock}",
                ]
            )
        )
        self.sina_card_var.set(
            "\n".join(
                [
                    "📰 Sina",
                    f"rows {_safe_value(registry, 'sina_fetch_row_count', '0')}",
                    f"state {sina_step.get('step_state', 'unknown')}",
                    f"updated {cycle_clock}",
                ]
            )
        )
        self.focus_card_var.set(
            "\n".join(
                [
                    "🎯 Current Focus",
                    _safe_value(control, "top_opportunity_theme", "none"),
                    _safe_value(control, "top_watch_symbol", ""),
                    f"updated {cycle_clock}",
                ]
            )
        )
        self.challenger_card_var.set(
            "\n".join(
                [
                    "⚔ Challenger",
                    _safe_value(control, "top_challenger_theme_slug", "none"),
                    _safe_value(control, "top_challenger_symbol", ""),
                    f"support {_safe_value(control, 'top_challenger_support_row_count', '0')}",
                ]
            )
        )

        self._refresh_step_tree(manifest)
        self._refresh_stage_cards(manifest)
        self._set_text(self.digest_text, self._compose_digest(registry, manifest))
        self._set_text(self.final_text, self._compose_final_result(control, opportunity_rows, risk_rows, watchlist_rows))
        self._set_text(self.path_text, self._compose_paths())

    def enable_runtime(self) -> None:
        self.switch_store.write(
            enabled=True,
            updated_by="control_panel_button",
            notes="operator started runtime from local control panel",
        )
        enable_result = self._run_schtasks("/Change", "/TN", TASK_NAME, "/ENABLE")
        if enable_result.returncode != 0:
            messagebox.showwarning(
                "Task Enable Warning",
                (enable_result.stderr or enable_result.stdout or f"failed to enable {TASK_NAME}").strip(),
            )
        run_result = self._run_schtasks("/Run", "/TN", TASK_NAME)
        if run_result.returncode != 0:
            messagebox.showwarning(
                "Task Run Warning",
                (run_result.stderr or run_result.stdout or f"failed to run {TASK_NAME}").strip(),
            )
        self.refresh()

    def disable_runtime(self) -> None:
        self.switch_store.write(
            enabled=False,
            updated_by="control_panel_button",
            notes="operator disabled runtime from local control panel",
        )
        self._run_schtasks("/End", "/TN", TASK_NAME)
        disable_result = self._run_schtasks("/Change", "/TN", TASK_NAME, "/DISABLE")
        if disable_result.returncode != 0:
            messagebox.showwarning(
                "Task Disable Warning",
                (disable_result.stderr or disable_result.stdout or f"failed to disable {TASK_NAME}").strip(),
            )
        self.refresh()

    def run_once(self) -> None:
        self.manual_output_message = "Running single-cycle runtime ..."
        self.refresh()

        def _worker() -> None:
            result = subprocess.run(
                [sys.executable, str(SCHEDULER_SCRIPT)],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                encoding=locale.getpreferredencoding(False),
                errors="replace",
            )
            raw_message = (result.stdout or result.stderr or "").strip()[-4000:]
            message = raw_message or f"return_code={result.returncode}"
            self.root.after(0, lambda: self._finish_run(result.returncode, message))

        threading.Thread(target=_worker, daemon=True).start()

    def _finish_run(self, return_code: int, message: str) -> None:
        self.manual_output_message = message
        self.refresh()
        if return_code != 0:
            messagebox.showwarning(
                "Runtime Finished With Warning",
                "The cycle returned a non-zero code. Check Latest Cycle Digest.",
            )


def main() -> None:
    root = tk.Tk()
    HotNewsRuntimeControlPanelV1(root)
    root.mainloop()


if __name__ == "__main__":
    main()
