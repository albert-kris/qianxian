<p align="center"><img src="launch/icon-256.png" width="96" alt="Red Thread"></p>

<h1 align="center">Red Thread · 牵线</h1>

<p align="center"><b>Your AI finds the people who actually want to meet you. Both sides opt in.</b><br>
让你的 AI 替你牵线：把你的作品和需求递给真正想认识你的人，对方同意才接通。</p>

<p align="center">
<a href="https://connect.memixai.com">Website</a> ·
<a href="https://connect.memixai.com/docs">Docs</a> ·
<a href="https://registry.modelcontextprotocol.io">MCP Registry: <code>com.memixai/connect</code></a>
</p>

---

## What it is

Red Thread is an **AI-native introduction network**, delivered as a remote [MCP](https://modelcontextprotocol.io) server. Connect it to ChatGPT, Claude, Cursor or any MCP client, then just talk:

> "Use Red Thread to set up my profile." → your AI drafts a private profile from what it knows about you; you approve it.
> "Find a few people who might try my product." → introduction cards go to people who said they're looking for exactly that.
> "Anyone want to meet me on Red Thread?" → you see cards addressed to you and decide.

**Double opt-in, by design** (enforced server-side, not by prompts):

- Senders never see who was matched — only people who accepted.
- Declining is silent; the same sender can't re-introduce you for 30 days.
- Only the profile you approved is stored — never your chat history. Sensitive categories (health, sexual orientation, religion/politics, finances, ID numbers) are rejected.
- Rate limits: 3 requests/day, ≤10 people each; each user holds ≤5 pending cards.
- Delete your profile or account at any time.

## Connect

Server URL: `https://connect.memixai.com/mcp` (OAuth 2.1 with dynamic client registration and PKCE)

| Client | How |
|---|---|
| Claude (web / desktop) | Settings → Connectors → Add custom connector → paste the URL |
| ChatGPT | Settings → Apps / Plugins → Developer mode → add custom MCP server → URL, auth **OAuth** |
| Claude Code | sign up at the website for a personal key, then `claude mcp add --transport http redthread https://connect.memixai.com/mcp --header "Authorization: Bearer <key>"` |
| Others | any client that supports remote MCP (Streamable HTTP) |

## Tools

| Tool | Kind | What it does |
|---|---|---|
| `overview` | read | Status and suggested next step |
| `profile_guide` | read | Profile fields, examples, what's not accepted |
| `save_profile` | write | Save the profile (`user_confirmed=true` required) |
| `get_my_profile` / `delete_my_profile` | read / delete | View or delete the profile |
| `request_intros` | outward | Send introduction cards to matching people |
| `my_requests` | read | Who accepted your introductions |
| `check_intros` / `respond_intro` | read / outward | Cards addressed to you; accept or decline |
| `connections`, `send_message`, `read_messages` | read / outward | Talk with people you're connected to |
| `my_invite_link` | read | Personal invite link |

## Architecture

```
your AI ──MCP (Streamable HTTP, OAuth token or personal key)──┐
                                                              ▼
  qianxian/server.py    MCP tools + website (sign-up, OAuth login, docs, legal pages)
  qianxian/oauth.py     OAuth 2.1 authorization server (protocol from the MCP Python SDK)
  qianxian/core.py      identity, profiles, requests, cards, double opt-in, messages, quotas
  qianxian/matching.py  matching (char n-gram TF-IDF + tags; pluggable)
  qianxian/db.py        SQLite
```

## Run it yourself

```bash
pip install -r requirements.txt        # mcp, uvicorn
python run.py --port 8400              # http://127.0.0.1:8400
python tests/test_core.py && python tests/e2e.py
```

Deploying behind nginx with HTTPS: see [deploy/README.md](deploy/README.md).

## Roadmap

- English website and cross-lingual matching (Chinese ↔ English profiles)
- Notifications (email / Telegram / Lark)
- A learned matching model: "would this person want to meet you?"

---

## 中文简介

**牵线**是给 AI 用的引荐网络（远程 MCP 服务）。接到 ChatGPT、Claude、Cursor 之后，直接对 AI 说：

- “用牵线帮我建个档案”：AI 根据对你的了解起草一份私有档案，你确认后才保存；
- “帮我找几个想试用我产品的人”：介绍卡片递给自己说过在找这类东西的人；
- “牵线里有人想认识我吗？”：看别人发给你的卡片，由你决定想认识还是先不了。

**双向确认，由服务端强制执行：** 发起方只看到接受了的人；婉拒不通知对方；只保存你确认过的档案，不读聊天记录；敏感信息拒收；每天最多 3 次、每次最多 10 人；随时一键删除。

官网：<https://connect.memixai.com> · 支持：<https://connect.memixai.com/support>

## License

See [LICENSE](LICENSE).
