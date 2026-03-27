"""
测试次数配额系统
"""
import sys
import os

# 添加路径
sys.path.insert(0, os.path.dirname(__file__))

from auth.quota_manager import quota_manager

print("=" * 50)
print("测试次数配额系统")
print("=" * 50)

# 测试游客fingerprint
test_fingerprint = "test_fp_12345"

# 1. 检查初始次数
print("\n1. 检查初始次数")
allowed, message, info = quota_manager.check_quota(None, test_fingerprint, 'parse')
print(f"解析检查 - allowed: {allowed}, message: {message}, info: {info}")

allowed, message, info = quota_manager.check_quota(None, test_fingerprint, 'download')
print(f"下载检查 - allowed: {allowed}, message: {message}, info: {info}")

# 2. 消耗1次解析次数
print("\n2. 消耗1次解析次数")
success = quota_manager.consume_quota(None, test_fingerprint, 'parse', 'test_req_1')
print(f"扣次结果: {success}")

# 3. 再次检查次数
print("\n3. 再次检查次数")
allowed, message, info = quota_manager.check_quota(None, test_fingerprint, 'parse')
print(f"解析检查 - allowed: {allowed}, message: {message}, info: {info}")

# 4. 尝试消耗第2次（应该失败）
print("\n4. 尝试消耗第2次解析次数（应该失败）")
allowed, message, info = quota_manager.check_quota(None, test_fingerprint, 'parse')
print(f"解析检查 - allowed: {allowed}, message: {message}, info: {info}")

if not allowed:
    print("✓ 权限检查正确阻止了第2次请求")
else:
    print("✗ 权限检查没有阻止第2次请求！")

# 5. 检查下载次数
print("\n5. 检查下载次数")
allowed, message, info = quota_manager.check_quota(None, test_fingerprint, 'download')
print(f"下载检查 - allowed: {allowed}, message: {message}, info: {info}")

# 6. 消耗1次下载次数
print("\n6. 消耗1次下载次数")
success = quota_manager.consume_quota(None, test_fingerprint, 'download', 'test_req_2')
print(f"扣次结果: {success}")

# 7. 再次检查下载次数
print("\n7. 再次检查下载次数")
allowed, message, info = quota_manager.check_quota(None, test_fingerprint, 'download')
print(f"下载检查 - allowed: {allowed}, message: {message}, info: {info}")

if not allowed:
    print("✓ 权限检查正确阻止了第2次下载请求")
else:
    print("✗ 权限检查没有阻止第2次下载请求！")

# 8. 检查数据库记录
print("\n8. 检查数据库记录")
import sqlite3

db_path = os.path.join(os.path.dirname(__file__), 'data', 'users.db')
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute('SELECT * FROM guest_quota WHERE fingerprint = ?', (test_fingerprint,))
result = cursor.fetchone()

if result:
    print(f"数据库记录: {dict(result)}")
else:
    print("没有找到数据库记录！")

conn.close()

print("\n" + "=" * 50)
print("测试完成")
print("=" * 50)
