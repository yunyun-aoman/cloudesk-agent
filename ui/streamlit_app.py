import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.agent import build_customer_service_graph  # noqa: E402


st.set_page_config(page_title="CloudDesk Agent", page_icon="CD", layout="wide")
st.title("CloudDesk 智能客服 Agent")

if "graph" not in st.session_state:
    st.session_state.graph = build_customer_service_graph()
if "conversation" not in st.session_state:
    st.session_state.conversation = []

with st.sidebar:
    st.subheader("示例问题")
    examples = [
        "专业版和基础版有什么区别？",
        "我登录不上去了，用户 u1001",
        "帮我查一下工单 T-1001",
        "我想退款，用户 u1002",
        "根据最近客服记录生成运营分析报告",
    ]
    selected = st.radio("选择一个示例", examples, label_visibility="collapsed")

message = st.chat_input("请输入你的问题")
if st.button("发送示例"):
    message = selected

for item in st.session_state.conversation:
    with st.chat_message(item["role"]):
        st.write(item["content"])

if message:
    with st.chat_message("user"):
        st.write(message)
    state = st.session_state.graph.invoke(
        {
            "user_input": message,
            "conversation": st.session_state.conversation,
        }
    )
    st.session_state.conversation = state.get("conversation", st.session_state.conversation)
    with st.chat_message("assistant"):
        st.write(state.get("response", ""))
        with st.expander("Agent 状态"):
            st.json(state)
