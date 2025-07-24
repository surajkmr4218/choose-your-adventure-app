from typing import Optional 
from datetime import datetime 
from pydantic import BaseModel

class StoryJobBase(BaseModel):
    theme = None 

class StoryJobResponse(BaseModel): 
    job_id = None 
    status = None 
    created_at = datetime 
    story_id = None 
    completed_at = None 
    error = None 

    class Config: 
        from_attributes = True

class StoryJobCreate(StoryJobBase): 
    pass