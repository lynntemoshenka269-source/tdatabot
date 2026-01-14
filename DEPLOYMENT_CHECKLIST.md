# USDT-TRC20 支付系统 - 部署验证清单

在部署到生产环境前，请按以下清单逐项验证：

## 1. 环境准备

- [ ] Python 3.7+ 已安装
- [ ] SQLite 3 已安装
- [ ] 服务器有稳定的网络连接
- [ ] 有足够的磁盘空间（至少500MB）

## 2. 依赖安装

```bash
# 检查并安装主程序依赖
pip3 install python-telegram-bot==13.15 telethon opentele

# 检查并安装支付系统依赖
pip3 install -r requirements_payment.txt

# 或使用自动安装脚本
bash setup_payment.sh
```

验证：
```bash
python3 -c "import qrcode, aiohttp, base58; print('✅ 依赖OK')"
```

## 3. 配置文件

### 3.1 创建 .env 文件

```bash
cp .env.example .env
nano .env
```

### 3.2 必需配置

- [ ] `TRON_WALLET_ADDRESS` - TRC20收款钱包地址
  - ✅ 格式：T开头，34位字符
  - ✅ 已测试可以接收USDT-TRC20
  - ⚠️ 建议使用专用钱包，不要与其他用途混用

- [ ] `TELEGRAM_BOT_TOKEN` - 机器人Token
  - ✅ 从 @BotFather 获取
  - ✅ 格式：数字:字母数字混合

### 3.3 可选配置

- [ ] `TRONGRID_API_KEY` - TronGrid API密钥
  - 申请地址: https://www.trongrid.io/
  - 免费套餐：100 requests/second
  - 建议申请以提高请求速率

- [ ] `TELEGRAM_NOTIFY_CHAT_ID` - 管理员通知Chat ID
  - 从 @userinfobot 获取
  - 收到支付时通知管理员

### 3.4 验证配置

```bash
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()

wallet = os.getenv('TRON_WALLET_ADDRESS', '')
token = os.getenv('TELEGRAM_BOT_TOKEN', '')

assert wallet.startswith('T') and len(wallet) == 34, '钱包地址格式错误'
assert ':' in token, 'Bot Token格式错误'

print('✅ 配置验证通过')
"
```

## 4. 数据库初始化

### 4.1 主数据库

```bash
# 确保主数据库存在
python3 -c "
import sqlite3
conn = sqlite3.connect('tdatabot.db')
print('✅ 主数据库 OK')
conn.close()
"
```

### 4.2 支付数据库

```bash
# 初始化支付数据库（第一次运行tron.py时自动创建）
python3 -c "
import sys
sys.path.insert(0, '.')
from tron import PaymentDatabase
db = PaymentDatabase('payment.db')
print('✅ 支付数据库初始化完成')
"
```

## 5. 功能测试

### 5.1 运行单元测试

```bash
python3 test_payment.py
```

预期输出：
```
✅ 通过: 7
❌ 失败: 0
🎉 所有测试通过！
```

### 5.2 测试机器人连接

```bash
# 启动主机器人（前台测试）
python3 tdata.py
```

- [ ] 机器人启动成功
- [ ] 发送 /start 可以收到回复
- [ ] 点击"开通/兑换会员"可以看到菜单
- [ ] 可以看到"💎 USDT充值购买"按钮

### 5.3 测试支付服务

```bash
# 启动支付服务（前台测试）
python3 tron.py
```

预期输出：
```
🚀 TRON支付服务启动中...
✅ 配置验证通过
📡 监听钱包: TXXXxxxXXXxxx...
⏱️ 轮询间隔: 10秒
🔐 最少确认数: 20
```

## 6. 创建测试订单

在Telegram中：
1. 点击"开通/兑换会员" → "💎 USDT充值购买"
2. 选择"7天会员 - 5 USDT"
3. 检查是否收到：
   - [ ] 订单信息
   - [ ] 支付金额（带随机小数）
   - [ ] 收款地址
   - [ ] 支付二维码

## 7. 小额测试支付

⚠️ **重要**: 建议先进行小额测试

1. 使用测试套餐（5 USDT）
2. 向收款地址转账精确金额
3. 等待约1-2分钟
4. 检查是否：
   - [ ] 收到支付成功通知
   - [ ] 会员已自动开通
   - [ ] 管理员收到通知（如果配置了）
   - [ ] 数据库中订单状态为 completed

查看日志：
```bash
tail -f tron.log | grep "交易匹配成功"
```

## 8. 安全检查

### 8.1 钱包安全

- [ ] 使用独立钱包专用于收款
- [ ] 已备份钱包私钥
- [ ] 定期将USDT转出到冷钱包
- [ ] 不在代码中硬编码私钥

### 8.2 .env 文件安全

```bash
# 检查.env文件权限
ls -la .env

# 应该是 -rw------- (600) 或 -rw-r----- (640)
# 如果不是，执行：
chmod 600 .env
```

### 8.3 .gitignore

```bash
# 确保敏感文件不会被提交
cat .gitignore | grep -E "\.env|\.db|\.log"
```

应该包含：
- .env
- *.db
- *.log

## 9. 部署到生产环境

### 9.1 使用 nohup（简单）

```bash
# 启动主机器人
nohup python3 tdata.py > tdata.log 2>&1 &

# 启动支付服务
nohup python3 tron.py > tron.log 2>&1 &

# 查看进程
ps aux | grep -E "tdata.py|tron.py"
```

### 9.2 使用 systemd（推荐）

```bash
# 复制服务文件
sudo cp tron-payment.service /etc/systemd/system/

# 编辑服务文件，修改路径和用户
sudo nano /etc/systemd/system/tron-payment.service

# 重新加载并启动
sudo systemctl daemon-reload
sudo systemctl start tron-payment
sudo systemctl enable tron-payment

# 查看状态
sudo systemctl status tron-payment
```

### 9.3 使用 screen/tmux

```bash
# Screen
screen -S tron
python3 tron.py
# Ctrl+A+D 断开

screen -S tdata
python3 tdata.py
# Ctrl+A+D 断开

# Tmux
tmux new -s tron
python3 tron.py
# Ctrl+B+D 断开

tmux new -s tdata
python3 tdata.py
# Ctrl+B+D 断开
```

## 10. 监控和维护

### 10.1 日志监控

```bash
# 实时查看支付服务日志
tail -f tron.log

# 查看错误
grep "❌" tron.log

# 查看成功支付
grep "✅.*交易匹配成功" tron.log
```

### 10.2 健康检查脚本

创建 `health_check.sh`:
```bash
#!/bin/bash
# 检查服务是否运行
if ! pgrep -f "tron.py" > /dev/null; then
    echo "⚠️ 支付服务未运行"
    # 自动重启
    nohup python3 /path/to/tron.py > /path/to/tron.log 2>&1 &
    echo "✅ 已重启支付服务"
fi
```

添加到 crontab:
```bash
# 每5分钟检查一次
*/5 * * * * /path/to/health_check.sh
```

### 10.3 数据库备份

```bash
# 创建备份脚本 backup_db.sh
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
cp payment.db payment.db.backup.$DATE
cp tdatabot.db tdatabot.db.backup.$DATE
echo "✅ 备份完成: $DATE"
```

添加到 crontab:
```bash
# 每天凌晨2点备份
0 2 * * * /path/to/backup_db.sh
```

### 10.4 日志轮转

创建 `/etc/logrotate.d/tron-payment`:
```
/path/to/tdatabot/tron.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 644 your_user your_user
}
```

## 11. 性能调优

### 11.1 调整轮询间隔

编辑 `tron.py`:
```python
# 高性能服务器
POLL_INTERVAL_SECONDS = 5  # 5秒

# 低性能或免费API
POLL_INTERVAL_SECONDS = 30  # 30秒
```

### 11.2 调整确认数

```python
# 快速到账（风险较高）
MIN_CONFIRMATIONS = 10

# 极安全（到账较慢）
MIN_CONFIRMATIONS = 50
```

## 12. 故障排查

### 问题1：订单创建失败
- 检查数据库权限
- 查看 `payment.db` 是否可写
- 检查用户是否有未完成订单

### 问题2：支付后未到账
- 确认支付服务是否运行：`ps aux | grep tron.py`
- 查看日志：`tail -f tron.log`
- 确认转账金额精确匹配
- 在 TronScan 查询交易状态

### 问题3：二维码无法显示
- 确认 qrcode 库已安装
- 检查 Pillow 是否正确安装
- 查看机器人日志

## 13. 最终验证清单

完成以下所有检查后，系统即可投入使用：

- [ ] 所有依赖已安装
- [ ] 配置文件已正确配置
- [ ] 数据库初始化成功
- [ ] 单元测试全部通过
- [ ] 机器人可以正常启动
- [ ] 支付服务可以正常启动
- [ ] 可以创建测试订单
- [ ] 小额测试支付成功
- [ ] 安全检查通过
- [ ] 日志监控正常
- [ ] 备份脚本已设置
- [ ] 健康检查已设置

## 14. 上线后关注

### 第1天
- [ ] 每小时检查一次日志
- [ ] 监控订单创建
- [ ] 监控支付到账
- [ ] 收集用户反馈

### 第1周
- [ ] 每天检查日志
- [ ] 统计支付成功率
- [ ] 统计平均到账时间
- [ ] 优化配置参数

### 长期
- [ ] 每周检查一次
- [ ] 定期备份数据库
- [ ] 关注 TRON 网络状态
- [ ] 更新依赖包（谨慎）

## 支持

如遇问题：
1. 查看 [PAYMENT_README.md](PAYMENT_README.md) 详细文档
2. 查看日志文件排查问题
3. 提交 GitHub Issue
4. 联系技术支持

---

✅ **验证完成后，系统即可正式使用！**
