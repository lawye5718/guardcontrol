#!/usr/bin/env python3
import time
import datetime
import os
import json
import subprocess
import sys

# ================= ⚠️ 绝对规则 (硬编码区) ⚠️ =================
# 你可以在这里改，但是一旦部署并锁定，想要改回来就必须请朋友解锁
# 格式: "域名": 每日允许秒数 (0 代表彻底禁止)
HARD_RULES = {
    "playok.com": 0,
    "x.com": 3600,   # 每天 1 小时
    "twitter.com": 3600 # 包含推特的主域名
}

# 存储每天使用时间的文件
USAGE_FILE = "/var/tmp/net_guard_usage.json"
# 外部可扩展配置 (可选)
EXTRA_CONFIG = "/usr/local/etc/net_guard_config.json"
# ==========================================================

def get_today_str():
    return datetime.datetime.now().strftime("%Y-%m-%d")

def load_usage():
    """读取今日已用时间"""
    default_data = {"date": get_today_str(), "usage": {}}
    if not os.path.exists(USAGE_FILE):
        return default_data
    try:
        with open(USAGE_FILE, 'r') as f:
            data = json.load(f)
            # 如果日期变了，重置计数
            if data.get("date") != get_today_str():
                return default_data
            return data
    except:
        return default_data

def save_usage(data):
    """保存时间"""
    with open(USAGE_FILE, 'w') as f:
        json.dump(data, f)

def get_active_browser_url():
    """
    使用 AppleScript 获取当前 Chrome/Safari/Edge 的活动标签页 URL。
    这种方法无视 VPN，直接看你在看什么。
    """
    script = """
    tell application "System Events"
        set frontApp to name of first application process whose frontmost is true
    end tell
    
    if frontApp is "Google Chrome" or frontApp is "Microsoft Edge" or frontApp is "Brave Browser" then
        tell application frontApp
            return URL of active tab of front window
        end tell
    else if frontApp is "Safari" then
        tell application "Safari"
            return URL of front document
        end tell
    else
        return ""
    end if
    """
    try:
        result = subprocess.check_output(["osascript", "-e", script], stderr=subprocess.DEVNULL)
        return result.decode('utf-8').strip()
    except:
        return ""

def kill_browser_tab(browser_name):
    """强制关闭标签页的 AppleScript"""
    script = f"""
    tell application "{browser_name}"
        close active tab of front window
        display notification "已拦截违规访问！" with title "NetGuard"
    end tell
    """
    subprocess.run(["osascript", "-e", script], stderr=subprocess.DEVNULL)

def enforce_hosts(domains):
    """
    非 Clash 环境下的底层拦截：写入 Hosts
    """
    try:
        with open("/etc/hosts", "r") as f:
            content = f.read()
        
        need_refresh = False
        with open("/etc/hosts", "a") as f:
            for domain in domains:
                # 简单的检查，防止重复写入过多
                if f"127.0.0.1 {domain}" not in content:
                    f.write(f"\n127.0.0.1 {domain}\n")
                    f.write(f"\n127.0.0.1 www.{domain}\n")
                    need_refresh = True
        
        if need_refresh:
            subprocess.run(["killall", "-HUP", "mDNSResponder"], stderr=subprocess.DEVNULL)
    except:
        pass

def main():
    print("Guardian started monitoring...")
    
    # 1. 先把 playok 永久写入 hosts (双重保险)
    enforce_hosts(["playok.com"])

    while True:
        try:
            current_url = get_active_browser_url()
            usage_data = load_usage()
            current_usage = usage_data["usage"]
            
            # 识别当前使用的是哪个浏览器 (用于关闭标签)
            # 这里简化处理，实际可以通过 AppleScript 同时返回 App 名称
            # 假设用户主要用 Chrome/Safari，这里只做 URL 匹配
            
            check_interval = 5 # 每5秒检查一次
            
            # --- 规则检查 ---
            
            # 1. 硬编码规则检查
            for domain, limit in HARD_RULES.items():
                if domain in current_url:
                    used = current_usage.get(domain, 0)
                    
                    if limit == 0: # 绝对禁止
                        # 立即尝试关闭 Chrome/Safari 标签
                        kill_browser_tab("Google Chrome") 
                        kill_browser_tab("Safari")
                        print(f"Blocked {domain}")
                    
                    elif used >= limit: # 时间耗尽
                        kill_browser_tab("Google Chrome")
                        kill_browser_tab("Safari")
                        print(f"Time limit exceeded for {domain}")
                    
                    else:
                        # 还在允许时间内，增加计数
                        current_usage[domain] = used + check_interval
                        print(f"{domain} usage: {used}s / {limit}s")

            # --- 保存数据 ---
            usage_data["usage"] = current_usage
            save_usage(usage_data)
            
        except Exception as e:
            # 捕获所有异常，防止进程崩溃退出
            print(f"Error: {e}")
        
        time.sleep(5)

if __name__ == "__main__":
    main()
