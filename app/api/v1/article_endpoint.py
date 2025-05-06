from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from app.services.article import generate_article
from app.models.articles import Article
from app.schemas.article_schema import ArticleRequest, ArticleResponse
from app.core.database import get_db
from app.auth.auth import get_current_user  
from app.models.users import Users
from app.services.article import generate_docx
from fastapi.responses import FileResponse

router = APIRouter()

@router.post("/create_article/", response_model=ArticleResponse)
async def create_article(
    article_input: ArticleRequest,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user) 
):

    if current_user.role != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to create an article."
        )

    try:
        article_content = generate_article(article_input.prompt)
        file_path = generate_docx(
            title=article_input.title, 
            content=article_content, 
            author=article_input.author  
        )
        
        new_article = Article(
            title=article_input.title,
            content=article_content,
            author=article_input.author,
            file_path=file_path
        )
        db.add(new_article)
        db.commit()
        db.refresh(new_article)

        return ArticleResponse(
            id=new_article.id,
            title=new_article.title,
            content=new_article.content,
            author=new_article.author,
            file_path=new_article.file_path
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/articles/", response_model=list[ArticleResponse])
async def get_articles(db: Session = Depends(get_db)):
    try:
        articles = db.query(Article).all()
        if not articles:
            raise HTTPException(status_code=404, detail="No articles found.")
        
        file_path = articles[0].file_path

        return FileResponse(file_path, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", filename=f"article_{articles[0].title}.docx")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))