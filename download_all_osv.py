import os
import requests

# 定义文件下载路径
ECOSYSTEMS_FILE = "https://osv-vulnerabilities.storage.googleapis.com/ecosystems.txt"

# 下载 ecosystems.txt 文件
response = requests.get(ECOSYSTEMS_FILE)
if response.status_code == 200:
    with open('ecosystems.txt', 'w') as file:
        file.write(response.text)
else:
    print("Failed to download ecosystems.txt")
    exit(1)

# 创建一个目录来存储下载的文件
os.makedirs('osv_data', exist_ok=True)

# 读取每一个生态系统并下载对应的 ZIP 文件
with open('ecosystems.txt', 'r') as file:
    ecosystems = file.readlines()

for ecosystem in ecosystems:
    ecosystem = ecosystem.strip()
    if ecosystem:
        print(f"Downloading vulnerabilities for {ecosystem}...")
        zip_url = f"https://osv-vulnerabilities.storage.googleapis.com/{ecosystem}/all.zip"
        response = requests.get(zip_url)
        if response.status_code == 200:
            with open(f'osv_data/{ecosystem}-all.zip', 'wb') as zip_file:
                zip_file.write(response.content)
        else:
            print(f"Failed to download {ecosystem}-all.zip")

print("Downloads completed.")