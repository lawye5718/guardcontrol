#!/usr/bin/env python3
import time
import datetime
import os
import json
import subprocess
import sys

# ================= ⚠️ 绝对规则 (硬编码区) ⚠️ =================
# 每日限额 3600秒 = 1小时
HARD_RULES = {
    "playok.com": 0,
    "x.com": 3600,
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

def get_console_user():
    """获取当前登录到物理控制台的用户名"""
    try:
        # stat -f%Su /dev/console 可以获取当前控制台的所有者
        return subprocess.check_output(['stat', '-f%Su', '/dev/console']).decode('utf-8').strip()
    except:
        return None

def get_active_browser_url():
    """
    使用 AppleScript 获取 URL。
    关键修正：以当前登录用户的身份运行 osascript，而不是 root。
    """
    script = """
    tell application "System Events"
        set frontApp to name of first application process whose frontmost is true
    end tell
    
    if frontApp is "Google Chrome" or frontApp is "Microsoft Edge" or frontApp is "Brave Browser" or frontApp is "Arc" then
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
        user = get_console_user()
        if user and user != "root":
            # 这里的魔法：用 sudo -u <用户> 切换身份去执行 osascript
            # 这样才能访问该用户的窗口服务器
            cmd = ["sudo", "-u", user, "osascript", "-e", script]
        else:
            # 如果获取不到用户，只能尝试直接运行（可能会失败）
            cmd = ["osascript", "-e", script]

        result = subprocess.check_output(cmd, stderr=subprocess.DEVNULL)
        return result.decode('utf-8').strip()
    except Exception as e:
        # 这里返回空字符串，避免报错刷屏
        return ""

def kill_browser_tab(browser_name):
    """
    关闭标签页同样需要以用户身份执行
    """
    script = f"""
    tell application "{browser_name}"
        close active tab of front window
        display notification "已拦截违规访问！" with title "NetGuard"
    end tell
    """
    try:
        user = get_console_user()
        if user and user != "root":
            cmd = ["sudo", "-u", user, "osascript", "-e", script]
        else:
            cmd = ["osascript", "-e", script]
        subprocess.run(cmd, stderr=subprocess.DEVNULL)
    except:
        pass

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
    
    # 1. Hosts 拦截 (Root 权限执行)
    block_list = [d for d, limit in HARD_RULES.items() if limit == 0]
    enforce_hosts(block_list)

    while True:
        try:
            # 2. URL 监控 (切换为用户权限执行)
            current_url = get_active_browser_url()
            
            # 简单的调试输出，确认能不能抓到
            if current_url:
                # print(f"DEBUG: Current URL: {current_url}") # 调试完可注释掉
                pass

            usage_data = load_usage()
            current_usage = usage_data["usage"]
            
            # 合并规则
            extra_rules = load_extra_rules()
            all_rules = extra_rules.copy()
            all_rules.update(HARD_RULES)
            
            check_interval = 2 # 提高一点频率，2秒检查一次
            triggered_apps = set() # 记录需要关闭的浏览器类型

            for domain, limit in all_rules.items():
                if domain in current_url:
                    used = current_usage.get(domain, 0)
                    
                    if limit == 0: 
                        print(f"Blocked access to {domain}")
                        triggered_apps.add("Google Chrome")
                        triggered_apps.add("Safari")
                        triggered_apps.add("Microsoft Edge")
                    
                    elif used >= limit: 
                        print(f"Time limit exceeded for {domain}")
                        triggered_apps.add("Google Chrome")
                        triggered_apps.add("Safari")
                        triggered_apps.add("Microsoft Edge")
                    
                    else:
                        current_usage[domain] = used + check_interval
                        print(f"{domain} usage: {used}s / {limit}s")
            
            # 执行关闭操作
            for app in triggered_apps:
                kill_browser_tab(app)

            usage_data["usage"] = current_usage
            save_usage(usage_data)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            # print(f"Main loop error: {e}")
            pass
        
        time.sleep(2)

if __name__ == "__main__":
    main()
