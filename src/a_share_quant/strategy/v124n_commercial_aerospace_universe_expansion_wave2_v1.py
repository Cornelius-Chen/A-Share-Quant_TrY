from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V124NCommercialAerospaceUniverseExpansionWave2Report:
    summary: dict[str, Any]
    added_rows: list[dict[str, Any]]
    pending_rows: list[dict[str, Any]]
    source_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "added_rows": self.added_rows,
            "pending_rows": self.pending_rows,
            "source_rows": self.source_rows,
            "interpretation": self.interpretation,
        }


class V124NCommercialAerospaceUniverseExpansionWave2Analyzer:
    def analyze(self) -> V124NCommercialAerospaceUniverseExpansionWave2Report:
        source_rows = [
            {
                "source_name": "新浪财经-航天强国战略升级与概念股梳理",
                "url": "https://finance.sina.com.cn/roll/2025-10-26/doc-infvfpzr1540466.shtml",
                "value": "提供偏产业链维度的正式组/卖铲方向补充。",
            },
            {
                "source_name": "搜狐-商业航天成政策焦点与创新高名单",
                "url": "https://www.sohu.com/a/983837634_122340993",
                "value": "给出卫星运营、中游制造、太空算力等方向的强势票与逻辑。",
            },
            {
                "source_name": "淘股吧-A股火箭回收概念股核心梳理",
                "url": "https://m.tgb.cn/a/2irP5VBP63P",
                "value": "补充火箭回收、结构件、材料、地面设备等卖铲与同走势镜像名单。",
            },
            {
                "source_name": "淘股吧-长征十号商业航天产业链受益标的梳理",
                "url": "https://www.tgb.cn/a/2ooGdt9HXdw",
                "value": "补充大运力+可回收方向链条。",
            },
            {
                "source_name": "淘股吧-商业航天复盘",
                "url": "https://www.tgb.cn/a/2o6uYTHZbwW",
                "value": "补充神剑股份、上海港湾等同走势镜像标的。",
            },
            {
                "source_name": "雪球/讨论-伪概念风险提示",
                "url": "https://xueqiu.com/1634786944/368571926/390771636",
                "value": "用于区分高置信卖铲与中置信待审票，例如西测测试在这类讨论里争议较大。",
            },
        ]

        added_rows = [
            {"symbol": "300900", "name": "广联航空", "group": "卖铲组", "subgroup": "航天结构件/制造配套", "confidence": "high", "reason": "火箭回收与航天制造链条中反复出现，工业位置更清晰。"},
            {"symbol": "688636", "name": "智明达", "group": "卖铲组", "subgroup": "航天电子/嵌入式计算", "confidence": "high", "reason": "多篇产业链梳理将其纳入火箭/卫星电子链。"},
            {"symbol": "688143", "name": "长盈通", "group": "卖铲组", "subgroup": "光纤器件/上游材料", "confidence": "high", "reason": "在火箭/卫星配套材料链条中多次出现。"},
            {"symbol": "688539", "name": "高华科技", "group": "卖铲组", "subgroup": "传感器/检测配套", "confidence": "high", "reason": "火箭回收及航天电子产业链梳理中多次出现。"},
            {"symbol": "688102", "name": "斯瑞新材", "group": "卖铲组", "subgroup": "高温合金/材料", "confidence": "high", "reason": "既在蓝箭相关资本映射中出现，也在高端材料链里站得住。"},
            {"symbol": "600862", "name": "中航高科", "group": "卖铲组", "subgroup": "航空航天复合材料", "confidence": "high", "reason": "航天强国与航空航天材料链条中的高置信卖铲。"},
            {"symbol": "688122", "name": "西部超导", "group": "卖铲组", "subgroup": "钛合金/超导材料", "confidence": "high", "reason": "高端材料与航天应用强相关。"},
            {"symbol": "603267", "name": "鸿远电子", "group": "卖铲组", "subgroup": "电子元器件", "confidence": "medium", "reason": "常见于军工航天高端元件链，但商业航天直接度略弱于前述票。"},
            {"symbol": "600316", "name": "洪都航空", "group": "同走势镜像组", "subgroup": "军工高辨识镜像", "confidence": "medium", "reason": "航天军工风险偏好抬升时常与商业航天同振。"},
            {"symbol": "000768", "name": "中航西飞", "group": "同走势镜像组", "subgroup": "大飞机/军工镜像", "confidence": "medium", "reason": "更偏大飞机，但常作为航天军工风险偏好的大票镜像。"},
            {"symbol": "603131", "name": "上海沪工", "group": "概念助推组", "subgroup": "卫星制造/概念助推", "confidence": "medium", "reason": "A股卫星制造与商业航天老题材高弹性标的。"},
            {"symbol": "603698", "name": "航天工程", "group": "同走势镜像组", "subgroup": "工程建设/高辨识镜像", "confidence": "medium", "reason": "名称与题材耦合度高，容易成为情绪镜像。"},
        ]

        pending_rows = [
            {"symbol": "300034", "name": "钢研高纳", "proposed_group": "卖铲组", "reason": "高温合金链条强相关，但商业航天直接暴露仍需再核。"},
            {"symbol": "600399", "name": "抚顺特钢", "proposed_group": "卖铲组", "reason": "材料属性很强，但更偏广义军工特钢。"},
            {"symbol": "603000", "name": "人民网", "proposed_group": "概念助推组", "reason": "若出现太空算力/政策主题传播，可能成为情绪扩散载体，但当前依据不足。"},
            {"symbol": "605180", "name": "华生科技", "proposed_group": "概念助推组", "reason": "网传题材偶有出现，但工业链条依据不够硬。"},
            {"symbol": "603679", "name": "华体科技", "proposed_group": "概念助推组", "reason": "可能受卫星互联网/智慧城市叙事共振，但需避免硬蹭。"},
        ]

        summary = {
            "acceptance_posture": "freeze_v124n_commercial_aerospace_universe_expansion_wave2_v1",
            "added_count": len(added_rows),
            "pending_count": len(pending_rows),
            "high_confidence_added_count": sum(1 for row in added_rows if row["confidence"] == "high"),
            "medium_confidence_added_count": sum(1 for row in added_rows if row["confidence"] == "medium"),
            "authoritative_rule": "wave2_should_expand_the_universe_but_keep_confidence_tags_explicit_instead_of_adding_everything_as_equal_truth",
            "recommended_next_posture": "merge_high_confidence_wave2_names_into_role_grammar_context_and_keep_pending_rows_outside_control_surface",
        }
        interpretation = [
            "V1.24N is a second-pass universe expansion rather than a claim that the board list is now complete.",
            "The key discipline is confidence-tagged expansion: add the names that repeatedly appear with defensible industrial or trading roles, and quarantine the ones that still look too loose.",
            "This lets the commercial-aerospace worker expand like an A-share board should, without turning into an everything-bagel theme list.",
        ]
        return V124NCommercialAerospaceUniverseExpansionWave2Report(
            summary=summary,
            added_rows=added_rows,
            pending_rows=pending_rows,
            source_rows=source_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V124NCommercialAerospaceUniverseExpansionWave2Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def write_csv(
    *,
    data_dir: Path,
    result: V124NCommercialAerospaceUniverseExpansionWave2Report,
) -> Path:
    data_dir.mkdir(parents=True, exist_ok=True)
    output_path = data_dir / "commercial_aerospace_universe_wave2_v1.csv"
    fieldnames = ["symbol", "name", "group", "subgroup", "confidence", "reason"]
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in result.added_rows:
            writer.writerow({name: row.get(name) for name in fieldnames})
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V124NCommercialAerospaceUniverseExpansionWave2Analyzer()
    result = analyzer.analyze()
    report_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v124n_commercial_aerospace_universe_expansion_wave2_v1",
        result=result,
    )
    csv_path = write_csv(
        data_dir=repo_root / "data" / "training",
        result=result,
    )
    print(report_path)
    print(csv_path)


if __name__ == "__main__":
    main()
