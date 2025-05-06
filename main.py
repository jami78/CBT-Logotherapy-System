from app.api.v1.chat import router as chat_router
from app.api.v1.auth import router as auth_router
from app.api.v1.article_endpoint import router as article_post_router
from app.api.v1.article_endpoint import router as article_get_router
from app.api.v1.voice_chat import router as voice_chat_router
from fastapi import FastAPI
import uvicorn

app = FastAPI()
app.include_router(chat_router, prefix="", tags=["Chat Endpoint"])
app.include_router(voice_chat_router, prefix="", tags=["Voice Chat Endpoint"])
app.include_router(auth_router, prefix="", tags=["Authentication"])
app.include_router(article_post_router, prefix="", tags=["Article Post Router"])
app.include_router(article_get_router, prefix="", tags=["Article Get Router"])

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)