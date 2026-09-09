import fs from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { FileBlob, Presentation, PresentationFile } from "@oai/artifact-tool";

const WORKSPACE = path.resolve(import.meta.dirname, "../../..");
const DELIVERABLES = path.resolve(import.meta.dirname, "..");
const SKILL_DIR = "C:\\Users\\Chen_zk\\.codex\\plugins\\cache\\openai-primary-runtime\\presentations\\26.905.11957\\skills\\presentations";
const RUNTIME_PYTHON = "C:\\Users\\Chen_zk\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe";
const BUILD_DIR = path.join(WORKSPACE, ".codex_tmp", "member_e_ppt");
const FINAL_DIR = path.join(DELIVERABLES, "slides");
const FINAL_PPTX = path.join(FINAL_DIR, "成员E_LeNet_DSE答辩.pptx");
const RENDER_DIR = path.join(FINAL_DIR, "rendered");
const FONT = "Microsoft YaHei";
process.env.RUNTIME_NODE_MODULES = "C:\\Users\\Chen_zk\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\node\\node_modules";

const { applyPresentationChartFont, finalizePresentation } = await import(
  pathToFileURL(path.join(SKILL_DIR, "container_tools", "artifact_tool_utils.mjs")).href,
);

const C = {
  navy: "#14213D",
  blue: "#2E6797",
  blue2: "#6E96B7",
  pale: "#E8F0F8",
  gold: "#C99116",
  paleGold: "#FBF2DC",
  gray: "#5B6B7F",
  light: "#F4F7FA",
  line: "#CBD5E1",
  white: "#FFFFFF",
  green: "#167C5A",
};

function addText(slide, text, position, style = {}) {
  const shape = slide.shapes.add({
    geometry: "textbox",
    position,
    fill: "none",
    line: { fill: "none", width: 0 },
  });
  shape.text = text;
  shape.text.style = {
    typeface: FONT,
    fontSize: 20,
    color: C.navy,
    autoFit: "none",
    ...style,
  };
  return shape;
}

function addTitle(slide, kicker, title, subtitle, number) {
  addText(slide, kicker, { left: 60, top: 34, width: 660, height: 24 }, { fontSize: 14, bold: true, color: C.blue, letterSpacing: 1.1 });
  addText(slide, title, { left: 60, top: 62, width: 1110, height: 58 }, { fontSize: 35, bold: true });
  addText(slide, subtitle, { left: 60, top: 116, width: 1100, height: 28 }, { fontSize: 16, color: C.gray });
  addText(slide, String(number).padStart(2, "0"), { left: 1180, top: 42, width: 48, height: 32 }, { fontSize: 15, bold: true, color: C.gray, alignment: "right" });
}

function addFooter(slide) {
  slide.shapes.add({ geometry: "line", position: { left: 60, top: 682, width: 1160, height: 0 }, fill: "none", line: { style: "solid", fill: C.line, width: 1 } });
  addText(slide, "成员 E · LeNet HLS / Vivado DSE · XC7Z020", { left: 60, top: 688, width: 520, height: 18 }, { fontSize: 10, color: C.gray });
}

function addCard(slide, position, title, body, accent = C.blue) {
  const card = slide.shapes.add({
    geometry: "roundRect",
    position,
    fill: C.white,
    line: { style: "solid", fill: C.line, width: 1 },
    borderRadius: 14,
  });
  slide.shapes.add({ geometry: "rect", position: { left: position.left, top: position.top, width: 7, height: position.height }, fill: accent, line: { fill: "none", width: 0 } });
  addText(slide, title, { left: position.left + 22, top: position.top + 16, width: position.width - 36, height: 26 }, { fontSize: 17, bold: true });
  addText(slide, body, { left: position.left + 22, top: position.top + 48, width: position.width - 36, height: position.height - 60 }, { fontSize: 13, color: C.gray, verticalAlignment: "top" });
  return card;
}

function addMetric(slide, position, label, value, note, accent = C.blue) {
  const valueFontSize = value.length > 13 ? 17 : value.length > 9 ? 20 : 23;
  slide.shapes.add({ geometry: "roundRect", position, fill: accent === C.gold ? C.paleGold : C.pale, line: { fill: "none", width: 0 }, borderRadius: 12 });
  addText(slide, label, { left: position.left + 15, top: position.top + 12, width: position.width - 30, height: 20 }, { fontSize: 11, color: C.gray });
  addText(slide, value, { left: position.left + 15, top: position.top + 35, width: position.width - 30, height: 30 }, { fontSize: valueFontSize, bold: true, color: C.navy });
  addText(slide, note, { left: position.left + 15, top: position.top + 76, width: position.width - 30, height: 18 }, { fontSize: 10, color: C.gray });
}

const presentation = Presentation.create({ slideSize: { width: 1280, height: 720 } });

// Slide 1 — method
{
  const slide = presentation.slides.add();
  slide.background.fill = C.light;
  addTitle(slide, "MEMBER E · EXPLORATION", "我负责把 LeNet 的 HLS 选择做成证据链", "5 组时钟约束 + 3 组结构实验 + 1 个 Vivado 最终闭环", 1);

  const table = slide.tables.add({
    rows: 4,
    columns: 4,
    left: 60,
    top: 174,
    width: 1160,
    height: 210,
    columnWidths: [170, 350, 300, 340],
    values: [
      ["实验维度", "配置", "唯一变量", "输出指标"],
      ["Clock DSE", "10 / 9 / 8 / 7.5 / 7 ns", "目标时钟周期", "cycles、Fmax、LUT/FF/BRAM/DSP"],
      ["Structural DSE", "baseline / Unroll ×2 / ×5", "MAC 循环展开因子", "有效并行度是否改变"],
      ["Vivado", "10 ns baseline", "最终候选", "post-route 时序、资源、功耗"],
    ],
  });
  table.styleOptions = { headerRow: true, bandedRows: true };
  table.borders.assign({ style: "solid", fill: C.line, width: 1 });
  const all = table.cells.block({ row: 0, column: 0, rowCount: 4, columnCount: 4 });
  all.textStyle.fontSize = 14;
  all.textStyle.typeface = FONT;
  all.textStyle.color = C.navy;
  for (let row = 0; row < 4; row += 1) {
    for (let col = 0; col < 4; col += 1) {
      table.getCell(row, col).text.style = { typeface: FONT, fontSize: 14, color: C.navy };
    }
  }
  for (let col = 0; col < 4; col += 1) {
    const cell = table.getCell(0, col);
    cell.fill = C.navy;
    cell.text.style = { typeface: FONT, fontSize: 14, bold: true, color: C.white };
  }

  addCard(slide, { left: 60, top: 420, width: 355, height: 200 }, "① 原始报告", "读取每个 solution 的 csynth.xml；保存 10 ns 的 csynth.rpt/xml 和 Vivado 原始报告。", C.blue);
  addCard(slide, { left: 462, top: 420, width: 355, height: 200 }, "② 自动核验", "重新提取所有指标，并与已有 CSV 逐项比对；任何差异都会让脚本失败。", C.gold);
  addCard(slide, { left: 864, top: 420, width: 356, height: 200 }, "③ 选择与归档", "画 Pareto 图、解释负结果，并用 post-route 时序/资源/功耗完成闭环。", C.green);
  addFooter(slide);
  slide.speakerNotes.textFrame.setText("数据源：handoff/LeNet_DSE_Framework_2022_2 下各配置的 csynth.xml；Vivado impl_1 的 timing/utilization/power/route reports。范围只包含成员 E。讲解重点：每次只改变一个变量，结论可追溯。 ");
}

// Slide 2 — DSE results with editable native charts
{
  const slide = presentation.slides.add();
  slide.background.fill = C.white;
  addTitle(slide, "RESULT · CLOCK & STRUCTURE", "10 ns 不是频率最高，但端到端更快、LUT 更少", "时钟越紧，估计 Fmax 越高；调度周期同时大幅增加", 2);

  const line = slide.charts.add("line", {
    position: { left: 55, top: 170, width: 555, height: 360 },
    title: "目标时钟周期 vs 延迟周期（M cycles）",
    titlePlacement: "aboveChart",
    categories: ["7 ns", "7.5 ns", "8 ns", "9 ns", "10 ns"],
    series: [{ name: "Latency", values: [2.847628, 2.548619, 2.546729, 2.247712, 1.647854], line: { style: "solid", fill: C.blue, width: 3 }, marker: { symbol: "circle", size: 7 }, points: [{ idx: 4, fill: C.gold }] }],
    hasLegend: false,
    xAxis: { textStyle: { typeface: FONT, fontSize: 11, fill: C.gray }, line: { style: "solid", fill: C.line, width: 1 } },
    yAxis: { min: 1.5, max: 3.0, majorUnit: 0.3, numberFormatCode: "0.0", title: "M cycles", majorGridlines: { style: "solid", fill: C.line, width: 1 }, textStyle: { typeface: FONT, fontSize: 10, fill: C.gray } },
    dataLabels: { showValue: true, position: "outEnd", textStyle: { typeface: FONT, fontSize: 10, fill: C.navy } },
    chartFill: C.white,
    plotAreaFill: C.white,
  });
  applyPresentationChartFont(line, { fontFamily: FONT });

  const points = [
    ["10 ns baseline", 1.647854, 17.108, C.gold],
    ["9 ns", 2.247712, 17.789, C.blue],
    ["8 ns", 2.546729, 18.423, C.blue],
    ["7.5 ns", 2.548619, 18.396, C.blue2],
    ["7 ns", 2.847628, 18.945, C.blue],
  ];
  const scatter = slide.charts.add("scatter", {
    position: { left: 650, top: 170, width: 570, height: 360 },
    title: "延迟—LUT Pareto（左下更优）",
    titlePlacement: "aboveChart",
    series: points.map(([name, x, y, color]) => ({
      name,
      xValues: [x],
      values: [y],
      fill: color,
      line: { fill: color, width: 1 },
      marker: { symbol: "circle", size: name === "10 ns baseline" ? 10 : 7 },
    })),
    scatterOptions: { style: "marker", varyColors: true },
    hasLegend: false,
    xAxis: { min: 1.5, max: 3.0, majorUnit: 0.3, numberFormatCode: "0.0", title: "Latency (M cycles)", majorGridlines: { style: "solid", fill: C.line, width: 1 }, textStyle: { typeface: FONT, fontSize: 10, fill: C.gray } },
    yAxis: { min: 16.8, max: 19.2, majorUnit: 0.4, numberFormatCode: "0.0", title: "LUT (k)", majorGridlines: { style: "solid", fill: C.line, width: 1 }, textStyle: { typeface: FONT, fontSize: 10, fill: C.gray } },
    chartFill: C.white,
    plotAreaFill: C.white,
  });
  applyPresentationChartFont(scatter, { fontFamily: FONT });
  addText(slide, "10 ns baseline", { left: 690, top: 454, width: 110, height: 18 }, { fontSize: 10, bold: true, color: C.gold });
  addText(slide, "9 ns", { left: 865, top: 385, width: 50, height: 18 }, { fontSize: 10, color: C.navy });
  addText(slide, "8 ns", { left: 995, top: 288, width: 50, height: 18 }, { fontSize: 10, color: C.navy });
  addText(slide, "7.5 ns", { left: 990, top: 321, width: 62, height: 18 }, { fontSize: 10, color: C.navy });
  addText(slide, "7 ns", { left: 1105, top: 220, width: 50, height: 18 }, { fontSize: 10, color: C.navy });

  slide.shapes.add({ geometry: "roundRect", position: { left: 60, top: 555, width: 1160, height: 92 }, fill: C.paleGold, line: { fill: "none", width: 0 }, borderRadius: 14 });
  addText(slide, "选择 clk_10ns_baseline", { left: 86, top: 574, width: 290, height: 28 }, { fontSize: 20, bold: true, color: C.navy });
  addText(slide, "1.648M cycles  ·  16.479 ms@10ns  ·  17,108 LUT", { left: 380, top: 574, width: 760, height: 28 }, { fontSize: 17, bold: true, color: C.gold });
  addText(slide, "Unroll ×2 / ×5 与 baseline 完全相同 → 局部展开不是当前瓶颈", { left: 86, top: 609, width: 1045, height: 24 }, { fontSize: 14, color: C.gray });
  addFooter(slide);
  slide.speakerNotes.textFrame.setText("来源：data/clock_dse_validated.csv、data/structural_dse_validated.csv。10 ns 的 HLS cycles 和 LUT 同时最低，且按目标周期换算的 16.479 ms 也最低。结构实验三组的 cycles/LUT/FF/BRAM/DSP 完全相同。机制解释是推断：AXI 访存、FP32 资源共享及上层调度限制了局部展开收益。 ");
}

// Slide 3 — implementation evidence and next step
{
  const slide = presentation.slides.add();
  slide.background.fill = C.light;
  addTitle(slide, "VIVADO POST-ROUTE", "10 ns 基线已经完成实现闭环", "Fully Routed；setup/hold 均有正裕量，资源与功耗有原始报告可追溯", 3);

  const timingBytes = await fs.readFile(path.join(DELIVERABLES, "figures", "vivado_timing_report_excerpt.png"));
  slide.images.add({
    blob: timingBytes,
    contentType: "image/png",
    alt: "Vivado 2022.2 timing summary 原始报告摘录，WNS +0.415 ns，WHS +0.028 ns",
    fit: "contain",
    position: { left: 52, top: 168, width: 700, height: 385 },
    geometry: "roundRect",
    borderRadius: 12,
  });

  addMetric(slide, { left: 790, top: 168, width: 200, height: 105 }, "WNS / WHS", "+0.415 / +0.028", "ns · Timing passed", C.gold);
  addMetric(slide, { left: 1010, top: 168, width: 210, height: 105 }, "LUT / Registers", "11,612 / 17,612", "21.83% / 16.55%", C.blue);
  addMetric(slide, { left: 790, top: 292, width: 200, height: 105 }, "BRAM / DSP", "37 / 5", "tiles / DSP48E1", C.blue);
  addMetric(slide, { left: 1010, top: 292, width: 210, height: 105 }, "Total On-Chip", "1.848 W", "Medium confidence", C.blue);

  slide.shapes.add({ geometry: "roundRect", position: { left: 790, top: 422, width: 430, height: 180 }, fill: C.white, line: { style: "solid", fill: C.line, width: 1 }, borderRadius: 14 });
  addText(slide, "结论与下一步", { left: 812, top: 440, width: 380, height: 28 }, { fontSize: 18, bold: true });
  addText(slide, "• 现有证据已满足成员 E 交付，停止无目标改码\n• 功耗是向量无关估算，不写成板级实测\n• 若教师强制要求改代码：权重缓存 + ARRAY_PARTITION + 并行 PE，再完整重跑 CSim/HLS/Vivado", { left: 812, top: 478, width: 382, height: 106 }, { fontSize: 13, color: C.gray, verticalAlignment: "top" });
  addFooter(slide);
  slide.speakerNotes.textFrame.setText("来源：source_reports/lenet_system_wrapper_timing_summary_routed.rpt、lenet_system_wrapper_utilization_placed.rpt、lenet_system_wrapper_power_routed.rpt、route_status.rpt。功耗 1.848 W 的 Confidence Level 为 Medium，未加载 Simulation Activity File；其中 PS7 约 1.530 W，不能描述为板级实测。 ");
}

await fs.mkdir(BUILD_DIR, { recursive: true });
await fs.mkdir(FINAL_DIR, { recursive: true });
await fs.mkdir(RENDER_DIR, { recursive: true });
const candidatePath = path.join(BUILD_DIR, "candidate.pptx");
await (await PresentationFile.exportPptx(presentation)).save(candidatePath);

const requirements = {
  explicitTotalSlideCount: 3,
  requiredNativeTableOwnerSlides: [1],
  requiredNativeChartOwnerSlides: [2],
  materializeLiteralChartWorkbooks: true,
};
const result = await finalizePresentation({
  ...requirements,
  workspaceDir: WORKSPACE,
  candidatePath,
  finalPath: FINAL_PPTX,
  pythonExecutable: RUNTIME_PYTHON,
  integrityValidatorPath: path.join(SKILL_DIR, "container_tools", "inspect_presentation_package_integrity.py"),
  layoutValidatorPath: path.join(SKILL_DIR, "container_tools", "inspect_presentation_layout_geometry.py"),
  layoutArgs: [
    "--expected-slide-size-emu", "12192000,6858000",
    "--validate-bullet-geometry",
    "--validate-heading-fit",
    "--require-native-table-slide", "1",
  ],
  requiredNativeTableOwnerSlides: [1],
  requiredNativeChartOwnerSlides: [2],
  materializeLiteralChartWorkbooks: true,
  fontPolicy: { basis: "design", families: [FONT], scriptFonts: { ea: FONT } },
  verifyArtifactToolImport: true,
  receiptPath: path.join(BUILD_DIR, "成员E_LeNet_DSE答辩.pptx.validation.json"),
});

const finalDeck = await PresentationFile.importPptx(await FileBlob.load(FINAL_PPTX));
for (let i = 0; i < finalDeck.slides.items.length; i += 1) {
  const preview = await finalDeck.export({ slide: finalDeck.slides.items[i], format: "png", scale: 1.5 });
  await fs.writeFile(path.join(RENDER_DIR, `slide-${i + 1}.png`), new Uint8Array(await preview.arrayBuffer()));
}

console.log(JSON.stringify({ final: FINAL_PPTX, validation: result?.passed ?? true, slides: finalDeck.slides.items.length }));
