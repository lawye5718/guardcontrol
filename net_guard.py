#!/usr/bin/env python3
import time
import subprocess
import os
import sys
import json
import urllib.request
import glob

# ================= ⚙️ 配置区域 (已根据你的反馈修正) =================
# 你的 macOS 用户名
USER_NAME = "yuanliang" 

# Clash API 地址
CLASH_API_URL = "http://127.0.0.1:9090"

# Clash 配置文件的根目录 (修正为你的实际路径)
# 脚本将扫描此目录下所有的 .yaml 文件
CLASH_BASE_DIR = f"/Users/{USER_NAME}/.config/clash"
# ==========================================================

# ================= 🚫 绝对黑名单 =================
BLOCKED_DOMAINS = [
    "playok.com",
    "www.playok.com"
]

# Clash 规则字符串
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

def get_api_active_config_path():
    """
    1. 优选策略：尝试从 API 获取当前正在使用的配置文件路径
    """
    try:
        req = urllib.request.Request(f"{CLASH_API_URL}/configs")
        with urllib.request.urlopen(req, timeout=2) as response:
            data = json.loads(response.read().decode())
            # API 返回的 path 可能是绝对路径，直接返回
            return data.get("path")
    except:
        return None

def find_all_config_files():
    """
    2. 全方位查找策略：扫描 CLASH_BASE_DIR 下所有的 .yaml 和 .yml 文件
    修正：不找 profiles 目录，直接找根目录
    """
    candidates = set()
    
    # 扫描目录下的所有 .yaml 文件 (包括 config.yaml 和 0814v2yun.yaml 等)
    yaml_files = glob.glob(os.path.join(CLASH_BASE_DIR, "*.yaml"))
    yml_files = glob.glob(os.path.join(CLASH_BASE_DIR, "*.yml"))
    
    for f in yaml_files + yml_files:
        candidates.add(f)
        
    return list(candidates)

def inject_rule_to_file(file_path):
    """将规则写入指定文件"""
    try:
        if not os.path.exists(file_path): return False

        with open(file_path, 'r') as f:
            lines = f.readlines()
        content = "".join(lines)

        # 检查是否已存在
        if "playok.com,REJECT" in content:
            return False # 规则已存在，跳过

        # 插入规则
        new_lines = []
        inserted = False
        for line in lines:
            new_lines.append(line)
            # 在 'rules:' 这一行下面立刻插入我们的规则
            if line.strip().startswith('rules:') and not inserted:
                new_lines.append(CLASH_RULE_STR + "\n")
                inserted = True
        
        if not inserted:
            # 如果没找到 rules:，就追加在最后
            new_lines.append("rules:\n")
            new_lines.append(CLASH_RULE_STR + "\n")

        with open(file_path, 'w') as f:
            f.writelines(new_lines)

        # 关键：修正权限 (把文件所有者改回 yuanliang)
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
        # 如果能提供具体路径最好，否则只发重载信号
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

def enforce_clash_strategy():
    """
    执行策略：
    1. 尝试获取 API 当前路径 -> 注入 -> 重载 (精确打击)
    2. 扫描目录下所有 YAML -> 注入 (地毯式轰炸，防止切换)
    """
    
    # 集合用于去重，避免重复处理
    target_files = set()

    # 步骤 1: 获取 API 当前正在用的文件 (高优先级)
    active_path = get_api_active_config_path()
    if active_path:
        target_files.add(active_path)
    
    # 步骤 2: 扫描目录下所有可能的文件 (补齐路径)
    all_local_files = find_all_config_files()
    for f in all_local_files:
        target_files.add(f)
    
    # 步骤 3: 对所有目标文件执行注入
    any_modified = False
    for path in target_files:
        if inject_rule_to_file(path):
            any_modified = True
            # print(f"Injected rule into: {path}") # 仅调试用
    
    # 步骤 4: 触发重载
    # 如果修改了文件，或者我们明确知道当前活跃的是哪个文件，就触发重载
    if any_modified:
        force_reload_clash(active_path)
    elif active_path:
        # 即使没修改(可能已经被手动改回去了)，也强制重载确保生效
        pass 

def main():
    if os.geteuid() != 0:
        print("Error: Must run as root.")
        sys.exit(1)

    while True:
        enforce_hosts()
        enforce_clash_strategy()
        # 2分钟检查一次
        time.sleep(120)

if __name__ == "__main__":
    main()
