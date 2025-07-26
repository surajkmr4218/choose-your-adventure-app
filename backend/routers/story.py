import uuid 
from typing import Optional
from datetime import datetime 
from fastapi import APIRouter, Depends, HTTPException, Cookie, Response, BackgroundTasks

from sqlalchemy.orm import Session
from backend.db.database import get_db, SessionLocal 
from backend.models.story import Story, StoryNode
from backend.models.job import StoryJob
from backend.schemas.story import (
    CompleteStoryResponse, CompleteStoryNodeResponse, CreateStoryRequest
)
from backend.schemas.job import StoryJobResponse

router = APIRouter(
    prefix="/stories",
    tags=["stories"]
)

def get_session_id(session_id): 
    if not session_id: 
        session_id = str(uuid.uuid4())
    return session_id

@router.post(path="/create", response_model=StoryJobResponse)
def create_story(
    request,
    background_tasks,
    response,
    session_id = Depends(get_session_id),
    db = Depends(get_db)
):
    response.set_cookies(key="session_id", value=session_id, httponly=True)

    job_id = str(uuid.uuid4())
    job = StoryJob(
        job_id=job_id,
        session_id=session_id,
        theme=request.theme,
        status="pending"
    )
    db.add(job)
    db.commit()

    # TODO: add background tasks, generate story

    return job

# necessary to have a separate session so it is not hanging
def generate_story_task(job_id, theme, session_id):
    db = SessionLocal()
