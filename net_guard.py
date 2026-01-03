#!/usr/bin/env python3
import time
import datetime
import os
import json
import subprocess
import sys

# ================= ⚠️ 绝对规则 (硬编码区) ⚠️ =================
# 注意：每日限额 3600秒 = 1小时。
# 虽然你要求每周7小时，但按"每日1小时"执行更符合代码逻辑（每天重置），
# 也能防止你在周一一天就把7小时全用光的"暴饮暴食"行为。
HARD_RULES = {
    "playok.com": 0,
    "x.com": 3600,   # 每天 1 小时
    "twitter.com": 3600
}

USAGE_FILE = "/var/tmp/net_guard_usage.json"
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
            if data.get("date") != get_today_str():
                return default_data
            return data
    except:
        return default_data

def save_usage(data):
    """保存时间"""
    try:
        with open(USAGE_FILE, 'w') as f:
            json.dump(data, f)
    except:
        pass

def load_extra_rules():
    """读取外部可配置的规则"""
    if not os.path.exists(EXTRA_CONFIG):
        return {}
    try:
        with open(EXTRA_CONFIG, 'r') as f:
            return json.load(f)
    except:
        return {}

def get_active_browser_url():
    # AppleScript 脚本保持不变
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
        # 注意：作为 root 运行时，AppleScript 可能会因为无法交互而失败
        # 这里不做复杂处理，依赖用户授予 Terminal/程序 辅助功能权限
        result = subprocess.check_output(["osascript", "-e", script], stderr=subprocess.DEVNULL)
        return result.decode('utf-8').strip()
    except:
        return ""

def kill_browser_tab(browser_name):
    script = f"""
    tell application "{browser_name}"
        close active tab of front window
        display notification "已拦截违规访问！" with title "NetGuard"
    end tell
    """
    subprocess.run(["osascript", "-e", script], stderr=subprocess.DEVNULL)

def enforce_hosts(domains):
    try:
        with open("/etc/hosts", "r") as f:
            content = f.read()
        
        need_refresh = False
        with open("/etc/hosts", "a") as f:
            for domain in domains:
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
    
    # 将硬编码的禁止域名写入 hosts
    block_list = [d for d, limit in HARD_RULES.items() if limit == 0]
    enforce_hosts(block_list)

    while True:
        try:
            current_url = get_active_browser_url()
            usage_data = load_usage()
            current_usage = usage_data["usage"]
            
            # --- 合并规则 ---
            # 优先使用硬编码规则，然后合并外部规则
            extra_rules = load_extra_rules()
            # 合并字典，HARD_RULES 优先级更高（如果重复，不会被覆盖）
            all_rules = extra_rules.copy()
            all_rules.update(HARD_RULES)
            
            check_interval = 5 
            
            triggered_domains = []
            
            for domain, limit in all_rules.items():
                if domain in current_url:
                    used = current_usage.get(domain, 0)
                    
                    if limit == 0: 
                        triggered_domains.append(domain)
                        print(f"Blocked {domain}")
                    
                    elif used >= limit: 
                        triggered_domains.append(domain)
                        print(f"Time limit exceeded for {domain}")
                    
                    else:
                        # 增加计数
                        current_usage[domain] = used + check_interval
                        print(f"{domain} usage: {used}s / {limit}s")
            
            # 如果有触发违规，执行关闭操作
            if triggered_domains:
                kill_browser_tab("Google Chrome")
                kill_browser_tab("Safari")
                kill_browser_tab("Microsoft Edge")
                kill_browser_tab("Brave Browser")

            # --- 保存数据 ---
            usage_data["usage"] = current_usage
            save_usage(usage_data)
            
        except Exception as e:
            print(f"Error: {e}")
        
        time.sleep(5)

if __name__ == "__main__":
    main()
