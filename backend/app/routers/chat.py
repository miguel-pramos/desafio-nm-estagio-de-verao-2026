import uuid
from typing import Any, List, Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query
from fastapi.responses import StreamingResponse
from openai import BaseModel

from app.config import AVAILABLE_TOOLS, TOOL_DEFINITIONS
from app.config.ai import OpenAIClientDep
from app.config.auth import UserDep
from app.config.db import SessionDep
from app.config.settings import SettingsDep
from app.repositories.ai import create_chat, load_chat
from app.schemas.ai import ClientMessage, ClientMessagePart
from app.utils.ai import (
    convert_to_openai_messages,
    patch_response_with_headers,
    stream_text,
    stream_text_with_persistence,
    build_context_message_from_documents,
)
from app.services.embedding import retrieve_docs

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    messages: Optional[List[ClientMessage]] = None
    message: Optional[ClientMessage] = None  # Single message when using persistence
    id: Optional[str] = None  # Chat ID


@router.post("")
async def handle_chat_data(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    settings: SettingsDep,
    session: SessionDep,
    user: UserDep,
    client: OpenAIClientDep,
    protocol=Query("data"),
):
    """Stream a message response from OpenAI, storing messages in database."""
    # Handle chat persistence
    chat_id = request.id
    previous_messages: List[dict[str, Any]] = []

    if chat_id:
        # Load previous messages
        try:
            previous_messages = load_chat(session, chat_id, user.id)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        # Convert to ClientMessage format for processing
        client_messages = []
        for msg in previous_messages:
            # Convert UIMessage format back to ClientMessage
            role = msg.get("role", "user")
            parts_data = msg.get("parts", [])
            content = ""

            # Convert parts to ClientMessagePart objects
            parts = []
            for part_data in parts_data:
                if part_data.get("type") == "text":
                    text = part_data.get("text", "")
                    content += text
                    parts.append(ClientMessagePart(type="text", text=text))

            client_messages.append(
                ClientMessage(
                    role=role, content=content, parts=parts if parts else None
                )
            )

        # Append new message if provided
        if request.message:
            client_messages.append(request.message)

        messages = client_messages
    else:
        # Use messages array directly
        if request.messages:
            messages = request.messages
        elif request.message:
            messages = [request.message]
        else:
            messages = []

    openai_messages = convert_to_openai_messages(messages)

    # Find the user query text (prefer request.message if present)
    user_query_text = ""
    if request.message and request.message.content:
        user_query_text = request.message.content
    elif messages:
        # assume the last user message is the query
        for m in reversed(messages):
            if m.role == "user":
                user_query_text = m.content or ""
                break
    # RAG
    docs = retrieve_docs(messages, 10)
    context_msg = build_context_message_from_documents(docs, 10_000)
    openai_messages = [context_msg] + openai_messages

    # Track messages for persistence if chat_id is provided
    ui_messages = []
    if chat_id:
        # Convert client messages to UIMessage format for storage
        # When loading from DB, messages already have IDs
        if previous_messages:
            ui_messages = previous_messages[:]

        # Add the new user message if provided
        if request.message:
            msg_dict: dict[str, Any] = {
                "id": f"msg-{uuid.uuid4().hex[:16]}",
                "role": request.message.role,
                "parts": [],
            }
            if request.message.parts:
                msg_dict["parts"] = [
                    part.model_dump() for part in request.message.parts
                ]  # type: ignore
            elif request.message.content:
                msg_dict["parts"] = [{"type": "text", "text": request.message.content}]  # type: ignore
            ui_messages.append(msg_dict)

    # Create streaming response with callback to save messages
    if chat_id:
        response = StreamingResponse(
            stream_text_with_persistence(
                client,
                openai_messages,
                TOOL_DEFINITIONS,
                AVAILABLE_TOOLS,
                settings.OPENAI_MODEL,
                protocol,
                ui_messages,
                chat_id,
                user.id,
                background_tasks,
            ),
            media_type="text/event-stream",
        )
    else:
        # No persistence, just stream
        response = StreamingResponse(
            stream_text(
                client,
                openai_messages,
                TOOL_DEFINITIONS,
                AVAILABLE_TOOLS,
                settings.OPENAI_MODEL,
                protocol,
            ),
            media_type="text/event-stream",
        )

    return patch_response_with_headers(response, protocol)


class CreateNewChatResponse(BaseModel):
    id: str


@router.post("/create", response_model=CreateNewChatResponse)
async def create_new_chat(
    session: SessionDep,
    user: UserDep,
):
    """Create a new chat and return its ID."""
    print(f"---- Creating new chat for user {user.id}")
    chat_id = create_chat(session, user.id)
    return CreateNewChatResponse(id=chat_id)


class GetChatMessagesResponse(BaseModel):
    id: str
    messages: List[dict[str, Any]]


@router.get("/{chat_id}", response_model=GetChatMessagesResponse)
async def get_chat_messages(
    session: SessionDep,
    user: UserDep,
    chat_id: str,
):
    """Load chat messages by chat ID."""
    try:
        messages = load_chat(session, chat_id, user.id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return GetChatMessagesResponse(id=chat_id, messages=messages)
