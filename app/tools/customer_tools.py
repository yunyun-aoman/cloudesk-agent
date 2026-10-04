import json
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from app.config import MOCK_DATA_DIR


def _read_json(name: str) -> Any:
    path = MOCK_DATA_DIR / name
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(name: str, data: Any) -> None:
    path = MOCK_DATA_DIR / name
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def get_user_status(user_id: str) -> dict[str, Any]:
    users = _read_json("users.json")
    user = users.get(user_id)
    if not user:
        return {"found": False, "message": f"未找到用户 {user_id}"}
    return {"found": True, "user": user}


def get_subscription_info(user_id: str) -> dict[str, Any]:
    subscriptions = _read_json("subscriptions.json")
    subscription = subscriptions.get(user_id)
    if not subscription:
        return {"found": False, "message": f"未找到用户 {user_id} 的订阅信息"}
    return {"found": True, "subscription": subscription}


def get_ticket_status(ticket_id: str) -> dict[str, Any]:
    tickets = _read_json("tickets.json")
    ticket = tickets.get(ticket_id)
    if not ticket:
        return {"found": False, "message": f"未找到工单 {ticket_id}"}
    return {"found": True, "ticket": ticket}


def create_ticket(user_id: str | None, title: str, description: str, priority: str = "medium") -> dict[str, Any]:
    tickets_path = Path(MOCK_DATA_DIR / "tickets.json")
    tickets = json.loads(tickets_path.read_text(encoding="utf-8"))
    ticket_id = f"T-{str(uuid4())[:8].upper()}"
    ticket = {
        "ticket_id": ticket_id,
        "user_id": user_id or "unknown",
        "title": title,
        "description": description,
        "priority": priority,
        "status": "open",
        "owner": "support-l2",
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }
    tickets[ticket_id] = ticket
    _write_json("tickets.json", tickets)
    return {"created": True, "ticket": ticket}

