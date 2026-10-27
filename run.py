"""启动服务：python run.py [--host 0.0.0.0] [--port 8400] [--public-url https://example.com]"""

import argparse
import os

import uvicorn

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8400)
    ap.add_argument("--public-url", default=None, help="对外访问的网址，用于生成接入命令")
    ap.add_argument("--db", default="data/qianxian.db")
    a = ap.parse_args()
    os.chdir(os.path.dirname(os.path.abspath(__file__)))  # 相对路径（数据库等）都以项目目录为准
    os.environ["QIANXIAN_DB"] = a.db
    os.environ["QIANXIAN_HOST"] = a.host
    os.environ["QIANXIAN_PUBLIC_URL"] = a.public_url or f"http://{a.host}:{a.port}"
    # 关闭时最多等 3 秒：ChatGPT 等客户端会保持长连接，默认会一直等到 systemd 超时（约 90 秒），期间服务不可用
    uvicorn.run("qianxian.server:app", factory=True, host=a.host, port=a.port, timeout_graceful_shutdown=3)
