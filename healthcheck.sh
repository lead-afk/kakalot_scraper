#!/bin/sh

sleep 2

FILE_PATH="./heartbeat"
MAX_MINUTES=15

if [ ! -f "$FILE_PATH" ]; then
    echo "File missing"
    exit 1
fi

# seconds since last modification
LAST_MODIFIED=$(stat -c %Y "$FILE_PATH")
NOW=$(date +%s)
AGE_SECONDS=$((NOW - LAST_MODIFIED))
AGE_MINUTES=$((AGE_SECONDS / 60))

if [ "$AGE_MINUTES" -gt "$MAX_MINUTES" ]; then
    echo "File too old: $AGE_MINUTES minutes"
    exit 1
fi

echo "OK: $AGE_MINUTES minutes old"
exit 0
