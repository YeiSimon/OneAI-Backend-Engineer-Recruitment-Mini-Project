import asyncio
import re
from crawl4ai import *
from datetime import datetime
from pymongo import MongoClient
from models import ArticleContent, ImageInfo, UrlUpdate
from typing import List, Dict, Optional, Any

# MongoDB連接設定
MONGO_URI = "mongodb://admin:password@localhost:27017/"
DB_NAME = "news_crawler"
URL_COLLECTION = "seed_urls"
ARTICLE_COLLECTION = "articles"

async def get_article_content(url: str) -> Optional[ArticleContent]:
    """
    從URL獲取文章內容
    
    Args:
        url: 文章URL
        
    Returns:
        ArticleContent模型，如果失敗則返回None
    """
    config = CrawlerRunConfig(
        target_elements=["div#story.area"]
    )
    
    try:
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(
                url=url,
                config=config
            )
            
            html = result.html
            
            # 擷取標題
            title_match = re.search(r'<h1[^>]*>(.*?)</h1>', html)
            title_text = title_match.group(1) if title_match else "標題未找到"
            
            # 擷取時間
            time_match = re.search(r'<div class="shareBar__info--author"><span>(.*?)</span>', html)
            time_text = time_match.group(1) if time_match else "時間未找到"
            
            # 擷取圖片資訊
            img_match = re.search(r'<img [^>]*src="([^"]+)"[^>]*title="([^"]+)"[^>]*alt="([^"]+)"', html)
            img_url = img_match.group(1) if img_match else "圖片未找到"
            img_title = img_match.group(2) if img_match else ""
            img_alt = img_match.group(3) if img_match else ""
            
            # 擷取內文段落
            paragraphs = re.findall(r'<p>(.*?)</p>', html)
            cleaned_paragraphs = [re.sub(r'<.*?>', '', p).strip() for p in paragraphs if p.strip()]
            article_text = '\n'.join(cleaned_paragraphs)
            
            # 使用Pydantic模型創建文章對象
            now = datetime.now()
            image_info = ImageInfo(
                url=img_url,
                title=img_title,
                alt=img_alt
            )
            
            article = ArticleContent(
                title=title_text,
                time=time_text,
                url=url,
                image=image_info,
                content=article_text,
                paragraphs=cleaned_paragraphs,
                crawled_at=now,
                updated_at=now
            )
            
            return article
    
    except Exception as e:
        print(f"爬取文章 {url} 時出錯: {e}")
        return None

def get_pending_urls(limit: int = 5) -> List[str]:
    """
    從MongoDB獲取待處理的URL
    
    Args:
        limit: 最大獲取數量
        
    Returns:
        URL列表
    """
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        url_collection = db[URL_COLLECTION]
        
        # 獲取狀態為pending的URL
        cursor = url_collection.find({"status": "pending"}).limit(limit)
        pending_urls = [doc["url"] for doc in cursor]
        
        return pending_urls
    except Exception as e:
        print(f"獲取待處理URL時出錯: {e}")
        return []
    finally:
        if 'client' in locals():
            client.close()

def update_url_status(url: str, status: str) -> bool:
    """
    更新URL的處理狀態
    
    Args:
        url: 要更新的URL
        status: 新狀態
        
    Returns:
        是否成功
    """
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        url_collection = db[URL_COLLECTION]
        
        # 使用Pydantic模型創建更新數據
        update = UrlUpdate(
            status=status,
            updated_at=datetime.now()
        )
        
        result = url_collection.update_one(
            {"url": url},
            {"$set": update.model_dump()}
        )
        
        return result.modified_count > 0
    except Exception as e:
        print(f"更新URL狀態時出錯: {e}")
        return False
    finally:
        if 'client' in locals():
            client.close()

def save_article(article: ArticleContent) -> bool:
    """
    保存文章到MongoDB
    
    Args:
        article: 文章對象
        
    Returns:
        是否成功
    """
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        article_collection = db[ARTICLE_COLLECTION]
        
        # 檢查是否已存在
        existing = article_collection.find_one({"url": article.url})
        
        if existing:
            # 更新現有文章
            result = article_collection.update_one(
                {"url": article.url},
                {"$set": article.model_dump()}
            )
            print(f"更新文章: {article.title}")
            return result.modified_count > 0
        else:
            # 插入新文章
            result = article_collection.insert_one(article.model_dump())
            print(f"新增文章: {article.title}")
            return result.inserted_id is not None
    
    except Exception as e:
        print(f"保存文章時出錯: {e}")
        return False
    finally:
        if 'client' in locals():
            client.close()

async def process_single_url(url: str) -> bool:
    """
    處理單個URL：爬取內容並保存
    
    Args:
        url: 要處理的URL
        
    Returns:
        是否成功
    """
    try:
        # 更新URL狀態為處理中
        update_url_status(url, "processing")
        
        # 爬取文章內容
        article = await get_article_content(url)
        
        if article:
            # 保存文章
            saved = save_article(article)
            
            if saved:
                # 更新URL狀態為已完成
                update_url_status(url, "completed")
                return True
        
        # 如果爬取或保存失敗
        update_url_status(url, "failed")
        return False
    
    except Exception as e:
        print(f"處理URL {url} 時出錯: {e}")
        update_url_status(url, "failed")
        return False

async def main():
    """
    主函數：獲取並處理待處理的URL
    """
    # 獲取待處理的URL
    pending_urls = get_pending_urls(limit=30)  # 一次處理10篇文章
    
    if not pending_urls:
        print("沒有待處理的URL")
        return
    
    print(f"開始處理 {len(pending_urls)} 個URL")
    
    # 創建協程任務
    tasks = []
    for url in pending_urls:
        # 添加一些延遲，避免過於密集的請求
        await asyncio.sleep(1)
        tasks.append(process_single_url(url))
    
    # 等待所有任務完成
    results = await asyncio.gather(*tasks)
    
    # 統計結果
    success_count = results.count(True)
    print(f"成功處理 {success_count} 個URL，失敗 {len(results) - success_count} 個")

if __name__ == "__main__":
    asyncio.run(main())