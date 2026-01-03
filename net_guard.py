#!/usr/bin/env python3
import time
import subprocess
import os
import sys
import json
import urllib.request

# ================= ⚙️ 配置区域 (必填) =================
# 请填入你的 macOS 用户名 (用于修正文件权限)
# 打开终端输入 `whoami` 即可查看
USER_NAME = "yuanliang"  # <--- 请修改这里！！！

# Clash 的外部控制端口 (默认 9090)
CLASH_API_URL = "http://127.0.0.1:9090"
# ==========================================================

# ================= 🚫 绝对黑名单 =================
BLOCKED_DOMAINS = [
    "playok.com",
    "www.playok.com"
]

# Clash 规则字符串 (缩进很重要)
CLASH_RULE_STR = "  - DOMAIN-SUFFIX,playok.com,REJECT"
# ===============================================

def enforce_hosts():
    """
    守护 /etc/hosts
    将黑名单域名永久指向 127.0.0.1
    """
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
            # 刷新 DNS 缓存
            subprocess.run(["killall", "-HUP", "mDNSResponder"], stderr=subprocess.DEVNULL)
            # print("Hosts repaired.")
    except Exception:
        pass

def get_current_clash_config_path():
    """
    通过 API 询问 Clash 当前正在使用哪个配置文件
    """
    try:
        # 相当于 curl http://127.0.0.1:9090/configs
        req = urllib.request.Request(f"{CLASH_API_URL}/configs")
        with urllib.request.urlopen(req, timeout=2) as response:
            data = json.loads(response.read().decode())
            # 返回绝对路径
            return data.get("path")
    except:
        # Clash 可能没开，或者端口不对
        return None

def reload_clash_config(config_path):
    """
    命令 Clash 热重载配置文件
    """
    try:
        # 相当于 curl -X PUT -d '{"path": "..."}' ...
        data = json.dumps({"path": config_path}).encode('utf-8')
        req = urllib.request.Request(f"{CLASH_API_URL}/configs", data=data, method='PUT')
        req.add_header('Content-Type', 'application/json')
        with urllib.request.urlopen(req, timeout=2) as response:
            pass
            # print("Clash reloaded.")
    except:
        pass

def enforce_clash_dynamic():
    """
    动态获取当前配置并注入规则
    """
    # 1. 找到当前活跃的配置文件
    config_path = get_current_clash_config_path()
    if not config_path or not os.path.exists(config_path):
        return

    try:
        # 2. 读取文件内容
        with open(config_path, 'r') as f:
            lines = f.readlines()
        
        content = "".join(lines)
        
        # 3. 检查规则是否已存在
        if "playok.com,REJECT" in content:
            return # 规则还在，无需操作

        # print(f"⚠️ 发现 Clash 配置 ({os.path.basename(config_path)}) 缺少规则，正在修复...")

        # 4. 寻找 'rules:' 标记并插入
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

        # 5. 写回文件
        with open(config_path, 'w') as f:
            f.writelines(new_lines)
        
        # 6. 关键：修正文件权限
        # 因为脚本是 root 运行的，写回后文件会变 root 所有，导致 Clash 无法再次读取
        try:
            # 获取用户的 uid 和 gid
            user_info = subprocess.check_output(['id', USER_NAME]).decode().strip()
            # 解析 uid=501(lawye) gid=20(staff) ...
            # 简单方法：直接用 id -u 和 id -g 命令
            uid = int(subprocess.check_output(['id', '-u', USER_NAME]).strip())
            gid = int(subprocess.check_output(['id', '-g', USER_NAME]).strip())
            os.chown(config_path, uid, gid)
        except:
            pass

        # 7. 强制重载让规则生效
        reload_clash_config(config_path)

    except Exception:
        pass

def main():
    # 必须以 Root 运行
    if os.geteuid() != 0:
        print("Error: Must run as root.")
        sys.exit(1)

    # print("Simple Guardian started (Interval: 120s)...")
    
    while True:
        enforce_hosts()
        enforce_clash_dynamic()
        
        # 每 2 分钟检查一次
        # 对于 PlayOK 这种下棋网站，断线一次就意味着判负，2分钟足够毁掉体验
        time.sleep(120)

if __name__ == "__main__":
    main()
