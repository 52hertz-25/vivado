import fs from "node:fs/promises";
import path from "node:path";
import { chromium } from "playwright";

const projectDir = path.resolve(import.meta.dirname, "../..");
const sourceDir = path.join(projectDir, "member_e_deliverables", "source_reports");
const outputDir = path.join(projectDir, "member_e_deliverables", "figures");

function escapeHtml(value) {
  return value.replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;");
}

async function extract(file, ranges) {
  const lines = (await fs.readFile(path.join(sourceDir, file), "utf8")).split(/\r?\n/);
  return ranges.flatMap(([first, last]) => lines.slice(first - 1, last)).join("\n");
}

function pageHtml(title, subtitle, source, excerpt, chips) {
  const chipHtml = chips.map(({ label, value, tone = "blue" }) =>
    `<div class="chip ${tone}"><span>${escapeHtml(label)}</span><strong>${escapeHtml(value)}</strong></div>`
  ).join("");
  return `<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><style>
    *{box-sizing:border-box} body{margin:0;background:#eef2f7;color:#152033;font-family:"Microsoft YaHei",Arial,sans-serif}
    main{width:1500px;height:820px;margin:0 auto;padding:48px 58px;background:white}
    .eyebrow{color:#44739d;font-size:18px;font-weight:700;letter-spacing:.08em;text-transform:uppercase}
    h1{font-size:40px;margin:10px 0 6px;line-height:1.2}.subtitle{font-size:20px;color:#55657a;margin-bottom:24px}
    .chips{display:flex;gap:14px;margin:0 0 22px}.chip{min-width:190px;padding:13px 17px;border-radius:8px;background:#e8f0f8;border-left:5px solid #2e6797}
    .chip.gold{background:#fbf2dc;border-color:#c99116}.chip span{display:block;font-size:13px;color:#607188}.chip strong{display:block;font-size:26px;margin-top:3px}
    .source{font-size:14px;color:#64748b;margin:0 0 8px}.report{height:520px;overflow:hidden;border:1px solid #b7c3d1;border-radius:7px;background:#0f1724;color:#dbe5ef;padding:20px 24px;font:17px/1.34 Consolas,"Courier New",monospace;white-space:pre-wrap}
    footer{position:absolute;bottom:22px;color:#708096;font-size:13px}
  </style></head><body><main><div class="eyebrow">Vivado 2022.2 · report excerpt</div><h1>${escapeHtml(title)}</h1>
  <div class="subtitle">${escapeHtml(subtitle)}</div><div class="chips">${chipHtml}</div>
  <div class="source">原始文件：${escapeHtml(source)}</div><pre class="report">${escapeHtml(excerpt)}</pre>
  </main></body></html>`;
}

const items = [
  {
    output: "vivado_timing_report_excerpt.png",
    title: "布线后时序满足约束",
    subtitle: "所有 setup/hold 端点均无负裕量",
    source: "lenet_system_wrapper_timing_summary_routed.rpt",
    ranges: [[131, 162]],
    chips: [{ label: "WNS", value: "+0.415 ns", tone: "gold" }, { label: "WHS", value: "+0.028 ns" }, { label: "Timing", value: "PASSED" }],
  },
  {
    output: "vivado_resource_report_excerpt.png",
    title: "布线前后资源规模可控",
    subtitle: "报告口径为 Vivado placed utilization；BRAM 使用 tile 计数",
    source: "lenet_system_wrapper_utilization_placed.rpt",
    ranges: [[29, 43], [102, 123]],
    chips: [{ label: "Slice LUT", value: "11,612", tone: "gold" }, { label: "Registers", value: "17,612" }, { label: "BRAM / DSP", value: "37 / 5" }],
  },
  {
    output: "vivado_power_report_excerpt.png",
    title: "片上功耗估算为 1.848 W",
    subtitle: "未加载仿真活动文件，属于 Medium-confidence 向量无关估算，不等同于板级实测",
    source: "lenet_system_wrapper_power_routed.rpt",
    ranges: [[29, 68]],
    chips: [{ label: "Total On-Chip", value: "1.848 W", tone: "gold" }, { label: "Confidence", value: "Medium" }, { label: "PS7", value: "1.530 W" }],
  },
];

await fs.mkdir(outputDir, { recursive: true });
const browser = await chromium.launch({ headless: true, executablePath: "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe" });
try {
  const page = await browser.newPage({ viewport: { width: 1500, height: 820 }, deviceScaleFactor: 1.4 });
  for (const item of items) {
    const excerpt = await extract(item.source, item.ranges);
    await page.setContent(pageHtml(item.title, item.subtitle, item.source, excerpt, item.chips), { waitUntil: "load" });
    await page.screenshot({ path: path.join(outputDir, item.output), fullPage: false });
  }
} finally {
  await browser.close();
}

console.log(`Generated ${items.length} Vivado report evidence images in ${outputDir}`);
