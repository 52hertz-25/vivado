#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""解析 Vitis HLS csynth.rpt，汇总成员 D 各版本 Conv2 性能与资源数据。
用法：python parse_csynth.py [提交目录]
默认读取当前脚本同级的提交目录结构。D0 数据来自 results/pe_experiments.csv。
"""
import re
import os
import csv
import json
import sys


def parse_csynth(path):
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        txt = f.read()
    data = {'file': os.path.basename(path)}
    m = re.search(r'\|ap_clk\s*\|\s*([\d.]+) ns\s*\|\s*([\d.]+) ns\|', txt)
    if m:
        data['target_ns'] = m.group(1)
        data['estimated_ns'] = m.group(2)
    m = re.search(r'\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*([\d.]+)\s*(ms|ns)\s*\|\s*([\d.]+)\s*(ms|ns)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\w+)\|', txt)
    if m:
        data['latency_min'] = int(m.group(1))
        data['latency_max'] = int(m.group(2))
        data['interval_min'] = int(m.group(7))
        data['interval_max'] = int(m.group(8))
        data['pipeline'] = m.group(9)
    m = re.search(r'\|Total\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\|', txt)
    if m:
        data['bram'] = int(m.group(1))
        data['dsp'] = int(m.group(2))
        data['ff'] = int(m.group(3))
        data['lut'] = int(m.group(4))
    return data


def main():
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    root = sys.argv[1] if len(sys.argv) > 1 else os.path.normpath(os.path.join(scripts_dir, '..'))
    reports = os.path.join(root, 'results', 'synthesis_reports')
    out = []
    baseline_lat = 3405954
    for cfg in ['D1', 'D2', 'D3', 'D4', 'D5']:
        rpt = os.path.join(reports, cfg, 'lenet_conv2_top_csynth.rpt')
        if os.path.exists(rpt):
            d = parse_csynth(rpt)
            d['config'] = cfg
            d['speedup'] = round(baseline_lat / d['latency_min'], 2)
            out.append(d)
    # D0 来自实验表
    csv_path = os.path.join(root, 'results', 'pe_experiments.csv')
    if os.path.exists(csv_path):
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            for row in csv.DictReader(f):
                if row['版本'] == 'D0':
                    out.insert(0, {'config': 'D0', 'latency_min': int(row['Latency(cycles)']),
                                   'dsp': int(row['DSP48E']), 'bram': int(row['BRAM_18K']),
                                   'ff': int(row['FF']), 'lut': int(row['LUT']),
                                   'estimated_ns': row['估计时钟(ns)'], 'speedup': 1.0})
    for d in out:
        print(json.dumps(d, ensure_ascii=False))


if __name__ == '__main__':
    main()
