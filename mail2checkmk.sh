#!/usr/bin/env bash
set -e

# check if the virtualenv exists
if [ ! -d ".venv/bin/" ]; then
    echo "Virtual environment not found, aborting."
    exit 1
fi

# check if the main python file exists
if [ ! -f "./main.py" ]; then
    echo "Python script not found, aborting."
    exit 1
fi

# Run mail2checkmk
exec .venv/bin/python main.py
