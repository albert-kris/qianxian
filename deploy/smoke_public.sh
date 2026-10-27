#!/bin/bash
# 公网自检：直连服务器 IP（绕过本机代理和假 IP），检查 HTTPS、OAuth 元数据和 MCP 鉴权。
#   bash deploy/smoke_public.sh [域名] [服务器IP]
H=${1:-connect.memixai.com}
IP=${2:?用法：bash deploy/smoke_public.sh 域名 服务器IP}
c() { curl --resolve "$H:443:$IP" --resolve "$H:80:$IP" --noproxy '*' -m 20 -s "$@"; }

echo "1 首页:              $(c -o /dev/null -w '%{http_code}' "https://$H/")"
echo "2 HTTP→HTTPS:        $(c -o /dev/null -w '%{http_code} -> %{redirect_url}' "http://$H/")"
echo "3 证书:              $(c -v -o /dev/null "https://$H/" 2>&1 | grep -E 'subject:|expire date' | sed 's/^\* *//' | tr '\n' ' ')"
echo "4 受保护资源元数据:  $(c "https://$H/.well-known/oauth-protected-resource/mcp")"
echo "5 授权服务器元数据:  $(c "https://$H/.well-known/oauth-authorization-server" | python -c 'import json,sys;d=json.load(sys.stdin);print(d["issuer"],"|",d["registration_endpoint"],"|",d.get("code_challenge_methods_supported"))')"
echo "6 未登录调用 MCP:    $(c -X POST -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' -d '{}' -o /dev/null -D - "https://$H/mcp" | grep -iE '^HTTP|www-authenticate' | tr -d '\r' | tr '\n' ' ')"
