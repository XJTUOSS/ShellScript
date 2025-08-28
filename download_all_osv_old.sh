#!/bin/bash

# 定义文件下载路径
ECOSYSTEMS_FILE="https://osv-vulnerabilities.storage.googleapis.com/ecosystems.txt"

# 下载 ecosystems.txt 文件
wget -O ecosystems.txt $ECOSYSTEMS_FILE

# 检查 ecosystems.txt 文件是否成功下载
if [ ! -f ecosystems.txt ]; then
    echo "Failed to download ecosystems.txt"
    exit 1
fi

# 创建一个目录来存储下载的文件
mkdir -p osv_data
cd osv_data

# 读取每一个生态系统并下载对应的 ZIP 文件
while IFS= read -r ecosystem
do
    echo "Downloading vulnerabilities for $ecosystem..."
    wget -O "${ecosystem}-all.zip" "https://osv-vulnerabilities.storage.googleapis.com/${ecosystem}/all.zip"
done < ../ecosystems.txt

echo "Downloads completed."
