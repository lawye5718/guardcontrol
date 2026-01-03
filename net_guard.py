#!/usr/bin/env python3
import time
import subprocess
import os
import sys

# ================= 🚫 绝对黑名单 =================
# 这里列出的域名将被永久、死板、毫无商量余地地指向本地回环地址
# 无论你是否使用豆包、Safari、Chrome，只要走系统 DNS，全部"无法连接"
BLOCKED_DOMAINS = [
    "playok.com",
    "www.playok.com",
    # 你以后可以在这里加新的，比如 "gambling.com"
]
# ===============================================

def enforce_hosts():
    """
    守护 hosts 文件。
    如果不包含黑名单域名，就立即追加写入并刷新 DNS。
    """
    try:
        # 读取当前 hosts
        hosts_path = "/etc/hosts"
        if not os.path.exists(hosts_path):
            return

        with open(hosts_path, "r") as f:
            content = f.read()
        
        need_refresh = False
        lines_to_add = []
        
        for domain in BLOCKED_DOMAINS:
            # 规则：必须指向 127.0.0.1
            entry = f"127.0.0.1 {domain}"
            
            # 如果文件中找不到这行配置
            if entry not in content:
                lines_to_add.append(entry)
                need_refresh = True
        
        if need_refresh:
            # 使用追加模式 'a'
            with open(hosts_path, "a") as f:
                f.write("\n# NetGuard Absolute Block\n")
                for line in lines_to_add:
                    f.write(f"{line}\n")
            
            print(f"已补刀: {lines_to_add}")
            
            # 强制刷新 macOS DNS 缓存
            subprocess.run(["killall", "-HUP", "mDNSResponder"], stderr=subprocess.DEVNULL)
            
    except Exception as e:
        # 即使报错也不要崩溃，保持沉默
        print(f"Error: {e}")

def main():
    # 确认以 Root 运行 (由 LaunchDaemon 保证)
    if os.geteuid() != 0:
        print("Error: Must run as root.")
        sys.exit(1)

    print("Simple Guardian is watching...")
    
    while True:
        enforce_hosts()
        # 每 5 秒巡逻一次
        time.sleep(5)

if __name__ == "__main__":
    main()
