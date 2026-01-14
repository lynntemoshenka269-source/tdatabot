#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 USDT 支付系统的 i18n 多语言支持
"""

import sys
sys.path.insert(0, '.')

# 导入 i18n 模块
from i18n import get_text as t, set_user_language, get_user_language

def test_payment_i18n():
    """测试支付系统的多语言支持"""
    
    # 测试用户 ID
    test_user_id_zh = 123456  # 中文用户
    test_user_id_en = 234567  # 英文用户
    test_user_id_ru = 345678  # 俄语用户
    
    # 设置用户语言
    set_user_language(test_user_id_zh, 'zh')
    set_user_language(test_user_id_en, 'en')
    set_user_language(test_user_id_ru, 'ru')
    
    print("=" * 80)
    print("测试 USDT 支付系统 i18n 多语言支持")
    print("=" * 80)
    print()
    
    # 测试关键词
    test_keys = [
        'payment_menu_title',
        'payment_plan_7d',
        'payment_order_created',
        'payment_success_title',
        'payment_order_cancelled',
        'payment_error_existing_order',
        'btn_cancel_order',
        'btn_back_payment_menu',
    ]
    
    print("📋 测试关键翻译键值：")
    print()
    
    for key in test_keys:
        print(f"Key: {key}")
        print(f"  🇨🇳 中文: {t(test_user_id_zh, key)}")
        print(f"  🇬🇧 英文: {t(test_user_id_en, key)}")
        print(f"  🇷🇺 俄文: {t(test_user_id_ru, key)}")
        print()
    
    # 验证所有支付相关的键是否存在
    print("=" * 80)
    print("验证所有支付键是否存在于三种语言中")
    print("=" * 80)
    print()
    
    payment_keys = [
        # 支付菜单
        'payment_menu_title', 'payment_menu_desc',
        'payment_plan_7d', 'payment_plan_30d', 'payment_plan_120d', 'payment_plan_365d',
        'btn_back_payment_menu',
        
        # 订单创建
        'payment_order_created', 'payment_order_id', 'payment_order_info',
        'payment_amount', 'payment_plan', 'payment_days',
        'payment_valid_time', 'payment_minutes', 'payment_seconds',
        
        # 收款地址
        'payment_wallet_address', 'payment_address_click_copy',
        
        # 重要提示
        'payment_important_notice',
        'payment_notice_1', 'payment_notice_2', 'payment_notice_3', 'payment_notice_4',
        
        # 扫码支付
        'payment_scan_qr', 'payment_scan_desc',
        
        # 按钮
        'btn_cancel_order', 'btn_back_main_menu', 'btn_repurchase',
        
        # 订单取消
        'payment_order_cancelled', 'payment_order_cancelled_title',
        'payment_order_cancelled_status', 'payment_repurchase_hint',
        
        # 订单超时
        'payment_order_expired', 'payment_order_expired_title',
        'payment_order_expired_status', 'payment_expired_hint',
        
        # 支付成功
        'payment_success_title', 'payment_success_confirmed',
        'payment_order_info_title', 'payment_member_days',
        'payment_member_expiry', 'payment_thanks',
        'payment_tx_info_title', 'payment_tx_hash',
        
        # 管理员通知
        'payment_admin_new_order', 'payment_user_id',
        'payment_address_info', 'payment_receive_address',
        'payment_send_address', 'btn_view_transaction',
        
        # 错误消息
        'payment_error_existing_order', 'payment_error_create_failed',
        'payment_error_invalid_plan', 'payment_error_not_found',
        'payment_error_already_paid', 'payment_error_expired',
        
        # 状态
        'payment_status', 'payment_status_pending', 'payment_status_paid',
        'payment_status_completed', 'payment_status_expired', 'payment_status_cancelled',
    ]
    
    missing_keys = {'zh': [], 'en': [], 'ru': []}
    
    for key in payment_keys:
        # 检查中文
        zh_text = t(test_user_id_zh, key)
        if zh_text == key:  # 如果返回的是key本身，说明没有翻译
            missing_keys['zh'].append(key)
        
        # 检查英文
        en_text = t(test_user_id_en, key)
        if en_text == key:
            missing_keys['en'].append(key)
        
        # 检查俄文
        ru_text = t(test_user_id_ru, key)
        if ru_text == key:
            missing_keys['ru'].append(key)
    
    # 输出结果
    all_good = True
    for lang, keys in missing_keys.items():
        if keys:
            all_good = False
            print(f"❌ {lang.upper()} 缺少以下键:")
            for key in keys:
                print(f"   - {key}")
        else:
            print(f"✅ {lang.upper()} 所有键都存在")
    
    print()
    
    if all_good:
        print("=" * 80)
        print("✅ 所有测试通过！USDT 支付系统已成功添加 i18n 多语言支持")
        print("=" * 80)
        return True
    else:
        print("=" * 80)
        print("❌ 部分键缺失，请检查上述输出")
        print("=" * 80)
        return False

if __name__ == "__main__":
    success = test_payment_i18n()
    sys.exit(0 if success else 1)
