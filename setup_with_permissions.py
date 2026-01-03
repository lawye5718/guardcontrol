#!/usr/bin/env python3
import os
import subprocess
import sys
import time
import getpass

def print_header():
    print("="*70)
    print("           GuardControl 部署向导 - Session Isolation 修复版")
    print("="*70)
    print("此版本已修复 macOS 权限隔离问题，但需要正确配置系统权限")
    print()

def check_console_user():
    """检查控制台用户"""
    try:
        user = subprocess.check_output(['stat', '-f%Su', '/dev/console']).decode('utf-8').strip()
        print(f"   ✅ 当前控制台用户: {user}")
        return user
    except:
        print("   ❌ 无法获取控制台用户")
        return None

def check_sudo_access():
    """检查sudo权限"""
    try:
        subprocess.run(['sudo', '-v'], check=True, capture_output=True)
        print("   ✅ 具有sudo权限")
        return True
    except:
        print("   ❌ 没有sudo权限")
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

def print_permission_instructions():
    """打印权限配置说明"""
    print("\n4. ⚠️  重要：权限配置说明")
    print("   在运行GuardControl之前，必须按以下步骤配置权限：")
    print()
    print("   A. 辅助功能权限：")
    print("      1. 打开 系统设置 -> 隐私与安全性 -> 辅助功能")
    print("      2. 点击左下角的锁图标并解锁")
    print("      3. 点击 '+' 添加应用")
    print("      4. 选择 'Terminal' (终端) 应用")
    print("      5. 如果使用Python运行脚本，也要添加Python")
    print()
    print("   B. 自动化权限：")
    print("      1. 打开 系统设置 -> 隐私与安全性 -> 自动化")
    print("      2. 找到 'Terminal' 项目")
    print("      3. 勾选 'AppleEvents' 下的浏览器 (Safari, Chrome等)")
    print()
    print("   C. 完成配置后，系统可能需要重启或Terminal需要重新打开")
    print()

def test_functionality():
    """测试功能"""
    print("5. 功能测试说明")
    print("   完成权限配置后，按以下步骤测试：")
    print()
    print("   A. 打开终端，运行：")
    print("      sudo python3 /usr/local/bin/net_guard.py")
    print()
    print("   B. 打开浏览器访问 x.com 或 twitter.com")
    print("   C. 观察终端是否输出类似：")
    print("      x.com usage: 2s / 3600s")
    print("   D. 如果能看到输出，说明URL抓取功能正常")
    print("   E. 按 Ctrl+C 停止测试")
    print()

def deploy_system():
    """部署系统"""
    print("\n6. 部署GuardControl系统")
    print("   确认权限已配置且功能测试通过后，可以部署系统：")
    print()
    print("   运行: sudo ./dist/guard_control")
    print("   选择 '1' 启用并锁定系统")
    print()
    print("   ⚠️  重要提醒：")
    print("   - 系统锁定后需要朋友的密码才能解锁")
    print("   - 请确保功能测试成功后再锁定系统")

def main():
    print_header()
    
    # 检查基本环境
    print("1. 检查系统环境...")
    user = check_console_user()
    has_sudo = check_sudo_access()
    
    if not user or not has_sudo:
        print("\n❌ 系统环境检查失败，无法继续部署。")
        return
    
    # 复制文件
    if not copy_files():
        print("\n❌ 文件复制失败，无法继续部署。")
        return
    
    # 编译控制程序
    if not compile_control():
        print("\n❌ 编译失败，无法继续部署。")
        return
    
    # 显示权限配置说明
    print_permission_instructions()
    
    # 显示功能测试说明
    test_functionality()
    
    # 显示部署说明
    deploy_system()
    
    print("\n" + "="*70)
    print("GuardControl 部署准备就绪！")
    print("请先完成权限配置，然后进行功能测试，最后再部署系统。")
    print("="*70)

if __name__ == "__main__":
    main()
