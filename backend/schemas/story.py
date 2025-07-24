from typing import List, Optional, Dict
from datetime import datetime
from pydantic import BaseModel

class StoryOptionsSchema(BaseModel):
    text = None
    none_id = None 

class StoryNodeBase(BaseModel):
    content = None
    is_ending = False 
    is_winning_ending = False 

# data from backend to frontend
class CompleteStoryNodeResponse(StoryNodeBase):
    id = None 
    options = None 

    class Config: 
        from_attributes = True  

class StoryBase(BaseModel): 
    title = None 
    session_id = None 
    class Config: 
        from_attributes = True 

class CreateStoryRequest(BaseModel): 
    theme = None 

class CompleteStoryResponse(BaseModel): 
    id = None 
    created_at = datetime
    root_node = CompleteStoryNodeResponse
    all_nodes = Dict[int, CompleteStoryNodeResponse]

    class Config:
        from_attributes = True