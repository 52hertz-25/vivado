#!/bin/bash
set -eu
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$PROJECT_DIR/scripts/python_env.sh"
INPUT_FILE="$PROJECT_DIR/data/raw/example/example.jpg"
OUTPUT_DIR="$PROJECT_DIR/data/preprocessed/example_$(date +%Y%m%d_%H%M%S)_$$"
echo '预处理 data/raw/example/example.jpg 中的 4×4 混合数字示例。'
echo '标签顺序：0,1,2,3,4,5,6,7,8,9,0,1,2,3,4,5。'
result_code=0
if "$PYTHON_BIN" -u "$PROJECT_DIR/src/preprocess.py" "$INPUT_FILE" --labels 0,1,2,3,4,5,6,7,8,9,0,1,2,3,4,5 --output "$OUTPUT_DIR"; then
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
