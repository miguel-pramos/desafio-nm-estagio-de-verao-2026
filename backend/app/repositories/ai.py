"""Utilities for chat persistence."""

from typing import Any, List

from sqlmodel import col, delete, select

from ..config.db import SessionDep
from ..models import Chat, Message


def create_chat(session: SessionDep, user_id: int):
    """Create a new chat and return its ID."""
    chat = Chat(user_id=user_id)
    session.add(chat)
    session.commit()
    session.refresh(chat)
    return chat.id


def load_chat(
    session: SessionDep,
    chat_id: str,
    user_id: int,
) -> List[dict[str, Any]]:
    """
    Load chat messages from database.
    Returns a list of UIMessage-compatible dictionaries.
    """
    # Verify chat belongs to user
    chat = session.get(Chat, chat_id)
    if not chat or chat.user_id != user_id:
        raise ValueError(f"Chat {chat_id} not found or access denied")

    # Load messages ordered by creation time
    statement = (
        select(Message)
        .where(Message.chat_id == chat_id)
        .order_by(col(Message.created_at).asc())
    )
    result = session.exec(statement)
    db_messages = list(result.all())

    # Convert to UIMessage format
    ui_messages = []
    for msg in db_messages:
        ui_messages.append(msg.data)

    return ui_messages


def save_chat(
    session: SessionDep,
    chat_id: str,
    user_id: int,
    messages: List[dict[str, Any]],
):
    """
    Save chat messages to database.
    messages should be in UIMessage format (list of dictionaries).
    """
    # Verify chat belongs to user
    chat = session.get(Chat, chat_id)
    if not chat or chat.user_id != user_id:
        raise ValueError(f"Chat {chat_id} not found or access denied")

    # Delete existing messages for this chat
    delete_messages = delete(Message).where(col(Message.chat_id) == chat_id)
    session.exec(delete_messages)

    # Save new messages
    for msg_data in messages:
        # Extract role and content for legacy fields
        role = msg_data.get("role", "user")
        content = ""
        if "parts" in msg_data:
            text_parts = [
                part.get("text", "")
                for part in msg_data["parts"]
                if part.get("type") == "text"
            ]
            content = "".join(text_parts)
        elif "content" in msg_data:
            content = msg_data["content"]

        message = Message(
            chat_id=chat_id,
            user_id=user_id,
            data=msg_data,
            role=role,
            content=content,
        )
        session.add(message)

    session.commit()


def list_chats(
    session: SessionDep,
    user_id: int,
    limit: int | None = None,
) -> List[dict[str, Any]]:
    """Return chat summaries for a user ordered by recent activity."""

    statement = (
        select(Chat)
        .where(Chat.user_id == user_id)
        .order_by(col(Chat.created_at).desc())
    )

    if limit:
        statement = statement.limit(limit)

    chats = session.exec(statement).all()

    summaries: List[dict[str, Any]] = []
    for chat in chats:
        last_message_statement = (
            select(Message)
            .where(Message.chat_id == chat.id)
            .order_by(col(Message.created_at).desc())
            .limit(1)
        )
        last_message = session.exec(last_message_statement).first()

        preview = ""
        last_role = None
        updated_at = chat.created_at

        if last_message is not None:
            preview = last_message.content or ""
            last_role = last_message.role
            updated_at = last_message.created_at

        summaries.append(
            {
                "id": chat.id,
                "preview": preview,
                "last_role": last_role,
                "updated_at": updated_at,
            }
        )

    summaries.sort(key=lambda item: item["updated_at"], reverse=True)

    return summaries


def delete_chat(
    session: SessionDep,
    chat_id: str,
    user_id: int,
):
    """
    Delete a chat and all its messages.
    Raises ValueError if chat not found or access denied.
    """
    # Verify chat belongs to user
    chat = session.get(Chat, chat_id)
    if not chat or chat.user_id != user_id:
        raise ValueError(f"Chat {chat_id} not found or access denied")

    # Delete messages first (due to foreign key constraint)
    delete_messages = delete(Message).where(col(Message.chat_id) == chat_id)
    session.exec(delete_messages)

    # Delete the chat
    session.delete(chat)
    session.commit()
