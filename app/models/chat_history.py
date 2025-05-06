from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    thread_id = Column(String, index=True, nullable=False)
    username = Column(String, ForeignKey("users.username"), nullable=False)
    user_input = Column(String, nullable=False)
    agent_response = Column(String, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    users = relationship("Users", back_populates="chat_history", foreign_keys=[username])