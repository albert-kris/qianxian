"""核心逻辑的单元测试（不起服务）：python tests/test_core.py"""

import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from qianxian.core import Network  # noqa: E402
from qianxian.db import DB  # noqa: E402

PROFILE = dict(headline="开发者", roles=["developer"], tags=["测试"], looking_for="想找能自动写测试的工具",
               offering="经验", user_confirmed=True)


def test_demo_isolation():
    net = Network(DB(os.path.join(tempfile.mkdtemp(), "t.db")))
    real_a, _ = net.signup("real_a")
    real_b, _ = net.signup("real_b")
    demo_r, _ = net.signup("demo_r")
    demo_s, _ = net.signup("demo_s")
    net.db.x("UPDATE users SET is_demo = 1 WHERE id IN (?, ?)", (demo_r, demo_s))
    for u in (real_a, real_b, demo_r, demo_s):
        net.save_profile(u, **PROFILE)

    net.request_intros(real_a, "自动写测试的工具", "想提高测试覆盖率的开发者")
    got = {c["from"].split("（")[0] for u in (real_b, demo_r) for c in net.check_intros(u)["cards"]}
    assert net.check_intros(real_b)["cards"], "真实用户应该收到真实用户的介绍"
    assert not net.check_intros(demo_r)["cards"], "演示账号不应收到真实用户的介绍"

    net.request_intros(demo_s, "自动写测试的工具", "想提高测试覆盖率的开发者")
    assert net.check_intros(demo_r)["cards"], "演示账号之间可以互相匹配"
    assert len(net.check_intros(real_b)["cards"]) == 1, "真实用户不应收到演示账号的介绍"
    print("通过 演示账号与真实用户互相隔离", got)


if __name__ == "__main__":
    test_demo_isolation()
