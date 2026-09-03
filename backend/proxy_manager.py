"""
代理管理模块 - 支持B站等平台的代理访问
通过环境变量控制是否启用代理
"""
import os
import requests
import time
from typing import Optional
import threading


class ProxyManager:
    """代理管理器 - 支持代理池获取和轮换"""

    def __init__(self):
        self.proxies = []  # 代理列表
        self.current_index = 0
        self.last_fetch_time = 0
        self.fetch_interval = 300  # 5分钟刷新一次
        self.lock = threading.Lock()

        # 从环境变量加载配置
        self.proxy_enabled = os.getenv('PROXY_ENABLED', 'false').lower() == 'true'
        self.proxy_api_url = os.getenv('PROXY_API_URL', '')
        self.static_proxy = os.getenv('STATIC_PROXY', '')  # 静态代理: http://user:pass@host:port
        self.bilibili_proxy = os.getenv('BILIBILI_PROXY', '')  # B站专用代理

        if self.proxy_enabled:
            print("[PROXY] 代理功能已启用", file=__import__('sys').stderr)
            # 初始化代理
            if self.static_proxy or self.bilibili_proxy:
                print(f"[PROXY] 使用静态代理配置", file=__import__('sys').stderr)
            elif self.proxy_api_url:
                self._fetch_proxies()
        else:
            print("[PROXY] 代理功能未启用（本地模式）", file=__import__('sys').stderr)

    def _fetch_proxies(self) -> bool:
        """从代理API获取代理列表"""
        if not self.proxy_api_url:
            return False

        try:
            current_time = time.time()
            if current_time - self.last_fetch_time < self.fetch_interval and self.proxies:
                return True

            print(f"[PROXY] 正在获取代理列表...", file=__import__('sys').stderr)

            response = requests.get(self.proxy_api_url, timeout=10)
            response.raise_for_status()

            new_proxies = []
            for line in response.text.strip().split('\n'):
                line = line.strip()
                if line and ':' in line:
                    if not line.startswith('http'):
                        line = f'http://{line}'
                    new_proxies.append(line)

            if new_proxies:
                with self.lock:
                    self.proxies = new_proxies
                    self.current_index = 0
                    self.last_fetch_time = current_time
                    print(f"[PROXY] ✓ 获取到 {len(new_proxies)} 个代理", file=__import__('sys').stderr)
                    return True

            return False

        except Exception as e:
            print(f"[PROXY] ✗ 获取代理失败: {e}", file=__import__('sys').stderr)
            return bool(self.proxies)

    def get_proxy(self, platform: str = None) -> Optional[str]:
        """获取代理URL"""
        if not self.proxy_enabled:
            return None

        # 平台特定代理（优先）
        if platform == 'bilibili' and self.bilibili_proxy:
            return self.bilibili_proxy

        # 静态代理
        if self.static_proxy:
            return self.static_proxy

        # 代理池轮换
        with self.lock:
            if not self.proxies:
                if not self._fetch_proxies():
                    return None

            if not self.proxies:
                return None

            proxy = self.proxies[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.proxies)
            return proxy

    def get_proxy_dict(self, platform: str = None) -> Optional[dict]:
        """获取requests格式的代理字典"""
        proxy_url = self.get_proxy(platform)
        if proxy_url:
            return {'http': proxy_url, 'https': proxy_url}
        return None

    def mark_failed(self, proxy_url: str):
        """标记失效代理"""
        with self.lock:
            if proxy_url in self.proxies:
                self.proxies.remove(proxy_url)
                print(f"[PROXY] 移除失效代理，剩余: {len(self.proxies)}", file=__import__('sys').stderr)


# 全局实例
_proxy_manager = None


def get_proxy_manager() -> ProxyManager:
    global _proxy_manager
    if _proxy_manager is None:
        _proxy_manager = ProxyManager()
    return _proxy_manager
