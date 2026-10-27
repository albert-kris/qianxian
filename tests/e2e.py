"""端到端测试：起一个真实服务，用官方 MCP 客户端模拟 5 个用户走完整流程。

python tests/e2e.py
"""

import asyncio
import base64
import hashlib
import json
import os
import re
import secrets
import subprocess
import sys
import tempfile
import time
import urllib.parse
import urllib.request

import httpx2
from mcp.client.client import Client, streamable_http_client

PORT = 8401
BASE = f"http://127.0.0.1:{PORT}"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PROFILES = {
    "alice": dict(headline="独立开发者，在做 AI 自动写单元测试的工具", roles=["founder", "developer"],
                  tags=["AI", "测试自动化", "Python", "开发者工具"], looking_for="想找愿意试用的早期用户和反馈",
                  offering="可以免费帮团队接入自动测试", summary="之前在大厂做测试平台", contact="alice@example.com"),
    "bob": dict(headline="创业公司后端负责人", roles=["developer"], tags=["后端", "Python", "测试"],
                looking_for="团队单元测试覆盖率太低，想找能自动写测试、提高覆盖率的工具", offering="可以分享高并发经验",
                summary="10 人技术团队", contact="tg:@bob_backend"),
    "carol": dict(headline="天使投资人，关注 AI 基础设施", roles=["investor"], tags=["AI", "开发者工具", "SaaS"],
                  looking_for="在看 AI 开发者工具、测试和代码质量方向的早期项目", offering="天使轮投资和产品建议",
                  summary="投过 3 个开发者工具项目", contact="carol@fund.example"),
    "dave": dict(headline="自由插画师", roles=["designer"], tags=["插画", "品牌设计"], looking_for="想接游戏和绘本的插画外包",
                 offering="插画和品牌视觉", summary="接过 50 多个商业项目", contact="dave@art.example"),
    "eve": dict(headline="测试工程师", roles=["developer"], tags=["测试", "自动化测试"], looking_for="想找自动化测试的新工具",
                offering="测试经验", summary="不想被打扰", contact="eve@example.com", discoverable=False),
}


def signup(handle):
    data = urllib.parse.urlencode({"handle": handle}).encode()
    page = urllib.request.urlopen(f"{BASE}/signup", data=data, timeout=10).read().decode()
    return re.search(r"qx_[A-Za-z0-9_\-]+", page).group(0)


def client(token):
    http = httpx2.AsyncClient(headers={"Authorization": f"Bearer {token}"}, timeout=30)
    return Client(streamable_http_client(f"{BASE}/mcp", http_client=http))


async def call(token, tool, **args):
    async with client(token) as c:
        r = await c.call_tool(tool, args)
    if r.structured_content is not None:
        out = r.structured_content
        return out.get("result", out) if isinstance(out, dict) and set(out) == {"result"} else out
    return json.loads(r.content[0].text)


def check(cond, msg):
    print(("通过 " if cond else "失败 ") + msg)
    if not cond:
        raise SystemExit(1)


async def main():
    tokens = {h: signup(h) for h in PROFILES}
    check(all(t.startswith("qx_") for t in tokens.values()), "5 个用户注册成功")

    async with client(tokens["alice"]) as c:
        names = {t.name for t in (await c.list_tools()).tools}
    check({"profile_guide", "save_profile", "request_intros", "check_intros", "respond_intro"} <= names,
          f"MCP 工具列表：{sorted(names)}")

    r = await call(tokens["bob"], "save_profile", **PROFILES["bob"])
    check("error" in r and "user_confirmed" in r["error"], "未经用户确认不能保存档案")
    r = await call(tokens["bob"], "save_profile", **{**PROFILES["bob"], "summary": "最近在看抑郁症"}, user_confirmed=True)
    check("error" in r and "敏感" in r["error"], "敏感信息被拒收")
    for h, p in PROFILES.items():
        r = await call(tokens[h], "save_profile", **p, user_confirmed=True)
        check(r.get("headline") == p["headline"], f"{h} 建档成功")

    r = await call(tokens["alice"], "request_intros",
                   pitch="我做了一个 AI 自动写单元测试的工具，能把覆盖率从 30% 提到 70%，想找团队免费试用并给反馈",
                   looking_for="测试覆盖率低、想提高代码质量的开发团队，或关注开发者工具的投资人", max_intros=5)
    print("   发起结果：", r)
    check(r.get("sent", 0) >= 2, "alice 的请求匹配并送达了至少 2 人")

    cards = {h: (await call(tokens[h], "check_intros"))["cards"] for h in ("bob", "carol", "dave", "eve")}
    check(len(cards["bob"]) == 1 and "AI 自动写单元测试" in cards["bob"][0]["pitch"], "bob 收到了介绍卡片")
    print("   bob 看到的卡片：", cards["bob"][0])
    check(len(cards["dave"]) == 0, "插画师 dave 没有被打扰（不相关）")
    check(len(cards["eve"]) == 0, "eve 关闭了接收，没有收到卡片")

    reqs = (await call(tokens["alice"], "my_requests"))["requests"]
    check(reqs[0]["accepted"] == 0 and not reqs[0]["accepted_people"], "对方回应前，alice 看不到任何名单")

    r = await call(tokens["bob"], "respond_intro", intro_id=cards["bob"][0]["intro_id"], accept=True)
    check(r["status"] == "accepted" and r["connected_with"]["contact"] == "alice@example.com", "bob 接受后看到 alice 的联系方式")
    if cards["carol"]:
        await call(tokens["carol"], "respond_intro", intro_id=cards["carol"][0]["intro_id"], accept=False)

    reqs = (await call(tokens["alice"], "my_requests"))["requests"]
    people = reqs[0]["accepted_people"]
    check(len(people) == 1 and people[0]["contact"] == "tg:@bob_backend", "alice 只看到接受了的 bob，看不到婉拒的人")

    iid = people[0]["intro_id"]
    await call(tokens["alice"], "send_message", intro_id=iid, body="你好 bob，周三方便视频 20 分钟吗？")
    await call(tokens["bob"], "send_message", intro_id=iid, body="可以，下午三点。")
    msgs = await call(tokens["bob"], "read_messages", intro_id=iid)
    check(len(msgs["messages"]) == 2 and "untrusted_content_note" in msgs, "接通后双方可以互发消息，且带不可信内容提示")
    r = await call(tokens["dave"], "send_message", intro_id=iid, body="插一句")
    check("error" in r, "第三方无法往别人的对话里发消息")

    for _ in range(2):
        await call(tokens["alice"], "request_intros", pitch="再试一次", looking_for="开发者")
    r = await call(tokens["alice"], "request_intros", pitch="第四次", looking_for="开发者")
    check("error" in r and "每天最多" in r["error"], "每天发起次数有上限（防骚扰）")

    r = httpx2.post(f"{BASE}/mcp", headers={"Authorization": "Bearer qx_fake"}, json={})
    check(r.status_code == 401, "无效密钥被拒绝（401）")

    ov = await call(tokens["bob"], "overview")
    check(ov["has_profile"] and ov["connections"] == 1 and ov["next_step"], f"overview 给出现状和下一步：{ov['next_step']}")
    inv = await call(tokens["alice"], "my_invite_link")
    code = urllib.parse.parse_qs(urllib.parse.urlparse(inv["link"]).query)["ref"][0]
    urllib.request.urlopen(f"{BASE}/signup", data=urllib.parse.urlencode({"handle": "grace", "ref": code}).encode(), timeout=10)
    inv = await call(tokens["alice"], "my_invite_link")
    check(inv["invited"] == 1 and "牵线" in inv["share_text"], "邀请链接注册的新用户记在邀请人名下")
    tok_h = signup("henry")
    r = await call(tok_h, "save_profile", headline="学生", roles=["student"], tags=["AI"], looking_for="找实习",
                   offering="写代码", user_confirmed=True)
    check(r.get("contact") == "", "联系方式可以不填")
    r = await call(tok_h, "request_intros", pitch="冷门需求", looking_for="会做陶艺的非洲鼓手", max_intros=3)
    check(r.get("sent") == 0 and "invite" in r, "匹配不到人时返回邀请链接")
    for path in ("/", "/docs", "/support", "/privacy", "/terms", "/me", "/favicon.svg", "/favicon.ico", "/icon.png"):
        check(httpx2.get(BASE + path).status_code == 200, f"页面 {path} 可访问")

    await oauth_flow(tokens["alice"])
    print("\n全部通过")


async def oauth_flow(alice_key):
    """模拟 ChatGPT / Claude 网页版的“添加连接器 → 登录 → 授权”全过程。"""
    print("\n-- OAuth 流程 --")
    h = httpx2.Client(base_url=BASE, follow_redirects=False, timeout=30)

    r = h.post("/mcp", json={})
    check(r.status_code == 401 and "resource_metadata" in r.headers.get("www-authenticate", ""),
          "未登录访问 MCP 返回 401，并指明资源元数据地址")
    meta_url = re.search(r'resource_metadata="([^"]+)"', r.headers["www-authenticate"]).group(1)
    prm = h.get(urllib.parse.urlparse(meta_url).path).json()
    asm = h.get("/.well-known/oauth-authorization-server").json()
    check(prm["authorization_servers"] and {"authorization_endpoint", "token_endpoint", "registration_endpoint"} <= set(asm),
          "元数据发现正常（受保护资源 + 授权服务器）")

    redirect = "https://chatgpt.com/connector_platform_oauth_redirect"
    reg = h.post("/register", json={"client_name": "ChatGPT", "redirect_uris": [redirect],
                                     "grant_types": ["authorization_code", "refresh_token"],
                                     "response_types": ["code"], "token_endpoint_auth_method": "none"}).json()
    check("client_id" in reg, "动态客户端注册成功")

    def authorize():
        verifier = secrets.token_urlsafe(48)
        challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
        r = h.get("/authorize", params={"response_type": "code", "client_id": reg["client_id"], "redirect_uri": redirect,
                                        "code_challenge": challenge, "code_challenge_method": "S256", "state": "st123",
                                        "scope": "qianxian", "resource": f"{BASE}/mcp"})
        login = urllib.parse.urlparse(r.headers["location"])
        return verifier, f"{login.path}?{login.query}"

    verifier, login_path = authorize()
    check(login_path.startswith("/login?req="), "授权请求跳转到牵线登录页")
    check("ChatGPT" in h.get(login_path).text, "登录页显示是哪个应用在申请授权")
    r = h.post(login_path, data={"key": "qx_wrong"})
    check(r.status_code == 200 and "无效" in r.text, "错误的密钥登录失败")
    r = h.post(login_path, data={"key": alice_key})
    back = urllib.parse.urlparse(r.headers["location"])
    q = urllib.parse.parse_qs(back.query)
    check(r.status_code == 302 and back.geturl().startswith(redirect) and q["state"] == ["st123"], "登录成功，带着授权码跳回 ChatGPT")

    tok_req = {"grant_type": "authorization_code", "code": q["code"][0], "redirect_uri": redirect,
               "client_id": reg["client_id"], "code_verifier": verifier, "resource": f"{BASE}/mcp"}
    bad = h.post("/token", data={**tok_req, "code_verifier": "wrong" * 10})
    check(bad.status_code == 400, "PKCE 校验：错误的 code_verifier 换不到令牌")
    tok = h.post("/token", data=tok_req).json()
    check(tok.get("access_token", "").startswith("qxa_") and tok.get("refresh_token"), "授权码换到访问令牌和刷新令牌")
    check(h.post("/token", data=tok_req).status_code == 400, "授权码只能用一次")

    prof = await call(tok["access_token"], "get_my_profile")
    check(prof.get("headline", "").startswith("独立开发者"), "用 OAuth 令牌调用 MCP，识别为 alice 本人")

    new = h.post("/token", data={"grant_type": "refresh_token", "refresh_token": tok["refresh_token"],
                                 "client_id": reg["client_id"]}).json()
    check(new.get("access_token") and new["access_token"] != tok["access_token"], "刷新令牌换到新的访问令牌")
    r = h.post("/mcp", headers={"Authorization": f"Bearer {tok['access_token']}"}, json={})
    check(r.status_code == 401, "刷新后旧的访问令牌失效（令牌轮换）")

    verifier, login_path = authorize()
    r = h.post(login_path, data={"handle": "frank"})
    q = urllib.parse.parse_qs(urllib.parse.urlparse(r.headers["location"]).query)
    tok = h.post("/token", data={"grant_type": "authorization_code", "code": q["code"][0], "redirect_uri": redirect,
                                 "client_id": reg["client_id"], "code_verifier": verifier}).json()
    r = await call(tok["access_token"], "get_my_profile")
    check(r.get("profile", "x") is None, "新用户在授权页直接注册，拿到令牌后可以开始建档")

    # 模拟 Claude：注册时申请自己的 scope（claudeai），也要能连上
    cb = "https://claude.ai/api/mcp/auth_callback"
    reg2 = h.post("/register", json={"client_name": "Claude", "redirect_uris": [cb], "scope": "claudeai",
                                      "grant_types": ["authorization_code", "refresh_token"],
                                      "response_types": ["code"], "token_endpoint_auth_method": "client_secret_post"})
    check(reg2.status_code == 201, f"申请其他 scope 的客户端也能注册（{reg2.status_code}）")
    reg2 = reg2.json()
    verifier = secrets.token_urlsafe(48)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    r = h.get("/authorize", params={"response_type": "code", "client_id": reg2["client_id"], "redirect_uri": cb,
                                    "code_challenge": challenge, "code_challenge_method": "S256", "state": "c1",
                                    "scope": "claudeai", "resource": f"{BASE}/mcp"})
    loc = urllib.parse.urlparse(r.headers.get("location", ""))
    r = h.post(f"{loc.path}?{loc.query}", data={"key": alice_key})
    q = urllib.parse.parse_qs(urllib.parse.urlparse(r.headers["location"]).query)
    tok = h.post("/token", data={"grant_type": "authorization_code", "code": q["code"][0], "redirect_uri": cb,
                                 "client_id": reg2["client_id"], "client_secret": reg2.get("client_secret", ""),
                                 "code_verifier": verifier}).json()
    r = await call(tok["access_token"], "get_my_profile")
    check(r.get("headline", "").startswith("独立开发者"), "Claude 式客户端（scope=claudeai）完成授权并调用工具")


if __name__ == "__main__":
    tmp = tempfile.mkdtemp()
    log = open(os.path.join(tmp, "server.log"), "w")  # 不能用 PIPE：没人读时缓冲区写满会把服务卡住
    srv = subprocess.Popen([sys.executable, "run.py", "--port", str(PORT), "--db", os.path.join(tmp, "test.db")],
                           cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
    try:
        for _ in range(50):
            try:
                urllib.request.urlopen(BASE + "/", timeout=1)
                break
            except Exception:
                time.sleep(0.3)
        asyncio.run(main())
    finally:
        srv.terminate()
