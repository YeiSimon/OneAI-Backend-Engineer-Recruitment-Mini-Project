from sqlalchemy.orm import Session
from datetime import datetime
from slugify import slugify
from . import models
from typing import List, Optional, Dict, Any


def add_news(db: Session, title: str, content: str, summary: str, 
             published_at: datetime, category_name: str, tags: List[str] = None):
    """向資料庫添加新聞"""
    # 處理分類
    category = db.query(models.Category).filter(models.Category.name == category_name).first()
    if not category:
        category = models.Category(name=category_name, slug=slugify(category_name))
        db.add(category)
        db.flush()
    
    # 創建新聞
    news = models.News(
        title=title,
        slug=slugify(title),
        content=content,
        summary=summary,
        published_at=published_at,
        category_id=category.id
    )
    db.add(news)
    db.flush()
    
    # 添加標籤
    if tags:
        for tag_name in tags:
            tag = db.query(models.Tag).filter(models.Tag.name == tag_name).first()
            if not tag:
                tag = models.Tag(name=tag_name, slug=slugify(tag_name))
                db.add(tag)
                db.flush()
            
            news_tag = models.NewsTag(news_id=news.id, tag_id=tag.id)
            db.add(news_tag)
    
    # 初始化新聞指標
    metrics = models.NewsMetrics(news_id=news.id, view_count=0)
    db.add(metrics)
    
    db.commit()
    return news


def get_hot_news(db: Session, limit: int = 5):
    """獲取熱門新聞"""
    return db.query(models.News) \
        .join(models.NewsMetrics, models.News.id == models.NewsMetrics.news_id) \
        .order_by(models.NewsMetrics.view_count.desc()) \
        .limit(limit) \
        .all()


def record_news_view(db: Session, news_id: int):
    """記錄新聞瀏覽"""
    metrics = db.query(models.NewsMetrics).filter(models.NewsMetrics.news_id == news_id).first()
    if metrics:
        metrics.view_count += 1
        metrics.last_updated = datetime.now()
    else:
        metrics = models.NewsMetrics(news_id=news_id, view_count=1)
        db.add(metrics)
    db.commit()


def add_entity_to_news(db: Session, news_id: int, entity_name: str, entity_type: str, role: str, metadata: Dict = None):
    """添加實體關聯"""
    entity = db.query(models.Entity).filter(
        models.Entity.name == entity_name,
        models.Entity.entity_type == entity_type
    ).first()
    
    if not entity:
        entity = models.Entity(name=entity_name, entity_type=entity_type, metadata=metadata)
        db.add(entity)
        db.flush()
    
    news_entity = models.NewsEntity(news_id=news_id, entity_id=entity.id, role=role)
    db.add(news_entity)
    db.commit()


def get_news_by_category(db: Session, category_slug: str, skip: int = 0, limit: int = 10):
    """獲取特定分類的新聞"""
    return db.query(models.News) \
        .join(models.Category, models.News.category_id == models.Category.id) \
        .filter(models.Category.slug == category_slug) \
        .order_by(models.News.published_at.desc()) \
        .offset(skip) \
        .limit(limit) \
        .all()


def get_news_by_tag(db: Session, tag_slug: str, skip: int = 0, limit: int = 10):
    """獲取特定標籤的新聞"""
    return db.query(models.News) \
        .join(models.NewsTag, models.News.id == models.NewsTag.news_id) \
        .join(models.Tag, models.NewsTag.tag_id == models.Tag.id) \
        .filter(models.Tag.slug == tag_slug) \
        .order_by(models.News.published_at.desc()) \
        .offset(skip) \
        .limit(limit) \
        .all()


def get_news_by_entity(db: Session, entity_name: str, entity_type: Optional[str] = None, skip: int = 0, limit: int = 10):
    """獲取與特定實體相關的新聞"""
    query = db.query(models.News) \
        .join(models.NewsEntity, models.News.id == models.NewsEntity.news_id) \
        .join(models.Entity, models.NewsEntity.entity_id == models.Entity.id) \
        .filter(models.Entity.name == entity_name)
    
    if entity_type:
        query = query.filter(models.Entity.entity_type == entity_type)
    
    return query.order_by(models.News.published_at.desc()) \
        .offset(skip) \
        .limit(limit) \
        .all()


def get_featured_news(db: Session, limit: int = 5):
    """獲取精選新聞"""
    return db.query(models.News) \
        .filter(models.News.is_featured == True) \
        .order_by(models.News.published_at.desc()) \
        .limit(limit) \
        .all()


def get_recent_news(db: Session, limit: int = 10):
    """獲取最新新聞"""
    return db.query(models.News) \
        .order_by(models.News.published_at.desc()) \
        .limit(limit) \
        .all()


def get_news_by_slug(db: Session, slug: str):
    """通過 slug 獲取特定新聞"""
    return db.query(models.News).filter(models.News.slug == slug).first()


def search_news(db: Session, query: str, skip: int = 0, limit: int = 10):
    """搜索新聞"""
    search = f"%{query}%"
    return db.query(models.News) \
        .filter(
            (models.News.title.ilike(search)) | 
            (models.News.content.ilike(search)) |
            (models.News.summary.ilike(search))
        ) \
        .order_by(models.News.published_at.desc()) \
        .offset(skip) \
        .limit(limit) \
        .all()