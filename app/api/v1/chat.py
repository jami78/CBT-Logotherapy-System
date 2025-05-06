from fastapi import HTTPException, Depends, APIRouter
from app.chat_graph import graph
from app.schemas.chat_schema import ChatInput, ChatResponse
from app.auth.auth import get_current_user
from app.core.database import get_db
from sqlalchemy.orm import Session
from langchain.schema import HumanMessage

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(chat_input: ChatInput= Depends(),
                  current_user: str = Depends(get_current_user),
                  db: Session = Depends(get_db)
):
    config = {"configurable": {"thread_id": chat_input.thread_id}}
    state = {
        "messages": [chat_input.user_input],
        "age_group": chat_input.age_group
    }
    agent_message = None
    try:
        for event in graph.stream(state, config):
            for val in event.values():
                state = val
                agent_message = state["messages"][-1]
            agent_message = str(agent_message)
        
        return ChatResponse(agent=agent_message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
