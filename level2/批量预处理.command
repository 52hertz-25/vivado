#!/bin/bash
set -eu
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$PROJECT_DIR/scripts/python_env.sh"
INPUT_DIR="$PROJECT_DIR/data/raw/dataset"
OUTPUT_DIR="$PROJECT_DIR/data/preprocessed/dataset_$(date +%Y%m%d_%H%M%S)_$$"
echo '把每页同一个数字的照片放进 data/raw/dataset。'
echo '文件名例如 0_01.jpg、0_02.jpg、1_01.jpg；每页 4 行 × 4 列，16 个数字。'
result_code=0
if "$PYTHON_BIN" -u "$PROJECT_DIR/src/preprocess.py" "$INPUT_DIR" --output "$OUTPUT_DIR"; then
  open "$OUTPUT_DIR/review" || echo "请手动打开：$OUTPUT_DIR/review"
  echo '预处理完成。请检查预览图及异常提示；提取成功不等于模型识别正确。'
else
  result_code=$?
  echo '未完成，请查看上面的提示；已经生成的部分结果会保留。'
fi
if [ -t 0 ]; then
  read -r -p '按回车关闭窗口。' REPLY || true
fi
exit "$result_code"
