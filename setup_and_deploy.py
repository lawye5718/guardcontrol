#!/usr/bin/env python3
import os
import subprocess
import sys
import getpass

def run_cmd(cmd, is_sudo=False):
    """执行命令"""
    if is_sudo:
        # 对于sudo命令，我们不使用shell=True以避免安全问题
        full_cmd = ["sudo"] + cmd.split()
        result = subprocess.run(full_cmd, capture_output=True, text=True)
    else:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"命令执行失败: {cmd}")
        print(f"错误: {result.stderr}")
        return False
    return True

def deploy():
    print("GuardControl 部署向导")
    print("="*40)
    
    # 检查是否以root权限运行
    if os.geteuid() == 0:
        print("警告: 请不要以 root 身份直接运行此脚本")
        print("请以普通用户身份运行，脚本会在需要时请求sudo权限")
        return False
    
    print("1. 复制 net_guard.py 到系统目录...")
    if not run_cmd("cp net_guard.py /usr/local/bin/", is_sudo=True):
        print("复制 net_guard.py 失败")
        return False
    print("   ✅ net_guard.py 复制成功")
    
    print("2. 设置执行权限...")
    if not run_cmd("chmod +x /usr/local/bin/net_guard.py", is_sudo=True):
        print("设置权限失败")
        return False
    print("   ✅ 权限设置成功")
    
    print("3. 创建配置目录...")
    run_cmd("mkdir -p /usr/local/etc", is_sudo=True)
    print("   ✅ 配置目录创建完成")
    
    print("4. 检查 PyInstaller 是否已安装...")
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
    
    print("5. 编译控制程序...")
    result = subprocess.run([sys.executable, "-m", "PyInstaller", "--onefile", "guard_control.py"], 
                           capture_output=True, text=True)
    if result.returncode != 0:
        print(f"编译失败: {result.stderr}")
        return False
    print("   ✅ 控制程序编译成功")
    
    print("6. 部署完成！现在可以运行 sudo ./dist/guard_control 来启动系统")
    print("   请记住：")
    print("   - 运行 'sudo ./dist/guard_control' 并选择 '1' 来启用系统")
    print("   - 以后如需解锁，需要朋友提供的密码")
    print("   - 请妥善保管此信息")
    
    return True

def test_run():
    print("测试运行 net_guard.py...")
    print("注意：这将启动监控程序，按 Ctrl+C 可停止")
    print("如果能看到 'Guardian started monitoring...' 说明程序正常")
    print("按 Enter 键继续测试，或 Ctrl+C 取消...")
    input()
    
    try:
        subprocess.run(["python3", "net_guard.py"])
    except KeyboardInterrupt:
        print("\n测试已停止")

def main():
    print("GuardControl 部署工具")
    print("1. 部署系统")
    print("2. 测试运行（不安装）")
    
    choice = input("请选择 (1/2): ")
    
    if choice == "1":
        if deploy():
            print("\n🎉 部署完成！")
            print("要启动系统，请运行: sudo ./dist/guard_control")
        else:
            print("\n❌ 部署失败，请检查错误信息")
    elif choice == "2":
        test_run()
    else:
        print("无效选择")

if __name__ == "__main__":
    main()
