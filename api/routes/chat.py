"""Chat session endpoints."""

import json

from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.models import ChatMessage, ChatSession
from core.schemas import (
    ChatHistoryResponse,
    ChatMessageResponse,
    ChatSessionResponse,
    CreateSessionRequest,
    SendMessageRequest,
    SourceInfo,
)
from services.rag_service import RAGService

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
)


@router.post("/sessions", response_model=ChatSessionResponse)
async def create_session(
    request: CreateSessionRequest,
    db: AsyncSession = Depends(get_db),
):
    """Create a new chat session."""
    session = ChatSession(title=request.title)
    if request.document_ids:
        session.document_ids = request.document_ids

    db.add(session)
    await db.commit()
    await db.refresh(session)

    return ChatSessionResponse(
        id=session.id,
        title=session.title,
        document_ids=session.document_ids,
        created_at=session.created_at,
    )


@router.get("/sessions", response_model=list[ChatSessionResponse])
async def list_sessions(
    db: AsyncSession = Depends(get_db),
):
    """List all chat sessions."""
    result = await db.execute(
        select(ChatSession).order_by(ChatSession.created_at.desc())
    )
    sessions = result.scalars().all()

    return [
        ChatSessionResponse(
            id=s.id,
            title=s.title,
            document_ids=s.document_ids,
            created_at=s.created_at,
        )
        for s in sessions
    ]


@router.get("/sessions/{session_id}", response_model=ChatHistoryResponse)
async def get_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a chat session with its message history."""
    result = await db.execute(
        select(ChatSession).where(ChatSession.id == session_id)
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    msg_result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at)
    )
    messages = msg_result.scalars().all()

    return ChatHistoryResponse(
        session=ChatSessionResponse(
            id=session.id,
            title=session.title,
            document_ids=session.document_ids,
            created_at=session.created_at,
        ),
        messages=[
            ChatMessageResponse(
                id=m.id,
                session_id=m.session_id,
                role=m.role,
                content=m.content,
                sources=[
                    SourceInfo(**s) for s in m.sources
                ],
                created_at=m.created_at,
            )
            for m in messages
        ],
    )


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete a chat session."""
    result = await db.execute(
        select(ChatSession).where(ChatSession.id == session_id)
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    await db.delete(session)
    await db.commit()

    return {"status": "deleted", "session_id": session_id}


@router.post("/sessions/{session_id}/messages", response_model=ChatMessageResponse)
async def send_message(
    session_id: int,
    request: SendMessageRequest,
    db: AsyncSession = Depends(get_db),
    x_openai_api_key: str | None = Header(None, alias="X-OpenAI-API-Key"),
):
    """Send a message and get a response."""
    result = await db.execute(
        select(ChatSession).where(ChatSession.id == session_id)
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    user_message = ChatMessage(
        session_id=session_id,
        role="user",
        content=request.content,
    )
    db.add(user_message)
    await db.commit()

    rag = RAGService(db)
    response = await rag.answer(
        query=request.content,
        top_k=5,
        document_ids=session.document_ids if session.document_ids else None,
        llm_provider=request.llm_provider,
        llm_model=request.llm_model,
        api_key=x_openai_api_key,
    )

    sources_data = [
        {
            "chunk_id": s.chunk_id,
            "document_id": s.document_id,
            "filename": s.filename,
            "content": s.content,
            "score": s.score,
            "page_number": s.page_number,
        }
        for s in response.sources
    ]

    assistant_message = ChatMessage(
        session_id=session_id,
        role="assistant",
        content=response.answer,
    )
    assistant_message.sources = sources_data
    db.add(assistant_message)
    await db.commit()
    await db.refresh(assistant_message)

    return ChatMessageResponse(
        id=assistant_message.id,
        session_id=assistant_message.session_id,
        role=assistant_message.role,
        content=assistant_message.content,
        sources=[SourceInfo(**s) for s in sources_data],
        created_at=assistant_message.created_at,
    )


@router.post("/sessions/{session_id}/messages/stream")
async def send_message_stream(
    session_id: int,
    request: SendMessageRequest,
    db: AsyncSession = Depends(get_db),
    x_openai_api_key: str | None = Header(None, alias="X-OpenAI-API-Key"),
):
    """Send a message and stream the response."""
    result = await db.execute(
        select(ChatSession).where(ChatSession.id == session_id)
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    user_message = ChatMessage(
        session_id=session_id,
        role="user",
        content=request.content,
    )
    db.add(user_message)
    await db.commit()

    rag = RAGService(db)
    stream, sources = await rag.answer_stream(
        query=request.content,
        top_k=5,
        document_ids=session.document_ids if session.document_ids else None,
        llm_provider=request.llm_provider,
        llm_model=request.llm_model,
        api_key=x_openai_api_key,
    )

    sources_data = [
        {
            "chunk_id": s.chunk_id,
            "document_id": s.document_id,
            "filename": s.filename,
            "content": s.content,
            "score": s.score,
            "page_number": s.page_number,
        }
        for s in sources
    ]

    async def generate():
        full_response = []
        yield f"event: sources\ndata: {json.dumps(sources_data)}\n\n"

        async for chunk in stream:
            full_response.append(chunk)
            yield f"event: token\ndata: {json.dumps(chunk)}\n\n"

        content = "".join(full_response)
        assistant_message = ChatMessage(
            session_id=session_id,
            role="assistant",
            content=content,
        )
        assistant_message.sources = sources_data
        db.add(assistant_message)
        await db.commit()

        yield f"event: done\ndata: {json.dumps({'message_id': assistant_message.id})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
