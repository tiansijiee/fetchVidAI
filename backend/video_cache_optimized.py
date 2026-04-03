"""
优化的视频缓存模块 - 支持硬链接秒开和智能清理
"""
import os
import time
import json
import shutil
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class OptimizedVideoCache:
    """优化的视频缓存管理器"""

    def __init__(
        self,
        cache_dir: str = 'video_cache',
        ttl_days: int = 30,  # 热门视频缓存30天
        max_size_gb: float = 20.0,
        enable_hard_link: bool = True
    ):
        """
        初始化优化的缓存管理器

        Args:
            cache_dir: 缓存目录
            ttl_days: 缓存有效期（天）
            max_size_gb: 最大缓存大小（GB）
            enable_hard_link: 是否启用硬链接（秒开）
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.ttl_seconds = ttl_days * 86400
        self.max_size_bytes = max_size_gb * 1024 * 1024 * 1024
        self.enable_hard_link = enable_hard_link

        # 缓存统计
        self.stats = {
            'hits': 0,
            'misses': 0,
            'hard_link_served': 0,
            'copy_served': 0,
            'evicted': 0
        }

        # 热度统计（每个视频的访问次数）
        self.popularity_file = self.cache_dir / '.popularity.json'
        self.popularity = self._load_popularity()

        logger.info(f"[CACHE] Initialized with TTL={ttl_days} days, max_size={max_size_gb}GB")

    def _load_popularity(self) -> Dict:
        """加载热度统计"""
        try:
            if self.popularity_file.exists():
                with open(self.popularity_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"[CACHE] Failed to load popularity: {e}")
        return {}

    def _save_popularity(self):
        """保存热度统计"""
        try:
            with open(self.popularity_file, 'w', encoding='utf-8') as f:
                json.dump(self.popularity, f, ensure_ascii=False)
        except Exception as e:
            logger.error(f"[CACHE] Failed to save popularity: {e}")

    def _get_cache_path(self, video_id: str) -> tuple:
        """获取缓存文件路径"""
        mp4_path = self.cache_dir / f'{video_id}.mp4'
        json_path = self.cache_dir / f'{video_id}.json'
        return mp4_path, json_path

    def get(self, video_id: str, output_path: str) -> Optional[Dict]:
        """
        获取缓存文件（优先使用硬链接实现秒开）

        Args:
            video_id: 视频ID
            output_path: 输出文件路径

        Returns:
            缓存信息字典，如果缓存不存在或已过期则返回None
        """
        mp4_path, json_path = self._get_cache_path(video_id)

        # 检查缓存文件是否存在
        if not mp4_path.exists() or not json_path.exists():
            self.stats['misses'] += 1
            logger.debug(f"[CACHE] Miss: {video_id}")
            return None

        try:
            # 读取缓存元数据
            with open(json_path, 'r', encoding='utf-8') as f:
                cache_info = json.load(f)

            cached_at = cache_info.get('cached_at', 0)

            # 检查是否过期
            if time.time() - cached_at > self.ttl_seconds:
                logger.info(f"[CACHE] Expired: {video_id}")
                self._remove_cache(video_id)
                self.stats['misses'] += 1
                return None

            # 🔥 核心：使用硬链接实现秒开（不复制文件，不占用额外空间）
            output = Path(output_path)
            output.parent.mkdir(parents=True, exist_ok=True)

            try:
                # 尝试创建硬链接（秒开！）
                if self.enable_hard_link:
                    # 如果输出文件已存在，先删除
                    if output.exists():
                        output.unlink()

                    # 创建硬链接（瞬间完成，不占用额外空间）
                    os.link(str(mp4_path), str(output))
                    method = 'hard_link'
                    self.stats['hard_link_served'] += 1
                    logger.info(f"[CACHE] ⚡ SEC (hard link): {video_id} -> {output.name}")
                else:
                    # 降级到复制
                    shutil.copy2(str(mp4_path), str(output))
                    method = 'copy'
                    self.stats['copy_served'] += 1
                    logger.info(f"[CACHE] ✓ HIT (copy): {video_id}")

            except OSError as e:
                # 硬链接失败（可能是跨文件系统），降级到复制
                logger.warning(f"[CACHE] Hard link failed, using copy: {e}")
                shutil.copy2(str(mp4_path), str(output))
                method = 'copy'
                self.stats['copy_served'] += 1

            # 更新热度（修复bug）
            current_popularity = self.popularity.get(video_id, {})
            if isinstance(current_popularity, dict):
                # 已有的dict格式
                current_count = current_popularity.get('count', 0)
                self.popularity[video_id] = {
                    'count': current_count + 1,
                    'created_at': current_popularity.get('created_at', time.time()),
                    'last_access': time.time()
                }
            else:
                # 旧的int格式，升级为dict
                self.popularity[video_id] = {
                    'count': current_popularity + 1,
                    'created_at': time.time(),
                    'last_access': time.time()
                }
            self._save_popularity()

            self.stats['hits'] += 1

            return {
                'file_path': str(output),
                'filename': cache_info.get('filename', 'video.mp4'),
                'file_size': mp4_path.stat().st_size,
                'cached_at': cached_at,
                'age_days': (time.time() - cached_at) / 86400,
                'access_count': self.popularity[video_id].get('count', 0),
                'method': method
            }

        except Exception as e:
            logger.error(f"[CACHE] Error getting cache: {e}")
            self.stats['misses'] += 1
            return None

    def put(self, video_id: str, source_file: str, filename: str, metadata: Dict = None) -> bool:
        """
        保存文件到缓存

        Args:
            video_id: 视频ID
            source_file: 源文件路径
            filename: 原始文件名
            metadata: 额外的元数据

        Returns:
            是否成功保存
        """
        mp4_path, json_path = self._get_cache_path(video_id)
        source = Path(source_file)

        if not source.exists():
            logger.error(f"[CACHE] Source file not found: {source_file}")
            return False

        try:
            # 移动文件到缓存目录（比复制快）
            if mp4_path.exists():
                mp4_path.unlink()

            shutil.move(str(source), str(mp4_path))

            # 保存元数据
            cache_info = {
                'video_id': video_id,
                'filename': filename,
                'cached_at': time.time(),
                'file_size': mp4_path.stat().st_size,
                'metadata': metadata or {}
            }

            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(cache_info, f, ensure_ascii=False, indent=2)

            # 初始化热度
            self.popularity[video_id] = {
                'count': 0,
                'created_at': time.time(),
                'last_access': time.time()
            }
            self._save_popularity()

            logger.info(f"[CACHE] ✓ Saved: {video_id} ({cache_info['file_size'] / (1024*1024):.1f} MB)")
            return True

        except Exception as e:
            logger.error(f"[CACHE] Error saving cache: {e}")
            return False

    def _remove_cache(self, video_id: str):
        """删除缓存文件"""
        mp4_path, json_path = self._get_cache_path(video_id)

        try:
            if mp4_path.exists():
                mp4_path.unlink()
            if json_path.exists():
                json_path.unlink()
            if video_id in self.popularity:
                del self.popularity[video_id]
            self.stats['evicted'] += 1
        except Exception as e:
            logger.error(f"[CACHE] Error removing cache: {e}")

    def smart_cleanup(self) -> Dict:
        """
        智能清理策略：
        1. 删除过期的缓存
        2. 如果大小超限，删除热度最低的文件
        """
        removed = []
        now = time.time()

        # 第一步：删除过期缓存
        for json_path in self.cache_dir.glob('*.json'):
            if json_path.name.startswith('.'):
                continue

            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    cache_info = json.load(f)

                cached_at = cache_info.get('cached_at', 0)
                video_id = cache_info.get('video_id')

                # 检查是否过期
                if now - cached_at > self.ttl_seconds:
                    removed.append({
                        'video_id': video_id,
                        'reason': 'expired',
                        'age_days': (now - cached_at) / 86400
                    })
                    self._remove_cache(video_id)

            except Exception as e:
                logger.error(f"[CACHE] Error checking expiration: {e}")

        # 第二步：如果大小超限，按热度清理
        total_size = sum(f.stat().st_size for f in self.cache_dir.glob('*.mp4'))

        if total_size > self.max_size_bytes:
            # 按热度排序（访问次数少的优先删除）
            videos_by_popularity = sorted(
                [(vid, data.get('count', 0)) for vid, data in self.popularity.items()],
                key=lambda x: x[1]
            )

            while total_size > self.max_size_bytes * 0.8 and videos_by_popularity:
                video_id, count = videos_by_popularity.pop(0)
                mp4_path, _ = self._get_cache_path(video_id)

                if mp4_path.exists():
                    file_size = mp4_path.stat().st_size
                    removed.append({
                        'video_id': video_id,
                        'reason': 'low_popularity',
                        'access_count': count
                    })
                    self._remove_cache(video_id)
                    total_size -= file_size

        self._save_popularity()

        return {
            'removed_count': len(removed),
            'removed': removed[:10],  # 只返回前10个
            'total_removed': len(removed)
        }

    def get_stats(self) -> Dict:
        """获取缓存统计信息"""
        # 计算总大小
        total_size = sum(f.stat().st_size for f in self.cache_dir.glob('*.mp4'))
        file_count = len(list(self.cache_dir.glob('*.mp4')))

        # 计算命中率
        total_requests = self.stats['hits'] + self.stats['misses']
        hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0

        return {
            'file_count': file_count,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'total_size_gb': round(total_size / (1024 * 1024 * 1024), 2),
            'max_size_gb': round(self.max_size_bytes / (1024 * 1024 * 1024), 2),
            'usage_percent': round((total_size / self.max_size_bytes) * 100, 2) if self.max_size_bytes > 0 else 0,
            'ttl_days': self.ttl_seconds / 86400,
            'stats': self.stats,
            'hit_rate_percent': round(hit_rate, 2),
            'top_popular': sorted(
                [(vid, data.get('count', 0)) for vid, data in self.popularity.items()],
                key=lambda x: x[1],
                reverse=True
            )[:5]
        }

    def clear_all(self) -> Dict:
        """清空所有缓存"""
        removed = 0
        size_freed = 0

        for mp4_path in self.cache_dir.glob('*.mp4'):
            size_freed += mp4_path.stat().st_size
            mp4_path.unlink()
            removed += 1

        for json_path in self.cache_dir.glob('*.json'):
            json_path.unlink()

        self.popularity.clear()
        self._save_popularity()

        logger.warning(f"[CACHE] Cleared all: {removed} files, {size_freed / (1024*1024):.1f} MB")

        return {
            'removed_count': removed,
            'freed_mb': round(size_freed / (1024 * 1024), 2)
        }


# 全局缓存实例
video_cache = OptimizedVideoCache()


def get_video_cache() -> OptimizedVideoCache:
    """获取全局视频缓存实例"""
    return video_cache
