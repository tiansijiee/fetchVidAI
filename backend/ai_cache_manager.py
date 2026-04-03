"""
AI结果缓存管理器 - 缓存AI总结、问答等结果
避免重复调用昂贵的AI API
"""
import os
import json
import time
import hashlib
from pathlib import Path
from typing import Dict, Optional, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class AIResultCache:
    """AI结果缓存管理器"""

    def __init__(
        self,
        cache_dir: str = 'ai_cache',
        ttl_days: int = 30,  # AI结果缓存30天
        max_size_gb: float = 1.0  # AI结果缓存最大1GB（文本很小）
    ):
        """
        初始化AI结果缓存

        Args:
            cache_dir: 缓存目录
            ttl_days: 缓存有效期（天）
            max_size_gb: 最大缓存大小（GB）
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.ttl_seconds = ttl_days * 86400
        self.max_size_bytes = max_size_gb * 1024 * 1024 * 1024

        # 统计信息
        self.stats = {
            'summary_hits': 0,
            'summary_misses': 0,
            'qa_hits': 0,
            'qa_misses': 0,
            'mindmap_hits': 0,
            'mindmap_misses': 0
        }

        logger.info(f"[AI-CACHE] Initialized: {cache_dir}, TTL={ttl_days}d")

    def _generate_key(self, content: str, prefix: str = '') -> str:
        """
        生成缓存键

        Args:
            content: 要缓存的内容
            prefix: 键前缀（如'summary', 'qa'等）

        Returns:
            缓存键
        """
        # 使用内容哈希作为键
        content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
        return f"{prefix}_{content_hash}" if prefix else content_hash

    def _get_cache_path(self, key: str) -> Path:
        """获取缓存文件路径"""
        return self.cache_dir / f'{key}.json'

    def get_summary(
        self,
        video_id: str,
        subtitle_text: str,
        video_title: str = '',
        video_description: str = ''
    ) -> Optional[Dict]:
        """
        获取缓存的视频总结

        Args:
            video_id: 视频ID
            subtitle_text: 字幕文本
            video_title: 视频标题
            video_description: 视频描述

        Returns:
            缓存的总结结果，如果不存在或已过期则返回None
        """
        # 生成缓存键（基于字幕内容）
        cache_key = self._generate_key(
            f"{video_id}_{subtitle_text[:500]}_{video_title}",
            'summary'
        )

        cache_path = self._get_cache_path(cache_key)

        if not cache_path.exists():
            self.stats['summary_misses'] += 1
            logger.debug(f"[AI-CACHE] Summary miss: {video_id}")
            return None

        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)

            # 检查是否过期
            cached_at = cache_data.get('cached_at', 0)
            if time.time() - cached_at > self.ttl_seconds:
                logger.info(f"[AI-CACHE] Summary expired: {video_id}")
                cache_path.unlink()
                self.stats['summary_misses'] += 1
                return None

            self.stats['summary_hits'] += 1
            logger.info(f"[AI-CACHE] Summary hit: {video_id} (saved API call!)")

            return cache_data.get('result')

        except Exception as e:
            logger.error(f"[AI-CACHE] Error reading summary cache: {e}")
            self.stats['summary_misses'] += 1
            return None

    def put_summary(
        self,
        video_id: str,
        subtitle_text: str,
        result: Dict,
        video_title: str = '',
        video_description: str = ''
    ) -> bool:
        """
        保存视频总结到缓存

        Args:
            video_id: 视频ID
            subtitle_text: 字幕文本
            result: AI总结结果
            video_title: 视频标题
            video_description: 视频描述

        Returns:
            是否成功保存
        """
        cache_key = self._generate_key(
            f"{video_id}_{subtitle_text[:500]}_{video_title}",
            'summary'
        )

        cache_path = self._get_cache_path(cache_key)

        cache_data = {
            'video_id': video_id,
            'video_title': video_title,
            'cached_at': time.time(),
            'subtitle_length': len(subtitle_text),
            'result': result
        }

        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)

            logger.info(f"[AI-CACHE] Summary saved: {video_id}")
            return True

        except Exception as e:
            logger.error(f"[AI-CACHE] Error saving summary: {e}")
            return False

    def get_qa_answer(
        self,
        video_id: str,
        question: str,
        context: str = ''
    ) -> Optional[str]:
        """
        获取缓存的问答答案

        Args:
            video_id: 视频ID
            question: 问题
            context: 上下文（字幕等）

        Returns:
            缓存的答案，如果不存在则返回None
        """
        cache_key = self._generate_key(
            f"{video_id}_{question}_{context[:200]}",
            'qa'
        )

        cache_path = self._get_cache_path(cache_key)

        if not cache_path.exists():
            self.stats['qa_misses'] += 1
            return None

        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)

            # 检查是否过期
            cached_at = cache_data.get('cached_at', 0)
            if time.time() - cached_at > self.ttl_seconds:
                cache_path.unlink()
                self.stats['qa_misses'] += 1
                return None

            self.stats['qa_hits'] += 1
            logger.info(f"[AI-CACHE] QA hit: {question[:50]}...")
            return cache_data.get('answer')

        except Exception as e:
            logger.error(f"[AI-CACHE] Error reading QA cache: {e}")
            self.stats['qa_misses'] += 1
            return None

    def put_qa_answer(
        self,
        video_id: str,
        question: str,
        answer: str,
        context: str = ''
    ) -> bool:
        """
        保存问答答案到缓存

        Args:
            video_id: 视频ID
            question: 问题
            answer: 答案
            context: 上下文

        Returns:
            是否成功保存
        """
        cache_key = self._generate_key(
            f"{video_id}_{question}_{context[:200]}",
            'qa'
        )

        cache_path = self._get_cache_path(cache_key)

        cache_data = {
            'video_id': video_id,
            'question': question,
            'answer': answer,
            'cached_at': time.time()
        }

        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)

            return True

        except Exception as e:
            logger.error(f"[AI-CACHE] Error saving QA: {e}")
            return False

    def get_mindmap(
        self,
        video_id: str,
        subtitle_text: str
    ) -> Optional[Dict]:
        """
        获取缓存的思维导图

        Args:
            video_id: 视频ID
            subtitle_text: 字幕文本

        Returns:
            缓存的思维导图，如果不存在则返回None
        """
        cache_key = self._generate_key(
            f"{video_id}_{subtitle_text[:500]}",
            'mindmap'
        )

        cache_path = self._get_cache_path(cache_key)

        if not cache_path.exists():
            self.stats['mindmap_misses'] += 1
            return None

        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)

            cached_at = cache_data.get('cached_at', 0)
            if time.time() - cached_at > self.ttl_seconds:
                cache_path.unlink()
                self.stats['mindmap_misses'] += 1
                return None

            self.stats['mindmap_hits'] += 1
            return cache_data.get('mindmap')

        except Exception as e:
            logger.error(f"[AI-CACHE] Error reading mindmap cache: {e}")
            self.stats['mindmap_misses'] += 1
            return None

    def put_mindmap(
        self,
        video_id: str,
        subtitle_text: str,
        mindmap: Dict
    ) -> bool:
        """保存思维导图到缓存"""
        cache_key = self._generate_key(
            f"{video_id}_{subtitle_text[:500]}",
            'mindmap'
        )

        cache_path = self._get_cache_path(cache_key)

        cache_data = {
            'video_id': video_id,
            'mindmap': mindmap,
            'cached_at': time.time()
        }

        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            return True

        except Exception as e:
            logger.error(f"[AI-CACHE] Error saving mindmap: {e}")
            return False

    def cleanup(self) -> Dict:
        """清理过期的缓存文件"""
        removed = 0
        now = time.time()

        for cache_file in self.cache_dir.glob('*.json'):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)

                cached_at = cache_data.get('cached_at', 0)
                if now - cached_at > self.ttl_seconds:
                    cache_file.unlink()
                    removed += 1

            except Exception as e:
                logger.error(f"[AI-CACHE] Error cleaning {cache_file}: {e}")

        logger.info(f"[AI-CACHE] Cleaned up {removed} expired files")
        return {'removed_count': removed}

    def get_stats(self) -> Dict:
        """获取缓存统计信息"""
        # 计算总大小
        total_size = sum(
            f.stat().st_size
            for f in self.cache_dir.glob('*.json')
        )

        file_count = len(list(self.cache_dir.glob('*.json')))

        # 计算命中率
        total_summary = self.stats['summary_hits'] + self.stats['summary_misses']
        summary_hit_rate = (
            self.stats['summary_hits'] / total_summary * 100
            if total_summary > 0 else 0
        )

        total_qa = self.stats['qa_hits'] + self.stats['qa_misses']
        qa_hit_rate = (
            self.stats['qa_hits'] / total_qa * 100
            if total_qa > 0 else 0
        )

        total_mindmap = self.stats['mindmap_hits'] + self.stats['mindmap_misses']
        mindmap_hit_rate = (
            self.stats['mindmap_hits'] / total_mindmap * 100
            if total_mindmap > 0 else 0
        )

        return {
            'file_count': file_count,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'ttl_days': self.ttl_seconds / 86400,
            'stats': self.stats,
            'hit_rates': {
                'summary_percent': round(summary_hit_rate, 2),
                'qa_percent': round(qa_hit_rate, 2),
                'mindmap_percent': round(mindmap_hit_rate, 2)
            }
        }

    def clear_all(self) -> Dict:
        """清空所有缓存"""
        removed = 0
        size_freed = 0

        for cache_file in self.cache_dir.glob('*.json'):
            size_freed += cache_file.stat().st_size
            cache_file.unlink()
            removed += 1

        logger.warning(f"[AI-CACHE] Cleared all: {removed} files")
        return {
            'removed_count': removed,
            'freed_mb': round(size_freed / (1024 * 1024), 2)
        }


# 全局AI缓存实例
ai_cache = AIResultCache()


def get_ai_cache() -> AIResultCache:
    """获取全局AI缓存实例"""
    return ai_cache