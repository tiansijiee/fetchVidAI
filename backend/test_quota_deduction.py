"""
直接测试次数扣减逻辑
"""
import sys
import io

# 设置标准输出为UTF-8编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
import json

BASE_URL = "http://localhost:5000"

print("=" * 60)
print("测试次数扣减逻辑")
print("=" * 60)

# 使用新的fingerprint
test_fp = "test_fp_deduction_999"
headers = {
    "Content-Type": "application/json",
    "X-Fingerprint": test_fp
}

# 1. 初始检查
print("\n1. 初始检查")
response = requests.get(f"{BASE_URL}/api/quota/remaining", headers=headers)
result = response.json()
print(f"初始状态: 解析={result['data']['parse_remaining']}/{result['data']['parse_limit']}, 下载={result['data']['download_remaining']}/{result['data']['download_limit']}")

# 2. 直接调用consume接口测试扣次
print("\n2. 直接测试扣次逻辑")
import sqlite3
import os
from auth.quota_manager import quota_manager

# 测试扣次
print("   扣除1次解析次数...")
success = quota_manager.consume_quota(None, test_fp, 'parse', 'test_req_001')
print(f"   扣次结果: {success}")

# 3. 检查扣次后的状态
print("\n3. 检查扣次后状态")
allowed, message, info = quota_manager.check_quota(None, test_fp, 'parse')
print(f"   解析检查 - allowed: {allowed}, remaining: {info.get('parse_remaining', 'N/A')}")
print(f"   消息: {message}")

# 4. 测试第二次扣次（应该成功，因为游客有1次限制）
print("\n4. 测试第二次解析请求")
allowed, message, info = quota_manager.check_quota(None, test_fp, 'parse')
if not allowed:
    print(f"   ✓ 第二次请求被正确阻止")
    print(f"   原因: {message}")
else:
    print(f"   第二次请求仍然允许（remaining={info.get('parse_remaining', 'N/A')}）")
    # 尝试再次扣次
    success = quota_manager.consume_quota(None, test_fp, 'parse', 'test_req_002')
    print(f"   扣次结果: {success}")

# 5. 再次检查状态
print("\n5. 最终状态检查")
allowed, message, info = quota_manager.check_quota(None, test_fp, 'parse')
print(f"   解析检查 - allowed: {allowed}, remaining: {info.get('parse_remaining', 'N/A')}")

# 6. 检查下载次数
print("\n6. 检查下载次数")
allowed, message, info = quota_manager.check_quota(None, test_fp, 'download')
print(f"   下载检查 - allowed: {allowed}, remaining: {info.get('download_remaining', 'N/A')}")

# 7. 通过API验证
print("\n7. 通过API验证最终状态")
response = requests.get(f"{BASE_URL}/api/quota/remaining", headers=headers)
result = response.json()
print(f"   API返回: 解析={result['data']['parse_remaining']}/{result['data']['parse_limit']}, 下载={result['data']['download_remaining']}/{result['data']['download_limit']}")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)
