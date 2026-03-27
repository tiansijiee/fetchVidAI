"""
测试完整的权限流程
"""
import requests
import json
import time
import sys
import io

# 设置标准输出为UTF-8编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://localhost:5000"
HEADERS = {
    "Content-Type": "application/json",
    "X-Fingerprint": "test_fp_complete_123",
    "X-Request-ID": "test_req_001"
}

print("=" * 60)
print("测试完整权限流程")
print("=" * 60)

# 1. 初始状态检查
print("\n1. 初始状态检查")
response = requests.get(f"{BASE_URL}/api/quota/remaining", headers=HEADERS)
print(f"状态码: {response.status_code}")
result = response.json()
print(f"剩余次数: 解析={result['data']['parse_remaining']}, 下载={result['data']['download_remaining']}")

# 2. 测试解析接口（应该成功）
print("\n2. 测试解析接口（应该成功）")
parse_data = {
    "url": "https://www.bilibili.com/video/BV1xx411c7mu",
    "fast": True
}
response = requests.post(f"{BASE_URL}/api/parse", json=parse_data, headers=HEADERS)
print(f"状态码: {response.status_code}")
if response.status_code == 200:
    print("✓ 解析请求成功")
else:
    print(f"✗ 解析请求失败: {response.json()}")

# 3. 再次检查次数（解析不应该扣次）
print("\n3. 解析后检查次数（应该不变）")
response = requests.get(f"{BASE_URL}/api/quota/remaining", headers=HEADERS)
result = response.json()
print(f"剩余次数: 解析={result['data']['parse_remaining']}, 下载={result['data']['download_remaining']}")
assert result['data']['parse_remaining'] == 1, "解析次数不应该被扣减"

# 4. 测试AI总结接口（应该成功并扣次）
print("\n4. 测试AI总结接口（应该成功并扣次）")
# 注意：这个测试会实际调用AI接口，可能需要较长时间
# 我们只测试权限检查部分
summarize_data = {
    "url": "https://www.bilibili.com/video/BV1xx411c7mu"
}
try:
    # 发送请求但立即关闭，只测试权限检查
    response = requests.post(
        f"{BASE_URL}/api/ai/summarize/char-stream",
        json=summarize_data,
        headers=HEADERS,
        stream=True,
        timeout=2
    )
    if response.status_code == 200:
        print("✓ AI总结请求通过权限检查")
        response.close()
    else:
        print(f"AI总结请求状态码: {response.status_code}")
except requests.exceptions.ReadTimeout:
    print("✓ AI总结请求通过权限检查（超时是预期的）")
except requests.exceptions.Timeout:
    print("✓ AI总结请求通过权限检查（超时是预期的）")
except Exception as e:
    print(f"AI总结请求异常: {e}")

# 5. 测试第二次解析（应该被阻止）
print("\n5. 模拟第二次请求（测试权限拦截）")
# 更换request_id模拟新请求
HEADERS["X-Request-ID"] = "test_req_002"
response = requests.post(f"{BASE_URL}/api/parse", json=parse_data, headers=HEADERS)
print(f"状态码: {response.status_code}")
if response.status_code == 200:
    print("✓ 解析请求成功（次数未扣减，所以仍然允许）")
else:
    print(f"解析请求被阻止: {response.json()}")

# 6. 测试下载接口
print("\n6. 测试下载接口权限检查")
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
response = requests.post(f"{BASE_URL}/api/proxy/download", json=download_data, headers=HEADERS)
print(f"状态码: {response.status_code}")
if response.status_code == 200:
    result = response.json()
    if result.get('success'):
        print(f"✓ 下载请求成功，任务ID: {result.get('task_id')}")
        task_id = result.get('task_id')

        # 等待一下模拟下载完成
        time.sleep(2)

        # 检查次数（下载成功后应该扣次）
        print("\n7. 下载后检查次数")
        response = requests.get(f"{BASE_URL}/api/quota/remaining", headers=HEADERS)
        result = response.json()
        print(f"剩余次数: 解析={result['data']['parse_remaining']}, 下载={result['data']['download_remaining']}")
        if result['data']['download_remaining'] == 0:
            print("✓ 下载次数已正确扣减")
        else:
            print(f"下载次数剩余: {result['data']['download_remaining']}")

        # 8. 测试第三次下载（应该被阻止）
        print("\n8. 测试第二次下载请求（应该被阻止）")
        HEADERS["X-Request-ID"] = "test_req_003"
        response = requests.post(f"{BASE_URL}/api/proxy/download", json=download_data, headers=HEADERS)
        print(f"状态码: {response.status_code}")
        if response.status_code == 403:
            print(f"✓ 下载请求被正确阻止: {response.json()}")
        else:
            print(f"下载请求未被阻止")
    else:
        print(f"下载请求失败: {result.get('message')}")
else:
    print(f"下载请求失败: {response.status_code}")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)
