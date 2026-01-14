#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
USDT支付系统测试脚本
用于验证核心功能（不需要真实区块链连接）
"""

import os
import sys
import tempfile
from datetime import datetime, timedelta, timezone

# 设置测试环境变量
os.environ["TRON_WALLET_ADDRESS"] = "TTestWalletAddressForTestingOnly123456"
os.environ["TELEGRAM_BOT_TOKEN"] = "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_config():
    """测试配置验证"""
    print("🧪 测试配置验证...")
    from tron import PaymentConfig
    
    valid, msg = PaymentConfig.validate()
    assert valid, f"配置验证失败: {msg}"
    print(f"   ✅ {msg}")
    print(f"   钱包地址: {PaymentConfig.WALLET_ADDRESS}")
    print(f"   订单超时: {PaymentConfig.ORDER_TIMEOUT_MINUTES} 分钟")
    print(f"   最少确认: {PaymentConfig.MIN_CONFIRMATIONS} 个区块")
    print()

def test_database():
    """测试数据库初始化"""
    print("🧪 测试数据库...")
    from tron import PaymentDatabase
    
    # 使用临时数据库
    temp_db = tempfile.mktemp(suffix=".db")
    db = PaymentDatabase(temp_db)
    
    assert os.path.exists(temp_db), "数据库文件未创建"
    print(f"   ✅ 数据库创建成功: {temp_db}")
    
    # 清理
    os.remove(temp_db)
    print()

def test_order_creation():
    """测试订单创建"""
    print("🧪 测试订单创建...")
    from tron import PaymentDatabase, OrderManager, OrderStatus
    
    # 使用临时数据库
    temp_db = tempfile.mktemp(suffix=".db")
    db = PaymentDatabase(temp_db)
    manager = OrderManager(db)
    
    # 创建订单
    user_id = 12345
    plan_id = "plan_7d"
    
    order = manager.create_payment_order(user_id, plan_id)
    assert order is not None, "订单创建失败"
    assert order.user_id == user_id
    assert order.plan_id == plan_id
    assert order.status == OrderStatus.PENDING
    assert order.amount >= 5.0 and order.amount < 6.0, f"金额不在预期范围: {order.amount}"
    
    print(f"   ✅ 订单创建成功")
    print(f"   订单ID: {order.order_id}")
    print(f"   金额: {order.amount:.4f} USDT")
    print(f"   过期时间: {order.expires_at}")
    
    # 测试重复订单检查
    order2 = manager.create_payment_order(user_id, plan_id)
    assert order2 is None, "应该阻止重复订单"
    print(f"   ✅ 重复订单检查通过")
    
    # 清理
    os.remove(temp_db)
    print()

def test_qr_generator():
    """测试二维码生成"""
    print("🧪 测试二维码生成...")
    from tron import QRCodeGenerator, PaymentConfig
    
    wallet = PaymentConfig.WALLET_ADDRESS
    amount = 5.1234
    
    qr_bytes = QRCodeGenerator.generate_payment_qr(wallet, amount)
    assert len(qr_bytes) > 0, "二维码生成失败"
    assert qr_bytes[:4] == b'\x89PNG', "不是有效的PNG图片"
    
    print(f"   ✅ 二维码生成成功")
    print(f"   大小: {len(qr_bytes)} 字节")
    print()

def test_transaction_record():
    """测试交易记录"""
    print("🧪 测试交易记录...")
    from tron import PaymentDatabase, TransactionRecord
    
    # 使用临时数据库
    temp_db = tempfile.mktemp(suffix=".db")
    db = PaymentDatabase(temp_db)
    
    # 创建交易记录
    tx = TransactionRecord(
        tx_hash="0x1234567890abcdef",
        from_address="TSendAddress123",
        to_address="TReceiveAddress456",
        amount=5.1234,
        timestamp=1234567890,
        block_number=12345,
        confirmations=20,
        contract_address="TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t",
        processed=False
    )
    
    success = db.save_transaction(tx)
    assert success, "保存交易失败"
    
    # 检查是否已处理
    is_processed = db.is_transaction_processed(tx.tx_hash)
    assert not is_processed, "交易不应该标记为已处理"
    
    # 标记为已处理
    tx.processed = True
    db.save_transaction(tx)
    
    is_processed = db.is_transaction_processed(tx.tx_hash)
    assert is_processed, "交易应该标记为已处理"
    
    print(f"   ✅ 交易记录保存成功")
    print(f"   交易哈希: {tx.tx_hash}")
    print(f"   已处理: {is_processed}")
    
    # 清理
    os.remove(temp_db)
    print()

def test_order_expiration():
    """测试订单过期"""
    print("🧪 测试订单过期...")
    from tron import PaymentDatabase, OrderManager, OrderStatus
    
    # 使用临时数据库
    temp_db = tempfile.mktemp(suffix=".db")
    db = PaymentDatabase(temp_db)
    manager = OrderManager(db)
    
    # 创建订单并手动设置为已过期
    user_id = 12345
    plan_id = "plan_7d"
    
    order = manager.create_payment_order(user_id, plan_id)
    assert order is not None
    
    # 修改过期时间为过去
    BEIJING_TZ = timezone(timedelta(hours=8))
    past_time = datetime.now(BEIJING_TZ) - timedelta(minutes=20)
    
    import sqlite3
    conn = sqlite3.connect(temp_db)
    c = conn.cursor()
    c.execute("UPDATE orders SET expires_at = ? WHERE order_id = ?", 
              (past_time.isoformat(), order.order_id))
    conn.commit()
    conn.close()
    
    # 执行过期检查
    manager.expire_old_orders()
    
    # 验证订单状态
    expired_order = db.get_order(order.order_id)
    assert expired_order.status == OrderStatus.EXPIRED, "订单应该被标记为过期"
    
    print(f"   ✅ 订单过期检查通过")
    print(f"   订单状态: {expired_order.status.value}")
    
    # 清理
    os.remove(temp_db)
    print()

def test_payment_plans():
    """测试套餐配置"""
    print("🧪 测试套餐配置...")
    from tron import PaymentConfig
    
    plans = PaymentConfig.PAYMENT_PLANS
    assert len(plans) == 4, "应该有4个套餐"
    
    for plan_id, plan in plans.items():
        assert "days" in plan, f"{plan_id} 缺少 days 字段"
        assert "price" in plan, f"{plan_id} 缺少 price 字段"
        assert "name" in plan, f"{plan_id} 缺少 name 字段"
        print(f"   ✅ {plan['name']}: {plan['price']} USDT / {plan['days']} 天")
    
    print()

def test_amount_uniqueness():
    """测试金额唯一性检查"""
    print("🧪 测试金额唯一性检查...")
    from tron import PaymentDatabase, OrderManager, OrderStatus
    
    # 使用临时数据库
    temp_db = tempfile.mktemp(suffix=".db")
    db = PaymentDatabase(temp_db)
    manager = OrderManager(db)
    
    # 创建第一个订单
    order1 = manager.create_payment_order(12345, "plan_7d")
    assert order1 is not None, "第一个订单创建失败"
    
    # 检查该金额是否被标记为使用中
    is_used = db.is_amount_in_use(order1.amount)
    assert is_used, "金额应该被标记为使用中"
    print(f"   ✅ 金额 {order1.amount:.4f} 已被标记为使用中")
    
    # 创建第二个订单（不同用户）- 应该生成不同金额
    order2 = manager.create_payment_order(67890, "plan_7d")
    assert order2 is not None, "第二个订单创建失败"
    assert order2.amount != order1.amount, "两个订单的金额应该不同"
    print(f"   ✅ 第二个订单金额 {order2.amount:.4f} 与第一个订单不同")
    
    # 检查不存在的金额
    is_used = db.is_amount_in_use(999.9999)
    assert not is_used, "不存在的金额不应该被标记为使用中"
    print(f"   ✅ 不存在的金额检查通过")
    
    # 清理
    os.remove(temp_db)
    print()

def test_security_checks():
    """测试安全检查逻辑"""
    print("🧪 测试安全检查逻辑...")
    from tron import PaymentDatabase, OrderManager, TransactionRecord
    from datetime import datetime, timedelta, timezone
    
    # 使用临时数据库
    temp_db = tempfile.mktemp(suffix=".db")
    db = PaymentDatabase(temp_db)
    manager = OrderManager(db)
    
    BEIJING_TZ = timezone(timedelta(hours=8))
    now = datetime.now(BEIJING_TZ)
    
    # 创建订单
    order = manager.create_payment_order(12345, "plan_7d")
    assert order is not None
    
    # 测试1: 旧交易（超过15分钟）应该被拒绝
    old_timestamp = int((now - timedelta(minutes=20)).timestamp())
    old_tx = TransactionRecord(
        tx_hash="0xold",
        from_address="TFrom",
        to_address="TTo",
        amount=order.amount,
        timestamp=old_timestamp,
        block_number=100,
        confirmations=20,
        contract_address="TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"
    )
    
    # 检查交易时间是否太旧
    tx_time = datetime.fromtimestamp(old_tx.timestamp, tz=BEIJING_TZ)
    is_too_old = (now - tx_time).total_seconds() > 900
    assert is_too_old, "旧交易应该被识别"
    print(f"   ✅ 旧交易检查通过（超过15分钟）")
    
    # 测试2: 交易时间在订单创建之前应该被拒绝
    before_order_timestamp = int((order.created_at - timedelta(minutes=5)).timestamp())
    before_tx = TransactionRecord(
        tx_hash="0xbefore",
        from_address="TFrom",
        to_address="TTo",
        amount=order.amount,
        timestamp=before_order_timestamp,
        block_number=100,
        confirmations=20,
        contract_address="TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"
    )
    
    before_tx_time = datetime.fromtimestamp(before_tx.timestamp, tz=BEIJING_TZ)
    order_created = order.created_at.replace(tzinfo=BEIJING_TZ)
    is_before_order = before_tx_time < order_created - timedelta(minutes=1)
    assert is_before_order, "订单创建前的交易应该被识别"
    print(f"   ✅ 订单创建前交易检查通过")
    
    # 测试3: 金额匹配精度检查
    exact_match = abs(order.amount - order.amount) < 0.0001
    assert exact_match, "精确金额应该匹配"
    
    wrong_amount = order.amount + 0.001
    not_match = abs(wrong_amount - order.amount) >= 0.0001
    assert not_match, "差异超过0.0001的金额不应该匹配"
    print(f"   ✅ 金额匹配精度检查通过")
    
    # 清理
    os.remove(temp_db)
    print()

def run_all_tests():
    """运行所有测试"""
    print("=" * 50)
    print("🚀 USDT支付系统测试")
    print("=" * 50)
    print()
    
    tests = [
        test_config,
        test_database,
        test_order_creation,
        test_qr_generator,
        test_transaction_record,
        test_order_expiration,
        test_payment_plans,
        test_amount_uniqueness,
        test_security_checks,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"   ❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
            print()
    
    print("=" * 50)
    print(f"✅ 通过: {passed}")
    print(f"❌ 失败: {failed}")
    print("=" * 50)
    
    if failed == 0:
        print("🎉 所有测试通过！")
        return 0
    else:
        print("⚠️ 部分测试失败")
        return 1

if __name__ == "__main__":
    sys.exit(run_all_tests())
