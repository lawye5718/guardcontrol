#!/bin/bash

# 部署GuardControl系统
echo "开始部署GuardControl系统..."

# 复制看门狗脚本到系统位置
sudo cp net_guard.py /usr/local/bin/
echo "已复制net_guard.py到/usr/local/bin/"

# 设置执行权限
sudo chmod +x /usr/local/bin/net_guard.py
echo "已设置net_guard.py执行权限"

echo "部署完成！"
echo ""
echo "下一步："
echo "1. 让您的朋友运行 generate_hash.py 生成哈希值"
echo "2. 将生成的哈希值替换 guard_control.py 中的占位符"
echo "3. 运行 'pyinstaller --onefile guard_control.py' 编译二进制文件"
echo "4. 按照说明销毁源代码文件"
echo "5. 运行 'sudo ./guard_control' 启动系统"
