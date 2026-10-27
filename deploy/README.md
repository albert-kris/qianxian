# 公网部署（目标：ChatGPT、Claude 网页版可接入）

两家都要求一个**公网可访问的 HTTPS 地址**，并通过 OAuth 登录（已实现）。正式地址：`connect.memixai.com`（memixai.com 已备案，服务器在阿里云北京；identai.cn 目前被阿里云以备案不合规拦截，恢复后可迁回）。

1. **DNS**：在阿里云 DNS 控制台给 memixai.com 加一条 A 记录：`connect` → `<服务器 IP>`。
2. **证书 + 反向代理**：`certbot certonly --webroot -w /www/wwwroot/acme -d connect.memixai.com` 申请证书，再把 `deploy/nginx-qianxian.conf` 放进宝塔的 nginx 站点目录，`nginx -t` 通过后 reload。
3. **部署服务**：`bash deploy/deploy.sh root@<你的服务器>`（上传代码、建虚拟环境、装依赖、启动 `qianxian` 服务）。
4. **自检**：打开 `https://connect.memixai.com/.well-known/oauth-authorization-server`，应返回 JSON。

## 接入

- **ChatGPT**：设置 → 应用与连接器 → 开启开发者模式 → 创建连接器，地址填 `https://connect.memixai.com/mcp`，认证选 OAuth。
- **Claude 网页版**：设置 → 连接器 → 添加自定义连接器，地址填 `https://connect.memixai.com/mcp`。
- **Claude Code**：`claude mcp add --transport http qianxian https://connect.memixai.com/mcp --header "Authorization: Bearer <个人密钥>"`

点“连接”后会跳到牵线的登录页：新用户起昵称，老用户粘贴个人密钥。

## 注意

- 这台服务器的系统盘只剩约 1.2G。依赖已经精简到 `mcp` + `uvicorn`，安装时不留缓存；数据库是一个 SQLite 文件，要定期备份 `/opt/qianxian/data/qianxian.db`。
- 换域名时，同时改 `deploy/qianxian.service` 里的 `--public-url` 和 nginx 的 `server_name`。
