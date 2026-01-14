# Payment System Fixes - Verification Guide

This document verifies the fixes for the three payment system issues.

## Issue 1: Missing Cancel Order Button ✅ FIXED

### Problem
The order page only showed QR code and information, with no cancel button.

### Solution
Added cancel button directly to the QR code photo message.

### Code Changes
**File: `tdata.py`**

```python
# Line 17271-17276: Added keyboard with cancel button
keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton("❌ 取消订单", callback_data=f"cancel_order:{order.order_id}")],
    [InlineKeyboardButton("🔙 返回主菜单", callback_data="back_to_main")]
])

query.message.bot.send_photo(
    chat_id=user_id,
    photo=photo,
    caption=caption,
    parse_mode='HTML',
    reply_markup=keyboard  # ← Added this parameter
)
```

**File: `tdata.py`**
```python
# Line 12768-12774: Updated callback handler to support both formats
elif data.startswith("cancel_order"):
    # Support both formats: cancel_order_ID and cancel_order:ID
    if ":" in data:
        order_id = data.split(":", 1)[1]
    else:
        order_id = data.replace("cancel_order_", "")
    self.handle_cancel_order(query, order_id)
```

### Verification
1. Create a payment order
2. The QR code photo message now includes:
   - ❌ 取消订单 button
   - 🔙 返回主菜单 button
3. Clicking the cancel button cancels the order

---

## Issue 2: Membership Granting Fails - Table Not Exists ✅ FIXED

### Problem
Error: `no such table: memberships`

### Solution
Added automatic table creation in `grant_membership` method.

### Code Changes
**File: `tron.py`**

```python
# Line 999-1007: Auto-create memberships table
async def grant_membership(self, order: PaymentOrder) -> bool:
    # ... existing code ...
    
    conn = sqlite3.connect(PaymentConfig.MAIN_DB)
    c = conn.cursor()
    
    # 自动建表：确保 memberships 表存在
    c.execute("""
        CREATE TABLE IF NOT EXISTS memberships (
            user_id INTEGER PRIMARY KEY,
            level TEXT DEFAULT '会员',
            expiry_time TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    """)
    
    # 检查用户是否已有会员记录
    c.execute("SELECT expiry_time FROM memberships WHERE user_id = ?", (order.user_id,))
    # ... rest of the code ...
```

### Verification
1. Delete the `memberships` table from the database (or use a new database)
2. Complete a payment
3. The system automatically creates the `memberships` table
4. Membership is granted successfully without errors

---

## Issue 3: Transaction Matching Security Vulnerabilities ✅ FIXED

### Problem
Three security vulnerabilities:
1. Old transactions could match new orders
2. Expired orders could be matched
3. Multiple users with same amount could conflict

### Solution
Implemented comprehensive security checks:

#### 3.1 Amount Uniqueness Check

**File: `tron.py`**

```python
# Line 435-454: Added is_amount_in_use method
def is_amount_in_use(self, amount: float) -> bool:
    """检查金额是否已被待支付订单使用"""
    try:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute("""
            SELECT 1 FROM orders 
            WHERE status = ? 
            AND ABS(amount - ?) < 0.00001
            LIMIT 1
        """, (OrderStatus.PENDING.value, amount))
        
        result = c.fetchone()
        conn.close()
        
        return result is not None
    except Exception as e:
        logger.error(f"❌ 检查金额失败: {e}")
        return True  # 出错时保守处理
```

#### 3.2 Generate Unique Amounts with Retries

**File: `tron.py`**

```python
# Line 497-510: Modified create_payment_order
# 生成唯一金额，最多尝试 50 次
base_amount = plan["price"]
max_attempts = 50
amount = None

for attempt in range(max_attempts):
    random_decimal = random.randint(1, 9999) / 10000  # 0.0001 - 0.9999
    candidate_amount = base_amount + random_decimal
    
    if not self.db.is_amount_in_use(candidate_amount):
        amount = candidate_amount
        break

if amount is None:
    logger.error(f"❌ 无法生成唯一金额")
    return None
```

#### 3.3 Comprehensive Transaction Matching Security Checks

**File: `tron.py`**

```python
# Line 876-924: Enhanced transaction matching with 5 security checks

# 验证合约地址
if tx.contract_address != PaymentConfig.USDT_CONTRACT:
    logger.warning(f"⚠️ 非官方USDT合约: {tx.contract_address}")
    tx.processed = True
    self.db.save_transaction(tx)
    continue

# 获取交易时间
tx_time = datetime.fromtimestamp(tx.timestamp, tz=BEIJING_TZ)
now = datetime.now(BEIJING_TZ)

# 安全检查1: 交易不能太旧（15分钟内）
if (now - tx_time).total_seconds() > 900:
    logger.info(f"⏱️ 交易太旧（超过15分钟），标记已处理: {tx.tx_hash[:16]}...")
    tx.processed = True
    self.db.save_transaction(tx)
    continue

# 匹配订单
matched_order = None
for order in pending_orders:
    # 安全检查2: 订单必须未过期
    order_expires = order.expires_at
    if order_expires.tzinfo is None:
        order_expires = order_expires.replace(tzinfo=BEIJING_TZ)
    
    if now > order_expires:
        self.db.update_order_status(order.order_id, OrderStatus.EXPIRED)
        continue
    
    # 安全检查3: 金额精确匹配
    if abs(tx.amount - order.amount) >= 0.0001:
        continue
    
    # 安全检查4: 交易时间必须在订单创建之后
    order_created = order.created_at
    if order_created.tzinfo is None:
        order_created = order_created.replace(tzinfo=BEIJING_TZ)
    
    if tx_time < order_created - timedelta(minutes=1):
        continue
    
    # 安全检查5: 交易时间必须在订单有效期内
    if tx_time > order_expires:
        continue
    
    matched_order = order
    break

# Process matched order...

else:
    # 未匹配的交易也标记已处理
    logger.info(f"ℹ️ 交易未匹配订单: {tx.amount:.4f} USDT")
    tx.processed = True
    self.db.save_transaction(tx)
```

### Security Checklist

| Check | Purpose | Status |
|-------|---------|--------|
| Amount uniqueness | Prevents same amount conflicts | ✅ |
| Transaction age < 15 min | Prevents old transaction matching | ✅ |
| Order not expired | Prevents expired order matching | ✅ |
| TX time > Order creation | Prevents old TX matching new order | ✅ |
| TX time < Order expiry | Prevents payment after expiry | ✅ |
| 20 block confirmations | Prevents double-spend attacks | ✅ |
| Mark all TX as processed | Prevents re-processing | ✅ |
| Invalid contract rejection | Prevents wrong token matching | ✅ |

### Verification

#### Test 1: Amount Uniqueness
```python
# Create two orders for different users
order1 = create_payment_order(user_id=111, plan_id="plan_7d")
order2 = create_payment_order(user_id=222, plan_id="plan_7d")

# Verify amounts are different
assert order1.amount != order2.amount
```

#### Test 2: Old Transaction Rejection
```python
# Transaction timestamp is 20 minutes old
old_tx_time = now - timedelta(minutes=20)

# This transaction should be marked as processed and not matched
# Because: (now - tx_time).total_seconds() > 900
```

#### Test 3: Transaction Before Order
```python
# Order created at: 2026-01-14 10:00:00
# Transaction timestamp: 2026-01-14 09:55:00

# This transaction should NOT match
# Because: tx_time < order_created - timedelta(minutes=1)
```

#### Test 4: Transaction After Order Expiry
```python
# Order expires at: 2026-01-14 10:10:00
# Transaction timestamp: 2026-01-14 10:11:00

# This transaction should NOT match
# Because: tx_time > order_expires
```

#### Test 5: Expired Order Handling
```python
# Order has expired
# System automatically marks it as EXPIRED
# Will not match any transaction
```

---

## Summary

All three issues have been fixed with comprehensive solutions:

1. ✅ **Cancel button added** - Users can now cancel orders directly from the QR code message
2. ✅ **Auto-create table** - Membership table is automatically created if it doesn't exist
3. ✅ **Security hardening** - Multiple layers of security checks prevent all known vulnerabilities

### Testing

To test the payment system:
```bash
cd /home/runner/work/tdatabot/tdatabot
python3 test_payment.py
```

Note: Requires payment dependencies:
```bash
pip install aiohttp qrcode[pil] Pillow base58
```

### Files Modified
- `tdata.py`: Cancel button and callback handler
- `tron.py`: Table auto-creation, amount uniqueness, security checks
- `test_payment.py`: Added new security tests
