import re

from app.agent.state import Intent


INTENT_KEYWORDS: list[tuple[Intent, tuple[str, ...]]] = [
    ("report_request", ("报告", "总结", "分析", "质检", "运营")),
    ("human_handoff", ("人工", "真人", "客服经理", "投诉")),
    ("refund_request", ("退款", "退费", "取消订阅", "赔偿")),
    ("create_ticket", ("创建工单", "生成工单", "新建工单", "提交工单", "提交问题", "故障反馈", "报障")),
    ("ticket_query", ("查询工单", "工单进度", "工单状态", "进度", "处理到哪", "状态")),
    ("account_issue", ("登录", "账号", "密码", "无法登陆", "无法登录")),
    ("api_question", ("api", "接口", "token", "密钥", "webhook")),
    ("pricing_question", ("价格", "多少钱", "套餐", "专业版", "基础版", "企业版")),
    ("technical_issue", ("报错", "故障", "不可用", "502", "超时", "慢")),
    ("product_question", ("产品", "什么样", "是什么", "功能", "支持", "怎么用", "介绍", "clouddesk")),
]


def classify_intent(text: str) -> Intent:
    normalized = text.lower()
    if re.fullmatch(r"\s*[tT]-?\d{4,8}\s*", text):
        return "ticket_query"
    if "工单" in normalized and any(word in normalized for word in ("创建", "生成", "新建", "提交", "建个", "开个")):
        return "create_ticket"
    if "工单" in normalized and any(word in normalized for word in ("查", "查询", "进度", "状态", "处理")):
        return "ticket_query"
    for intent, keywords in INTENT_KEYWORDS:
        if any(keyword.lower() in normalized for keyword in keywords):
            return intent
    return "unclear"
