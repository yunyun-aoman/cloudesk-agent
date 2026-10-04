# CloudDesk Intelligent Customer Service Agent

基于 LangGraph + RAG + Tools + Skills 的 SaaS 智能客服 Agent 示例项目。

> 项目放在 F 盘，避免占用 C 盘。当前路径：
> `F:\codex\.codex\visualizations\2026\10\04\01a10618-e8ee-79f3-b9a5-a822e76c8237\cloudesk-agent`

## 能力范围

- 意图识别：产品咨询、价格咨询、账号问题、API 问题、退款、工单查询、创建工单、转人工、报告生成。
- RAG：从 `knowledge_base/` 中检索 CloudDesk 产品文档并回答。
- Tools：模拟查询用户、订阅、工单，创建工单。
- Skills：自研报告生成能力，包括会话总结、工单报告、客服运营分析。
- LangGraph：用状态图编排意图识别、路由、工具调用、RAG、Skills 和回复生成。

## 快速开始

```powershell
cd F:\codex\.codex\visualizations\2026\10\04\01a10618-e8ee-79f3-b9a5-a822e76c8237\cloudesk-agent
python -m venv .venv
.\.venv\Scripts\Activate.ps1
$env:PIP_CACHE_DIR="$PWD\.pip-cache"
pip install -r requirements.txt
```

如果暂时因为网络无法安装依赖，也可以直接运行 CLI 核心 Demo。项目内置了轻量本地执行器；安装 `langgraph` 后会自动切换为正式 `StateGraph` 工作流。

运行命令行 Demo：

```powershell
python -m app.cli
```

运行 API：

```powershell
uvicorn app.api:app --reload --port 8000
```

打开前端界面：

```text
http://127.0.0.1:8000
```

运行 Streamlit 页面：

```powershell
streamlit run ui/streamlit_app.py
```

## 示例问题

```text
专业版和基础版有什么区别？
我登录不上去了，用户 u1001
帮我查一下工单 T-1001
我想退款，用户 u1002
根据最近客服记录生成运营分析报告
把这段对话生成工单报告
```

## 目录结构

```text
app/
  agent/
    graph.py
    intents.py
    state.py
  rag/
    retriever.py
  skills/
    report_skill.py
  tools/
    customer_tools.py
  api.py
  cli.py
  config.py
data/
  mock/
knowledge_base/
ui/
```
