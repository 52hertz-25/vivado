#!/bin/bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$PROJECT_ROOT/scripts/python_env.sh"
OUTPUT_ROOT="$PROJECT_ROOT/data/robustness"

if [ -d "$OUTPUT_ROOT" ] && [ "$(find "$OUTPUT_ROOT" -mindepth 1 -print -quit)" ]; then
    OUTPUT_ROOT="$PROJECT_ROOT/data/robustness_$(date +%Y%m%d_%H%M%S)_$$"
fi

"$PYTHON_BIN" "$PROJECT_ROOT/src/generate_robustness.py" \
    --input "$PROJECT_ROOT/data/preprocessed/dataset/processed_28x28" \
    --output "$OUTPUT_ROOT"

echo
echo "扰动数据已生成：$OUTPUT_ROOT"
open "$OUTPUT_ROOT"
