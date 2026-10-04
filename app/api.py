from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.agent import build_customer_service_graph
from app.config import PROJECT_ROOT


app = FastAPI(title="CloudDesk Customer Service Agent")
agent_graph = build_customer_service_graph()
STATIC_DIR = PROJECT_ROOT / "app" / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class ChatRequest(BaseModel):
    message: str = Field(..., examples=["专业版和基础版有什么区别？"])
    user_id: str | None = Field(default=None, examples=["u1001"])
    conversation: list[dict[str, str]] = Field(default_factory=list)


class ChatResponse(BaseModel):
    intent: str
    response: str
    state: dict


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/")
def frontend() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    state = agent_graph.invoke(
        {
            "user_input": request.message,
            "user_id": request.user_id,
            "conversation": request.conversation,
        }
    )
    return ChatResponse(
        intent=state.get("intent", "unknown"),
        response=state.get("response", ""),
        state=state,
    )
