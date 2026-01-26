#!/bin/bash

# 使用ps和grep命令查找包含'uvicorn'的进程
PROCESS=$(ps aux | grep 'streamlit' | grep -v grep)

# 检查是否找到了进程
if [[ -n $PROCESS ]]; then
    # 使用awk提取进程ID
    PID=$(echo $PROCESS | awk '{print $2}')
    echo "Found the process with PID: $PID"
    
    # 使用kill命令终止进程
    kill -9 $PID
    
    # 检查进程是否已经终止
    if [[ $? -eq 0 ]]; then
        echo "Process $PID has been terminated."
    else
        echo "Failed to terminate the process $PID."
    fi
else
    echo "No process containing 'streamlit' is currently running."
fi
