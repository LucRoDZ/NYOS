from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas import ChatRequest, ChatResponse
from app.services.gemini_service import (
    chat_with_gemini,
    generate_summary_stream,
    generate_report,
)
from app import models

router = APIRouter(prefix="/chat", tags=["chat"])


@router.get("/conversations")
async def get_conversations(db: Session = Depends(get_db)):
    convs = (
        db.query(models.Conversation)
        .order_by(models.Conversation.created_at.desc())
        .all()
    )
    return [{"id": c.id, "title": c.title, "created_at": c.created_at} for c in convs]


@router.post("/conversations")
async def create_conversation(db: Session = Depends(get_db)):
    conv = models.Conversation(title="Nouvelle conversation")
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return {"id": conv.id, "title": conv.title, "created_at": conv.created_at}


@router.delete("/conversations/{conv_id}")
async def delete_conversation(conv_id: int, db: Session = Depends(get_db)):
    conv = (
        db.query(models.Conversation).filter(models.Conversation.id == conv_id).first()
    )
    if conv:
        db.delete(conv)
        db.commit()
    return {"status": "deleted"}


@router.post("/{conv_id}", response_model=ChatResponse)
async def chat(conv_id: int, request: ChatRequest, db: Session = Depends(get_db)):
    conv = (
        db.query(models.Conversation).filter(models.Conversation.id == conv_id).first()
    )
    if not conv:
        conv = models.Conversation(title=request.message[:50])
        db.add(conv)
        db.commit()
        db.refresh(conv)
        conv_id = conv.id

    if conv.title == "Nouvelle conversation":
        conv.title = request.message[:50] + ("..." if len(request.message) > 50 else "")
        db.commit()

    db.add(
        models.ChatMessage(
            conversation_id=conv_id, role="user", content=request.message
        )
    )
    db.commit()

    response = await chat_with_gemini(request.message, db)

    db.add(
        models.ChatMessage(conversation_id=conv_id, role="assistant", content=response)
    )
    db.commit()

    return ChatResponse(response=response)


@router.get("/summary/stream")
async def get_summary_stream(db: Session = Depends(get_db)):
    return StreamingResponse(
        generate_summary_stream(db),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )


@router.get("/report")
async def get_report(db: Session = Depends(get_db)):
    report = await generate_report(db)
    return {"report": report}


@router.get("/{conv_id}/history")
async def get_history(conv_id: int, db: Session = Depends(get_db)):
    messages = (
        db.query(models.ChatMessage)
        .filter(models.ChatMessage.conversation_id == conv_id)
        .order_by(models.ChatMessage.created_at)
        .all()
    )
    return [
        {"role": m.role, "content": m.content, "created_at": m.created_at}
        for m in messages
    ]
