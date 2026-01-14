#!/bin/bash
# USDT-TRC20 支付系统安装脚本

echo "================================"
echo "USDT-TRC20 支付系统安装向导"
echo "================================"
echo ""

# 检查Python版本
echo "🔍 检查Python版本..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ Python版本: $python_version"
echo ""

# 安装依赖
echo "📦 安装依赖包..."
pip3 install -r requirements_payment.txt
if [ $? -eq 0 ]; then
    echo "✅ 依赖安装成功"
else
    echo "❌ 依赖安装失败"
    exit 1
fi
echo ""

# 检查.env文件
echo "🔧 检查配置文件..."
if [ ! -f .env ]; then
    echo "⚠️  未找到 .env 文件，正在创建..."
    cat > .env << EOF
# TRON钱包配置（必需）
TRON_WALLET_ADDRESS=

# TronGrid API Key（建议申请）
# 申请地址: https://www.trongrid.io/
TRONGRID_API_KEY=

# Telegram配置（必需）
TELEGRAM_BOT_TOKEN=

# 管理员通知（可选）
TELEGRAM_NOTIFY_CHAT_ID=
EOF
    echo "✅ 已创建 .env 模板文件"
    echo "⚠️  请编辑 .env 文件填写配置信息"
    echo ""
else
    echo "✅ .env 文件已存在"
    echo ""
fi

# 测试配置
echo "🧪 测试配置..."
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()

wallet = os.getenv('TRON_WALLET_ADDRESS', '')
token = os.getenv('TELEGRAM_BOT_TOKEN', '')

if not wallet:
    print('❌ 未配置 TRON_WALLET_ADDRESS')
    exit(1)
    
if not token:
    print('❌ 未配置 TELEGRAM_BOT_TOKEN')
    exit(1)

print('✅ 配置验证通过')
print(f'📡 收款钱包: {wallet}')
print(f'🤖 Bot Token: {token[:10]}...')
"

if [ $? -eq 0 ]; then
    echo ""
    echo "================================"
    echo "✅ 安装完成！"
    echo "================================"
    echo ""
    echo "启动支付监听服务："
    echo "  nohup python3 tron.py > tron.log 2>&1 &"
    echo ""
    echo "查看日志："
    echo "  tail -f tron.log"
    echo ""
    echo "停止服务："
    echo "  ps aux | grep tron.py"
    echo "  kill <PID>"
    echo ""
else
    echo ""
    echo "❌ 配置验证失败"
    echo "请编辑 .env 文件填写正确的配置信息"
    echo ""
fi
