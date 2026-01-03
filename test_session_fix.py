#!/usr/bin/env python3
import subprocess
import time

def get_console_user():
    """获取当前登录到物理控制台的用户名"""
    try:
        return subprocess.check_output(['stat', '-f%Su', '/dev/console']).decode('utf-8').strip()
    except:
        return None

def test_applescript_with_user():
    """测试使用用户身份运行AppleScript"""
    script = '''
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
        return "NO_BROWSER"
    end if
    '''
    
    user = get_console_user()
    print(f"当前控制台用户: {user}")
    
    if user and user != "root":
        print("尝试以用户身份运行AppleScript...")
        cmd = ["sudo", "-u", user, "osascript", "-e", script]
    else:
        print("无法获取用户，尝试直接运行...")
        cmd = ["osascript", "-e", script]
    
    try:
        result = subprocess.check_output(cmd, stderr=subprocess.DEVNULL)
        url = result.decode('utf-8').strip()
        print(f"成功获取URL: {url}")
        return True
    except Exception as e:
        print(f"获取URL失败: {e}")
        return False

def main():
    print("GuardControl Session Isolation 修复测试")
    print("="*50)
    
    print("\n1. 测试获取控制台用户...")
    user = get_console_user()
    if user:
        print(f"   ✅ 获取到控制台用户: {user}")
    else:
        print("   ❌ 无法获取控制台用户")
        return False
    
    print("\n2. 测试AppleScript访问...")
    success = test_applescript_with_user()
    
    if success:
        print("\n   ✅ Session Isolation 修复测试通过")
        print("   现在net_guard.py应该能够正常获取浏览器URL")
    else:
        print("\n   ❌ 测试失败")
        print("   请确保已按以下步骤配置权限：")
        print("   - 系统设置 -> 隐私与安全性 -> 辅助功能：添加Terminal")
        print("   - 系统设置 -> 隐私与安全性 -> 自动化：允许Terminal控制浏览器")
    
    return success

if __name__ == "__main__":
    main()
