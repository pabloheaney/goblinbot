#!/bin/bash

echo "正在啟動 Display Bot..."
python main.py &

echo "正在啟動 Admin Bot..."
python admin_bot.py &

wait -n

exit $?
