from app.agent import build_customer_service_graph


def main() -> None:
    graph = build_customer_service_graph()
    conversation: list[dict[str, str]] = []
    print("CloudDesk 智能客服 Agent，输入 exit 结束。")

    while True:
        user_input = input("\n用户：").strip()
        if user_input.lower() in {"exit", "quit"}:
            break
        state = graph.invoke({"user_input": user_input, "conversation": conversation})
        conversation = state.get("conversation", conversation)
        print(f"Agent：{state.get('response')}")


if __name__ == "__main__":
    main()

