import re
from typing import Any

try:
    from langgraph.graph import END, StateGraph
except ModuleNotFoundError:
    END = "__end__"
    StateGraph = None

from app.agent.intents import classify_intent
from app.agent.state import AgentState
from app.rag import retrieve_knowledge
from app.skills import (
    generate_conversation_summary,
    generate_operation_report,
    generate_ticket_report,
)
from app.tools import (
    create_ticket,
    get_subscription_info,
    get_ticket_status,
    get_user_status,
)


def _extract_user_id(text: str) -> str | None:
    match = re.search(r"\b[uU]\d{4}\b", text)
    return match.group(0).lower() if match else None


def _extract_ticket_id(text: str) -> str | None:
    match = re.search(r"\b[Tt]-?\d{4,8}\b", text)
    if not match:
        return None
    ticket_id = match.group(0).upper()
    return ticket_id if "-" in ticket_id else f"T-{ticket_id[1:]}"


def classify_node(state: AgentState) -> AgentState:
    text = state["user_input"]
    state["intent"] = classify_intent(text)
    state["user_id"] = state.get("user_id") or _extract_user_id(text)
    state["ticket_id"] = state.get("ticket_id") or _extract_ticket_id(text)
    if state["intent"] == "unclear" and state.get("ticket_id"):
        state["intent"] = "ticket_query"
    return state


def route_after_classify(state: AgentState) -> str:
    intent = state["intent"]
    if intent in {"product_question", "pricing_question", "api_question", "technical_issue"}:
        return "rag"
    if intent in {"account_issue", "refund_request", "ticket_query", "create_ticket", "human_handoff"}:
        return "tools"
    if intent == "report_request":
        return "skills"
    return "clarify"


def rag_node(state: AgentState) -> AgentState:
    contexts = retrieve_knowledge(state["user_input"])
    if not contexts and state.get("intent") == "product_question":
        contexts = retrieve_knowledge("CloudDesk 产品介绍 功能 支持")
    state["retrieved_context"] = contexts
    return state


def tools_node(state: AgentState) -> AgentState:
    intent = state["intent"]
    user_id = state.get("user_id")
    text = state["user_input"]

    if intent == "account_issue":
        state["tool_result"] = get_user_status(user_id) if user_id else {
            "missing": "user_id",
            "message": "需要用户 ID 才能查询账号状态，例如 u1001。",
        }
    elif intent == "ticket_query":
        ticket_id = state.get("ticket_id")
        state["tool_result"] = get_ticket_status(ticket_id) if ticket_id else {
            "missing": "ticket_id",
            "message": "需要工单号才能查询进度，例如 T-1001。",
        }
    elif intent in {"refund_request", "create_ticket", "human_handoff"}:
        report = generate_ticket_report(text, user_id)
        created = create_ticket(
            user_id=user_id,
            title=report["工单标题"],
            description=report["问题描述"],
            priority=report["优先级"],
        )
        state["tool_result"] = created
        state["skill_result"] = report
    else:
        state["tool_result"] = get_subscription_info(user_id) if user_id else {
            "message": "当前问题可能需要补充用户 ID。",
        }
    return state


def skills_node(state: AgentState) -> AgentState:
    text = state["user_input"]
    conversation = state.get("conversation", [])

    if "运营" in text or "分析" in text:
        records = [
            {"intent": "pricing_question", "status": "resolved", "human_handoff": False},
            {"intent": "account_issue", "status": "resolved", "human_handoff": False},
            {"intent": "refund_request", "status": "unresolved", "human_handoff": True},
            {"intent": "api_question", "status": "resolved", "human_handoff": False},
        ]
        state["skill_result"] = generate_operation_report(records)
    elif "工单" in text:
        state["skill_result"] = generate_ticket_report(text, state.get("user_id"), state.get("tool_result"))
    else:
        state["skill_result"] = generate_conversation_summary(conversation)
    return state


def clarify_node(state: AgentState) -> AgentState:
    state["response"] = "我还需要更多信息才能处理。你可以说明问题类型、用户 ID 或工单号，例如：u1001 登录失败，或查询 T-1001。"
    return state


def response_node(state: AgentState) -> AgentState:
    intent = state["intent"]

    if state.get("response"):
        return state

    if state.get("skill_result") and intent == "report_request":
        state["response"] = _format_report(state["skill_result"])
    elif state.get("tool_result"):
        state["response"] = _format_tool_response(state)
    elif state.get("retrieved_context"):
        state["response"] = _format_rag_response(state)
    else:
        state["response"] = "暂时没有检索到足够信息，我建议补充用户 ID、工单号或更具体的问题描述。"

    conversation = state.get("conversation", [])
    conversation.extend(
        [
            {"role": "user", "content": state["user_input"]},
            {"role": "assistant", "content": state["response"]},
        ]
    )
    state["conversation"] = conversation
    return state


def _format_rag_response(state: AgentState) -> str:
    contexts = state["retrieved_context"]
    answer_lines = ["根据 CloudDesk 知识库，相关信息如下："]
    for item in contexts:
        answer_lines.append(f"- 来源 {item['source']}：{item['content'][:180]}")
    answer_lines.append("如果你提供用户 ID，我还可以继续查询账户或订阅状态。")
    return "\n".join(answer_lines)


def _format_tool_response(state: AgentState) -> str:
    result = state["tool_result"]
    if result.get("created"):
        ticket = result["ticket"]
        report = state.get("skill_result")
        extra = f"\n\n同时已生成工单报告：\n{_format_report(report)}" if report else ""
        return f"已创建工单 {ticket['ticket_id']}，优先级 {ticket['priority']}，当前状态 {ticket['status']}。{extra}"
    if result.get("found"):
        return f"查询结果：{result}"
    return result.get("message", f"工具返回：{result}")


def _format_report(report: dict[str, Any] | None) -> str:
    if not report:
        return "暂无报告内容。"
    lines = [f"{report.get('title', '报告')}"]
    for key, value in report.items():
        if key in {"skill", "title"}:
            continue
        lines.append(f"{key}：{value}")
    return "\n".join(lines)


def build_customer_service_graph():
    if StateGraph is None:
        return LocalCustomerServiceGraph()

    graph = StateGraph(AgentState)
    graph.add_node("classify", classify_node)
    graph.add_node("rag", rag_node)
    graph.add_node("tools", tools_node)
    graph.add_node("skills", skills_node)
    graph.add_node("clarify", clarify_node)
    graph.add_node("generate_response", response_node)

    graph.set_entry_point("classify")
    graph.add_conditional_edges(
        "classify",
        route_after_classify,
        {
            "rag": "rag",
            "tools": "tools",
            "skills": "skills",
            "clarify": "clarify",
        },
    )
    graph.add_edge("rag", "generate_response")
    graph.add_edge("tools", "generate_response")
    graph.add_edge("skills", "generate_response")
    graph.add_edge("clarify", END)
    graph.add_edge("generate_response", END)
    return graph.compile()


class LocalCustomerServiceGraph:
    """Dependency-light runner for local demos when LangGraph is not installed."""

    def invoke(self, state: AgentState) -> AgentState:
        state = classify_node(state)
        route = route_after_classify(state)
        if route == "rag":
            state = rag_node(state)
            return response_node(state)
        if route == "tools":
            state = tools_node(state)
            return response_node(state)
        if route == "skills":
            state = skills_node(state)
            return response_node(state)
        return clarify_node(state)
