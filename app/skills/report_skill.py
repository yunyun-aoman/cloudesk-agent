from collections import Counter
from typing import Any


def generate_conversation_summary(conversation: list[dict[str, str]]) -> dict[str, Any]:
    user_messages = [item["content"] for item in conversation if item.get("role") == "user"]
    assistant_messages = [item["content"] for item in conversation if item.get("role") == "assistant"]
    latest_user_issue = user_messages[-1] if user_messages else "暂无用户问题"

    return {
        "skill": "conversation_summary",
        "title": "客服会话总结报告",
        "用户问题": latest_user_issue,
        "处理过程": "Agent 已完成意图识别，并根据问题选择知识库检索、业务工具或转人工流程。",
        "Agent回复": assistant_messages[-1] if assistant_messages else "暂无回复",
        "是否解决": "需根据用户后续反馈确认",
        "是否创建工单": any("工单" in message for message in assistant_messages),
        "是否转人工": any("人工" in message for message in assistant_messages),
        "后续建议": "若用户仍未解决，建议创建高优先级工单并转二线客服。",
    }


def generate_ticket_report(
    user_input: str,
    user_id: str | None,
    tool_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    priority = "high" if any(word in user_input for word in ("退款", "投诉", "不可用", "故障")) else "medium"
    return {
        "skill": "ticket_report",
        "title": "工单处理报告",
        "工单标题": user_input[:36],
        "问题类型": "退款/投诉/技术故障" if priority == "high" else "普通咨询",
        "问题描述": user_input,
        "用户信息": user_id or "未提供用户 ID",
        "已执行操作": tool_result or "尚未调用业务工具",
        "当前状态": "待客服进一步处理",
        "优先级": priority,
        "建议处理人": "support-l2" if priority == "high" else "support-l1",
        "建议处理方案": "先复现用户问题，再结合订阅状态、账户状态和日志信息给出处理结论。",
    }


def generate_operation_report(records: list[dict[str, Any]]) -> dict[str, Any]:
    intents = [record.get("intent", "unknown") for record in records]
    counter = Counter(intents)
    unresolved = [record for record in records if record.get("status") == "unresolved"]
    handoff_count = sum(1 for record in records if record.get("human_handoff"))
    total = len(records)

    return {
        "skill": "operation_report",
        "title": "客服运营分析报告",
        "报告周期": "最近样例数据",
        "总咨询量": total,
        "主要问题类型": counter.most_common(3),
        "高频问题": ["套餐差异", "登录失败", "API Token 使用", "退款政策"],
        "未解决问题": len(unresolved),
        "转人工比例": f"{handoff_count / total:.0%}" if total else "0%",
        "产品改进建议": "补充登录排障引导、API 错误码页面和套餐对比表。",
        "知识库补充建议": "增加退款时效、SLA 升级规则和 Webhook 示例。",
    }

