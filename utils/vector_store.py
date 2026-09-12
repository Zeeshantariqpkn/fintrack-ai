"""
Lightweight in-memory vector store for FinTrack AI.
"""
from __future__ import annotations

import hashlib
import os
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

try:
    import requests
except ImportError:  # pragma: no cover
    requests = None  # type: ignore


DEFAULT_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
DEFAULT_EMBED_DIM = 384

HF_FEATURE_URL = "https://api-inference.huggingface.co/pipeline/feature-extraction/{model}"


def _get_hf_token() -> str:
    tok = os.environ.get("HF_TOKEN", "")
    if tok:
        return tok
    try:
        import streamlit as st
        tok = st.secrets.get("HF_TOKEN", "")
        if tok:
            os.environ["HF_TOKEN"] = tok
    except Exception:
        pass
    return tok


def _hf_available() -> bool:
    return bool(_get_hf_token()) and requests is not None


def _hash_embed(text: str, dim: int = DEFAULT_EMBED_DIM) -> np.ndarray:
    vec = np.zeros(dim, dtype=np.float32)
    tokens = str(text).lower().split()
    if not tokens:
        return vec
    for tok in tokens:
        h = hashlib.md5(tok.encode("utf-8")).hexdigest()
        idx = int(h[:8], 16) % dim
        sign = 1.0 if int(h[8:10], 16) % 2 == 0 else -1.0
        vec[idx] += sign
    norm = np.linalg.norm(vec)
    return vec / norm if norm > 0 else vec


def embed_texts_hf(texts: List[str], model: str) -> Optional[np.ndarray]:
    if not _hf_available() or not texts:
        return None
    url = HF_FEATURE_URL.format(model=model)
    headers = {"Authorization": f"Bearer {_get_hf_token()}"}
    payload = {"inputs": texts, "options": {"wait_for_model": True}}
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=45)
        if resp.status_code != 200:
            return None
        data = resp.json()
        arr = np.array(data, dtype=np.float32)
        if arr.ndim == 1:
            arr = arr.reshape(1, -1)
        if arr.ndim == 3:
            arr = arr.mean(axis=1)
        norms = np.linalg.norm(arr, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return arr / norms
    except Exception:
        return None


def embed_texts(
    texts: List[str],
    model: str = DEFAULT_EMBEDDING_MODEL,
    prefer_hf: bool = True,
) -> Tuple[np.ndarray, str]:
    if prefer_hf and _hf_available():
        hf = embed_texts_hf(texts, model)
        if hf is not None and hf.shape[0] == len(texts):
            return hf, "huggingface"
    mat = np.stack([_hash_embed(t) for t in texts], axis=0)
    return mat, "hash-fallback"


class VectorStore:
    def __init__(self) -> None:
        self.documents: List[Dict[str, Any]] = []
        self.matrix: Optional[np.ndarray] = None
        self.provider: str = "uninitialized"
        self.model: str = DEFAULT_EMBEDDING_MODEL

    def is_ready(self) -> bool:
        return self.matrix is not None and len(self.documents) > 0

    def size(self) -> int:
        return len(self.documents)

    def build(
        self,
        documents: List[Dict[str, Any]],
        model: str = DEFAULT_EMBEDDING_MODEL,
        prefer_hf: bool = True,
    ) -> None:
        self.documents = list(documents)
        self.model = model
        if not documents:
            self.matrix = None
            self.provider = "empty"
            return
        texts = [str(d.get("text", "")) for d in documents]
        mat, provider = embed_texts(texts, model=model, prefer_hf=prefer_hf)
        self.matrix = mat
        self.provider = provider

    def search(
        self,
        query: str,
        top_k: int = 5,
        model: str = DEFAULT_EMBEDDING_MODEL,
        prefer_hf: bool = True,
    ) -> List[Dict[str, Any]]:
        if not self.is_ready():
            return []
        q_vec, _ = embed_texts([query], model=model, prefer_hf=prefer_hf)
        q = q_vec[0]
        sims = self.matrix @ q
        order = np.argsort(-sims)[:top_k]
        results: List[Dict[str, Any]] = []
        for i in order:
            doc = dict(self.documents[int(i)])
            doc["score"] = float(sims[int(i)])
            results.append(doc)
        return results

    def stats(self) -> Dict[str, Any]:
        return {
            "size": self.size(),
            "provider": self.provider,
            "model": self.model,
            "dim": int(self.matrix.shape[1]) if self.matrix is not None else 0,
        }


def get_vector_store() -> VectorStore:
    import streamlit as st
    if "vector_store" not in st.session_state:
        st.session_state.vector_store = VectorStore()
    return st.session_state.vector_store


def reset_vector_store() -> VectorStore:
    import streamlit as st
    st.session_state.vector_store = VectorStore()
    return st.session_state.vector_store


def build_documents_from_state(state: Any) -> List[Dict[str, Any]]:
    docs: List[Dict[str, Any]] = []

    for e in state.stats.get("evidence", []):
        docs.append({
            "kind": "analytics",
            "text": f"[Analytics] {e['metric']}: {e['interpretation']}",
            "metric": e["metric"],
            "value": e["value"],
        })

    for r in state.risk.get("risks", []):
        docs.append({
            "kind": "risk",
            "text": (
                f"[Risk · {r.get('severity','')}] {r['title']}: {r['description']} "
                f"Evidence: {r.get('evidence','')}"
            ),
            "title": r["title"],
        })

    for o in state.opportunity.get("opportunities", []):
        docs.append({
            "kind": "opportunity",
            "text": (
                f"[Opportunity · {o.get('impact','')}] {o['title']}: {o['description']} "
                f"Evidence: {o.get('evidence','')}"
            ),
            "title": o["title"],
        })

    if state.decision:
        docs.append({
            "kind": "decision",
            "text": (
                f"[Decision · {state.decision.get('priority','')}] "
                f"{state.decision.get('title','')}: {state.decision.get('decision','')} "
                f"Reasoning: {state.decision.get('reasoning','')} "
                f"Expected impact: {state.decision.get('expected_impact','')}"
            ),
            "title": state.decision.get("title", ""),
        })
    if state.critic:
        docs.append({
            "kind": "critic",
            "text": (
                f"[Critic · {state.critic.get('status','')}] "
                f"{state.critic.get('reasoning','')}"
            ),
        })

    if state.summary:
        docs.append({
            "kind": "insight",
            "text": f"[Insight] {state.summary.get('narrative','')}",
        })

    for vendor, total in list(state.stats.get("vendor_totals", {}).items())[:10]:
        docs.append({
            "kind": "vendor",
            "text": f"[Vendor] {vendor} spent ${total:,.0f} in total expenses.",
            "vendor": vendor,
            "total": total,
        })

    for cat, total in state.stats.get("category_totals", {}).items():
        docs.append({
            "kind": "category",
            "text": f"[Category] {cat} totals ${total:,.0f} in expenses.",
            "category": cat,
            "total": total,
        })

    return docs
