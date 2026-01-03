# GuardControl - 自律契约系统

这是一个基于代码的自律系统，将"执行权"交给代码（机器），将"撤销权"交给第三方（朋友），并将规则"铸造"进二进制文件中。

## 系统架构

1. **信任根 (Root of Trust)**: 你的朋友。他掌握唯一的明文密码。
2. **加密锁 (The Lock)**: SHA-256 哈希值。我们只保存密码的"指纹"，不保存密码本身。
3. **看门狗 (The Guardian)**: 一个后台 Python 进程 (`net_guard.py`)。
   - 硬编码规则: `playok.com` (0秒), `x.com` (3600秒/天)。
   - 执行手段:
     - 网络层: 修改 `/etc/hosts` (针对直连)。
     - 应用层: 监控浏览器当前标签页 URL (针对 VPN/Clash)。如果发现违规，直接通过 AppleScript 秒关标签页。
4. **控制台 (The Gatekeeper)**: 编译后的二进制程序 (`guard_control`)。
   - 负责安装、锁定文件 (`chflags schg`)、解锁、卸载。
   - 唯一能停止看门狗的地方，但必须通过哈希校验。

## 部署步骤

### 第一阶段：生成密钥

请邀请您的朋友，在他的手机或电脑上（或者您的电脑终端，但您不能看），执行以下命令生成哈希值：

```bash
python3 generate_hash.py
```

步骤：
1. 朋友想一个复杂的密码（例如：`D0ntUnl0ckM3!2026`）。
2. 运行 `generate_hash.py` 获取 Hash。
3. 朋友把生成的这串长字符（Hash）发给您。
4. 朋友发誓：除非您真的需要维护系统（比如修电脑）或者绝交，否则绝不告诉您原始密码。

### 第二阶段：替换哈希值

将 `guard_control.py` 中的占位符 `PASSWORD_HASH` 替换为朋友提供的哈希值：

```python
PASSWORD_HASH = "朋友提供的SHA256哈希值"
```

### 第三阶段：编译控制台

安装 PyInstaller 并编译控制台：

```bash
pip3 install pyinstaller
pyinstaller --onefile guard_control.py
```

### 第四阶段：部署文件

运行部署脚本：

```bash
sudo ./deploy.sh
```

### 第五阶段：销毁源码

删除源代码文件，断后路：

```bash
rm guard_control.py
rm guard_control.spec
rm -rf build/
```

### 第六阶段：启动系统

运行控制台程序：

```bash
sudo ./dist/guard_control
```

选择 "1. 🔒 启用并锁死" 来启动系统。

## 功能说明

- 后台服务启动，每5秒检查一次浏览器。
- 即使开着 Clash，打开被禁网站时，Python 脚本会调用 AppleScript 在几毫秒内强制关闭标签页，并弹窗警告。
- `net_guard.py` 被系统锁定，无法编辑。
- `plist` 被锁定，无法停止后台服务。
- 想要解锁？必须运行控制台程序并输入朋友掌握的密码。

## 添加新规则

如果想添加新规则（比如禁止 gambling.com）：
您不需要解锁核心。可以在代码里预留 `EXTRA_CONFIG`。可以编写另一个简单的脚本去读写 `/usr/local/etc/net_guard_config.json`，让看门狗读取软规则。但是，硬编码的规则是写死在被锁定的 Python 文件里的，永远无法通过 Config 覆盖。

## 安全机制

- 使用 `chflags schg` 命令锁定关键文件，即使使用 `sudo` 也无法编辑或删除
- 密码以哈希形式存储，无法反向破解
- 通过 AppleScript 直接控制浏览器，绕过网络层限制
