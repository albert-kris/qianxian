"""OAuth 2.1 授权服务器：ChatGPT、Claude 网页版接入 MCP 时要求的登录方式。

协议部分（元数据发现、动态客户端注册、PKCE 校验、/authorize、/token、/revoke）由 MCP SDK 提供，
这里只实现存储和“用户在我们的页面上登录”这一步：
  1. 客户端（ChatGPT / Claude）把用户带到 /authorize → authorize() 记下请求，跳转到 /login?req=…
  2. 用户在 /login 注册新昵称或输入已有密钥 → 生成授权码，跳回客户端的 redirect_uri
  3. 客户端用授权码 + PKCE 换访问令牌；之后每次调用 MCP 都带着它

兼容旧方式：Authorization: Bearer qx_… 的个人密钥仍然有效（Claude Code、Cursor 用）。
"""

import hashlib
import json
import secrets
import time

from mcp.server.auth.provider import (
    AccessToken,
    AuthorizationCode,
    AuthorizationParams,
    OAuthAuthorizationServerProvider,
    RefreshToken,
    TokenError,
    construct_redirect_uri,
)
from mcp.shared.auth import OAuthClientInformationFull, OAuthToken

from .core import Error, Network

SCOPE = "qianxian"
ACCESS_TTL = 3600
REFRESH_TTL = 60 * 86400
CODE_TTL = 300
PENDING_TTL = 900

SCHEMA = """
CREATE TABLE IF NOT EXISTS oauth_clients (client_id TEXT PRIMARY KEY, info TEXT NOT NULL, created REAL NOT NULL);
CREATE TABLE IF NOT EXISTS oauth_pending (id TEXT PRIMARY KEY, client_id TEXT NOT NULL, params TEXT NOT NULL, created REAL NOT NULL);
CREATE TABLE IF NOT EXISTS oauth_codes (code_hash TEXT PRIMARY KEY, data TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS oauth_tokens (
    token_hash TEXT PRIMARY KEY,
    kind TEXT NOT NULL,              -- access / refresh
    grant_id TEXT NOT NULL,          -- 同一次授权发出的令牌共享，撤销时一起撤
    client_id TEXT NOT NULL,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    scopes TEXT NOT NULL,
    resource TEXT,
    expires_at INTEGER NOT NULL
);
"""


def _h(s):
    return hashlib.sha256(s.encode()).hexdigest()


class Provider(OAuthAuthorizationServerProvider[AuthorizationCode, RefreshToken, AccessToken]):
    def __init__(self, net: Network, public_url: str):
        self.net = net
        self.db = net.db
        self.public = public_url
        with self.db.lock:
            self.db.conn.executescript(SCHEMA)

    # ---------- 客户端注册（ChatGPT / Claude 会自动注册） ----------

    async def get_client(self, client_id):
        row = self.db.one("SELECT info FROM oauth_clients WHERE client_id = ?", (client_id,))
        return OAuthClientInformationFull.model_validate_json(row["info"]) if row else None

    async def register_client(self, client_info):
        # 客户端登记的 scope 里总是包含 qianxian，之后它申请 qianxian 也不会被拒
        scopes = set((client_info.scope or "").split()) | {SCOPE}
        client_info.scope = " ".join(sorted(scopes))
        self.db.x("INSERT OR REPLACE INTO oauth_clients (client_id, info, created) VALUES (?, ?, ?)",
                  (client_info.client_id, client_info.model_dump_json(), time.time()))

    # ---------- 授权：跳到我们的登录页 ----------

    async def authorize(self, client, params: AuthorizationParams):
        req = secrets.token_urlsafe(24)
        self.db.x("DELETE FROM oauth_pending WHERE created < ?", (time.time() - PENDING_TTL,))
        self.db.x("INSERT INTO oauth_pending (id, client_id, params, created) VALUES (?, ?, ?, ?)",
                  (req, client.client_id, params.model_dump_json(), time.time()))
        return f"{self.public}/login?req={req}"

    def pending(self, req):
        row = self.db.one("SELECT * FROM oauth_pending WHERE id = ? AND created > ?", (req, time.time() - PENDING_TTL))
        if not row:
            raise Error("登录请求已过期，请回到 AI 应用里重新点“连接”")
        client = self.db.one("SELECT info FROM oauth_clients WHERE client_id = ?", (row["client_id"],))
        name = json.loads(client["info"]).get("client_name") if client else None
        return row, AuthorizationParams.model_validate_json(row["params"]), name or row["client_id"]

    def complete_login(self, req, uid):
        """用户在登录页通过验证后调用：发授权码，返回要跳回去的地址。"""
        row, params, _ = self.pending(req)
        self.db.x("DELETE FROM oauth_pending WHERE id = ?", (req,))
        code = secrets.token_urlsafe(32)
        # 不管客户端申请了什么 scope，令牌都带上 qianxian（MCP 端点要求它）
        scopes = sorted(set(params.scopes or []) | {SCOPE})
        ac = AuthorizationCode(code=code, scopes=scopes, expires_at=time.time() + CODE_TTL,
                               client_id=row["client_id"], code_challenge=params.code_challenge,
                               redirect_uri=params.redirect_uri,
                               redirect_uri_provided_explicitly=params.redirect_uri_provided_explicitly,
                               resource=params.resource, subject=str(uid))
        self.db.x("INSERT INTO oauth_codes (code_hash, data) VALUES (?, ?)", (_h(code), ac.model_dump_json()))
        return construct_redirect_uri(str(params.redirect_uri), code=code, state=params.state)

    async def load_authorization_code(self, client, authorization_code):
        row = self.db.one("SELECT data FROM oauth_codes WHERE code_hash = ?", (_h(authorization_code),))
        if not row:
            return None
        ac = AuthorizationCode.model_validate_json(row["data"])
        if ac.client_id != client.client_id or ac.expires_at < time.time():
            return None
        return ac

    # ---------- 发放 / 刷新令牌 ----------

    def _issue(self, client_id, uid, scopes, resource, grant_id=None):
        grant_id = grant_id or secrets.token_hex(8)
        access, refresh = "qxa_" + secrets.token_urlsafe(32), "qxr_" + secrets.token_urlsafe(32)
        now = int(time.time())
        for tok, kind, ttl in ((access, "access", ACCESS_TTL), (refresh, "refresh", REFRESH_TTL)):
            self.db.x("""INSERT INTO oauth_tokens (token_hash, kind, grant_id, client_id, user_id, scopes, resource, expires_at)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                      (_h(tok), kind, grant_id, client_id, uid, " ".join(scopes), resource, now + ttl))
        return OAuthToken(access_token=access, token_type="Bearer", expires_in=ACCESS_TTL,
                          scope=" ".join(scopes), refresh_token=refresh)

    async def exchange_authorization_code(self, client, authorization_code):
        if not self.db.n("DELETE FROM oauth_codes WHERE code_hash = ?", (_h(authorization_code.code),)):
            raise TokenError("invalid_grant", "授权码已被使用")
        return self._issue(client.client_id, int(authorization_code.subject), authorization_code.scopes,
                           authorization_code.resource)

    def _token_row(self, token, kind):
        return self.db.one("SELECT * FROM oauth_tokens WHERE token_hash = ? AND kind = ? AND expires_at > ?",
                           (_h(token), kind, int(time.time())))

    async def load_refresh_token(self, client, refresh_token):
        row = self._token_row(refresh_token, "refresh")
        if not row or row["client_id"] != client.client_id:
            return None
        return RefreshToken(token=refresh_token, client_id=row["client_id"], scopes=row["scopes"].split(),
                            expires_at=row["expires_at"], resource=row["resource"], subject=str(row["user_id"]))

    async def exchange_refresh_token(self, client, refresh_token, scopes):
        row = self._token_row(refresh_token.token, "refresh")
        if not row:
            raise TokenError("invalid_grant", "刷新令牌无效")
        # 轮换：旧的这一组令牌作废，发新的
        self.db.x("DELETE FROM oauth_tokens WHERE grant_id = ?", (row["grant_id"],))
        return self._issue(client.client_id, row["user_id"], scopes or row["scopes"].split(), row["resource"])

    # ---------- 校验访问令牌（每次调用 MCP 时） ----------

    async def load_access_token(self, token):
        if token.startswith("qx_"):  # 个人密钥（Claude Code / Cursor）
            try:
                uid, _ = self.net.auth(token)
            except Error:
                return None
            return AccessToken(token=token, client_id="personal-key", scopes=[SCOPE], subject=str(uid))
        row = self._token_row(token, "access")
        if not row:
            return None
        return AccessToken(token=token, client_id=row["client_id"], scopes=row["scopes"].split(),
                           expires_at=row["expires_at"], resource=row["resource"], subject=str(row["user_id"]))

    async def revoke_token(self, token):
        row = self.db.one("SELECT grant_id FROM oauth_tokens WHERE token_hash = ?", (_h(token.token),))
        if row:
            self.db.x("DELETE FROM oauth_tokens WHERE grant_id = ?", (row["grant_id"],))
