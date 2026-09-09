#!/usr/bin/env python3
"""Build a visually verifiable PDF companion for the Member E DOCX report."""

from __future__ import annotations

import csv
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (Image, KeepTogether, PageBreak, Paragraph,
                               SimpleDocTemplate, Spacer, Table, TableStyle)


UPGRADE = Path(__file__).resolve().parents[1]
OUT = UPGRADE / "report" / "Member_E_Joint_DSE_Report.pdf"
JOINT = UPGRADE / "joint_dse"
MEMORY = UPGRADE / "memory_cache_candidate"
AXI = UPGRADE / "zynq_axi_integration"

pdfmetrics.registerFont(TTFont("CJK", r"C:\Windows\Fonts\simhei.ttf"))
BLUE = colors.HexColor("#17365D")
TEAL = colors.HexColor("#087E8B")
ORANGE = colors.HexColor("#E07A1F")
PALE = colors.HexColor("#EEF5F9")


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


base = getSampleStyleSheet()
styles = {
    "title": ParagraphStyle("title", fontName="CJK", fontSize=24, leading=32,
                            textColor=BLUE, alignment=TA_CENTER, spaceAfter=16),
    "subtitle": ParagraphStyle("subtitle", fontName="CJK", fontSize=13, leading=20,
                               textColor=TEAL, alignment=TA_CENTER, spaceAfter=18),
    "h1": ParagraphStyle("h1", fontName="CJK", fontSize=17, leading=23,
                         textColor=BLUE, spaceBefore=4, spaceAfter=10),
    "h2": ParagraphStyle("h2", fontName="CJK", fontSize=12, leading=17,
                         textColor=TEAL, spaceBefore=7, spaceAfter=5),
    "body": ParagraphStyle("body", fontName="CJK", fontSize=9.2, leading=14,
                           textColor=colors.HexColor("#263238"), spaceAfter=5),
    "small": ParagraphStyle("small", fontName="CJK", fontSize=7.4, leading=10,
                            textColor=colors.HexColor("#263238")),
    "caption": ParagraphStyle("caption", fontName="CJK", fontSize=8, leading=11,
                              alignment=TA_CENTER, textColor=colors.HexColor("#5B6573")),
}


def P(text, style="body"):
    return Paragraph(text.replace("&", "&amp;"), styles[style])


def bullet(text):
    return Paragraph("- " + text.replace("&", "&amp;"), styles["body"])


def table(headers, rows, widths, font=7.4):
    data = [[Paragraph(str(x), ParagraphStyle("th", fontName="CJK", fontSize=font,
                                               leading=font + 2, textColor=colors.white,
                                               alignment=TA_CENTER)) for x in headers]]
    for row in rows:
        data.append([Paragraph(str(x).replace("&", "&amp;"),
                               ParagraphStyle("td", fontName="CJK", fontSize=font,
                                              leading=font + 2.3, textColor=colors.HexColor("#263238")))
                     for x in row])
    t = Table(data, colWidths=[w * cm for w in widths], repeatRows=1, hAlign="CENTER")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BLUE), ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#AAB8C2")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3), ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ] + [("BACKGROUND", (0, i), (-1, i), PALE) for i in range(2, len(data), 2)]))
    return t


def badge(label, text, color):
    return Table([[P(label, "body"), P(text, "body")]], colWidths=[3.0 * cm, 13.1 * cm],
                 style=TableStyle([("BACKGROUND", (0, 0), (0, 0), color),
                                   ("TEXTCOLOR", (0, 0), (0, 0), colors.white),
                                   ("BACKGROUND", (1, 0), (1, 0), colors.HexColor("#F5F7F9")),
                                   ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#AAB8C2")),
                                   ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                   ("LEFTPADDING", (0, 0), (-1, -1), 8),
                                   ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                                   ("TOPPADDING", (0, 0), (-1, -1), 7),
                                   ("BOTTOMPADDING", (0, 0), (-1, -1), 7)]))


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("CJK", 7.5)
    canvas.setFillColor(colors.HexColor("#5B6573"))
    canvas.drawCentredString(A4[0] / 2, 0.7 * cm, f"成员 E（陈正堃） | {doc.page}")
    canvas.drawRightString(A4[0] - 1.8 * cm, A4[1] - 1.0 * cm, "LeNet 任务 2 · 成员 E 升级交付")
    canvas.restoreState()


def build():
    v = read_csv(JOINT / "results" / "joint_dse_validated.csv")
    cfg = read_csv(JOINT / "joint_dse_configs.csv")
    mem = read_csv(MEMORY / "results" / "memory_cache_comparison.csv")
    story = [Spacer(1, 2.2 * cm), P("成员 E 升级任务交付报告", "title"),
             P("LeNet 联合位宽 × PE/Pipeline DSE、片上权重缓存与 Zynq AXI 集成", "subtitle"),
             badge("课程任务", "任务 2：基于 HLS 的 LeNet FPGA 加速器（路线 B）", BLUE), Spacer(1, 8),
             badge("成员分工", "成员 E 陈正堃：HLS IP 封装、Vivado 综合/资源分析、自动搜索脚本", TEAL), Spacer(1, 8),
             badge("器件与约束", "XC7Z020-CLG400-1；统一目标周期 10.0 ns", ORANGE), Spacer(1, 8),
             badge("报告日期", "2026-09-09", colors.HexColor("#5B6573")), Spacer(1, 1.5 * cm),
             P("数据原则：仅报告仓库中可追溯的实测/既有工程结果；缺失项保持空值并标记阻塞。", "caption"), PageBreak()]

    story += [P("1. 交付结论", "h1"),
              badge("主线 DSE", "13 个联合配置；4 个 FP32 已完成本机 Vitis HLS CSim/综合，9 个量化配置因成员 F 输入缺失而阻塞。", BLUE), Spacer(1, 6),
              badge("推荐配置", "D2：243,101 cycles，2.43101 ms@10ns，LUT 13,444，FF 16,887，DSP 7。", TEAL), Spacer(1, 6),
              badge("缓存候选", "两组均完成 HLS；缓存延迟 +0.1037%、LUT +780、BRAM18K +10，停止采用。", ORANGE), Spacer(1, 6),
              badge("AXI 集成", "实际运行 Vivado batch 强制校验 BD、导出报告和 XSA；26,721 条网络全部完成，WNS +0.415 ns。", colors.HexColor("#5B6573")),
              P("1.1 推荐依据", "h2"), bullet("D2 相对 D0 周期数减少 80.40%，是四个 FP32 候选中延迟最低者。"),
              bullet("D1 被 D2 同时在延迟和资源上支配；D3 增加 OC 并行后延迟反而增加 16.50%。"),
              bullet("D0 是最低资源备选；资源优先时仍有明确价值。"),
              P("1.2 声明边界", "h2"), P("INT8/INT6/INT4 缺成员 F 的量化源码、scale/zero-point 与真实准确率，不填造结果。缓存候选已由 HLS 证明没有性能收益。没有板上推理记录。"), PageBreak()]

    rows = [[c["config_id"], c["precision"], c["pe_variant"], c["pipeline_mode"],
             "READY" if c["planned_status"] == "READY" else "BLOCKED_F"] for c in cfg]
    story += [P("2. 背景与联合实验矩阵", "h1"),
              P("课程任务 2 面向 LeNet FPGA 推理。成员 E 负责 HLS IP 封装、Vivado 综合/资源分析和自动搜索；本升级将位宽与 PE/Pipeline 放在同一控制变量下。"),
              table(["配置 ID", "位宽", "结构", "Pipeline/PE", "状态"], rows, [5.0, 1.4, 1.2, 5.3, 2.4], 6.5),
              P("统一设置：xc7z020clg400-1、10.0 ns、同一 Conv2/testbench/model。D3 只作为 FP32 负对照。", "caption"), PageBreak()]

    rows = []
    for r in v:
        if r["precision"] == "FP32":
            rows.append([r["pe_variant"], r["pipeline_mode"], f'{int(r["latency_cycles"]):,}',
                         f'{float(r["latency_ms_at_target"]):.5f}', f'{int(r["lut"]):,}',
                         f'{int(r["ff"]):,}', r["dsp"], r["pareto_status"], r["selection_role"] or "—"])
    story += [P("3. FP32 × PE/Pipeline 实测结果", "h1"),
              P("成员 E 在本机 Vitis HLS 2022.2 对成员 D 的 D0-D3 源码逐一执行 CSim 与 C Synthesis，并从本次原始 XML 重新解析结果。"),
              table(["结构", "策略", "Cycles", "ms@10ns", "LUT", "FF", "DSP", "Pareto", "角色"], rows,
                    [1.0, 4.4, 2.3, 1.8, 1.5, 1.6, 1.0, 1.5, 2.0], 6.5),
              P("D0→D1 延迟 -79.46%，但 LUT +93.39%、FF +416.93%；D1→D2 延迟 -4.57%、LUT -16.96%、FF -37.77%，故 D2 支配 D1。D2→D3 延迟 +16.50%。"),
              P("99.30% 是成员 B 的 FP32 软件基线引用并结合成员 D 的 CSim PASS；不是四个结构分别跑完整 MNIST 得到的独立准确率。"), PageBreak()]

    chart = Image(str(JOINT / "figures" / "joint_pareto_accuracy_latency_resource.png"), width=16.3 * cm, height=9.6 * cm)
    story += [P("4. 联合 Pareto 结果", "h1"), chart,
              P("图 1 FP32 候选的延迟—资源 Pareto；量化配置因输入缺失不进入曲线。", "caption"),
              P("资源压力取 LUT、FF、BRAM、DSP 占器件容量百分比的最大值；平衡评分对延迟和资源压力分别 min-max 归一化后等权相加。D2 得分 0.303153 最低，因此推荐。", "body"),
              P("成员 F 提交量化类型、scale/zero-point、量化参数与真实 MNIST 准确率后，可直接补齐已固定的 9 个配置 ID并运行同一脚本。"), PageBreak()]

    mrows = [[r["config_id"], r["status"], r["csim"], r["max_abs_error"], r["decision"]] for r in mem]
    story += [P("5. 片上权重缓存候选", "h1"),
              P("在 D2 基线上将 2,400 个 Conv2 权重预取到静态本地数组：双端口 BRAM 绑定、cyclic factor=5 分割、搬运循环 PIPELINE II=1。卷积主体保持 PE_MAC=5。"),
              table(["配置", "状态", "测试", "最大绝对误差", "决策"], mrows, [4.3, 4.2, 2.0, 2.5, 3.2], 7.1),
              P("两个版本均完成 Vitis HLS CSim 与综合，最大绝对误差 2.7756691e-3 < 5e-3。缓存延迟由 243,101 增至 243,353 cycles（+0.1037%），LUT +780、FF -4,766、BRAM18K +10、DSP 不变，结论为 STOP_NO_PERFORMANCE_GAIN。"),
              P("采用判据", "h2"), bullet("baseline/cache 必须先分别 CSim PASS，再用相同器件、10 ns、testbench 综合。"),
              bullet("仅当延迟/II 改善且资源增量可接受时进入主线；否则作为否定实验保留。"), PageBreak()]

    fig = Image(str(AXI / "figures" / "block_design_connection_map.png"), width=16.4 * cm, height=8.9 * cm)
    story += [P("6. Zynq AXI 集成交付", "h1"), fig,
              P("图 2 从 lenet_system.bd 重建的连接图（不是 GUI 截图）。", "caption"),
              table(["地址/偏移", "寄存器", "用途"], [
                  ["0x4000_0000", "control base", "PS M_AXI_GP0 → HLS control"], ["+0x00", "AP_CTRL", "start/done/idle/ready"],
                  ["+0x10/+0x14", "feature_in", "输入 DDR 地址"], ["+0x1C/+0x20", "weight", "权重 DDR 地址"],
                  ["+0x28/+0x2C", "bias", "偏置 DDR 地址"], ["+0x34/+0x38", "feature_out", "输出 DDR 地址"]],
                    [3.3, 5.0, 7.5], 7.5), PageBreak()]

    story += [P("7. Vivado 实现证据", "h1"),
              P("以下来自 2026-09-09 实际执行的 Vivado 2022.2 batch：强制校验 BD、加载 impl_1、重新生成实现报告并导出 XSA。"),
              table(["指标", "结果", "判定"], [["时钟", "10.000 ns / 100 MHz", "统一约束"], ["WNS / TNS", "+0.415 / 0.000 ns", "PASS"],
                    ["WHS / THS", "+0.028 / 0.000 ns", "PASS"], ["可路由网络", "26,721 / 26,721", "全部完成"],
                    ["路由错误", "0", "PASS"], ["LUT / FF", "11,612 / 17,612", "整套系统"], ["BRAM / DSP", "37 / 5", "整套系统"]],
                    [5.0, 5.5, 5.3], 8.2),
              P("IP 固定与追溯", "h2"), bullet("VLNV user.org:hls:lenet_full_top:1.0；component.xml、export.zip、IP zip、驱动均归档。"),
              bullet("BD、地址表、PS 轮询伪代码、实现报告、校验历史与 SHA-256 清单完整保存。"),
              bullet("rerun_vivado_reports.tcl 可重新 validate BD，并从 routed DCP 导出 route/timing/utilization/power/XSA。"), PageBreak()]

    story += [P("8. 文件对应与最终结论", "h1"),
              table(["工作项", "核心文件", "用途"], [["联合矩阵", "joint_dse/joint_dse_configs.csv", "13 个 ID 与依赖"],
                    ["HLS 编排", "joint_dse/scripts/run_joint_dse.tcl", "CSim→综合"], ["结构化结果", "joint_dse/results/joint_dse_validated.csv", "唯一结果表"],
                    ["缓存源码", "memory_cache_candidate/src/lenet_conv_cache.cpp", "本地 BRAM 权重"], ["AXI 证据", "zynq_axi_integration/", "IP、BD、地址、驱动、报告"],
                    ["正式报告", "report/Member_E_Joint_DSE_Report.docx", "成员 E 总交付"]], [3.0, 7.3, 5.5], 7.5),
              P("当前阻塞", "h2"), bullet("成员 F 的 INT8/INT6/INT4 源码、scale/zero-point、参数与真实准确率。"),
              bullet("Vitis HLS 2022.2 需在纯英文临时路径运行；本次已完成并将原始证据复制回项目。"),
              bullet("板级软件和实机结果需与成员 C 联调。"),
              P("成员 E 已实际完成 4 组 FP32 HLS CSim/综合、联合 Pareto、缓存 HLS 对照、Vivado BD 校验与实现报告/XSA 导出。主线推荐 D2，资源保守备选 D0；缓存候选因无性能收益停止。量化结果等待成员 F，不用估算补齐。", "body")]

    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(OUT), pagesize=A4, rightMargin=1.8 * cm, leftMargin=1.8 * cm,
                            topMargin=1.55 * cm, bottomMargin=1.45 * cm,
                            title="Member E Joint DSE Report", author="陈正堃")
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(f"Saved {OUT}")


if __name__ == "__main__":
    build()
