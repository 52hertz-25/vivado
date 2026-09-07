#!/bin/bash
# Source this file from a launcher in the project root.
if [ -n "${PYTHON_BIN:-}" ]; then
    :
elif [ -n "${CONDA_PREFIX:-}" ] && [ "${CONDA_DEFAULT_ENV:-}" = "xgb_env" ]; then
    PYTHON_BIN="$CONDA_PREFIX/bin/python"
else
    for prefix in "$HOME/miniforge3" "$HOME/miniconda3" "$HOME/anaconda3"; do
        if [ -x "$prefix/envs/xgb_env/bin/python" ]; then
            PYTHON_BIN="$prefix/envs/xgb_env/bin/python"
            break
        fi
    done
fi
if [ -z "${PYTHON_BIN:-}" ]; then
    echo '请激活 xgb_env，或用 PYTHON_BIN 指定 Python 路径。' >&2
    exit 1
fi
