#!/usr/bin/env python3
import os
import subprocess
import sys
import getpass
import time

def run_cmd(cmd, is_sudo=False, capture_output=True):
    """执行命令"""
    try:
        if is_sudo:
            full_cmd = ["sudo"] + cmd.split()
            result = subprocess.run(full_cmd, capture_output=capture_output, text=True)
        else:
            result = subprocess.run(cmd, shell=True, capture_output=capture_output, text=True)
        
        if result.returncode != 0 and capture_output:
            print(f"命令执行失败: {cmd}")
            print(f"错误: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"执行命令时出错: {e}")
        return False

def check_applescript_permission():
    """检查AppleScript权限"""
    script = """
    tell application "System Events"
        set frontApp to name of first application process whose frontmost is true
    end tell
    return frontApp
    """
    
    try:
        result = subprocess.check_output(["osascript", "-e", script], stderr=subprocess.DEVNULL)
        app_name = result.decode('utf-8').strip()
        print(f"成功获取前台应用: {app_name}")
        return True
    except:
        print("❌ AppleScript权限检查失败")
        print("需要在系统设置中授予Terminal辅助功能权限")
        return False

def main():
    print("GuardControl 最终部署向导")
    print("="*50)
    print()
    
    print("1. 检查AppleScript权限...")
    if not check_applescript_permission():
        print()
        print("⚠️  重要提醒 - 权限配置要求:")
        print("   在运行守护程序之前，您必须先配置以下权限：")
        print("   1. 打开 系统设置 -> 隐私与安全性 -> 辅助功能")
        print("   2. 点击左下角的锁图标并解锁")
        print("   3. 点击 '+' 添加应用")
        print("   4. 添加 'Terminal' (终端) 应用")
        print("   5. 如果使用Python运行脚本，也要添加Python")
        print()
        print("   5. 打开 系统设置 -> 隐私与安全性 -> 自动化")
        print("   6. 展开 'Terminal' 项目")
        print("   7. 勾选 'AppleEvents' 下的 'Safari' 和 'Google Chrome' (或其他浏览器)")
        print()
        print("完成这些设置后，按 Enter 键继续...")
        input()
        print()
    
    print("2. 检查AppleScript权限（再次确认）...")
    if not check_applescript_permission():
        print("❌ 权限配置不正确，无法继续部署。")
        print("请按照上面的说明正确配置权限后重试。")
        return False
    
    print("✅ 权限配置检查通过")
    print()
    
    print("3. 复制 net_guard.py 到系统目录...")
    if not run_cmd("cp net_guard.py /usr/local/bin/", is_sudo=True):
        print("复制 net_guard.py 失败")
        return False
    print("   ✅ net_guard.py 复制成功")
    
    print("4. 设置执行权限...")
    if not run_cmd("chmod +x /usr/local/bin/net_guard.py", is_sudo=True):
        print("设置权限失败")
        return False
    print("   ✅ 权限设置成功")
    
    print("5. 创建配置目录...")
    run_cmd("mkdir -p /usr/local/etc", is_sudo=True)
    print("   ✅ 配置目录创建完成")
    
    print("6. 检查 PyInstaller 是否已安装...")
    result = subprocess.run([sys.executable, "-m", "pip", "show", "pyinstaller"], 
                           capture_output=True, text=True)
    if result.returncode != 0:
        print("   PyInstaller 未安装，正在安装...")
        result = subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], 
                               capture_output=True, text=True)
        if result.returncode != 0:
            print("   安装 PyInstaller 失败，请手动安装: pip3 install pyinstaller")
            return False
        else:
            print("   ✅ PyInstaller 安装成功")
    else:
        print("   ✅ PyInstaller 已安装")
    
    print("7. 编译控制程序...")
    result = subprocess.run([sys.executable, "-m", "PyInstaller", "--onefile", "guard_control.py"], 
                           capture_output=True, text=True)
    if result.returncode != 0:
        print(f"编译失败: {result.stderr}")
        return False
    print("   ✅ 控制程序编译成功")
    
    print()
    print("🎉 部署准备完成！")
    print()
    print("现在进行最终测试：")
    print("1. 打开浏览器（Chrome/Safari），访问 x.com 或 twitter.com")
    print("2. 在新终端窗口中运行: sudo python3 /usr/local/bin/net_guard.py")
    print("3. 观察终端是否输出 'x.com usage: ...' 或 'twitter.com usage: ...'")
    print("4. 如果看到输出，说明监控功能正常")
    print("5. 按 Ctrl+C 停止测试")
    print()
    print("要启动完整系统，请运行: sudo ./dist/guard_control")
    print("   选择 '1' 来启用并锁定系统")
    print()
    print("⚠️  重要提醒：")
    print("   - 启动后，系统将无法轻易停止 - 需要朋友的密码才能解锁")
    print("   - 请确保权限配置正确后再运行")
    
    return True

def test_run():
    print("测试运行 net_guard.py...")
    print("请打开浏览器访问 x.com 或 twitter.com 来测试监控功能")
    print("观察终端是否有输出 usage 信息...")
    print("按 Ctrl+C 停止测试")
    print()
    
    try:
        subprocess.run(["sudo", "python3", "/usr/local/bin/net_guard.py"])
    except KeyboardInterrupt:
        print("\n测试已停止")

if __name__ == "__main__":
    print("GuardControl 最终部署向导")
    print("1. 完整部署")
    print("2. 仅测试运行")
    
    choice = input("请选择 (1/2): ")
    
    if choice == "1":
        main()
    elif choice == "2":
        test_run()
    else:
        print("无效选择")
