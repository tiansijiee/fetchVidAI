"""
测试下载次数扣减
"""
import sys
import io

# 设置标准输出为UTF-8编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
import json
import time

BASE_URL = "http://localhost:5000"

print("=" * 60)
print("测试下载次数扣减")
print("=" * 60)

# 使用新的fingerprint
test_fp = "test_fp_download_888"
headers = {
    "Content-Type": "application/json",
    "X-Fingerprint": test_fp,
    "X-Request-ID": "test_dl_001"
}

# 1. 初始检查
print("\n1. 初始检查")
response = requests.get(f"{BASE_URL}/api/quota/remaining", headers=headers)
result = response.json()
print(f"初始状态: 解析={result['data']['parse_remaining']}/{result['data']['parse_limit']}, 下载={result['data']['download_remaining']}/{result['data']['download_limit']}")

# 2. 直接扣减下载次数
print("\n2. 直接扣减下载次数")
from auth.quota_manager import quota_manager

success = quota_manager.consume_quota(None, test_fp, 'download', 'test_dl_001')
print(f"扣次结果: {success}")

# 3. 检查扣次后状态
print("\n3. 检查扣次后状态")
allowed, message, info = quota_manager.check_quota(None, test_fp, 'download')
print(f"下载检查 - allowed: {allowed}")
print(f"消息: {message}")

# 4. 测试第二次下载请求（应该被阻止）
print("\n4. 测试第二次下载请求（应该被阻止）")
download_data = {
    "video_info": {
        "title": "测试视频",
        "uploader": "测试UP主",
        "url": "https://www.bilibili.com/video/BV1xx411c7mu"
    },
    "options": {
        "format": "mp4"
    }
}
headers["X-Request-ID"] = "test_dl_002"
response = requests.post(f"{BASE_URL}/api/proxy/download", json=download_data, headers=headers)
print(f"状态码: {response.status_code}")
if response.status_code == 403:
    result = response.json()
    print(f"✓ 下载请求被正确阻止")
    print(f"错误消息: {result.get('message')}")
    print(f"错误代码: {result.get('code')}")
elif response.status_code == 200:
    result = response.json()
    if result.get('success'):
        print(f"✗ 下载请求未被阻止，任务ID: {result.get('task_id')}")
        print("这表示权限检查可能没有生效")
else:
    print(f"响应: {response.json()}")

# 5. 通过API验证最终状态
print("\n5. 通过API验证最终状态")
response = requests.get(f"{BASE_URL}/api/quota/remaining", headers=headers)
result = response.json()
print(f"最终状态: 解析={result['data']['parse_remaining']}/{result['data']['parse_limit']}, 下载={result['data']['download_remaining']}/{result['data']['download_limit']}")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)
