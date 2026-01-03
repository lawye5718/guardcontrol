# GuardControl 部署指南 - 简化版

## 概述
GuardControl 现在采用简化策略，只使用 hosts 文件封锁，不再需要复杂的浏览器监控和权限配置。

## 功能变更
- ✅ 移除浏览器 URL 监控功能
- ✅ 移除 AppleScript 权限需求
- ✅ 移除辅助功能和自动化权限配置
- ✅ 保留 hosts 文件永久封锁功能
- ✅ 极大提升稳定性和简单性

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

### 3. 测试运行（可选）
```bash
sudo python3 /usr/local/bin/net_guard.py
```
你应该看到输出 "Simple Guardian is watching..."，并且 `/etc/hosts` 文件会被添加 playok.com 的封锁条目。

### 4. 核弹级锁定
```bash
sudo ./dist/guard_control
# 选择 1
```

## 针对 Clash 用户的特别说明
由于我们移除了浏览器监控功能，Clash 用户需要手动添加规则以确保 playok.com 被阻止：

在 Clash 配置文件中添加规则：
```yaml
rules:
  - DOMAIN-SUFFIX,playok.com,REJECT
  # 放在所有规则的最上面
```

## 结果确认
一旦执行锁定：
- ✅ 无需权限焦虑：不需要配置 Accessibility 或 Automation 权限
- ✅ playok.com 被永久封锁：访问 playok.com -> 系统 Hosts 拦截 -> "无法连接到服务器"
- ✅ Clash 模式：添加了 REJECT 规则后，Clash 也会拦截
- ✅ 想改 Hosts？：被文件系统锁死，无法修改
- ✅ 想关脚本？：需要朋友的密码

## 验证功能
可以使用以下命令验证封锁是否生效：
```bash
ping playok.com
# 应该显示 PING playok.com (127.0.0.1)
```

## 添加新的封锁域名
如果需要封锁更多域名，可以修改 net_guard.py 中的 `BLOCKED_DOMAINS` 列表。
