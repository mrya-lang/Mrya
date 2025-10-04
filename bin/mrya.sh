#!/bin/sh

# Require exactly Python 3.10.x
PYTHON_BIN="$(command -v python3.10)"

if [ -z "$PYTHON_BIN" ]; then
    echo "Error: Python 3.10 is required but not found." >&2
    exit 1
fi

MRYA_BASE_RUN="$PYTHON_BIN ../src"

exec $MRYA_BASE_RUN/mrya_main.py "$@"
