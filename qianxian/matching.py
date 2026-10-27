"""匹配：给一条“帮我找人”的请求，在私有档案里打分排序。

MVP 用字符 n-gram 的 TF-IDF 余弦相似度（对中文和中英混排都稳），加标签重合度。
纯 Python 实现，不依赖 numpy / scikit-learn，部署包更小。
接口只有 rank()，以后可以直接换成我们自己的决策模型（判断“这个人会不会想认识”）。
"""

import math
import re
from collections import Counter

W_NEED, W_IDENTITY, W_TAGS = 0.6, 0.3, 0.1
MIN_SCORE = 0.05


def _tokens(text):
    return {t.lower() for t in re.findall(r"[A-Za-z][A-Za-z0-9+#.\-]{1,}|[一-鿿]{2,}", text)}


def _ngrams(text):
    """按词切开后取 2~3 字符的 n-gram，词两侧补空格（同 sklearn 的 char_wb）。"""
    grams = Counter()
    for w in re.findall(r"\S+", text.lower()):
        w = f" {w} "
        for n in (2, 3):
            grams.update(w[i:i + n] for i in range(len(w) - n + 1))
    return grams


def _tfidf(docs):
    counts = [_ngrams(d) for d in docs]
    df = Counter(g for c in counts for g in c)
    n = len(docs)
    vecs = []
    for c in counts:
        v = {g: (1 + math.log(tf)) * (math.log((1 + n) / (1 + df[g])) + 1) for g, tf in c.items()}
        norm = math.sqrt(sum(x * x for x in v.values())) or 1.0
        vecs.append({g: x / norm for g, x in v.items()})
    return vecs


def _cos(a, b):
    if len(a) > len(b):
        a, b = b, a
    return sum(x * b.get(g, 0.0) for g, x in a.items())


def rank(request_text, candidates, limit):
    """candidates: [{user_id, need_text, identity_text, tags}]。返回 [(user_id, score, matched_terms)]，按分数降序。"""
    if not candidates:
        return []
    n = len(candidates)
    vecs = _tfidf([request_text] + [c["need_text"] for c in candidates] + [c["identity_text"] for c in candidates])
    q = vecs[0]
    req_lower, req_terms = request_text.lower(), _tokens(request_text)
    out = []
    for i, c in enumerate(candidates):
        tags = {t.lower() for t in c["tags"]}
        hit = sorted(t for t in tags if t in req_lower or t in req_terms)
        tag_score = len(hit) / max(1, len(tags))
        score = W_NEED * _cos(q, vecs[1 + i]) + W_IDENTITY * _cos(q, vecs[1 + n + i]) + W_TAGS * tag_score
        if score >= MIN_SCORE:
            out.append((c["user_id"], float(score), hit))
    out.sort(key=lambda x: -x[1])
    return out[:limit]
