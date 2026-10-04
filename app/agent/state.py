from typing import Any, Literal, TypedDict


Intent = Literal[
    "product_question",
    "pricing_question",
    "account_issue",
    "technical_issue",
    "api_question",
    "refund_request",
    "ticket_query",
    "create_ticket",
    "human_handoff",
    "report_request",
    "unclear",
]


class AgentState(TypedDict, total=False):
    user_input: str
    user_id: str | None
    intent: Intent
    route: str
    retrieved_context: list[dict[str, str]]
    tool_result: dict[str, Any]
    skill_result: dict[str, Any]
    response: str
    conversation: list[dict[str, str]]
    ticket_id: str | None

