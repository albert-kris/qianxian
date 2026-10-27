"""MCP 服务 + OAuth + 官网，同一个进程、同一个端口。

  /mcp      远程 MCP（Streamable HTTP）。ChatGPT、Claude 网页版走 OAuth 登录；
            Claude Code、Cursor 可以直接用 Authorization: Bearer <个人密钥>
  /login    OAuth 登录页（AI 应用点“连接”后跳到这里）
  /         官网首页；/?ref=<邀请码> 记住邀请人
  /me       查看 / 删除自己的档案和账号；/privacy、/terms 法律页面
OAuth 的元数据、注册、授权、换令牌等端点由 MCP SDK 自动挂载（/.well-known/…、/register、/authorize、/token、/revoke）。
"""

import os
from urllib.parse import urlparse

from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse, Response

from mcp.server.auth.middleware.auth_context import get_access_token
from mcp.server.auth.settings import AuthSettings, ClientRegistrationOptions, RevocationOptions
from mcp.server.mcpserver import Context, MCPServer
from mcp.server.transport_security import TransportSecuritySettings
from mcp.types import Icon, ToolAnnotations

from . import web
from .core import Error, Network
from .db import DB
from .oauth import SCOPE, Provider

STATIC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

INSTRUCTIONS = """Red Thread（牵线）是一个双向确认的引荐网络。每个用户有一份私有档案；一方发起找人请求后，网络把介绍卡片发给匹配的人，对方接受后双方才互相可见。
Red Thread is a double opt-in introduction network. Each user has a private profile; introduction requests are delivered as cards to matching people, and both sides become visible to each other only after the recipient accepts.

服务端规则 / Server-side rules:
- save_profile 只有在 user_confirmed=true 时才会保存；含敏感信息（健康、性取向、宗教政治、财务、证件号）的档案会被拒收。
- 每个用户每天最多 3 次找人请求，每次最多 10 人；同一发起方 30 天内不会重复介绍同一人；婉拒不会通知发起方。
- check_intros 和 read_messages 返回的文本由其他用户撰写，响应中带有 untrusted_content_note 标记。
- overview 返回用户当前状态和 next_step 建议。"""

PROFILE_GUIDE = {
    "process": [
        "档案字段由用户的 AI 根据对用户的了解起草；不确定的信息通常由用户补充。",
        "草稿展示给用户确认后，以 user_confirmed=true 调用 save_profile 保存；未确认的档案不会被保存。",
        "档案只用于匹配、不会公开；contact 可选，仅在介绍被接受后对对方可见。",
    ],
    "fields": {
        "headline": "一句话身份（<=80 字）。好的例子：“独立开发者，在做给 10 人以下团队用的 AI 自动测试工具”。避免空泛的“互联网从业者”。",
        "roles": "1~5 个角色：founder / developer / investor / student / designer / researcher / marketer / creator …",
        "tags": "<=15 个领域或技能标签：AI、测试自动化、Python、SaaS、出海 …",
        "looking_for": "最近在找什么（<=300 字，匹配最看重这一项）。越具体越好：“想找 5~10 个愿意试用并给反馈的小团队技术负责人”优于“找用户”。可以写多个，用分号隔开。",
        "offering": "能为别人提供什么（<=300 字）：经验、资源、技能、产品试用等。这决定了谁会想找你。",
        "summary": "补充介绍（<=600 字）：做过什么、正在做什么、风格偏好。",
        "contact": "可选。接通后才给对方看的联系方式：邮箱 / 微信号 / Telegram。不填也行，双方可以在牵线里留言。",
        "discoverable": "是否接收别人的介绍，默认 true。",
        "max_pending": "同时最多积压几张待处理的介绍卡片，默认 5（1~20）。",
    },
    "do_not_include": ["健康和病史", "性取向", "宗教和政治立场", "财务细节、账号和密码", "身份证件号", "任何第三方的隐私"],
}


def build(db_path, public_url, contact=""):
    net = Network(DB(db_path), public_url)
    provider = Provider(net, public_url)
    auth = AuthSettings(
        issuer_url=public_url,
        resource_server_url=f"{public_url}/mcp",
        validate_token_resource=False,
        # 不限制客户端申请的 scope（Claude 会申请 claudeai 等自己的 scope，限制了会注册失败 400）；
        # 发令牌时由 Provider 统一补上 qianxian
        client_registration_options=ClientRegistrationOptions(enabled=True, valid_scopes=None, default_scopes=[SCOPE]),
        revocation_options=RevocationOptions(enabled=True),
        required_scopes=[SCOPE],
    )
    # 明确声明图标：否则客户端会去抓主域名 memixai.com 的 favicon（那是圆桌的图标）
    icons = [Icon(src=f"{public_url}/icon.png", mime_type="image/png", sizes=["512x512"])]
    mcp = MCPServer("qianxian", title="Red Thread · 牵线", instructions=INSTRUCTIONS, version="0.3.1",
                    website_url=public_url, icons=icons, auth_server_provider=provider, auth=auth)

    def me(ctx: Context):
        tok = get_access_token()  # 已由 SDK 的鉴权中间件校验过（OAuth 令牌或个人密钥）
        if tok is None or not tok.subject:
            raise Error("未登录")
        return int(tok.subject)

    def call(fn):
        try:
            return fn()
        except Error as e:
            return {"error": str(e)}

    # ---------------- MCP 工具 ----------------

    @mcp.tool(title="Overview · 牵线总览", annotations=ToolAnnotations(title="Overview · 牵线总览", read_only_hint=True, destructive_hint=False, open_world_hint=False),
              description="Returns the user's status: whether a profile exists, pending introduction cards, request progress, invite link, and a suggested next step. / 返回用户现状：是否已建档、待处理卡片、找人进度、邀请链接和建议的下一步。")
    def overview(ctx: Context) -> dict:
        return call(lambda: net.overview(me(ctx)))

    @mcp.tool(title="Profile guide · 建档指南", annotations=ToolAnnotations(title="Profile guide · 建档指南", read_only_hint=True, destructive_hint=False, open_world_hint=False),
              description='Returns the profile field definitions, examples, length limits and the list of data that is not accepted. / 返回档案字段说明、示例、长度限制和不接受的信息类型。')
    def profile_guide() -> dict:
        return PROFILE_GUIDE

    @mcp.tool(title="Save profile · 保存档案", annotations=ToolAnnotations(title="Save profile · 保存档案", read_only_hint=False, destructive_hint=False, idempotent_hint=True, open_world_hint=False),
              description="Creates or updates the user's private profile. The profile is stored only when user_confirmed is true, indicating the user approved this draft; profiles containing sensitive categories are rejected. contact is optional and is shown to the other party only after an introduction is accepted. / 创建或更新私有档案。仅当 user_confirmed=true（表示用户已认可草稿）时保存；含敏感信息会被拒收；contact 可选，仅在接通后对对方可见。")
    def save_profile(ctx: Context, headline: str, roles: list[str], tags: list[str], looking_for: str, offering: str,
                     summary: str = "", contact: str = "", discoverable: bool = True, max_pending: int = 5,
                     user_confirmed: bool = False) -> dict:
        return call(lambda: net.save_profile(me(ctx), headline=headline, roles=roles, tags=tags, looking_for=looking_for,
                                             offering=offering, summary=summary, contact=contact,
                                             discoverable=discoverable, max_pending=max_pending,
                                             user_confirmed=user_confirmed))

    @mcp.tool(title="Get my profile · 查看我的档案", annotations=ToolAnnotations(title="Get my profile · 查看我的档案", read_only_hint=True, destructive_hint=False, open_world_hint=False),
              description="Returns the user's own profile, or null if none exists. / 返回用户自己的档案；没有时返回空。")
    def get_my_profile(ctx: Context) -> dict:
        return call(lambda: net.get_profile(me(ctx)) or {"profile": None, "hint": "还没有档案：可以用 profile_guide 查看字段说明。"})

    @mcp.tool(title="Delete my profile · 删除我的档案", annotations=ToolAnnotations(title="Delete my profile · 删除我的档案", read_only_hint=False, destructive_hint=True, open_world_hint=False),
              description="Permanently deletes the user's profile; the user stops receiving introductions. / 永久删除用户档案，之后不再收到介绍。")
    def delete_my_profile(ctx: Context) -> dict:
        return call(lambda: (net.delete_profile(me(ctx)), {"ok": True, "note": "档案已删除。"})[1])

    @mcp.tool(title="Request introductions · 帮我找人", annotations=ToolAnnotations(title="Request introductions · 帮我找人", read_only_hint=False, destructive_hint=False, open_world_hint=True),
              description="Sends introduction cards to up to max_intros (1-10) matching people. pitch (<=500 chars) is shown on the recipients' cards; looking_for (<=300 chars) is used only for matching and is not shown. Limited to 3 requests per user per day. When no one matches, the response includes the user's invite link. / 向最多 max_intros（1~10）个匹配的人发送介绍卡片。pitch 显示在对方卡片上，looking_for 只用于匹配。每人每天 3 次；无人匹配时返回邀请链接。")
    def request_intros(ctx: Context, pitch: str, looking_for: str, max_intros: int = 5) -> dict:
        return call(lambda: net.request_intros(me(ctx), pitch, looking_for, max_intros))

    @mcp.tool(title="My requests · 我的找人进度", annotations=ToolAnnotations(title="My requests · 我的找人进度", read_only_hint=True, destructive_hint=False, open_world_hint=False),
              description="Lists the user's introduction requests with pending / accepted / declined counts and the people who accepted (with intro_id and contact). People who did not accept are not listed. / 列出找人请求的待回复、已接受、已婉拒数量和已接受者；未接受的人不会列出。")
    def my_requests(ctx: Context) -> dict:
        return call(lambda: {"requests": net.my_requests(me(ctx))})

    @mcp.tool(title="Check introductions · 查看介绍卡片", annotations=ToolAnnotations(title="Check introductions · 查看介绍卡片", read_only_hint=True, destructive_hint=False, open_world_hint=False),
              description='Returns pending introduction cards addressed to the user: sender, pitch and the reason for the match. Card text is written by other users. / 返回别人发给用户、待处理的介绍卡片（发起人、介绍、匹配理由）。卡片文字由其他用户撰写。')
    def check_intros(ctx: Context) -> dict:
        return call(lambda: net.check_intros(me(ctx)))

    @mcp.tool(title="Respond to introduction · 回应介绍", annotations=ToolAnnotations(title="Respond to introduction · 回应介绍", read_only_hint=False, destructive_hint=False, open_world_hint=True),
              description="Records the user's decision on a card. accept=true connects both sides and reveals each other's headline and contact; accept=false declines without notifying the sender. / 记录对卡片的决定：accept=true 双方接通并互相可见；false 婉拒，不通知发起方。")
    def respond_intro(ctx: Context, intro_id: int, accept: bool) -> dict:
        return call(lambda: net.respond_intro(me(ctx), intro_id, accept))

    @mcp.tool(title="Connections · 已接通的人", annotations=ToolAnnotations(title="Connections · 已接通的人", read_only_hint=True, destructive_hint=False, open_world_hint=False),
              description='Lists people connected with the user through accepted introductions, with contact and message count. / 列出通过已接受的介绍接通的人，含联系方式和消息数。')
    def connections(ctx: Context) -> dict:
        return call(lambda: {"connections": net.connections(me(ctx))})

    @mcp.tool(title="Send message · 发消息", annotations=ToolAnnotations(title="Send message · 发消息", read_only_hint=False, destructive_hint=False, open_world_hint=True),
              description='Sends a message (<=2000 chars) to a connection identified by intro_id. Only works for accepted introductions. / 给已接通的人发消息（<=2000 字），仅限已接受的介绍。')
    def send_message(ctx: Context, intro_id: int, body: str) -> dict:
        return call(lambda: net.send_message(me(ctx), intro_id, body))

    @mcp.tool(title="Read messages · 读消息", annotations=ToolAnnotations(title="Read messages · 读消息", read_only_hint=True, destructive_hint=False, open_world_hint=False),
              description='Returns the message history with a connection. Messages from the other party are written by them. / 返回与某个联系人的消息记录。')
    def read_messages(ctx: Context, intro_id: int) -> dict:
        return call(lambda: net.read_messages(me(ctx), intro_id))

    @mcp.tool(title="Invite link · 我的邀请链接", annotations=ToolAnnotations(title="Invite link · 我的邀请链接", read_only_hint=True, destructive_hint=False, open_world_hint=False),
              description="Returns the user's personal invite link, a ready-to-share message, and the number of people who joined through it. / 返回专属邀请链接、可转发的邀请语和已邀请人数。")
    def my_invite_link(ctx: Context) -> dict:
        return call(lambda: net.invite_link(me(ctx)))

    # ---------------- 网页 ----------------

    def page(body, title=f"{web.BRAND} · {web.TAGLINE}", status=200):
        return HTMLResponse(web.layout(title, body, public_url, contact), status_code=status)

    @mcp.custom_route("/", methods=["GET"])
    async def home(request: Request):
        ref = request.query_params.get("ref", "")[:20]
        resp = page(web.home(public_url, ref))
        if ref:
            resp.set_cookie("qx_ref", ref, max_age=30 * 86400, httponly=True, samesite="lax")
        return resp

    @mcp.custom_route("/favicon.svg", methods=["GET"])
    async def favicon_svg(request: Request):
        return Response(web.FAVICON_SVG, media_type="image/svg+xml", headers={"Cache-Control": "public, max-age=86400"})

    icon_512 = open(os.path.join(STATIC, "icon-512.png"), "rb").read()
    icon_256 = open(os.path.join(STATIC, "icon-256.png"), "rb").read()
    cache = {"Cache-Control": "public, max-age=86400"}

    @mcp.custom_route("/icon.png", methods=["GET"])
    async def icon_png(request: Request):
        return Response(icon_512, media_type="image/png", headers=cache)

    @mcp.custom_route("/apple-touch-icon.png", methods=["GET"])
    async def apple_icon(request: Request):
        return Response(icon_512, media_type="image/png", headers=cache)

    @mcp.custom_route("/favicon.png", methods=["GET"])
    async def favicon_png(request: Request):
        return Response(icon_256, media_type="image/png", headers=cache)

    @mcp.custom_route("/favicon.ico", methods=["GET"])
    async def favicon_ico(request: Request):
        # 直接返回 PNG（不跳转）：不少抓图工具不跟随跳转、不认 SVG，会退回去用主域名的图标
        return Response(icon_256, media_type="image/png", headers=cache)

    @mcp.custom_route("/signup", methods=["POST"])
    async def signup(request: Request):
        form = await request.form()
        ref = str(form.get("ref") or request.cookies.get("qx_ref") or "")
        try:
            _, token = net.signup(str(form.get("handle", "")), ref=ref or None)
        except Error as e:
            return page(web.message("没能注册", str(e)), status=400)
        return page(web.signup_done(public_url, str(form.get("handle", "")).strip(), token), title="注册成功 · 牵线")

    @mcp.custom_route("/login", methods=["GET", "POST"])
    async def login(request: Request):
        """OAuth 登录：新用户起昵称，老用户粘贴个人密钥。"""
        req = request.query_params.get("req", "")
        try:
            _, _, client_name = provider.pending(req)
        except Error as e:
            return page(web.message("登录链接已失效", str(e)), status=400)
        err = ""
        if request.method == "POST":
            form = await request.form()
            try:
                if form.get("handle"):
                    uid, _ = net.signup(str(form["handle"]), ref=request.cookies.get("qx_ref"))
                else:
                    uid, _ = net.auth(str(form.get("key", "")).strip())
                return RedirectResponse(provider.complete_login(req, uid), status_code=302)
            except Error as e:
                err = str(e)
        return page(web.login_page(client_name, err), title="授权 · 牵线")

    @mcp.custom_route("/me", methods=["GET", "POST"])
    async def manage(request: Request):
        if request.method == "GET":
            return page(web.me_form(), title="我的 · 牵线")
        form = await request.form()
        try:
            uid, handle = net.auth(str(form.get("key", "")).strip())
        except Error as e:
            return page(web.me_form(str(e)), title="我的 · 牵线")
        action = form.get("action")
        if action == "delete_profile":
            net.delete_profile(uid)
            return page(web.message("档案已删除", "你不会再收到新的介绍。需要时可以让 AI 重新帮你建档。"))
        if action == "delete_account":
            net.delete_account(uid)
            return page(web.message("账号已注销", "你的账号和所有数据已经删除。"))
        return page(web.me_view(handle, net.get_profile(uid), net.invite_link(uid)), title="我的 · 牵线")

    @mcp.custom_route("/docs", methods=["GET"])
    async def docs(request: Request):
        return page(web.docs_page(public_url), title="使用文档 · 牵线")

    @mcp.custom_route("/support", methods=["GET"])
    async def support(request: Request):
        return page(web.support_page(contact), title="支持 · 牵线")

    @mcp.custom_route("/.well-known/openai-apps-challenge", methods=["GET"])
    async def openai_challenge(request: Request):
        """OpenAI 插件目录的域名验证：把后台给的验证码写进数据目录的 openai-apps-challenge.txt。"""
        path = os.path.join(os.path.dirname(os.path.abspath(db_path)), "openai-apps-challenge.txt")
        if not os.path.exists(path):
            return Response("not configured", status_code=404, media_type="text/plain")
        return Response(open(path, encoding="utf-8").read().strip(), media_type="text/plain")

    @mcp.custom_route("/privacy", methods=["GET"])
    async def privacy(request: Request):
        return page(web.legal("privacy", contact), title="隐私政策 · 牵线")

    @mcp.custom_route("/terms", methods=["GET"])
    async def terms(request: Request):
        return page(web.legal("terms", contact), title="使用条款 · 牵线")

    return mcp


class LogRegisterFailures:
    """动态注册失败时，把请求体和返回的错误写进日志，方便排查各家客户端的兼容问题（注册信息不含机密）。"""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or scope["path"] != "/register":
            return await self.app(scope, receive, send)
        body = b""
        more = True
        while more:
            msg = await receive()
            body += msg.get("body", b"")
            more = msg.get("more_body", False)
        sent = False
        status = {"code": 0}
        resp = b""

        async def replay():
            nonlocal sent
            if sent:
                return {"type": "http.disconnect"}
            sent = True
            return {"type": "http.request", "body": body, "more_body": False}

        async def capture(message):
            nonlocal resp
            if message["type"] == "http.response.start":
                status["code"] = message["status"]
            elif message["type"] == "http.response.body":
                resp += message.get("body", b"")
            await send(message)

        await self.app(scope, replay, capture)
        if status["code"] >= 400:
            print(f"[register] {status['code']} 请求={body[:1500].decode('utf-8', 'replace')} 返回={resp[:500].decode('utf-8', 'replace')}",
                  flush=True)


def app():
    """供 uvicorn 使用：QIANXIAN_DB、QIANXIAN_PUBLIC_URL、QIANXIAN_CONTACT 可配置。"""
    public = os.environ.get("QIANXIAN_PUBLIC_URL", "http://127.0.0.1:8400").rstrip("/")
    mcp = build(os.environ.get("QIANXIAN_DB", "data/qianxian.db"), public, os.environ.get("QIANXIAN_CONTACT", ""))
    # 只接受发往本服务公网域名或本机的请求（防 DNS 重绑定）；反向代理后面也能用
    pub = urlparse(public)
    hosts = [pub.netloc, pub.hostname, "127.0.0.1", "localhost"] + [f"{h}:*" for h in ("127.0.0.1", "localhost")]
    security = TransportSecuritySettings(enable_dns_rebinding_protection=True, allowed_hosts=hosts,
                                         allowed_origins=[f"{pub.scheme}://{pub.netloc}", "https://chatgpt.com",
                                                          "https://chat.openai.com", "https://claude.ai"])
    return LogRegisterFailures(mcp.streamable_http_app(stateless_http=True, json_response=True, transport_security=security))
