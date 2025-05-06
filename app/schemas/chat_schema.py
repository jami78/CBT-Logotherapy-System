from pydantic import BaseModel
from enum import Enum

class AgeGroup(str, Enum):
    adolescents = "Adolescents (10-18)"
    young_adults = "Young Adults (19-30)"
    adults = "Adults (31+)"

class ChatInput(BaseModel):
    user_input: str
    thread_id: str
    age_group: AgeGroup

class VoiceChatInput(BaseModel):
    thread_id: str
    age_group: AgeGroup


class ChatResponse(BaseModel):
    agent: str