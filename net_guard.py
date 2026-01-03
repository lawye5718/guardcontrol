#!/usr/bin/env python3
import time
import subprocess
import os
import sys
import json
import urllib.request
import glob

# ================= ⚙️ 配置区域 (必填) =================
# 你的 macOS 用户名
USER_NAME = "yuanliang" 

# Clash API 地址
CLASH_API_URL = "http://127.0.0.1:9090"

# Clash 配置文件的常见根目录 (Clash X / Pro 默认都在这里)
CLASH_BASE_DIR = f"/Users/{USER_NAME}/.config/clash"
# ==========================================================

# ================= 🚫 绝对黑名单 =================
BLOCKED_DOMAINS = [
    "playok.com",
    "www.playok.com"
]

CLASH_RULE_STR = "  - DOMAIN-SUFFIX,playok.com,REJECT"
# ===============================================

def enforce_hosts():
    """守护 /etc/hosts"""
    try:
        hosts_path = "/etc/hosts"
        if not os.path.exists(hosts_path): return

        with open(hosts_path, "r") as f: content = f.read()
        
        need_refresh = False
        lines_to_add = []
        
        for domain in BLOCKED_DOMAINS:
            entry = f"127.0.0.1 {domain}"
            if entry not in content:
                lines_to_add.append(entry)
                need_refresh = True
        
        if need_refresh:
            with open(hosts_path, "a") as f:
                f.write("\n# NetGuard Block\n")
                for line in lines_to_add:
                    f.write(f"{line}\n")
            subprocess.run(["killall", "-HUP", "mDNSResponder"], stderr=subprocess.DEVNULL)
    except Exception:
        pass

def get_api_config_path():
    """尝试从 API 获取路径 (可能会失败返回 None)"""
    try:
        req = urllib.request.Request(f"{CLASH_API_URL}/configs")
        with urllib.request.urlopen(req, timeout=2) as response:
            data = json.loads(response.read().decode())
            return data.get("path")
    except:
        return None

def find_all_config_files():
    """
    [Plan B] 扫描所有可能的配置文件
    """
    candidates = []
    
    # 1. 默认 config.yaml
    default_cfg = os.path.join(CLASH_BASE_DIR, "config.yaml")
    if os.path.exists(default_cfg):
        candidates.append(default_cfg)
    
    # 2. profiles 目录下的所有 yaml 文件 (订阅文件)
    profiles_dir = os.path.join(CLASH_BASE_DIR, "profiles")
    if os.path.exists(profiles_dir):
        # 扫描 .yaml 和 .yml
        candidates.extend(glob.glob(os.path.join(profiles_dir, "*.yaml")))
        candidates.extend(glob.glob(os.path.join(profiles_dir, "*.yml")))
    
    return candidates

def inject_rule_to_file(file_path):
    """将规则写入指定文件"""
    try:
        if not os.path.exists(file_path): return False

        with open(file_path, 'r') as f:
            lines = f.readlines()
        content = "".join(lines)

        # 检查是否已存在
        if "playok.com,REJECT" in content:
            return False # 规则已存在

        # 插入规则
        new_lines = []
        inserted = False
        for line in lines:
            new_lines.append(line)
            if line.strip().startswith('rules:') and not inserted:
                new_lines.append(CLASH_RULE_STR + "\n")
                inserted = True
        
        if not inserted:
            new_lines.append("rules:\n")
            new_lines.append(CLASH_RULE_STR + "\n")

        with open(file_path, 'w') as f:
            f.writelines(new_lines)

        # 修正权限 (chown 回给用户)
        try:
            uid = int(subprocess.check_output(['id', '-u', USER_NAME]).strip())
            gid = int(subprocess.check_output(['id', '-g', USER_NAME]).strip())
            os.chown(file_path, uid, gid)
        except:
            pass
            
        return True # 写入成功
    except Exception:
        return False

def force_reload_clash(config_path=None):
    """强制 Clash 重载配置"""
    try:
        # 如果不知道具体路径，就只发送重载信号
        payload = {}
        if config_path:
            payload = {"path": config_path}
            
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(f"{CLASH_API_URL}/configs", data=data, method='PUT')
        req.add_header('Content-Type', 'application/json')
        with urllib.request.urlopen(req, timeout=2):
            pass
    except:
        pass

def enforce_clash_shotgun():
    """
    全覆盖模式：无论 API 返回什么，扫描所有文件并注入
    """
    # 1. 尝试获取 API 指向的特定文件
    api_path = get_api_config_path()
    
    targets = set()
    if api_path:
        targets.add(api_path)
    
    # 2. 扫描本地所有可能的配置文件
    local_files = find_all_config_files()
    for f in local_files:
        targets.add(f)
    
    # 3. 对找到的每一个文件执行注入
    any_modified = False
    for path in targets:
        if inject_rule_to_file(path):
            any_modified = True
            # print(f"Injected rule into: {path}")
    
    # 4. 只有当文件确实被修改过，或者我们知道确切路径时，才触发重载
    # 如果不知道路径且没改文件，就不频繁重载以免打断连接
    if any_modified:
        force_reload_clash(api_path)
    elif api_path:
        # 即使没修改(可能被手动恢复了)，如果知道路径，也确保重载一次以防万一
        pass 

def main():
    if os.geteuid() != 0:
        print("Error: Must run as root.")
        sys.exit(1)

    while True:
        enforce_hosts()
        enforce_clash_shotgun()
        time.sleep(120)

if __name__ == "__main__":
    main()
