#!/usr/bin/env bash
set -e

# check if the virtualenv exists
if [ ! -d "/opt/Mail2CheckMk/.venv/bin/" ]; then
    echo "Virtual environment not found, aborting."
    exit 1
fi

# check if the main python file exists
if [ ! -f "/opt/Mail2CheckMk/main.py" ]; then
    echo "Python script not found, aborting."
    exit 1
fi

# Run mail2checkmk
exec /opt/Mail2CheckMk/.venv/bin/python /opt/Mail2CheckMk/main.py
