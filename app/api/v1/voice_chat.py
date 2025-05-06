
import os
import shutil
import tempfile
import whisper
from fastapi import HTTPException, Depends, APIRouter, UploadFile, File, Form
from app.chat_graph import graph
from app.schemas.chat_schema import ChatResponse
from app.schemas.chat_schema import VoiceChatInput
from app.auth.auth import get_current_user
from app.core.database import get_db
from sqlalchemy.orm import Session
import logging 

WHISPER_MODEL_NAME = "base"
try:
    print(f"Loading Whisper model: {WHISPER_MODEL_NAME}...")
    whisper_model = whisper.load_model(WHISPER_MODEL_NAME)
    print("Whisper model loaded successfully.")
except Exception as e:
    print(f"Error loading Whisper model: {e}. Transcription will fail.")
    whisper_model = None

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/chat/voice", response_model=ChatResponse)
async def voice_chat_endpoint(
    chat_input: VoiceChatInput= Depends(),
    audio_file: UploadFile = File(..., description="The user's voice input audio file."),
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not whisper_model:
        raise HTTPException(status_code=503, detail="Whisper model is not available.")
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_audio_file:
            shutil.copyfileobj(audio_file.file, tmp_audio_file)
            tmp_path = tmp_audio_file.name 

        logger.info(f"Audio saved temporarily to: {tmp_path}")
        try:
            transcription_result = whisper_model.transcribe(tmp_path, fp16=False)
            user_input_text = transcription_result["text"]
            logger.info(f"Transcription successful. Text: {user_input_text}")
        except Exception as transcribe_error:
            logger.error(f"Whisper transcription failed: {transcribe_error}")
            raise HTTPException(status_code=500, detail=f"Audio transcription failed: {transcribe_error}")

    except Exception as file_error:
        logger.error(f"Error handling uploaded file: {file_error}")
        raise HTTPException(status_code=500, detail=f"Failed to process uploaded audio file: {file_error}")
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
                logger.info(f"Temporary file deleted: {tmp_path}")
            except OSError as cleanup_error:
                logger.error(f"Error deleting temporary file {tmp_path}: {cleanup_error}")
        await audio_file.close()
    config = {"configurable": {"thread_id": chat_input.thread_id}} 
    state = {
        "messages": [user_input_text],
        "age_group": chat_input.age_group
    }
    agent_message_content = None 

    try:
        for event in graph.stream(state, config):
            for key, value in event.items():
                if "messages" in value:
                    last_message = value["messages"][-1]
                    if hasattr(last_message, 'content'):
                        agent_message_content = last_message.content
                    else:
                        agent_message_content = str(last_message) 

        if agent_message_content is None:
             logger.warning("Graph stream finished but no agent message content extracted.")
             final_state = graph.invoke(state, config)
             last_message = final_state["messages"][-1]
             if hasattr(last_message, 'content'):
                 agent_message_content = last_message.content
             else:
                 agent_message_content = str(last_message)

        return ChatResponse(agent=agent_message_content)

    except Exception as e:
        logger.error(f"Langchain graph processing failed: {e}", exc_info=True) # Log stack trace
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")