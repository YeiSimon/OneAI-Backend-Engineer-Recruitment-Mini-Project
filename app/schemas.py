from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class CategoryBase(BaseModel):
    name: str
    slug: str


class CategoryCreate(CategoryBase):
    pass


class Category(CategoryBase):
    id: int
    
    class Config:
        orm_mode = True


class TagBase(BaseModel):
    name: str
    slug: str


class TagCreate(TagBase):
    pass


class Tag(TagBase):
    id: int
    
    class Config:
        orm_mode = True


class NewsMetricsBase(BaseModel):
    view_count: int = 0
    last_updated: datetime


class NewsMetrics(NewsMetricsBase):
    id: int
    news_id: int
    
    class Config:
        orm_mode = True


class EntityBase(BaseModel):
    name: str
    entity_type: str
    metadata: Optional[Dict[str, Any]] = None


class EntityCreate(EntityBase):
    pass


class Entity(EntityBase):
    id: int
    
    class Config:
        orm_mode = True


class NewsEntityBase(BaseModel):
    role: str


class NewsEntity(NewsEntityBase):
    id: int
    news_id: int
    entity_id: int
    
    class Config:
        orm_mode = True


class NewsBase(BaseModel):
    title: str
    slug: str
    content: str
    summary: Optional[str] = None
    published_at: datetime
    thumbnail_url: Optional[str] = None
    is_featured: bool = False
    category_id: int


class NewsCreate(BaseModel):
    title: str
    content: str
    summary: Optional[str] = None
    published_at: Optional[datetime] = None
    thumbnail_url: Optional[str] = None
    is_featured: bool = False
    category_name: str
    tags: Optional[List[str]] = None


class NewsUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    thumbnail_url: Optional[str] = None
    is_featured: Optional[bool] = None
    category_id: Optional[int] = None


class News(NewsBase):
    id: int
    created_at: datetime
    updated_at: datetime
    category: Category
    tags: List[Tag] = []
    metrics: Optional[NewsMetrics] = None
    
    class Config:
        orm_mode = True


class NewsDetail(News):
    entities: List[Entity] = []


class NewsSearchResult(BaseModel):
    total: int
    items: List[News]


class NewsListResponse(BaseModel):
    items: List[News]
    total: int
    page: int
    size: int
    pages: int