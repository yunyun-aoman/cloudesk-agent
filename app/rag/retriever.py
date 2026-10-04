from dataclasses import dataclass
import re

from app.config import KNOWLEDGE_BASE_DIR


@dataclass
class DocumentChunk:
    source: str
    content: str


def _tokenize(text: str) -> set[str]:
    words = set(re.findall(r"[a-zA-Z0-9_]+", text.lower()))
    chinese_terms = {
        term
        for term in (
            "价格",
            "套餐",
            "产品",
            "介绍",
            "功能",
            "什么样",
            "是什么",
            "专业版",
            "基础版",
            "企业版",
            "登录",
            "账号",
            "工单",
            "退款",
            "api",
            "接口",
            "知识库",
            "sla",
            "客户",
        )
        if term in text.lower()
    }
    return words | chinese_terms


def _load_chunks() -> list[DocumentChunk]:
    chunks: list[DocumentChunk] = []
    for path in sorted(KNOWLEDGE_BASE_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        parts = [part.strip() for part in re.split(r"\n#{1,3} ", text) if part.strip()]
        for part in parts:
            chunks.append(DocumentChunk(source=path.name, content=part))
    return chunks


def retrieve_knowledge(query: str, top_k: int = 3) -> list[dict[str, str]]:
    query_terms = _tokenize(query)
    scored: list[tuple[int, DocumentChunk]] = []
    for chunk in _load_chunks():
        score = len(query_terms & _tokenize(chunk.content))
        if score:
            scored.append((score, chunk))

    scored.sort(key=lambda item: item[0], reverse=True)
    return [
        {"source": chunk.source, "content": chunk.content}
        for _, chunk in scored[:top_k]
    ]
