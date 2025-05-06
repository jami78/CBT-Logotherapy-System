from pydantic import BaseModel

class ArticleRequest(BaseModel):
    title: str
    prompt: str  
    author: str  

class ArticleResponse(BaseModel):
    id: int
    title: str
    content: str
    author: str