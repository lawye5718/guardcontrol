# GuardControl 部署指南 - 动态追踪版

## 概述
GuardControl 现在采用动态追踪策略，不仅使用 hosts 文件封锁，还能动态追踪并修改 Clash 配置文件。

## 功能特点
- ✅ 保留 hosts 文件永久封锁功能
- ✅ 动态追踪 Clash 配置文件
- ✅ 自动在 Clash 配置中添加 playok.com 封锁规则
- ✅ 无需浏览器监控和复杂权限配置
- ✅ 每2分钟检查一次，确保封锁始终生效

## 部署步骤

### 1. 确保脚本已复制到系统目录
```bash
sudo cp net_guard.py /usr/local/bin/
sudo chmod +x /usr/local/bin/net_guard.py
```

### 2. (如果之前已部署) 解锁系统
```bash
sudo ./dist/guard_control
# 选择 2，输入朋友的密码
```

### 3. 修改用户名配置
在 net_guard.py 文件中，将第29行的 USER_NAME 修改为您的用户名：
```python
USER_NAME = "your_actual_username"  # 使用 whoami 命令查看您的用户名
```

### 4. 测试运行（可选）
```bash
sudo python3 /usr/local/bin/net_guard.py
```
脚本会每2分钟运行一次，检查并确保 playok.com 被正确封锁。

### 5. 核弹级锁定
```bash
sudo ./dist/guard_control
# 选择 1
```

## 功能说明
- **Hosts 封锁**：确保 playok.com 被添加到 /etc/hosts 文件，指向 127.0.0.1
- **Clash 动态追踪**：脚本会通过 Clash API 查询当前使用的配置文件，并自动在该配置中添加 `DOMAIN-SUFFIX,playok.com,REJECT` 规则
- **权限修正**：自动修正配置文件权限，防止 Clash 无法读取

## 结果确认
一旦执行锁定：
- ✅ playok.com 被永久封锁：访问 playok.com -> 系统 Hosts 拦截 -> "无法连接到服务器"
- ✅ Clash 模式：脚本动态追踪并修改当前使用的 Clash 配置，确保 playok.com 被拒绝访问
- ✅ 无需权限焦虑：不需要配置 Accessibility 或 Automation 权限
- ✅ 想改 Hosts？：被文件系统锁死，无法修改
- ✅ 想关脚本？：需要朋友的密码

## 验证功能
可以使用以下命令验证封锁是否生效：
```bash
ping playok.com
# 应该显示 PING playok.com (127.0.0.1)
```

## 注意事项
- 确保 Clash 的外部控制端口（默认9090）已启用
- 脚本每2分钟运行一次，频率适中，不会占用过多系统资源
- 如果需要封锁更多域名，可以修改 net_guard.py 中的 `BLOCKED_DOMAINS` 列表
