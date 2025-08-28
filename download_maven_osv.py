#!/usr/bin/env python3
"""
Maven OSV 漏洞下载脚本
专门用于下载Maven生态系统的漏洞数据并解压到指定目录
"""

import os
import zipfile
import requests
import sys
from pathlib import Path

def get_project_root():
    """获取项目根目录"""
    current_file = Path(__file__).resolve()
    # 从当前文件位置向上查找，直到找到包含ThreatSync目录的根目录
    current_dir = current_file.parent
    while current_dir.parent != current_dir:
        if (current_dir / "ThreatSync").exists() and (current_dir / "README.md").exists():
            return current_dir
        current_dir = current_dir.parent
    
    # 如果没找到，使用相对路径
    return current_file.parent.parent.parent

def download_maven_vulnerabilities():
    """下载Maven生态系统的漏洞数据"""
    
    # 获取项目根目录
    project_root = get_project_root()
    print(f"项目根目录: {project_root}")
    
    # 设置目标目录
    target_dir = project_root / "data" / "structured" / "osv" / "zip" / "maven"
    temp_dir = project_root / "temp_maven_download"
    
    # 创建必要的目录
    target_dir.mkdir(parents=True, exist_ok=True)
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"目标目录: {target_dir}")
    print(f"临时目录: {temp_dir}")
    
    # Maven生态系统的ZIP文件URL
    maven_zip_url = "https://osv-vulnerabilities.storage.googleapis.com/Maven/all.zip"
    zip_file_path = temp_dir / "maven-all.zip"
    
    try:
        print("开始下载Maven漏洞数据...")
        print(f"下载URL: {maven_zip_url}")
        
        # 下载ZIP文件
        response = requests.get(maven_zip_url, stream=True)
        response.raise_for_status()
        
        # 获取文件大小
        total_size = int(response.headers.get('content-length', 0))
        downloaded_size = 0
        
        with open(zip_file_path, 'wb') as zip_file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    zip_file.write(chunk)
                    downloaded_size += len(chunk)
                    if total_size > 0:
                        progress = (downloaded_size / total_size) * 100
                        print(f"\r下载进度: {progress:.1f}% ({downloaded_size}/{total_size} bytes)", end='')
        
        print(f"\n下载完成: {zip_file_path}")
        
        # 解压ZIP文件到目标目录
        print("开始解压Maven漏洞数据...")
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            # 获取ZIP文件中的文件列表
            file_list = zip_ref.namelist()
            total_files = len(file_list)
            
            for i, file_name in enumerate(file_list):
                zip_ref.extract(file_name, target_dir)
                progress = (i + 1) / total_files * 100
                print(f"\r解压进度: {progress:.1f}% ({i+1}/{total_files} 文件)", end='')
        
        print(f"\n解压完成，文件已保存到: {target_dir}")
        
        # 统计解压后的文件数量
        json_files = list(target_dir.glob("*.json"))
        print(f"共解压了 {len(json_files)} 个JSON漏洞文件")
        
        # 清理临时文件
        if zip_file_path.exists():
            zip_file_path.unlink()
            print("临时ZIP文件已删除")
        
        if temp_dir.exists() and not any(temp_dir.iterdir()):
            temp_dir.rmdir()
            print("临时目录已删除")
            
    except requests.exceptions.RequestException as e:
        print(f"下载失败: {e}")
        sys.exit(1)
    except zipfile.BadZipFile as e:
        print(f"ZIP文件损坏: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"发生错误: {e}")
        sys.exit(1)

def main():
    """主函数"""
    print("=" * 60)
    print("Maven OSV 漏洞下载脚本")
    print("=" * 60)
    
    try:
        download_maven_vulnerabilities()
        print("Maven漏洞数据下载和解压完成！")
    except KeyboardInterrupt:
        print("\n用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"脚本执行失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
