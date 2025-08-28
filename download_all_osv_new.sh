#!/bin/bash

# OSV 漏洞下载脚本 (Shell版本)
# 下载所有生态系统的漏洞数据

echo "================================================================================"
echo "OSV 漏洞下载脚本 - 所有生态系统"
echo "================================================================================"

# 获取脚本所在目录的父目录（项目根目录）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "项目根目录: $PROJECT_ROOT"

# 设置目录路径
BASE_TARGET_DIR="$PROJECT_ROOT/data/structured/osv/zip"
TEMP_DIR="$PROJECT_ROOT/temp_osv_download"

# 创建必要的目录
mkdir -p "$BASE_TARGET_DIR"
mkdir -p "$TEMP_DIR"

echo "目标目录: $BASE_TARGET_DIR"
echo "临时目录: $TEMP_DIR"

# 检查curl或wget是否可用
if command -v curl &> /dev/null; then
    DOWNLOAD_CMD="curl"
elif command -v wget &> /dev/null; then
    DOWNLOAD_CMD="wget"
else
    echo "错误: 需要安装curl或wget来下载文件"
    exit 1
fi

# 检查unzip是否可用
if ! command -v unzip &> /dev/null; then
    echo "错误: 需要安装unzip来解压文件"
    exit 1
fi

# 生态系统列表文件URL
ECOSYSTEMS_URL="https://osv-vulnerabilities.storage.googleapis.com/ecosystems.txt"
ECOSYSTEMS_FILE="$TEMP_DIR/ecosystems.txt"

echo "下载生态系统列表..."

# 下载生态系统列表
if [ "$DOWNLOAD_CMD" = "curl" ]; then
    curl -L -o "$ECOSYSTEMS_FILE" "$ECOSYSTEMS_URL"
    DOWNLOAD_STATUS=$?
else
    wget -O "$ECOSYSTEMS_FILE" "$ECOSYSTEMS_URL"
    DOWNLOAD_STATUS=$?
fi

# 检查下载是否成功
if [ $DOWNLOAD_STATUS -ne 0 ]; then
    echo "下载生态系统列表失败"
    exit 1
fi

echo "生态系统列表下载完成: $ECOSYSTEMS_FILE"

# 读取生态系统列表
readarray -t ECOSYSTEMS < "$ECOSYSTEMS_FILE"

# 移除空行
VALID_ECOSYSTEMS=()
for ecosystem in "${ECOSYSTEMS[@]}"; do
    ecosystem=$(echo "$ecosystem" | tr -d '\r\n' | xargs)
    if [ -n "$ecosystem" ]; then
        VALID_ECOSYSTEMS+=("$ecosystem")
    fi
done

echo "找到 ${#VALID_ECOSYSTEMS[@]} 个生态系统: ${VALID_ECOSYSTEMS[*]}"

# 处理每个生态系统
for i in "${!VALID_ECOSYSTEMS[@]}"; do
    ecosystem="${VALID_ECOSYSTEMS[$i]}"
    current=$((i + 1))
    total=${#VALID_ECOSYSTEMS[@]}
    
    echo ""
    echo "[$current/$total] 处理生态系统: $ecosystem"
    
    ZIP_URL="https://osv-vulnerabilities.storage.googleapis.com/$ecosystem/all.zip"
    ZIP_FILE="$TEMP_DIR/$ecosystem-all.zip"
    TARGET_DIR="$BASE_TARGET_DIR/$ecosystem"
    
    # 创建生态系统目录
    mkdir -p "$TARGET_DIR"
    
    echo "  下载 $ecosystem 漏洞数据..."
    echo "  下载URL: $ZIP_URL"
    
    # 下载ZIP文件
    if [ "$DOWNLOAD_CMD" = "curl" ]; then
        curl -L --progress-bar -o "$ZIP_FILE" "$ZIP_URL"
        DOWNLOAD_STATUS=$?
    else
        wget --progress=bar:force -O "$ZIP_FILE" "$ZIP_URL"
        DOWNLOAD_STATUS=$?
    fi
    
    # 检查下载是否成功
    if [ $DOWNLOAD_STATUS -ne 0 ]; then
        echo "  下载 $ecosystem 失败"
        continue
    fi
    
    echo "  下载完成: $ZIP_FILE"
    
    # 获取文件大小
    if [ -f "$ZIP_FILE" ]; then
        FILE_SIZE=$(stat -c%s "$ZIP_FILE" 2>/dev/null || stat -f%z "$ZIP_FILE" 2>/dev/null || echo "未知")
        echo "  文件大小: $FILE_SIZE bytes"
    fi
    
    # 解压文件
    echo "  解压 $ecosystem 漏洞数据..."
    unzip -q "$ZIP_FILE" -d "$TARGET_DIR"
    
    if [ $? -eq 0 ]; then
        echo "  解压完成，文件已保存到: $TARGET_DIR"
        
        # 统计JSON文件数量
        JSON_COUNT=$(find "$TARGET_DIR" -name "*.json" | wc -l)
        echo "  共解压了 $JSON_COUNT 个JSON漏洞文件"
        
        # 清理临时ZIP文件
        rm -f "$ZIP_FILE"
        echo "  临时ZIP文件已删除"
    else
        echo "  解压 $ecosystem 失败"
    fi
done

# 清理临时文件
rm -f "$ECOSYSTEMS_FILE"
echo ""
echo "生态系统列表文件已删除"

# 如果临时目录为空则删除
if [ -z "$(ls -A "$TEMP_DIR")" ]; then
    rmdir "$TEMP_DIR"
    echo "临时目录已删除"
fi

echo ""
echo "所有生态系统漏洞数据下载和解压完成！"

# 统计总JSON文件数
TOTAL_JSON_COUNT=$(find "$BASE_TARGET_DIR" -name "*.json" | wc -l)
echo "总共处理了 $TOTAL_JSON_COUNT 个JSON漏洞文件"

echo "脚本执行完成！"
