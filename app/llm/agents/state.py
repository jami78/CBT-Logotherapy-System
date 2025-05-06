from typing import TypedDict, Annotated
from operator import add


class AgentState(TypedDict):
    messages: Annotated[list, add]
    transition: bool
    age_group: str
    
