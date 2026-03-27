"""
测试API的权限系统
"""
import requests
import json

BASE_URL = "http://localhost:5000"
HEADERS = {
    "Content-Type": "application/json",
    "X-Fingerprint": "test_fp_visitor_123"
}

print("=" * 60)
print("测试API权限系统")
print("=" * 60)

# 1. 测试剩余次数接口
print("\n1. 测试剩余次数接口")
response = requests.get(f"{BASE_URL}/api/quota/remaining", headers=HEADERS)
print(f"状态码: {response.status_code}")
print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

# 2. 测试解析接口（第一次）
print("\n2. 测试解析接口（第一次）")
parse_data = {
    "url": "https://www.bilibili.com/video/BV1xx411c7mu",
    "fast": True  # 使用快速模式
}
response = requests.post(f"{BASE_URL}/api/parse", json=parse_data, headers=HEADERS)
print(f"状态码: {response.status_code}")
if response.status_code == 403:
    print(f"被阻止: {response.json()}")
else:
    print(f"成功")

# 3. 再次测试剩余次数
print("\n3. 再次测试剩余次数")
response = requests.get(f"{BASE_URL}/api/quota/remaining", headers=HEADERS)
print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

print("\n" + "=" * 60)
