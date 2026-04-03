"""
优化的数据库管理模块 - SQLite 生产级配置
"""
import sqlite3
import os
import time
import threading
from contextlib import contextmanager
from typing import Optional, Dict, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class OptimizedDatabaseManager:
    """优化的SQLite数据库管理器"""

    def __init__(self, db_path: str = 'data/users.db'):
        """
        初始化数据库管理器

        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self.db_dir = os.path.dirname(db_path)
        self.lock = threading.RLock()  # 可重入锁

        # 确保数据库目录存在
        os.makedirs(self.db_dir, exist_ok=True)

        # 初始化数据库
        self._init_database()

        # 性能统计
        self.stats = {
            'queries': 0,
            'slow_queries': 0,
            'errors': 0
        }

        logger.info(f"[DB] Database initialized: {db_path}")

    def _init_database(self):
        """初始化数据库表结构和优化配置"""
        # 首次启动时应用性能优化
        is_new_db = not os.path.exists(self.db_path)

        with self.get_connection() as conn:
            # 应用生产级性能优化
            conn.execute('PRAGMA journal_mode=WAL')  # 写前日志，提升并发
            conn.execute('PRAGMA synchronous=NORMAL')  # 平衡性能和安全
            conn.execute('PRAGMA cache_size=-64000')  # 64MB 负缓存
            conn.execute('PRAGMA temp_store=MEMORY')  # 临时表放内存
            conn.execute('PRAGMA mmap_size=30000000000')  # 启用内存映射
            conn.execute('PRAGMA page_size=4096')  # 设置页大小
            conn.execute('PRAGMA foreign_keys=ON')  # 启用外键约束

            # 创建表（如果不存在）
            self._create_tables(conn)

            # 创建索引（提升查询性能）
            self._create_indexes(conn)

            conn.commit()

        if is_new_db:
            logger.info("[DB] New database created with optimizations")

    def _create_tables(self, conn):
        """创建数据库表"""
        # 用户表
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                role VARCHAR(20) DEFAULT 'guest',
                membership_expire TIMESTAMP DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 使用记录表
        conn.execute('''
            CREATE TABLE IF NOT EXISTS user_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date DATE NOT NULL,
                download_count INTEGER DEFAULT 0,
                summary_count INTEGER DEFAULT 0,
                qa_count INTEGER DEFAULT 0,
                last_reset TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                UNIQUE(user_id, date)
            )
        ''')

        # 支付记录表
        conn.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                stripe_payment_intent_id VARCHAR(255) UNIQUE,
                amount INTEGER NOT NULL,
                currency VARCHAR(3) DEFAULT 'CNY',
                status VARCHAR(20) DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        # 游客使用记录表（新增）
        conn.execute('''
            CREATE TABLE IF NOT EXISTS guest_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fingerprint VARCHAR(255) NOT NULL,
                date DATE NOT NULL,
                download_count INTEGER DEFAULT 0,
                summary_count INTEGER DEFAULT 0,
                qa_count INTEGER DEFAULT 0,
                last_reset TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(fingerprint, date)
            )
        ''')

    def _create_indexes(self, conn):
        """创建索引以提升查询性能"""
        indexes = [
            'CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)',
            'CREATE INDEX IF NOT EXISTS idx_users_role ON users(role)',
            'CREATE INDEX IF NOT EXISTS idx_user_usage_user_id ON user_usage(user_id)',
            'CREATE INDEX IF NOT EXISTS idx_user_usage_date ON user_usage(date)',
            'CREATE INDEX IF NOT EXISTS idx_payments_user_id ON payments(user_id)',
            'CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status)',
            'CREATE INDEX IF NOT EXISTS idx_guest_usage_fingerprint ON guest_usage(fingerprint)',
            'CREATE INDEX IF NOT EXISTS idx_guest_usage_date ON guest_usage(date)',
        ]

        for idx_sql in indexes:
            try:
                conn.execute(idx_sql)
            except sqlite3.OperationalError:
                pass  # 索引可能已存在

    @contextmanager
    def get_connection(self):
        """
        获取数据库连接（线程安全的上下文管理器）

        用法:
            with db.get_connection() as conn:
                result = conn.execute('SELECT * FROM users')
        """
        conn = None
        try:
            conn = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                timeout=10.0  # 10秒超时
            )
            conn.row_factory = sqlite3.Row  # 返回字典格式
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            self.stats['errors'] += 1
            logger.error(f"[DB] Error: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def execute_query(self, query: str, params: tuple = (), auto_commit: bool = True) -> sqlite3.Cursor:
        """
        执行SQL查询

        Args:
            query: SQL查询语句
            params: 查询参数
            auto_commit: 是否自动提交

        Returns:
            游标对象
        """
        start_time = time.time()
        self.stats['queries'] += 1

        with self.get_connection() as conn:
            try:
                cursor = conn.execute(query, params)
                elapsed = time.time() - start_time

                # 记录慢查询（超过100ms）
                if elapsed > 0.1:
                    self.stats['slow_queries'] += 1
                    logger.warning(f"[DB] Slow query ({elapsed:.3f}s): {query[:100]}")

                return cursor
            except Exception as e:
                logger.error(f"[DB] Query failed: {e}")
                raise

    def fetch_one(self, query: str, params: tuple = ()) -> Optional[Dict]:
        """获取单条记录"""
        cursor = self.execute_query(query, params)
        row = cursor.fetchone()
        return dict(row) if row else None

    def fetch_all(self, query: str, params: tuple = ()) -> List[Dict]:
        """获取所有记录"""
        cursor = self.execute_query(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def insert(self, table: str, data: Dict) -> int:
        """
        插入数据

        Args:
            table: 表名
            data: 数据字典

        Returns:
            插入的行ID
        """
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        query = f'INSERT INTO {table} ({columns}) VALUES ({placeholders})'

        with self.get_connection() as conn:
            cursor = conn.execute(query, tuple(data.values()))
            return cursor.lastrowid

    def update(self, table: str, data: Dict, where: str, where_params: tuple = ()) -> int:
        """
        更新数据

        Args:
            table: 表名
            data: 要更新的数据字典
            where: WHERE子句
            where_params: WHERE参数

        Returns:
            影响的行数
        """
        set_clause = ', '.join([f'{k} = ?' for k in data.keys()])
        query = f'UPDATE {table} SET {set_clause} WHERE {where}'

        with self.get_connection() as conn:
            cursor = conn.execute(query, tuple(data.values()) + where_params)
            return cursor.rowcount

    def get_stats(self) -> Dict:
        """获取数据库统计信息"""
        db_size = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0

        # 获取表统计
        with self.get_connection() as conn:
            cursor = conn.execute('''
                SELECT name, (SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name=main.name) as is_table
                FROM sqlite_master WHERE type='table'
            ''')
            tables = [row[0] for row in cursor.fetchall()]

            table_stats = {}
            for table in tables:
                try:
                    count = conn.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0]
                    table_stats[table] = count
                except:
                    pass

        return {
            'db_path': self.db_path,
            'db_size_mb': round(db_size / (1024 * 1024), 2),
            'table_stats': table_stats,
            'query_stats': self.stats,
            'hit_rate_percent': round(
                (1 - self.stats['errors'] / max(self.stats['queries'], 1)) * 100, 2
            )
        }

    def backup(self, backup_path: str = None) -> bool:
        """
        备份数据库

        Args:
            backup_path: 备份文件路径，如果为None则自动生成

        Returns:
            是否成功
        """
        if backup_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_dir = os.path.join(self.db_dir, 'backups')
            os.makedirs(backup_dir, exist_ok=True)
            backup_path = os.path.join(backup_dir, f'users_db_{timestamp}.db')

        try:
            # 使用SQLite的备份API（更可靠）
            source = sqlite3.connect(self.db_path)
            dest = sqlite3.connect(backup_path)

            source.backup(dest)

            source.close()
            dest.close()

            logger.info(f"[DB] Backup created: {backup_path}")
            return True

        except Exception as e:
            logger.error(f"[DB] Backup failed: {e}")
            return False

    def vacuum(self):
        """优化数据库（回收空间）"""
        with self.get_connection() as conn:
            conn.execute('VACUUM')
            conn.commit()
        logger.info("[DB] Database vacuumed")

    def analyze(self):
        """更新统计信息（优化查询计划）"""
        with self.get_connection() as conn:
            conn.execute('ANALYZE')
            conn.commit()
        logger.info("[DB] Database analyzed")


# 全局数据库实例
db_manager = OptimizedDatabaseManager()


def get_db_manager() -> OptimizedDatabaseManager:
    """获取全局数据库管理器实例"""
    return db_manager