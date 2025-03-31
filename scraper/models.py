from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional
from datetime import datetime

class ImageInfo(BaseModel):
    """圖片資訊的模型"""
    url: str = Field(..., description="圖片URL")
    title: str = Field(default="", description="圖片標題")
    alt: str = Field(default="", description="圖片替代文字")

class SeedUrl(BaseModel):
    """種子URL的模型"""
    url: str = Field(..., description="新聞文章的URL")
    status: str = Field(default="pending", description="處理狀態 (pending, processing, completed, failed)")
    created_at: datetime = Field(default_factory=datetime.now, description="創建時間")
    updated_at: Optional[datetime] = Field(default=None, description="最後更新時間")

    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://tw-nba.udn.com/nba/story/7002/8640845",
                "status": "pending",
                "created_at": "2025-03-30T12:00:00",
                "updated_at": None
            }
        }

class ArticleContent(BaseModel):
    """文章內容的模型"""
    title: str = Field(..., description="文章標題")
    time: str = Field(..., description="發布時間")
    url: str = Field(..., description="文章URL")
    image: ImageInfo = Field(..., description="文章圖片資訊")
    content: str = Field(..., description="文章完整內容")
    paragraphs: List[str] = Field(..., description="文章段落列表")
    crawled_at: datetime = Field(default_factory=datetime.now, description="爬取時間")
    updated_at: Optional[datetime] = Field(default=None, description="最後更新時間")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "NBA新聞標題",
                "time": "2025/03/30 12:34",
                "url": "https://tw-nba.udn.com/nba/story/7002/8640845",
                "image": {
                    "url": "https://example.com/image.jpg",
                    "title": "圖片標題",
                    "alt": "圖片描述"
                },
                "content": "這是完整的文章內容...",
                "paragraphs": ["第一段內容", "第二段內容", "..."],
                "crawled_at": "2025-03-30T12:34:56",
                "updated_at": None
            }
        }

class UrlUpdate(BaseModel):
    """更新URL狀態的模型"""
    status: str = Field(..., description="新的處理狀態")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新時間")

class UrlListResponse(BaseModel):
    """URL列表響應模型"""
    total: int = Field(..., description="總URL數量")
    urls: List[SeedUrl] = Field(..., description="URL列表")

class ArticleListResponse(BaseModel):
    """文章列表響應模型"""
    total: int = Field(..., description="總文章數量")
    articles: List[ArticleContent] = Field(..., description="文章列表")