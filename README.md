# TData Bot - Telegram账号检测机器人

功能强大的Telegram账号检测和管理机器人，支持USDT-TRC20自动支付系统。

## 主要功能

- 📱 Telegram账号检测
- 🔄 格式转换（TData ↔ Session）
- 🔐 2FA管理
- 👥 账号分类
- 🧹 一键清理
- 📝 资料修改
- 💳 **USDT-TRC20 自动支付系统**（新增）

## USDT支付系统 ⭐

完整的USDT-TRC20自动支付系统，支持：
- ✅ 扫码支付 / 复制地址支付
- ✅ 4个套餐选择（7天/30天/120天/365天）
- ✅ 自动监听区块链交易
- ✅ 20次区块确认
- ✅ 防假U/防0元购/防重复发放
- ✅ 自动到账，Telegram通知

详细文档：[PAYMENT_README.md](PAYMENT_README.md)

## 快速开始

### 1. 克隆仓库
```bash
git clone https://github.com/lynntemoshenka269-source/tdatabot.git
cd tdatabot
```

### 2. 安装依赖
```bash
# 安装主程序依赖
pip install python-telegram-bot==13.15 telethon opentele

# 安装支付系统依赖
pip install -r requirements_payment.txt
```

### 3. 配置环境变量
```bash
# 复制示例配置
cp .env.example .env

# 编辑配置文件
nano .env
```

必需配置：
```
TRON_WALLET_ADDRESS=你的TRC20收款钱包地址
TELEGRAM_BOT_TOKEN=你的机器人Token
```

### 4. 启动服务

#### 启动主机器人
```bash
python tdata.py
```

#### 启动支付监听服务
```bash
# 后台运行
nohup python tron.py > tron.log 2>&1 &

# 查看日志
tail -f tron.log
```

## 目录结构

```
tdatabot/
├── tdata.py                  # 主机器人程序
├── tron.py                   # 支付监听服务
├── requirements_payment.txt  # 支付系统依赖
├── setup_payment.sh         # 自动安装脚本
├── PAYMENT_README.md        # 支付系统详细文档
├── .env.example             # 配置文件模板
├── i18n/                    # 多语言支持
│   ├── zh.py               # 中文
│   ├── en.py               # 英文
│   └── ru.py               # 俄文
└── ...
```

## 使用流程

### 用户购买会员
1. 用户发送 `/start` 启动机器人
2. 点击 "💳 开通/兑换会员" → "💎 USDT充值购买"
3. 选择套餐（7天/30天/120天/365天）
4. 获得订单和支付二维码
5. 使用TRC20钱包扫码支付
6. 约1分钟后自动到账

### 管理员配置
1. 配置收款钱包地址
2. 启动支付监听服务
3. 服务自动监听区块链
4. 收到支付自动发放会员
5. 发送通知给用户和管理员

## 一键安装脚本

```bash
# 运行自动安装脚本
bash setup_payment.sh
```

脚本会自动：
- 检查Python版本
- 安装所需依赖
- 创建配置文件模板
- 验证配置

## 数据库

- `tdatabot.db` - 主数据库（用户、会员、卡密等）
- `payment.db` - 支付数据库（订单、交易记录）

## 安全特性

### 支付安全
- ✅ 官方USDT合约验证
- ✅ 20次区块确认
- ✅ 精确金额匹配
- ✅ 交易哈希去重
- ✅ 订单超时保护

### 数据安全
- ✅ SQLite本地存储
- ✅ 会员时长累加
- ✅ 过期自动检查

## 性能优化

- 10秒轮询间隔（可调整）
- 异步HTTP请求
- 数据库索引优化
- 订单自动过期清理

## 监控和维护

```bash
# 查看支付服务状态
ps aux | grep tron.py

# 查看实时日志
tail -f tron.log

# 重启支付服务
pkill -f tron.py
nohup python tron.py > tron.log 2>&1 &
```

## 环境要求

- Python 3.7+
- SQLite 3
- 稳定的网络连接
- Linux / macOS / Windows

## 依赖包

### 主程序
- python-telegram-bot==13.15
- telethon
- opentele
- phonenumbers

### 支付系统
- qrcode[pil]
- Pillow
- aiohttp
- base58

## 常见问题

**Q: 支付后多久到账？**
A: 约1分钟（等待20个区块确认）

**Q: 支持哪些钱包？**
A: 所有支持TRC20的钱包（如TronLink、TokenPocket、imToken等）

**Q: 转账手续费多少？**
A: TRON网络手续费约0.1 TRX（极低）

**Q: 可以退款吗？**
A: 自动系统不支持退款，需要联系管理员

更多问题请查看 [PAYMENT_README.md](PAYMENT_README.md)

## 技术支持

- 📖 文档: [PAYMENT_README.md](PAYMENT_README.md)
- 🐛 问题: GitHub Issues
- 💬 讨论: GitHub Discussions

## 许可证

本项目遵循 MIT 许可证。

## 更新日志

### v8.1 (最新)
- ✨ 新增 USDT-TRC20 自动支付系统
- ✨ 支持扫码支付和地址复制
- ✨ 4个套餐选择
- ✨ 自动监听区块链并发放会员
- ✨ 完整的安全验证机制
- ✨ Telegram通知用户和管理员

### v8.0
- 原有功能...

---

**⚠️ 重要提示**: 
1. 请妥善保管 `.env` 文件，不要泄露钱包地址和Bot Token
2. 建议申请 TronGrid API Key 提高请求速率
3. 定期备份数据库文件
4. 建议使用 systemd 管理支付服务（生产环境）
