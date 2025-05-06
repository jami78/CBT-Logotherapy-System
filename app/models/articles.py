from sqlalchemy import Column, Integer, String, Text, DateTime, func
from app.core.database import Base

class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    content = Column(Text, nullable=False)
    author = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    file_path = Column(String)