#!/bin/bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$PROJECT_ROOT/scripts/python_env.sh"
OUTPUT_ROOT="$PROJECT_ROOT/results/robustness"

if [ -d "$OUTPUT_ROOT" ] && [ "$(find "$OUTPUT_ROOT" -mindepth 1 -print -quit)" ]; then
    OUTPUT_ROOT="$PROJECT_ROOT/results/robustness_$(date +%Y%m%d_%H%M%S)_$$"
fi

"$PYTHON_BIN" "$PROJECT_ROOT/work/evaluate_robustness.py" \
    --robustness-root "$PROJECT_ROOT/data/robustness" \
    --output "$OUTPUT_ROOT" \
    --device "${DEVICE:-mps}"

echo
echo "鲁棒性评估完成：$OUTPUT_ROOT"
open "$OUTPUT_ROOT"
