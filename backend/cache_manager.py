"""
缓存管理模块 - 负责视频缓存的自动清理和统计
"""
import os
import time
import json
import shutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class CacheManager:
    """视频缓存管理器"""

    def __init__(
        self,
        cache_dir: str = 'video_cache',
        max_age_days: int = 7,
        max_size_gb: float = 10.0,
        max_file_count: int = 1000
    ):
        """
        初始化缓存管理器

        Args:
            cache_dir: 缓存目录路径
            max_age_days: 缓存文件最大保留天数
            max_size_gb: 缓存目录最大大小（GB）
            max_file_count: 最大缓存文件数量
        """
        self.cache_dir = cache_dir
        self.max_age_seconds = max_age_days * 86400
        self.max_size_bytes = max_size_gb * 1024 * 1024 * 1024
        self.max_file_count = max_file_count

        # 确保缓存目录存在
        os.makedirs(self.cache_dir, exist_ok=True)

        # 统计信息
        self.stats = {
            'total_files': 0,
            'total_size_mb': 0.0,
            'oldest_file_days': 0.0,
            'newest_file_days': 0.0,
            'cache_hit_possible': 0,
            'cache_miss': 0
        }

    def get_cache_stats(self) -> Dict:
        """
        获取缓存统计信息

        Returns:
            包含缓存统计数据的字典
        """
        total_size = 0
        file_count = 0
        oldest_mtime = float('inf')
        newest_mtime = 0
        oldest_file = None
        newest_file = None

        try:
            for filename in os.listdir(self.cache_dir):
                filepath = os.path.join(self.cache_dir, filename)
                if os.path.isfile(filepath):
                    file_size = os.path.getsize(filepath)
                    file_mtime = os.path.getmtime(filepath)

                    total_size += file_size
                    file_count += 1

                    if file_mtime < oldest_mtime:
                        oldest_mtime = file_mtime
                        oldest_file = filename

                    if file_mtime > newest_mtime:
                        newest_mtime = file_mtime
                        newest_file = filename

            now = time.time()
            self.stats = {
                'total_files': file_count,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'total_size_gb': round(total_size / (1024 * 1024 * 1024), 2),
                'max_size_gb': round(self.max_size_bytes / (1024 * 1024 * 1024), 2),
                'size_usage_percent': round((total_size / self.max_size_bytes) * 100, 2) if self.max_size_bytes > 0 else 0,
                'oldest_file': oldest_file,
                'oldest_file_days': round((now - oldest_mtime) / 86400, 2) if oldest_mtime != float('inf') else 0,
                'newest_file': newest_file,
                'newest_file_days': round((now - newest_mtime) / 86400, 2) if newest_mtime > 0 else 0,
                'cache_dir': self.cache_dir
            }

            logger.info(f"[CACHE] Stats: {self.stats['total_files']} files, "
                       f"{self.stats['total_size_gb']} GB ({self.stats['size_usage_percent']}% used)")

        except Exception as e:
            logger.error(f"[CACHE] Error getting stats: {e}")
            self.stats['error'] = str(e)

        return self.stats

    def cleanup_old_cache(self, dry_run: bool = False) -> Dict:
        """
        清理超过指定天数的缓存文件

        Args:
            dry_run: 如果为True，只模拟清理不实际删除

        Returns:
            清理结果统计
        """
        now = time.time()
        removed_count = 0
        removed_size = 0
        removed_files = []

        try:
            for filename in os.listdir(self.cache_dir):
                filepath = os.path.join(self.cache_dir, filename)

                if os.path.isfile(filepath):
                    file_mtime = os.path.getmtime(filepath)
                    file_age = now - file_mtime

                    # 删除超过最大期限的文件
                    if file_age > self.max_age_seconds:
                        file_size = os.path.getsize(filepath)

                        if not dry_run:
                            os.remove(filepath)
                            logger.info(f"[CACHE] Removed old cache: {filename} "
                                       f"({file_age / 86400:.1f} days old, {file_size / (1024*1024):.1f} MB)")
                        else:
                            logger.info(f"[CACHE-DRYRUN] Would remove: {filename} "
                                       f"({file_age / 86400:.1f} days old)")

                        removed_count += 1
                        removed_size += file_size
                        removed_files.append(filename)

            result = {
                'removed_count': removed_count,
                'freed_mb': round(removed_size / (1024 * 1024), 2),
                'removed_files': removed_files[:10],  # 只返回前10个
                'dry_run': dry_run
            }

            if not dry_run and removed_count > 0:
                logger.info(f"[CACHE] Cleanup completed: removed {removed_count} files, "
                           f"freed {result['freed_mb']} MB")

            return result

        except Exception as e:
            logger.error(f"[CACHE] Error during cleanup: {e}")
            return {'error': str(e), 'removed_count': 0, 'freed_mb': 0}

    def cleanup_by_size(self, target_size_gb: float = None) -> Dict:
        """
        根据缓存大小清理（删除最旧的文件直到满足大小限制）

        Args:
            target_size_gb: 目标大小（GB），如果为None则使用max_size_gb

        Returns:
            清理结果统计
        """
        target_size = (target_size_gb or self.max_size_bytes / (1024**3)) * 1024**3

        # 获取所有文件及其信息
        files = []
        for filename in os.listdir(self.cache_dir):
            filepath = os.path.join(self.cache_dir, filename)
            if os.path.isfile(filepath):
                files.append({
                    'path': filepath,
                    'name': filename,
                    'size': os.path.getsize(filepath),
                    'mtime': os.path.getmtime(filepath)
                })

        # 按修改时间排序（最旧的在前）
        files.sort(key=lambda x: x['mtime'])

        # 计算当前总大小
        total_size = sum(f['size'] for f in files)

        removed_count = 0
        removed_size = 0

        # 删除最旧的文件直到满足大小限制
        for file_info in files:
            if total_size - removed_size <= target_size:
                break

            try:
                os.remove(file_info['path'])
                removed_count += 1
                removed_size += file_info['size']
                logger.info(f"[CACHE] Removed by size: {file_info['name']} "
                           f"({file_info['size'] / (1024*1024):.1f} MB)")
            except Exception as e:
                logger.error(f"[CACHE] Error removing {file_info['name']}: {e}")

        result = {
            'removed_count': removed_count,
            'freed_mb': round(removed_size / (1024 * 1024), 2),
            'total_size_mb_before': round(total_size / (1024 * 1024), 2),
            'total_size_mb_after': round((total_size - removed_size) / (1024 * 1024), 2)
        }

        if removed_count > 0:
            logger.info(f"[CACHE] Size-based cleanup: removed {removed_count} files, "
                       f"freed {result['freed_mb']} MB")

        return result

    def cleanup_by_count(self, target_count: int = None) -> Dict:
        """
        根据文件数量清理（删除最旧的文件直到满足数量限制）

        Args:
            target_count: 目标文件数量，如果为None则使用max_file_count

        Returns:
            清理结果统计
        """
        target = target_count or self.max_file_count

        # 获取所有文件及其信息
        files = []
        for filename in os.listdir(self.cache_dir):
            filepath = os.path.join(self.cache_dir, filename)
            if os.path.isfile(filepath):
                files.append({
                    'path': filepath,
                    'name': filename,
                    'size': os.path.getsize(filepath),
                    'mtime': os.path.getmtime(filepath)
                })

        # 按修改时间排序（最旧的在前）
        files.sort(key=lambda x: x['mtime'])

        current_count = len(files)
        removed_count = 0
        removed_size = 0

        # 删除最旧的文件
        for file_info in files:
            if current_count - removed_count <= target:
                break

            try:
                os.remove(file_info['path'])
                removed_count += 1
                removed_size += file_info['size']
                logger.info(f"[CACHE] Removed by count: {file_info['name']}")
            except Exception as e:
                logger.error(f"[CACHE] Error removing {file_info['name']}: {e}")

        result = {
            'removed_count': removed_count,
            'freed_mb': round(removed_size / (1024 * 1024), 2),
            'file_count_before': current_count,
            'file_count_after': current_count - removed_count
        }

        if removed_count > 0:
            logger.info(f"[CACHE] Count-based cleanup: removed {removed_count} files")

        return result

    def smart_cleanup(self) -> Dict:
        """
        智能清理：根据多种条件自动决定清理策略

        Returns:
            清理结果统计
        """
        stats = self.get_cache_stats()
        results = []

        # 1. 清理超过最大期限的文件
        if stats.get('oldest_file_days', 0) > 7:
            result = self.cleanup_old_cache()
            results.append(('age', result))
            logger.info(f"[CACHE] Smart cleanup: age-based cleanup completed")

        # 2. 如果大小超限，按大小清理
        if stats.get('size_usage_percent', 0) > 90:
            target_gb = stats.get('max_size_gb', 10) * 0.7  # 清理到70%
            result = self.cleanup_by_size(target_gb)
            results.append(('size', result))
            logger.info(f"[CACHE] Smart cleanup: size-based cleanup completed")

        # 3. 如果文件数量超限，按数量清理
        if stats.get('total_files', 0) > self.max_file_count:
            target_count = int(self.max_file_count * 0.7)  # 清理到70%
            result = self.cleanup_by_count(target_count)
            results.append(('count', result))
            logger.info(f"[CACHE] Smart cleanup: count-based cleanup completed")

        return {
            'strategies_used': [r[0] for r in results],
            'total_removed': sum(r[1].get('removed_count', 0) for r in results),
            'total_freed_mb': round(sum(r[1].get('freed_mb', 0) for r in results), 2),
            'details': results
        }

    def get_video_cache_info(self, video_id: str) -> Optional[Dict]:
        """
        获取特定视频的缓存信息

        Args:
            video_id: 视频ID

        Returns:
            缓存信息字典，如果不存在则返回None
        """
        cache_file = os.path.join(self.cache_dir, f'{video_id}.json')

        if not os.path.exists(cache_file):
            return None

        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_info = json.load(f)

            # 检查视频文件是否存在
            video_file = cache_info.get('file_path')
            cache_info['video_exists'] = video_file and os.path.exists(video_file)

            # 添加缓存年龄
            cache_time = cache_info.get('cached_at', 0)
            cache_info['age_days'] = (time.time() - cache_time) / 86400

            return cache_info

        except Exception as e:
            logger.error(f"[CACHE] Error reading cache info for {video_id}: {e}")
            return None

    def clear_all_cache(self) -> Dict:
        """
        清空所有缓存（慎用！）

        Returns:
            清理结果
        """
        removed_count = 0
        removed_size = 0

        try:
            for filename in os.listdir(self.cache_dir):
                filepath = os.path.join(self.cache_dir, filename)
                if os.path.isfile(filepath):
                    file_size = os.path.getsize(filepath)
                    os.remove(filepath)
                    removed_count += 1
                    removed_size += file_size

            logger.warning(f"[CACHE] Cleared all cache: {removed_count} files, "
                         f"{removed_size / (1024*1024):.1f} MB")

            return {
                'removed_count': removed_count,
                'freed_mb': round(removed_size / (1024 * 1024), 2)
            }

        except Exception as e:
            logger.error(f"[CACHE] Error clearing cache: {e}")
            return {'error': str(e)}


# 全局缓存管理器实例
cache_manager = CacheManager()


def get_cache_manager() -> CacheManager:
    """获取全局缓存管理器实例"""
    return cache_manager
