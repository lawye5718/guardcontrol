import hashlib
import subprocess
import sys
import getpass
import os

# ================= 🔐 核心密钥区 �� =================
# 替换下方字符串为你朋友给你的 SHA256 Hash
PASSWORD_HASH = "9e7cae479aa6225c02e55646dc360bd980c47974f8ada384439f9137d834b197" 
# ===================================================

SCRIPT_PATH = "/usr/local/bin/net_guard.py"
PLIST_PATH = "/Library/LaunchDaemons/com.sys.netguard.plist"

PLIST_CONTENT = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.sys.netguard</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>{SCRIPT_PATH}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
"""

def run_cmd(cmd):
    subprocess.run(cmd, shell=True, stderr=subprocess.DEVNULL)

def install():
    print("正在安装并锁定系统...")
    # 1. 生成 Plist
    with open("/tmp/temp.plist", "w") as f:
        f.write(PLIST_CONTENT)
    run_cmd(f"sudo mv /tmp/temp.plist {PLIST_PATH}")
    
    # 2. 确保脚本有执行权限
    run_cmd(f"sudo chmod +x {SCRIPT_PATH}")
    
    # 3. 加载服务
    run_cmd(f"sudo launchctl load -w {PLIST_PATH}")
    
    # 4. 核弹级锁定 (Schg Flags)
    # 锁定脚本：你不能修改 net_guard.py 里的硬编码规则
    run_cmd(f"sudo chflags schg {SCRIPT_PATH}") 
    # 锁定Plist：你不能卸载服务
    run_cmd(f"sudo chflags schg {PLIST_PATH}")
    
    print("✅ 锁定完成！playok 已被放逐，x.com 每日限时 1 小时。")

def uninstall():
    print("⚠️  检测到卸载请求...")
    pwd = getpass.getpass("请输入【朋友掌握的】解锁密码: ")
    
    if hashlib.sha256(pwd.encode()).hexdigest() == PASSWORD_HASH:
        print("🔓 密码正确。正在解除封印...")
        run_cmd(f"sudo chflags noschg {SCRIPT_PATH}")
        run_cmd(f"sudo chflags noschg {PLIST_PATH}")
        run_cmd(f"sudo launchctl unload -w {PLIST_PATH}")
        run_cmd(f"sudo rm {PLIST_PATH}")
        # 不删除脚本，方便你下次重新启用，如果想删也可以删
        print("✅ 系统已解锁。自由（和诱惑）回来了。")
    else:
        print("❌ 密码错误！操作被拒绝。")

def main():
    if os.geteuid() != 0:
        print("请加 sudo 运行！")
        sys.exit(1)
        
    print("--- 绝交卫士 v1.0 ---")
    print("1. 🔒 启用并锁死")
    print("2. 🔓 朋友来解锁")
    choice = input("选择: ")
    
    if choice == "1":
        install()
    elif choice == "2":
        uninstall()

if __name__ == "__main__":
    main()
