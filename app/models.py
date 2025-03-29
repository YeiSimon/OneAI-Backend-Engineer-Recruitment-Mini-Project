from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, LargeBinary, UniqueConstraint, JSON, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class News(Base):
    __tablename__ = "news"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    slug = Column(String(300), unique=True, nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(Text)
    published_at = Column(DateTime, nullable=False)
    thumbnail_url = Column(String(512))
    is_featured = Column(Boolean, default=False)
    category_id = Column(Integer, ForeignKey("categories.id"))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    category = relationship("Category", back_populates="news")
    tags = relationship("Tag", secondary="news_tags", back_populates="news")
    metrics = relationship("NewsMetrics", back_populates="news", uselist=False)
    entities = relationship("Entity", secondary="news_entities", back_populates="news")
    image = relationship("NewsImage", back_populates="news", uselist=False)
    
    # Indexes
    __table_args__ = (
        Index("idx_news_published_at", "published_at"),
        Index("idx_news_category_id", "category_id"),
        Index("idx_news_is_featured", "is_featured"),
    )
    
class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    slug = Column(String(120), nullable=False, unique=True)
    
    # Relationships
    news = relationship("News", back_populates="category")


class Tag(Base):
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    slug = Column(String(120), nullable=False, unique=True)
    
    # Relationships
    news = relationship("News", secondary="news_tags", back_populates="tags")


class NewsTag(Base):
    __tablename__ = "news_tags"
    
    id = Column(Integer, primary_key=True)
    news_id = Column(Integer, ForeignKey("news.id", ondelete="CASCADE"))
    tag_id = Column(Integer, ForeignKey("tags.id", ondelete="CASCADE"))
    
    # Unique constraint
    __table_args__ = (
        UniqueConstraint('news_id', 'tag_id', name='uq_news_tag'),
        Index("idx_news_tags_news_id", "news_id"),
        Index("idx_news_tags_tag_id", "tag_id"),
    )


class NewsMetrics(Base):
    __tablename__ = "news_metrics"
    
    id = Column(Integer, primary_key=True)
    news_id = Column(Integer, ForeignKey("news.id", ondelete="CASCADE"), unique=True)
    view_count = Column(Integer, default=0)
    last_updated = Column(DateTime, default=func.now())
    
    # Relationships
    news = relationship("News", back_populates="metrics")
    
    # Indexes
    __table_args__ = (
        Index("idx_news_metrics_view_count", "view_count", postgresql_using='btree', postgresql_ops={'view_count': 'DESC'}),
    )


class Entity(Base):
    __tablename__ = "entities"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    entity_type = Column(String(50), nullable=False)
    meta_info = Column(JSON)
    
    # Relationships
    news = relationship("News", secondary="news_entities", back_populates="entities")


class NewsEntity(Base):
    __tablename__ = "news_entities"
    
    id = Column(Integer, primary_key=True)
    news_id = Column(Integer, ForeignKey("news.id", ondelete="CASCADE"))
    entity_id = Column(Integer, ForeignKey("entities.id", ondelete="CASCADE"))
    role = Column(String(50), nullable=False)
    
    # Unique constraint
    __table_args__ = (
        UniqueConstraint('news_id', 'entity_id', 'role', name='uq_news_entity_role'),
    )

class NewsImage(Base):
    __tablename__ = "news_images"
    
    id = Column(Integer, primary_key=True, index=True)
    news_id = Column(Integer, ForeignKey("news.id"), nullable=False)
    image_data = Column(LargeBinary, nullable=False)
    mime_type = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    
    # 關聯
    news = relationship("News", back_populates="image")