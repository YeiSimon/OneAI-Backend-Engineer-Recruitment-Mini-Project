from fastapi import FastAPI, Depends, HTTPException, Query, Response, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware

from . import crud, models, schemas
from .database import get_db

app = FastAPI(title="NBA 新聞網站 API", description="NBA 新聞網站的 API 端點")

origins = [
    "http://localhost:4200",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "NBA 新聞網站 API 運行中"}

@app.get("/news/", response_model=schemas.NewsListResponse)
async def read_news(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """獲取新聞列表"""
    news = crud.get_recent_news(db, limit=limit)
    total = db.query(models.News).count()
    
      # 設置圖片 URL
    for item in news:
        if hasattr(item, 'image') and item.image:
            item.image_url = f"/news/{item.id}/image"

    return {
        "items": news,
        "total": total,
        "page": skip // limit + 1,
        "size": limit,
        "pages": (total + limit - 1) // limit
    }

@app.get("/news/hot/", response_model=List[schemas.News])
async def read_hot_news(
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """獲取熱門新聞"""
    return crud.get_hot_news(db, limit=limit)

@app.get("/news/featured/", response_model=List[schemas.News])
async def read_featured_news(
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """獲取精選新聞"""
    return crud.get_featured_news(db, limit=limit)

@app.get("/news/{slug}", response_model=schemas.NewsDetail)
async def read_news_by_slug(slug: str, db: Session = Depends(get_db)):
    """獲取特定新聞詳情"""
    news = crud.get_news_by_slug(db, slug=slug)
    if not news:
        raise HTTPException(status_code=404, detail="新聞不存在")
    
    # 記錄瀏覽量
    crud.record_news_view(db, news.id)
    
    return news

@app.get("/categories/{category_slug}/news/", response_model=List[schemas.News])
async def read_news_by_category(
    category_slug: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """獲取特定分類的新聞"""
    return crud.get_news_by_category(db, category_slug=category_slug, skip=skip, limit=limit)

@app.get("/tags/{tag_slug}/news/", response_model=List[schemas.News])
async def read_news_by_tag(
    tag_slug: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """獲取特定標籤的新聞"""
    return crud.get_news_by_tag(db, tag_slug=tag_slug, skip=skip, limit=limit)

@app.get("/search/", response_model=schemas.NewsSearchResult)
async def search_news(
    q: str = Query(..., min_length=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """搜索新聞"""
    news = crud.search_news(db, query=q, skip=skip, limit=limit)
    
    # 計算總數
    search = f"%{q}%"
    total = db.query(models.News).filter(
        (models.News.title.ilike(search)) | 
        (models.News.content.ilike(search)) |
        (models.News.summary.ilike(search))
    ).count()
    
    return {
        "total": total,
        "items": news
    }

# API 端點: 添加新聞
@app.post("/news/", response_model=schemas.News)
async def create_news(
    news: schemas.NewsCreate,
    db: Session = Depends(get_db)
):
    """添加新聞"""
    published_at = news.published_at or datetime.now()
    
    return crud.add_news(
        db=db,
        title=news.title,
        content=news.content,
        summary=news.summary,
        published_at=published_at,
        category_name=news.category_name,
        tags=news.tags
    )

@app.post("/news/{news_id}/image", response_model=schemas.News)
async def upload_news_image(
    news_id: int, 
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """為指定新聞上傳圖片"""
    # 檢查新聞是否存在
    news = db.query(models.News).filter(models.News.id == news_id).first()
    if not news:
        raise HTTPException(status_code=404, detail="找不到新聞")
    
    # 讀取圖片數據
    image_data = await image.read()
    mime_type = image.content_type or "image/jpeg"
    
    # 檢查是否已有圖片
    existing_image = db.query(models.NewsImage).filter(models.NewsImage.news_id == news_id).first()
    
    if existing_image:
        # 更新現有圖片
        existing_image.image_data = image_data
        existing_image.mime_type = mime_type
    else:
        # 創建新圖片
        news_image = models.NewsImage(
            news_id=news_id,
            image_data=image_data,
            mime_type=mime_type,
            created_at = datetime.now()
        )
        db.add(news_image)
    
    db.commit()
    
    # 返回更新後的新聞
    news = db.query(models.News).filter(models.News.id == news_id).first()
    news.image_url = f"/news/{news_id}/image"
    return news

@app.get("/news/{news_id}/image")
async def get_news_image(news_id: int, db: Session = Depends(get_db)):
    """獲取新聞圖片"""
    news_image = db.query(models.NewsImage).filter(models.NewsImage.news_id == news_id).first()
    if not news_image:
        raise HTTPException(status_code=404, detail="圖片不存在")
    
    return Response(
        content=news_image.image_data, 
        media_type=news_image.mime_type
    )

@app.post("/news/{news_id}/entity/", response_model=schemas.News)
async def add_entity(
    news_id: int,
    entity: schemas.EntityCreate,
    role: str = Query(..., description="實體在新聞中的角色"),
    db: Session = Depends(get_db)
):
    """向新聞添加實體關聯"""
    # 檢查新聞是否存在
    news = db.query(models.News).filter(models.News.id == news_id).first()
    if not news:
        raise HTTPException(status_code=404, detail="新聞不存在")
    
    crud.add_entity_to_news(
        db=db,
        news_id=news_id,
        entity_name=entity.name,
        entity_type=entity.entity_type,
        role=role,
        metadata=entity.metadata
    )
    
    return news

@app.get("/entities/{entity_type}/", response_model=List[schemas.Entity])
async def read_entities_by_type(
    entity_type: str,
    db: Session = Depends(get_db)
):
    """獲取特定類型的實體列表"""
    entities = db.query(models.Entity).filter(models.Entity.entity_type == entity_type).all()
    return entities

@app.get("/entities/{entity_type}/{name}/news/", response_model=List[schemas.News])
async def read_news_by_entity(
    entity_type: str,
    name: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """獲取與特定實體相關的新聞"""
    return crud.get_news_by_entity(
        db=db,
        entity_name=name,
        entity_type=entity_type,
        skip=skip,
        limit=limit
    )