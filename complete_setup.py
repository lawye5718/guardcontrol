#!/usr/bin/env python3
import os
import subprocess
import sys
import time
import getpass

def print_header():
    print("="*60)
    print("           GuardControl 完整部署和测试向导")
    print("="*60)
    print()

def check_permissions():
    """检查系统权限"""
    print("1. 检查系统权限...")
    
    # 检查AppleScript权限
    script = '''
    tell application "System Events"
        set frontApp to name of first application process whose frontmost is true
    end tell
    return frontApp
    '''
    
    try:
        result = subprocess.check_output(["osascript", "-e", script], stderr=subprocess.DEVNULL)
        app_name = result.decode('utf-8').strip()
        print(f"   ✅ AppleScript权限正常 (当前前台应用: {app_name})")
        return True
    except:
        print("   ❌ AppleScript权限不足")
        print("   请按以下步骤配置权限：")
        print("   - 系统设置 -> 隐私与安全性 -> 辅助功能")
        print("   - 添加 Terminal 应用")
        print("   - 系统设置 -> 隐私与安全性 -> 自动化")
        print("   - 确保 Terminal 有权控制浏览器")
        return False

def copy_files():
    """复制文件到系统目录"""
    print("\n2. 复制文件到系统目录...")
    
    try:
        # 复制net_guard.py
        subprocess.run(["sudo", "cp", "net_guard.py", "/usr/local/bin/"], check=True)
        subprocess.run(["sudo", "chmod", "+x", "/usr/local/bin/net_guard.py"], check=True)
        print("   ✅ net_guard.py 复制并设置权限成功")
        
        # 创建配置目录
        subprocess.run(["sudo", "mkdir", "-p", "/usr/local/etc"], check=True)
        print("   ✅ 配置目录创建成功")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ 文件复制失败: {e}")
        return False

def compile_control():
    """编译控制程序"""
    print("\n3. 编译控制程序...")
    
    try:
        # 检查PyInstaller
        result = subprocess.run([sys.executable, "-m", "pip", "show", "pyinstaller"], 
                               capture_output=True, text=True)
        if result.returncode != 0:
            print("   安装 PyInstaller...")
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], 
                          check=True, capture_output=True)
        
        # 编译控制程序
        subprocess.run([sys.executable, "-m", "PyInstaller", "--onefile", "guard_control.py"], 
                      check=True, capture_output=True)
        print("   ✅ 控制程序编译成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ 编译失败: {e}")
        return False

def test_functionality():
    """测试功能"""
    print("\n4. 功能测试...")
    print("   这将启动GuardControl守护进程进行测试")
    print("   请在浏览器中访问 x.com 或 twitter.com 来测试监控功能")
    print("   观察终端是否输出 'x.com usage: ...' 或 'twitter.com usage: ...'")
    print("   按 Enter 键开始测试...")
    input()
    
    print("\n   启动测试守护进程 (按 Ctrl+C 停止)...")
    print("   提示：打开浏览器访问 x.com 或 twitter.com 来测试监控功能")
    
    try:
        # 运行测试守护进程
        result = subprocess.run(["sudo", "python3", "/usr/local/bin/net_guard.py"])
        if result.returncode == 0:
            print("   测试完成")
        else:
            print("   测试结束")
    except KeyboardInterrupt:
        print("\n   测试已停止")
    except Exception as e:
        print(f"   测试出错: {e}")

def deploy_system():
    """部署系统"""
    print("\n5. 部署GuardControl系统...")
    print("   注意：此操作将永久锁定系统，需要朋友的密码才能解锁")
    print("   确认要继续吗？(输入 'YES' 继续，其他取消): ", end="")
    
    confirm = input().strip()
    if confirm != "YES":
        print("   操作已取消")
        return False
    
    try:
        print("   启动GuardControl系统...")
        subprocess.run(["sudo", "./dist/guard_control"], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"   部署失败: {e}")
        return False

def main():
    print_header()
    
    # 检查权限
    if not check_permissions():
        print("\n⚠️  权限配置不完整，无法继续部署。")
        print("请先按说明配置权限，然后重新运行此脚本。")
        return
    
    # 复制文件
    if not copy_files():
        print("\n❌ 文件复制失败，无法继续部署。")
        return
    
    # 编译控制程序
    if not compile_control():
        print("\n❌ 编译失败，无法继续部署。")
        return
    
    # 功能测试
    print("\n" + "="*60)
    print("准备进行功能测试")
    print("="*60)
    test_functionality()
    
    # 询问是否部署
    print("\n" + "="*60)
    print("是否要部署GuardControl系统？")
    print("="*60)
    print("1. 是，部署系统")
    print("2. 否，仅完成设置，不部署")
    
    choice = input("请选择 (1/2): ").strip()
    
    if choice == "1":
        deploy_system()
    else:
        print("\n设置完成！")
        print("要手动部署，请运行: sudo ./dist/guard_control")
    
    print("\n🎉 GuardControl 设置完成！")

if __name__ == "__main__":
    main()
