from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V124LCommercialAerospaceWebConceptUniverseReviewReport:
    summary: dict[str, Any]
    universe_rows: list[dict[str, Any]]
    source_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "universe_rows": self.universe_rows,
            "source_rows": self.source_rows,
            "interpretation": self.interpretation,
        }


class V124LCommercialAerospaceWebConceptUniverseReviewAnalyzer:
    def analyze(self) -> V124LCommercialAerospaceWebConceptUniverseReviewReport:
        source_rows = [
            {
                "source_name": "东方财富财富号-盘中主要热点题材",
                "url": "https://caifuhao.eastmoney.com/news/20260108205209680359740",
                "value": "给出一批商业航天热股名单，并单独点名“参股蓝箭航天：鲁信创投、金风科技”。",
            },
            {
                "source_name": "新浪财经-商业航天概念再度上演涨停潮",
                "url": "https://finance.sina.com.cn/stock/jsy/2026-01-08/doc-inhfqyhp6590844.shtml",
                "value": "列出一批强势涨停/主升浪标的，包含鲁信创投、金风科技、顺灏股份、华菱线缆、航天电子、航天科技、乾照光电、派克新材等。",
            },
            {
                "source_name": "同花顺-概念细分（太空光伏/算力/火箭回收/蓝箭航天）",
                "url": "https://news.10jqka.com.cn/20260108/c673859497.shtml",
                "value": "给出更偏产业链和细分方向的关联理由，如巨力索具、海兰信、超捷股份、泰胜风能。",
            },
            {
                "source_name": "同花顺-商业航天板块爆发",
                "url": "https://news.10jqka.com.cn/20260112/c673928411.shtml",
                "value": "给出ETF持仓和盘中强势标的，包含中国卫星、航天电子、海格通信、天银机电、中科星图、华力创通、航天宏图、航天环宇。",
            },
            {
                "source_name": "新浪财经-华菱线缆收购星鑫航天事件",
                "url": "https://finance.sina.com.cn/roll/2026-01-21/doc-inhhzyea3582419.shtml",
                "value": "明确华菱线缆并非纯蹭概念，长期为神舟/长征等重点工程配套供应线缆产品，是典型卖铲人。",
            },
            {
                "source_name": "韭研公社-持有蓝箭航天的各个公司",
                "url": "https://www.jiuyangongshe.com/square_publish/4_97",
                "value": "社区汇总指出金风科技、鲁信创投、电广传媒、张江高科、斯瑞新材等与蓝箭航天有资本连接，体现A股特有的跨板块概念扩散。",
            },
            {
                "source_name": "同花顺-商业航天板块集体跳水",
                "url": "https://news.10jqka.com.cn/field/20260113/673980017.shtml",
                "value": "点名航天发展、中国卫通等高辨识度龙头在概念过热后同样会成为情绪主轴。",
            },
            {
                "source_name": "e公司/产业报道-*ST铖昌深耕卫星通信领域",
                "url": "https://www.egsea.com/news/detail/2139593.html",
                "value": "明确*ST铖昌在卫星通信、星载领域持续发力，商业航天相关性强。",
            },
            {
                "source_name": "新浪/产业链梳理-卫星互联网核心企业概念股",
                "url": "https://k.sina.com.cn/article_7857201856_1d45362c001902wm5i.html",
                "value": "明确臻镭科技为星载射频芯片与微系统方案商，覆盖卫星收发链路。",
            },
            {
                "source_name": "搜狐/再升科技航天材料逻辑",
                "url": "https://www.sohu.com/a/968936119_122102189",
                "value": "指出再升科技向SpaceX稳定供应太空级保温材料，但当前收入结构仍以传统业务为主。",
            },
            {
                "source_name": "新浪财经-西测测试商业航天核心赛道",
                "url": "https://finance.sina.com.cn/stock/bxjj/2025-12-26/doc-inheautp8208706.shtml",
                "value": "西测测试被市场直接作为商业航天强势龙头点名，且具备检测/试验平台属性。",
            },
            {
                "source_name": "概念资金流/盘面报道-中超控股居前",
                "url": "https://www.futurephecda.com/news/11316",
                "value": "商业航天概念净流入中，中超控股居前，说明其是A股主题扩散中的重要助推票。",
            },
        ]

        universe_rows = [
            {"symbol": "002085", "name": "万丰奥威", "group": "正式组", "subgroup": "低空/飞行器平台龙头", "rationale": "当前本地 snapshot 已将其识别为商业航天/航空交叉中的液态主驱动之一，必须进入正式组。"},
            {"symbol": "000738", "name": "航发控制", "group": "正式组", "subgroup": "核心控制/稳定支撑", "rationale": "当前本地 snapshot 已将其识别为商业航天/航天航空交叉中的稳定核心支撑。"},
            {"symbol": "600118", "name": "中国卫星", "group": "正式组", "subgroup": "卫星整机/核心龙头", "rationale": "多源报道反复作为商业航天和卫星制造核心龙头出现。"},
            {"symbol": "601698", "name": "中国卫通", "group": "正式组", "subgroup": "卫星运营/核心龙头", "rationale": "板块高辨识龙头，概念过热时也被监管风险提示。"},
            {"symbol": "600879", "name": "航天电子", "group": "正式组", "subgroup": "核心配套", "rationale": "ETF持仓与热点名单反复出现，属于主驱动链条。"},
            {"symbol": "688066", "name": "航天宏图", "group": "正式组", "subgroup": "卫星应用/遥感服务", "rationale": "多篇行业评论列作下游运营服务龙头。"},
            {"symbol": "003009", "name": "中天火箭", "group": "正式组", "subgroup": "火箭细分龙头", "rationale": "行业评论反复归入高纯度商业航天链。"},
            {"symbol": "688523", "name": "航天环宇", "group": "正式组", "subgroup": "卫星/航天器配套", "rationale": "近期活跃且在ETF/热点报道中持续出现。"},
            {"symbol": "688568", "name": "中科星图", "group": "正式组", "subgroup": "卫星数据应用", "rationale": "近期盘中强势名单高频出现。"},
            {"symbol": "300045", "name": "华力创通", "group": "正式组", "subgroup": "卫星导航/通信配套", "rationale": "ETF与热点报道中多次出现。"},
            {"symbol": "002465", "name": "海格通信", "group": "正式组", "subgroup": "通信导航配套", "rationale": "近期ETF持仓和板块强势名单高频出现。"},
            {"symbol": "300342", "name": "天银机电", "group": "正式组", "subgroup": "卫星/航天配套", "rationale": "ETF近期强势持仓之一。"},
            {"symbol": "002792", "name": "通宇通讯", "group": "卖铲组", "subgroup": "有源相控阵天线", "rationale": "新浪直接点名为有源相控阵天线细分龙头。"},
            {"symbol": "002413", "name": "雷科防务", "group": "卖铲组", "subgroup": "有源相控阵天线", "rationale": "与通宇通讯并列被点名。"},
            {"symbol": "001208", "name": "华菱线缆", "group": "卖铲组", "subgroup": "特种线缆/卖铲人", "rationale": "实质切入航空航天线缆与并购星鑫航天事件，非纯概念。"},
            {"symbol": "301306", "name": "西测测试", "group": "卖铲组", "subgroup": "检测验证/质量守门人", "rationale": "多篇报道把它作为商业航天核心赛道强势票，同时具备元器件到整机全流程测试验证能力。"},
            {"symbol": "301005", "name": "超捷股份", "group": "卖铲组", "subgroup": "箭体结构件", "rationale": "同花顺列出其为蓝箭/天兵/中科宇航提供箭体大部段等。"},
            {"symbol": "002342", "name": "巨力索具", "group": "卖铲组", "subgroup": "火箭回收/地面装置", "rationale": "同花顺细分方向明确给出可回收火箭产品支持。"},
            {"symbol": "300065", "name": "海兰信", "group": "卖铲组", "subgroup": "海上回收系统", "rationale": "同花顺给出海南商发回收系统中标线索。"},
            {"symbol": "300129", "name": "泰胜风能", "group": "卖铲组", "subgroup": "箭体/贮箱/回收设施", "rationale": "同花顺给出与整箭商合作布局火箭结构与回收设施。"},
            {"symbol": "001270", "name": "*ST铖昌", "group": "卖铲组", "subgroup": "星载相控阵T/R芯片", "rationale": "多篇产业报道明确其在低轨卫星与星载领域持续发力，是商业航天核心芯片卖铲人。"},
            {"symbol": "688270", "name": "臻镭科技", "group": "卖铲组", "subgroup": "星载射频芯片/微系统", "rationale": "卫星互联网与商业航天报道多次点名，属于星载收发链路核心芯片供应商。"},
            {"symbol": "600783", "name": "鲁信创投", "group": "概念助推组", "subgroup": "参股蓝箭航天/资本映射", "rationale": "东方财富、新浪、社区都把它列为典型商业航天助推主力。"},
            {"symbol": "002202", "name": "金风科技", "group": "概念助推组", "subgroup": "参股蓝箭航天/资本映射", "rationale": "东方财富和社区汇总都指向其为蓝箭航天重要股权关联方。"},
            {"symbol": "002565", "name": "顺灏股份", "group": "概念助推组", "subgroup": "太空算力/概念强弹性", "rationale": "同花顺与新浪多次作为强势概念股提及。"},
            {"symbol": "603601", "name": "再升科技", "group": "概念助推组", "subgroup": "航天保温材料/概念弹性", "rationale": "具备真实航天材料和SpaceX供应逻辑，但公开资料显示当前营收仍非商业航天主导，更像高价值概念助推。"},
            {"symbol": "002471", "name": "中超控股", "group": "概念助推组", "subgroup": "主题扩散助推/高弹性", "rationale": "多篇盘面与资金流报道把它列为商业航天概念主力净流入和强势涨停代表，更像A股主题助推主力。"},
            {"symbol": "000547", "name": "航天发展", "group": "同走势镜像组", "subgroup": "情绪龙头/概念高辨识", "rationale": "同花顺和东方财富多次点名其为商业航天高辨识龙头。"},
            {"symbol": "002519", "name": "银河电子", "group": "同走势镜像组", "subgroup": "情绪强势镜像", "rationale": "东方财富与新浪近期涨停名单中高频出现。"},
            {"symbol": "600775", "name": "南京熊猫", "group": "同走势镜像组", "subgroup": "情绪强势镜像", "rationale": "新浪强势主升浪名单中出现。"},
            {"symbol": "600135", "name": "乐凯胶片", "group": "同走势镜像组", "subgroup": "情绪强势镜像", "rationale": "新浪与东方财富名单中出现。"},
            {"symbol": "601399", "name": "国机重装", "group": "同走势镜像组", "subgroup": "情绪强势镜像", "rationale": "新浪涨停主升浪名单中出现。"},
            {"symbol": "600869", "name": "远东股份", "group": "同走势镜像组", "subgroup": "情绪强势镜像", "rationale": "新浪强势名单中出现。"},
            {"symbol": "605123", "name": "派克新材", "group": "同走势镜像组", "subgroup": "材料/高弹性镜像", "rationale": "新浪与东方财富名单中出现。"},
            {"symbol": "002361", "name": "神剑股份", "group": "同走势镜像组", "subgroup": "情绪强势镜像", "rationale": "多篇行情报道高频点名。"},
            {"symbol": "300102", "name": "乾照光电", "group": "同走势镜像组", "subgroup": "情绪强势镜像", "rationale": "多篇行情报道高频点名。"},
            {"symbol": "000901", "name": "航天科技", "group": "同走势镜像组", "subgroup": "高辨识镜像", "rationale": "多篇行情报道高频点名。"},
            {"symbol": "301079", "name": "邵阳液压", "group": "同走势镜像组", "subgroup": "情绪强势镜像", "rationale": "新浪、东方财富高频强势名单。"},
            {"symbol": "002865", "name": "钧达股份", "group": "同走势镜像组", "subgroup": "跨细分热点镜像", "rationale": "强势名单反复出现，适合当扩散镜像观察。"},
        ]

        summary = {
            "acceptance_posture": "freeze_v124l_commercial_aerospace_web_concept_universe_review_v1",
            "source_count": len(source_rows),
            "symbol_count": len(universe_rows),
            "group_count": 4,
            "authoritative_rule": "commercial_aerospace_research_should_use_a_dual_universe_direct_industry_plus_cross_board_concept_propulsion_view",
            "direct_group_count": sum(1 for row in universe_rows if row["group"] == "正式组"),
            "concept_propulsion_count": sum(1 for row in universe_rows if row["group"] == "概念助推组"),
            "shovel_count": sum(1 for row in universe_rows if row["group"] == "卖铲组"),
            "similar_path_count": sum(1 for row in universe_rows if row["group"] == "同走势镜像组"),
            "recommended_next_posture": "upgrade_commercial_aerospace_role_grammar_from_three_symbol_core_to_web_extended_dual_universe",
        }
        interpretation = [
            "V1.24L upgrades the commercial-aerospace universe from a narrow direct-board sample to an A-share style dual universe.",
            "The research unit should still distinguish formal industry owners from concept-propulsion names, but it should not discard the latter because they often act as real force multipliers in A-share theme runs.",
            "This matters especially for board breadth, diffusion, sympathy leadership, and shovel-seller capture.",
        ]
        return V124LCommercialAerospaceWebConceptUniverseReviewReport(
            summary=summary,
            universe_rows=universe_rows,
            source_rows=source_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V124LCommercialAerospaceWebConceptUniverseReviewReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def write_csv(
    *,
    data_dir: Path,
    result: V124LCommercialAerospaceWebConceptUniverseReviewReport,
) -> Path:
    data_dir.mkdir(parents=True, exist_ok=True)
    output_path = data_dir / "commercial_aerospace_web_concept_universe_v1.csv"
    fieldnames = ["symbol", "name", "group", "subgroup", "rationale"]
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in result.universe_rows:
            writer.writerow({name: row.get(name) for name in fieldnames})
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V124LCommercialAerospaceWebConceptUniverseReviewAnalyzer()
    result = analyzer.analyze()
    report_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v124l_commercial_aerospace_web_concept_universe_review_v1",
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
