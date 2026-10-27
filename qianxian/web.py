"""官网页面：首页、注册结果、OAuth 授权页、档案管理、隐私政策、使用条款。

纯字符串模板，不引入前端构建。视觉主题是“红线”：牵线 = 月老的红线，把两个人连起来。
"""

import html

BRAND = "Red Thread 牵线"
TAGLINE = "让你的 AI，替你牵线"

LOGO_SVG = """<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
<circle cx="14" cy="40" r="9" fill="currentColor"/><circle cx="50" cy="24" r="9" fill="currentColor"/>
<path d="M22 36 C 30 12, 34 52, 42 28" fill="none" stroke="#e5484d" stroke-width="5" stroke-linecap="round"/></svg>"""

FAVICON_SVG = """<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg"><rect width="64" height="64" rx="14" fill="#16131a"/>
<circle cx="18" cy="40" r="7" fill="#fff"/><circle cx="46" cy="24" r="7" fill="#fff"/>
<path d="M24 37 C 31 16, 34 50, 41 28" fill="none" stroke="#ff5a5f" stroke-width="5" stroke-linecap="round"/></svg>"""

CSS = """
:root{--bg:#faf8f5;--surface:#ffffff;--ink:#16131a;--muted:#6b6470;--line:#e9e4de;--accent:#e5484d;--accent-ink:#ffffff;
--soft:#fdecec;--code:#f3efea;--shadow:0 1px 2px rgba(22,19,26,.04),0 8px 24px rgba(22,19,26,.06)}
@media (prefers-color-scheme:dark){:root{--bg:#121014;--surface:#1b181f;--ink:#f4f1f6;--muted:#a59fac;--line:#2c2731;
--accent:#ff6369;--accent-ink:#16131a;--soft:#2a1719;--code:#221e26;--shadow:none}}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.7 -apple-system,BlinkMacSystemFont,"PingFang SC","Hiragino Sans GB","Microsoft YaHei",system-ui,sans-serif}
a{color:inherit}a:hover{color:var(--accent)}
.wrap{max-width:1040px;margin:0 auto;padding:0 20px}
header.top{position:sticky;top:0;z-index:5;background:color-mix(in srgb,var(--bg) 88%,transparent);backdrop-filter:blur(10px);border-bottom:1px solid var(--line)}
header.top .wrap{display:flex;align-items:center;justify-content:space-between;height:60px}
.brand{display:flex;align-items:center;gap:10px;font-weight:700;text-decoration:none;letter-spacing:.2px}
.brand svg{width:28px;height:28px;color:var(--ink)}.brand small{font-weight:500;color:var(--muted);margin-left:2px}
nav a{margin-left:22px;text-decoration:none;color:var(--muted);font-size:15px}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;border:0;border-radius:999px;padding:12px 22px;font:inherit;font-weight:600;cursor:pointer;text-decoration:none;transition:transform .15s,opacity .15s}
.btn:hover{transform:translateY(-1px)}.btn.primary{background:var(--ink);color:var(--bg)}.btn.primary:hover{color:var(--bg)}
.btn.ghost{background:transparent;border:1px solid var(--line);color:var(--ink)}
.btn.red{background:var(--accent);color:var(--accent-ink)}.btn.red:hover{color:var(--accent-ink)}
.hero{padding:84px 0 56px;display:grid;grid-template-columns:1.1fr .9fr;gap:48px;align-items:center}
.eyebrow{display:inline-block;font-size:13px;font-weight:600;color:var(--accent);background:var(--soft);padding:4px 12px;border-radius:999px}
h1{font-size:clamp(36px,5.6vw,58px);line-height:1.12;margin:18px 0 18px;letter-spacing:-.5px}
h1 em{font-style:normal;color:var(--accent)}
.lead{font-size:18px;color:var(--muted);max-width:34em;margin:0 0 28px}
.cta{display:flex;flex-wrap:wrap;gap:12px;align-items:center}
.signup{display:flex;gap:8px;flex-wrap:wrap;margin-top:6px}
.signup input,.field{flex:1 1 200px;min-width:0;border:1px solid var(--line);background:var(--surface);color:var(--ink);border-radius:999px;padding:12px 18px;font:inherit}
.field{border-radius:12px;width:100%}
.note{font-size:13px;color:var(--muted);margin-top:10px}
.chat{background:var(--surface);border:1px solid var(--line);border-radius:20px;padding:20px;box-shadow:var(--shadow)}
.msg{max-width:88%;padding:10px 14px;border-radius:16px;margin:10px 0;font-size:15px;line-height:1.55}
.msg.me{margin-left:auto;background:var(--ink);color:var(--bg);border-bottom-right-radius:6px}
.msg.ai{background:var(--code);border-bottom-left-radius:6px}
.card{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:12px 14px;margin-top:8px;font-size:14px}
.card b{display:block;margin-bottom:2px}.card .why{color:var(--muted)}
.pill{display:inline-block;margin:8px 6px 0 0;padding:5px 12px;border-radius:999px;font-size:13px;font-weight:600}
.pill.yes{background:var(--accent);color:var(--accent-ink)}.pill.no{border:1px solid var(--line);color:var(--muted)}
section{padding:56px 0;border-top:1px solid var(--line)}
h2{font-size:clamp(26px,3.4vw,34px);margin:0 0 10px;letter-spacing:-.3px}
.sub{color:var(--muted);margin:0 0 32px}
.grid3{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}
.tile{background:var(--surface);border:1px solid var(--line);border-radius:18px;padding:22px}
.tile .n{font-size:13px;font-weight:700;color:var(--accent)}.tile h3{margin:6px 0 6px;font-size:19px}.tile p{margin:0;color:var(--muted);font-size:15px}
.promise{display:grid;grid-template-columns:repeat(2,1fr);gap:14px 28px}
.promise div{display:flex;gap:12px}.promise .dot{flex:none;width:22px;height:22px;border-radius:50%;background:var(--soft);color:var(--accent);display:grid;place-items:center;font-size:13px;font-weight:700;margin-top:3px}
.promise p{margin:0}.promise b{display:block}.promise span{color:var(--muted);font-size:15px}
.tabs{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:14px}
.tab{border:1px solid var(--line);background:transparent;color:var(--muted);border-radius:999px;padding:7px 16px;font:inherit;font-size:14px;cursor:pointer}
.tab[aria-selected=true]{background:var(--ink);color:var(--bg);border-color:var(--ink)}
.panel{display:none}.panel.on{display:block}
.panel ol{margin:0;padding-left:20px}.panel li{margin:6px 0}
pre,code.k{background:var(--code);border-radius:10px;font:14px/1.6 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
code.k{padding:2px 8px}
.copy{position:relative}.copy pre{margin:10px 0;padding:14px 88px 14px 16px;overflow-x:auto;white-space:pre-wrap;word-break:break-all}
.copy button{position:absolute;top:8px;right:8px;border:1px solid var(--line);background:var(--surface);color:var(--ink);border-radius:8px;padding:4px 10px;font-size:13px;cursor:pointer}
.say{display:flex;flex-wrap:wrap;gap:10px}.say span{background:var(--surface);border:1px solid var(--line);border-radius:999px;padding:8px 16px;font-size:15px}
details{border-bottom:1px solid var(--line);padding:14px 0}summary{cursor:pointer;font-weight:600}details p{color:var(--muted);margin:8px 0 0}
footer{border-top:1px solid var(--line);padding:28px 0 40px;color:var(--muted);font-size:14px}
footer .wrap{display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap}footer a{margin-left:16px}
.box{max-width:620px;margin:56px auto;background:var(--surface);border:1px solid var(--line);border-radius:20px;padding:32px;box-shadow:var(--shadow)}
.box h1{font-size:30px;margin:0 0 8px}.box h3{margin:26px 0 6px;font-size:17px}
.err{background:var(--soft);color:var(--accent);border-radius:10px;padding:10px 14px;margin:14px 0}
.keybox{background:var(--code);border-radius:12px;padding:14px 16px;font:15px ui-monospace,Menlo,Consolas,monospace;word-break:break-all}
.doc{max-width:760px;margin:48px auto}.doc h1{font-size:34px}.doc h2{font-size:20px;margin-top:28px}.doc p,.doc li{color:var(--muted)}
table.kv{width:100%;border-collapse:collapse;font-size:15px}table.kv td{border-top:1px solid var(--line);padding:10px 8px;vertical-align:top}
table.kv td:first-child{color:var(--muted);width:30%}
@media (max-width:820px){.hero{grid-template-columns:1fr;padding-top:48px}.grid3,.promise{grid-template-columns:1fr}nav a.hide{display:none}.box{margin:24px 16px;padding:24px}}
"""

JS = """
document.querySelectorAll('.copy button').forEach(b=>b.onclick=()=>{navigator.clipboard.writeText(b.previousElementSibling.innerText);b.textContent='已复制';setTimeout(()=>b.textContent='复制',1500)});
document.querySelectorAll('.tab').forEach(t=>t.onclick=()=>{document.querySelectorAll('.tab').forEach(x=>x.setAttribute('aria-selected',x===t));
document.querySelectorAll('.panel').forEach(p=>p.classList.toggle('on',p.id===t.dataset.p))});
"""


def e(s):
    return html.escape(str(s))


def layout(title, body, public_url, contact=""):
    mail = f'<a href="mailto:{e(contact)}">{e(contact)}</a>' if contact else ""
    return f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(title)}</title>
<meta name="description" content="让你的 ChatGPT / Claude 替你找人：AI 根据对你的了解写一份私有档案，把你的作品和需求递给真正想认识你的人，对方同意才接通。">
<meta property="og:title" content="{BRAND} · {TAGLINE}"><meta property="og:description" content="AI 帮你找到真正想认识你的人，对方同意才接通。">
<link rel="icon" href="/favicon.png" type="image/png" sizes="256x256"><link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta property="og:image" content="{public_url}/icon.png"><style>{CSS}</style></head><body>
<header class="top"><div class="wrap"><a class="brand" href="/">{LOGO_SVG}{BRAND}</a>
<nav><a class="hide" href="/#how">怎么用</a><a class="hide" href="/docs">文档</a><a href="/#connect">接入</a><a href="/me">我的</a></nav></div></header>
{body}
<footer><div class="wrap"><div>© 2026 词元迭代 Tokeniter · {BRAND}</div><div>{mail}<a href="/docs">文档</a><a href="/support">支持</a><a href="/privacy">隐私政策</a><a href="/terms">使用条款</a></div></div></footer>
<script>{JS}</script></body></html>"""


def copy_block(text):
    return f'<div class="copy"><pre>{e(text)}</pre><button type="button">复制</button></div>'


def home(public_url, ref=""):
    mcp = f"{public_url}/mcp"
    ref_input = f'<input type="hidden" name="ref" value="{e(ref)}">' if ref else ""
    invited = '<p class="note">你是被朋友邀请来的，注册后你们会自动关联。</p>' if ref else ""
    return f"""
<main class="wrap">
<div class="hero">
  <div>
    <span class="eyebrow">给 ChatGPT · Claude 用的引荐网络</span>
    <h1>让你的 AI，<br>替你<em>牵线</em>。</h1>
    <p class="lead">你的 AI 最懂你。让它把你的作品、需求和想法，递到真正想认识你的人手里。<b>对方点头才接通</b>，不群发、不打扰。</p>
    <form class="signup" method="post" action="/signup">{ref_input}
      <input name="handle" placeholder="起个昵称，例如 小王做AI" required maxlength="24" aria-label="昵称">
      <button class="btn primary">免费注册</button>
    </form>{invited}
    <p class="note">已经注册？<a href="#connect">直接接入你的 AI</a> · 免费 · 随时删除</p>
  </div>
  <div class="chat" aria-label="使用示例">
    <div class="msg me">帮我找几个可能想试用我 AI 测试工具的人</div>
    <div class="msg ai">好的。我根据你的档案写了一段介绍，已经递给 3 位可能感兴趣的人。他们同意后我会告诉你。</div>
    <div class="msg ai">有一张介绍卡片给你：
      <div class="card"><b>阿杰 · 创业公司后端负责人</b><span class="why">“团队测试覆盖率太低，想找能自动写测试的工具”</span></div>
      <span class="pill yes">想认识</span><span class="pill no">先不了</span>
    </div>
  </div>
</div>
</main>

<section id="how"><div class="wrap">
  <h2>三步，一句话就能用</h2><p class="sub">不用学新软件，在你常用的 AI 里说话就行。</p>
  <div class="grid3">
    <div class="tile"><div class="n">01 · 建档</div><h3>AI 替你写档案</h3><p>你的 AI 根据对你的了解，起草一份私有档案：你是谁、在找什么、能提供什么。你看过、点头才保存。</p></div>
    <div class="tile"><div class="n">02 · 找人</div><h3>说出你想找谁</h3><p>“找想试用我产品的人”“找懂增长的合伙人”。牵线在网络里匹配，把你的介绍递给最可能感兴趣的人。</p></div>
    <div class="tile"><div class="n">03 · 接通</div><h3>对方同意才接通</h3><p>对方的 AI 把卡片拿给他看。他点“想认识”，你们才互相看到；婉拒的话，你不会知道。</p></div>
  </div>
</div></section>

<section id="trust"><div class="wrap">
  <h2>把隐私放在第一位</h2><p class="sub">引荐网络最怕变成骚扰网络。这些规则写在代码里，不是写在宣传里。</p>
  <div class="promise">
    <div><span class="dot">1</span><p><b>你看不到名单</b><span>发起方只看到“接受了的人”。没回应、婉拒的人，你永远不知道是谁。</span></p></div>
    <div><span class="dot">2</span><p><b>婉拒没有压力</b><span>点“先不了”，对方不会收到任何通知，也不会再被同一个人打扰。</span></p></div>
    <div><span class="dot">3</span><p><b>只存档案，不存聊天</b><span>我们只保存你确认过的那份档案，不读、不存你和 AI 的聊天记录。</span></p></div>
    <div><span class="dot">4</span><p><b>敏感信息不收</b><span>健康、性取向、宗教政治、财务和证件信息，系统直接拒收。</span></p></div>
    <div><span class="dot">5</span><p><b>防骚扰额度</b><span>每人每天最多发起 3 次、每次最多 10 人；每人同时最多收 5 张卡片。</span></p></div>
    <div><span class="dot">6</span><p><b>一键删除</b><span>随时在“我的”页面删除档案或注销账号，数据立即清除。</span></p></div>
  </div>
</div></section>

<section id="connect"><div class="wrap">
  <h2>接入你的 AI</h2><p class="sub">选一个你常用的。接入后对 AI 说：“用牵线帮我建个档案”。</p>
  <div class="tabs" role="tablist">
    <button class="tab" role="tab" aria-selected="true" data-p="p-claude">Claude</button>
    <button class="tab" role="tab" aria-selected="false" data-p="p-chatgpt">ChatGPT</button>
    <button class="tab" role="tab" aria-selected="false" data-p="p-code">Claude Code</button>
    <button class="tab" role="tab" aria-selected="false" data-p="p-other">Cursor · 其他</button>
  </div>
  <div class="panel on" id="p-claude"><ol>
    <li>打开 Claude 网页版或桌面版 → <b>设置 → 连接器 → 添加自定义连接器</b></li>
    <li>名称填“牵线”，地址填：</li></ol>{copy_block(mcp)}
    <ol start="3"><li>点“连接”，在牵线页面注册或登录，授权完成即可。</li></ol></div>
  <div class="panel" id="p-chatgpt"><ol>
    <li>ChatGPT → <b>设置</b> → 打开<b>开发者模式</b>（不同版本在“应用与连接器 → 高级”或“安全与登录”里）</li>
    <li>新建连接器，地址填下面这个，认证选 <b>OAuth</b>：</li></ol>{copy_block(mcp)}
    <ol start="3"><li>点“连接”，在牵线页面注册或登录即可。</li></ol>
    <p class="note">自定义连接器目前只对部分 ChatGPT 账号开放；找不到开关时可以先用 Claude。</p></div>
  <div class="panel" id="p-code"><p>先在上方注册拿到个人密钥，再在终端运行：</p>
    {copy_block(f'claude mcp add --transport http qianxian {mcp} --header "Authorization: Bearer 你的密钥"')}</div>
  <div class="panel" id="p-other"><p>任何支持远程 MCP 的客户端都可以接入（Cursor、Cherry Studio 等）。地址：</p>{copy_block(mcp)}
    <p>支持 OAuth 的客户端会自动跳到登录页；不支持的，请求头加上 <code class="k">Authorization: Bearer 你的密钥</code>。</p></div>
</div></section>

<section><div class="wrap">
  <h2>接入后，这样跟 AI 说</h2><p class="sub">牵线会告诉你的 AI 该怎么做，你只要说出想法。</p>
  <div class="say"><span>“用牵线帮我建个档案”</span><span>“帮我找几个想试用我产品的人”</span><span>“牵线里有人找我吗？”</span>
  <span>“我想找一个懂增长的合伙人”</span><span>“给我一个邀请链接，我发给朋友”</span><span>“把我的档案删掉”</span></div>
</div></section>

<section><div class="wrap">
  <h2>常见问题</h2>
  <details><summary>它和发广告、群发私信有什么不同？</summary><p>牵线只把你的介绍递给“自己说过在找这类东西”的人，而且对方同意才接通。每天额度有限，同一个人 30 天内不会被同一个人重复打扰。</p></details>
  <details><summary>我的 AI 会把我的隐私发出去吗？</summary><p>不会自动发。档案是你的 AI 起草、你逐条确认后才保存的；联系方式只在对方接受后才给对方看，而且可以不填，直接在牵线里留言。</p></details>
  <details><summary>要钱吗？</summary><p>目前免费。</p></details>
  <details><summary>网络里现在人多吗？</summary><p>刚刚起步。用“给我一个邀请链接”把它分享给可能感兴趣的朋友，网络越大，越容易找到对的人。</p></details>
</div></section>"""


def signup_done(public_url, handle, token):
    mcp = f"{public_url}/mcp"
    return f"""<div class="box"><h1>欢迎，{e(handle)}</h1>
<p>这是你的<b>个人密钥</b>，只显示这一次，请马上保存（它等于你的账号，不要发给别人）：</p>
{copy_block(token)}
<h3>接入 Claude / ChatGPT（推荐）</h3><p>在连接器设置里添加自定义连接器，地址填下面这个；点“连接”后粘贴上面的密钥登录：</p>{copy_block(mcp)}
<h3>接入 Claude Code</h3>{copy_block(f'claude mcp add --transport http qianxian {mcp} --header "Authorization: Bearer {token}"')}
<h3>然后对你的 AI 说</h3><div class="say"><span>“用牵线帮我建个档案”</span></div>
<p class="note" style="margin-top:20px"><a href="/#connect">查看各个 AI 的详细接入步骤 →</a></p></div>"""


def login_page(client_name, err=""):
    who = e(client_name)
    error = f'<div class="err">{e(err)}</div>' if err else ""
    return f"""<div class="box"><h1>授权 {who} 使用牵线</h1>
<p>授权后，{who} 可以以你的身份：读写你的牵线档案、帮你发起找人、查看并回应别人给你的介绍。所有对外动作都会先征求你的同意。</p>{error}
<h3>第一次来</h3><form method="post" class="signup"><input name="handle" placeholder="起个昵称" required maxlength="24"><button class="btn red">注册并授权</button></form>
<h3>已有账号</h3><form method="post" class="signup"><input name="key" placeholder="粘贴个人密钥 qx_…" required><button class="btn primary">授权</button></form>
<p class="note">可以随时在 <a href="/me">我的</a> 页面删除数据或注销账号。</p></div>"""


def message(title, text, link=("/", "回到首页")):
    return f'<div class="box"><h1>{e(title)}</h1><p>{e(text)}</p><p><a class="btn ghost" href="{link[0]}">{e(link[1])}</a></p></div>'


def me_form(err=""):
    error = f'<div class="err">{e(err)}</div>' if err else ""
    return f"""<div class="box"><h1>我的牵线</h1><p>输入个人密钥，查看档案、删除档案或注销账号。</p>{error}
<form method="post"><input class="field" name="key" placeholder="个人密钥 qx_…" required>
<div class="cta" style="margin-top:14px"><button class="btn primary" name="action" value="view">查看</button>
<button class="btn ghost" name="action" value="delete_profile" onclick="return confirm('确定删除档案？删除后不会再收到介绍。')">删除档案</button>
<button class="btn ghost" name="action" value="delete_account" onclick="return confirm('确定注销？所有数据会立即删除且无法恢复。')">注销账号</button></div></form></div>"""


LABELS = {"headline": "一句话身份", "roles": "角色", "tags": "标签", "looking_for": "在找什么", "offering": "能提供什么",
          "summary": "补充介绍", "contact": "联系方式（接通后可见）", "discoverable": "接收介绍", "max_pending": "最多待处理卡片"}


def me_view(handle, profile, invite):
    if profile:
        rows = "".join(f"<tr><td>{LABELS.get(k, k)}</td><td>{e('、'.join(v) if isinstance(v, list) else ('是' if v is True else '否' if v is False else v))}</td></tr>"
                       for k, v in profile.items() if k in LABELS)
        body = f'<table class="kv">{rows}</table>'
    else:
        body = '<p>还没有档案。对你的 AI 说：“用牵线帮我建个档案”。</p>'
    return f"""<div class="box"><h1>{e(handle)}</h1>{body}
<h3>邀请朋友加入（已邀请 {invite['invited']} 人）</h3>{copy_block(invite['link'])}</div>"""


TOOLS_DOC = [
    ("overview", "牵线总览", "现状和建议的下一步。不知道从哪开始时，AI 会先调用它。", "只读"),
    ("profile_guide", "建档指南", "字段说明、好坏示例、确认流程、禁止写入的敏感信息。", "只读"),
    ("save_profile", "保存档案", "保存你确认过的档案。必须 user_confirmed=true。", "写入"),
    ("get_my_profile", "查看我的档案", "查看自己的档案。", "只读"),
    ("delete_my_profile", "删除我的档案", "删除档案，之后不再收到介绍。", "删除"),
    ("request_intros", "帮我找人", "把你的介绍递给最可能感兴趣的人（每天 3 次、每次最多 10 人）。", "对外"),
    ("my_requests", "我的找人进度", "看谁接受了你的介绍。没接受的人不会出现。", "只读"),
    ("check_intros", "查看介绍卡片", "别人想认识你的卡片。", "只读"),
    ("respond_intro", "回应介绍", "想认识 / 先不了。婉拒不会通知对方。", "对外"),
    ("connections", "已接通的人", "双方都同意的联系人。", "只读"),
    ("send_message", "发消息", "给已接通的人留言。", "对外"),
    ("read_messages", "读消息", "读取与某个联系人的消息。", "只读"),
    ("my_invite_link", "我的邀请链接", "专属邀请链接和可直接转发的邀请语。", "只读"),
]


def docs_page(public_url):
    mcp = f"{public_url}/mcp"
    rows = "".join(f"<tr><td><code class='k'>{n}</code><br>{t}</td><td>{d}</td><td>{k}</td></tr>" for n, t, d, k in TOOLS_DOC)
    return f"""<div class="doc wrap"><h1>使用文档</h1>
<p>{BRAND} 是一个远程 MCP 服务：你常用的 AI（ChatGPT、Claude、Cursor 等）接入后，就能替你建档、找人、回应介绍。</p>
<h2>1. 接入</h2><p>服务地址：</p>{copy_block(mcp)}
<ul><li><b>Claude</b>：设置 → 连接器 → 添加自定义连接器 → 填上面的地址 → 连接 → 在牵线页面注册或登录。</li>
<li><b>ChatGPT</b>：设置 → 插件（或应用与连接器）→ 添加自定义 MCP 服务器 → 地址同上，身份验证选 OAuth → 创建 → 登录授权。</li>
<li><b>Claude Code</b>：在<a href="/">首页</a>注册拿到个人密钥后运行
<code class="k">claude mcp add --transport http qianxian {mcp} --header "Authorization: Bearer 密钥"</code></li></ul>
<h2>2. 开始用</h2><ol><li>说“用牵线帮我建个档案”：AI 起草档案，你确认后保存。</li>
<li>说“帮我找几个想试用我产品的人”：AI 和你确认介绍语后发起，对方同意才会出现在你的列表里。</li>
<li>说“牵线里有人找我吗？”：AI 把介绍卡片拿给你看，由你决定想认识还是先不了。</li>
<li>接通后说“帮我给他打个招呼”：AI 起草消息，你同意后发送。</li></ol>
<h2>3. 工具一览</h2><table class="kv"><tr><td><b>工具</b></td><td><b>作用</b></td><td><b>类型</b></td></tr>{rows}</table>
<h2>4. 规则</h2><ul><li>所有对外动作（保存档案、发起找人、回应介绍、发消息）都需要你本人同意。</li>
<li>发起方看不到没接受的人；婉拒不通知对方；同一人 30 天内不会被同一人重复打扰。</li>
<li>每人每天最多发起 3 次请求，每次最多 10 人；每人同时最多 5 张待处理卡片（可调）。</li>
<li>健康、性取向、宗教政治、财务和证件信息不会被保存。</li></ul>
<p>更多问题见<a href="/support">支持</a>，数据处理见<a href="/privacy">隐私政策</a>。</p></div>"""


def support_page(contact):
    mail = f'<a href="mailto:{e(contact)}">{e(contact)}</a>' if contact else "（即将公布）"
    return f"""<div class="doc wrap"><h1>支持</h1>
<p>遇到问题、想反馈建议，或要举报骚扰内容，请发邮件到 {mail}，我们通常在 2 个工作日内回复。</p>
<h2>常见问题</h2>
<p><b>连接时提示授权失败？</b> 回到 AI 应用里重新点“连接”。登录链接 15 分钟内有效。</p>
<p><b>忘了个人密钥？</b> 密钥只在注册时显示一次。可以用新昵称重新注册，或通过 ChatGPT / Claude 的 OAuth 登录（新用户直接注册）。</p>
<p><b>不想再收到介绍？</b> 让 AI 删除档案，或在<a href="/me">我的</a>页面删除；也可以在档案里关闭“接收介绍”。</p>
<p><b>收到骚扰？</b> 直接婉拒即可（对方不会知道），并把对方昵称发到上面的邮箱，我们会处理。</p>
<p>更多用法见<a href="/docs">使用文档</a>。</p></div>"""


def legal(kind, contact):
    who = f"邮件 {e(contact)}" if contact else "官网公布的联系方式"
    if kind == "privacy":
        return f"""<div class="doc wrap"><h1>隐私政策</h1><p>更新日期：2026 年 10 月 27 日</p>
<p>{BRAND}（以下简称“牵线”）由词元迭代 Tokeniter 运营。我们只收集提供引荐服务所必需的信息。</p>
<h2>我们收集什么</h2><ul><li>账号：你设置的昵称；个人密钥只以不可逆的哈希形式保存。</li>
<li>档案：你的 AI 起草、经你确认后提交的内容（一句话身份、角色、标签、在找什么、能提供什么、补充介绍、可选的联系方式）。</li>
<li>使用记录：你发起的找人请求、收到和回应的介绍、接通后在牵线内发送的消息。</li>
<li>授权信息：你授权的 AI 应用（如 ChatGPT、Claude）的客户端标识和访问令牌（只存哈希）。</li></ul>
<h2>我们不收集什么</h2><ul><li>你和 AI 的聊天记录。牵线只收到你确认后提交的档案。</li>
<li>健康、性取向、宗教政治立场、财务和证件号等敏感信息；系统会拒收包含这类内容的档案。</li></ul>
<h2>信息怎么用</h2><ul><li>档案只用于匹配，不会公开展示。别人收到的介绍卡片只包含发起方的昵称、一句话身份和他写的介绍。</li>
<li>你的联系方式只在你接受介绍（或对方接受你的介绍）后才对对方可见。</li>
<li>发起方看不到未接受或婉拒的人；婉拒不会通知对方。</li>
<li>我们不出售你的信息，也不用于广告。</li></ul>
<h2>保存与删除</h2><p>数据保存在中国境内的服务器上。你可以随时在“我的”页面删除档案或注销账号，相关数据会立即删除。</p>
<h2>联系我们</h2><p>如有任何问题，请通过{who}联系我们。</p></div>"""
    return f"""<div class="doc wrap"><h1>使用条款</h1><p>更新日期：2026 年 10 月 27 日</p>
<p>使用{BRAND}即表示你同意以下条款。</p>
<h2>你承诺</h2><ul><li>档案内容真实，不冒充他人，不包含他人隐私。</li>
<li>不利用牵线发送广告、诈骗、骚扰或违法内容；不绕过额度限制批量打扰他人。</li>
<li>保管好个人密钥；通过你的密钥或授权的 AI 应用发生的操作视为你本人的操作。</li></ul>
<h2>我们承诺</h2><ul><li>按隐私政策处理你的信息；对方同意才接通。</li>
<li>对违反条款的账号，我们可以限制功能或删除账号。</li></ul>
<h2>免责</h2><p>牵线只负责匹配和传递介绍，不对用户之间的后续沟通、交易或合作作出保证。请自行判断对方的身份和意图。</p>
<h2>联系我们</h2><p>请通过{who}联系我们。</p></div>"""
