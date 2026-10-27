#!/bin/bash
# 把牵线部署到服务器：上传代码 → 建 Python 3.11 虚拟环境 → 装依赖 → 启动 systemd 服务。
# 不会动 nginx 和 DNS：那两步见 deploy/README.md。
#   bash deploy/deploy.sh root@your-server
set -euo pipefail
HOST=${1:?用法：bash deploy/deploy.sh root@服务器}
cd "$(dirname "$0")/.."

tar --exclude=data --exclude=__pycache__ --exclude=.pytest_cache -czf /tmp/qianxian.tgz qianxian run.py requirements.txt deploy
scp -q /tmp/qianxian.tgz "$HOST":/tmp/
ssh "$HOST" 'set -e
  mkdir -p /opt/qianxian/data && tar -xzf /tmp/qianxian.tgz -C /opt/qianxian && rm /tmp/qianxian.tgz
  cd /opt/qianxian
  UV=$(command -v uv || echo /root/.local/bin/uv)
  [ -d .venv ] || $UV venv --python /usr/bin/python3.11 .venv
  # 国内服务器连不上 pypi.org，用阿里云镜像（可用 PIP_MIRROR 覆盖）
  UV_NO_CACHE=1 $UV pip install --python .venv/bin/python -q --index-url "${PIP_MIRROR:-https://mirrors.aliyun.com/pypi/simple/}" -r requirements.txt
  cp deploy/qianxian.service /etc/systemd/system/qianxian.service
  systemctl daemon-reload && systemctl enable -q qianxian && systemctl restart qianxian
  sleep 2 && systemctl is-active qianxian && curl -s -o /dev/null -w "本机自检 HTTP %{http_code}\n" http://127.0.0.1:8400/
  df -h / | tail -1'
