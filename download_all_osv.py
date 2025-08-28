#!/usr/bin/env python3
"""
OSV 漏洞下载脚本
下载所有生态系统的漏洞数据并解压到指定目录
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

def download_all_osv_vulnerabilities():
    """下载所有生态系统的漏洞数据"""
    
    # 获取项目根目录
    project_root = get_project_root()
    print(f"项目根目录: {project_root}")
    
    # 设置目录
    base_target_dir = project_root / "data" / "structured" / "osv" / "zip"
    temp_dir = project_root / "temp_osv_download"
    
    # 创建必要的目录
    base_target_dir.mkdir(parents=True, exist_ok=True)
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"目标目录: {base_target_dir}")
    print(f"临时目录: {temp_dir}")
    
    # 定义文件下载路径
    ecosystems_file_url = "https://osv-vulnerabilities.storage.googleapis.com/ecosystems.txt"
    ecosystems_file_path = temp_dir / "ecosystems.txt"
    
    try:
        # 下载 ecosystems.txt 文件
        print("下载生态系统列表...")
        response = requests.get(ecosystems_file_url)
        response.raise_for_status()
        
        with open(ecosystems_file_path, 'w') as file:
            file.write(response.text)
        
        print(f"生态系统列表下载完成: {ecosystems_file_path}")
        
        # 读取每一个生态系统
        with open(ecosystems_file_path, 'r') as file:
            ecosystems = [line.strip() for line in file.readlines() if line.strip()]
        
        print(f"找到 {len(ecosystems)} 个生态系统: {', '.join(ecosystems)}")
        
        # 下载每个生态系统的ZIP文件
        for i, ecosystem in enumerate(ecosystems, 1):
            print(f"\n[{i}/{len(ecosystems)}] 处理生态系统: {ecosystem}")
            
            zip_url = f"https://osv-vulnerabilities.storage.googleapis.com/{ecosystem}/all.zip"
            zip_file_path = temp_dir / f"{ecosystem}-all.zip"
            target_dir = base_target_dir / ecosystem
            
            # 创建生态系统目录
            target_dir.mkdir(parents=True, exist_ok=True)
            
            try:
                print(f"  下载 {ecosystem} 漏洞数据...")
                response = requests.get(zip_url, stream=True)
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
                                print(f"\r  下载进度: {progress:.1f}% ({downloaded_size}/{total_size} bytes)", end='')
                
                print(f"\n  下载完成: {zip_file_path}")
                
                # 解压ZIP文件到目标目录
                print(f"  解压 {ecosystem} 漏洞数据...")
                with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                    # 获取ZIP文件中的文件列表
                    file_list = zip_ref.namelist()
                    total_files = len(file_list)
                    
                    for j, file_name in enumerate(file_list):
                        zip_ref.extract(file_name, target_dir)
                        progress = (j + 1) / total_files * 100
                        print(f"\r  解压进度: {progress:.1f}% ({j+1}/{total_files} 文件)", end='')
                
                print(f"\n  解压完成，文件已保存到: {target_dir}")
                
                # 统计解压后的文件数量
                json_files = list(target_dir.glob("*.json"))
                print(f"  共解压了 {len(json_files)} 个JSON漏洞文件")
                
                # 清理临时ZIP文件
                if zip_file_path.exists():
                    zip_file_path.unlink()
                    print(f"  临时ZIP文件已删除")
                    
            except requests.exceptions.RequestException as e:
                print(f"  下载 {ecosystem} 失败: {e}")
                continue
            except zipfile.BadZipFile as e:
                print(f"  解压 {ecosystem} 失败: {e}")
                continue
            except Exception as e:
                print(f"  处理 {ecosystem} 时发生错误: {e}")
                continue
        
        # 清理临时文件
        if ecosystems_file_path.exists():
            ecosystems_file_path.unlink()
            print("\n生态系统列表文件已删除")
        
        if temp_dir.exists() and not any(temp_dir.iterdir()):
            temp_dir.rmdir()
            print("临时目录已删除")
            
        print("\n所有生态系统漏洞数据下载和解压完成！")
        
        # 统计总文件数
        total_json_files = len(list(base_target_dir.glob("**/*.json")))
        print(f"总共处理了 {total_json_files} 个JSON漏洞文件")
        
    except requests.exceptions.RequestException as e:
        print(f"下载生态系统列表失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"发生错误: {e}")
        sys.exit(1)

def main():
    """主函数"""
    print("=" * 80)
    print("OSV 漏洞下载脚本 - 所有生态系统")
    print("=" * 80)
    
    try:
        download_all_osv_vulnerabilities()
        print("脚本执行完成！")
    except KeyboardInterrupt:
        print("\n用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"脚本执行失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
