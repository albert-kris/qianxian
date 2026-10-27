"""SQLite 存储。MVP 阶段单文件数据库足够；表结构保持简单，方便以后迁到 Postgres。"""

import json
import os
import sqlite3
import threading
import time

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    handle TEXT UNIQUE NOT NULL,
    token_hash TEXT UNIQUE NOT NULL,
    created REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS profiles (
    user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    headline TEXT NOT NULL,          -- 一句话身份，例如“独立开发者，做 AI 编程工具”
    roles TEXT NOT NULL,             -- JSON 数组：investor / founder / developer / student …
    tags TEXT NOT NULL,              -- JSON 数组：领域和技能
    looking_for TEXT NOT NULL,       -- 最近在找什么（匹配最看重这一项）
    offering TEXT NOT NULL,          -- 能提供什么
    summary TEXT NOT NULL,           -- 补充介绍
    contact TEXT NOT NULL,           -- 只在双方都同意后才给对方看
    discoverable INTEGER NOT NULL,   -- 0 = 不接收任何介绍
    max_pending INTEGER NOT NULL,    -- 同时最多积压几张待处理卡片（保护注意力）
    updated REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS requests (
    id INTEGER PRIMARY KEY,
    from_user INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    pitch TEXT NOT NULL,             -- 我是谁、我做了什么（会出现在对方的卡片上）
    looking_for TEXT NOT NULL,       -- 想找什么样的人（只用于匹配，不展示）
    max_intros INTEGER NOT NULL,
    created REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS intros (
    id INTEGER PRIMARY KEY,
    request_id INTEGER NOT NULL REFERENCES requests(id) ON DELETE CASCADE,
    to_user INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    score REAL NOT NULL,
    reason TEXT NOT NULL,            -- 给收件人看的“为什么推给你”
    status TEXT NOT NULL,            -- pending / accepted / declined
    created REAL NOT NULL,
    responded REAL
);
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY,
    intro_id INTEGER NOT NULL REFERENCES intros(id) ON DELETE CASCADE,
    from_user INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    body TEXT NOT NULL,
    created REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_intros_to ON intros(to_user, status);
CREATE INDEX IF NOT EXISTS idx_intros_req ON intros(request_id);
"""


class DB:
    def __init__(self, path):
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.executescript(SCHEMA)
        self.lock = threading.Lock()
        self._migrate()

    def _migrate(self):
        """给老数据库补新列（SQLite 只能 ADD COLUMN）。"""
        cols = {r["name"] for r in self.conn.execute("PRAGMA table_info(users)")}
        if "invite_code" not in cols:
            self.conn.execute("ALTER TABLE users ADD COLUMN invite_code TEXT")
        if "referrer" not in cols:
            self.conn.execute("ALTER TABLE users ADD COLUMN referrer INTEGER")
        if "is_demo" not in cols:  # 审核用的演示账号：只和演示账号互相匹配，不打扰真实用户
            self.conn.execute("ALTER TABLE users ADD COLUMN is_demo INTEGER NOT NULL DEFAULT 0")
        self.conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_users_invite ON users(invite_code)")
        self.conn.commit()

    def q(self, sql, args=()):
        with self.lock:
            return self.conn.execute(sql, args).fetchall()

    def one(self, sql, args=()):
        rows = self.q(sql, args)
        return rows[0] if rows else None

    def x(self, sql, args=()):
        with self.lock:
            cur = self.conn.execute(sql, args)
            self.conn.commit()
            return cur.lastrowid

    def n(self, sql, args=()):
        """执行写操作，返回影响的行数。"""
        with self.lock:
            cur = self.conn.execute(sql, args)
            self.conn.commit()
            return cur.rowcount


def now():
    return time.time()


def dumps(v):
    return json.dumps(v, ensure_ascii=False)


def loads(s):
    return json.loads(s) if s else []
