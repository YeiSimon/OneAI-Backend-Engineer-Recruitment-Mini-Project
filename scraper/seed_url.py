import re
import asyncio
from crawl4ai import *
from datetime import datetime
from pymongo import MongoClient
from models import SeedUrl, UrlUpdate
from typing import List, Set

# MongoDB連接設定
MONGO_URI = "mongodb://admin:password@localhost:27017/"
DB_NAME = "news_crawler"
URL_COLLECTION = "seed_urls"

async def get_seed_urls(page_num: int = 1) -> List[str]:
    """
    從UDN NBA新聞頁面爬取文章URL
    
    Args:
        page_num: 頁碼，從1開始
        
    Returns:
        文章URL列表
    """
    config = CrawlerRunConfig(
        target_elements=["div#news_list"],
    )
    
    url = f"https://tw-nba.udn.com/nba/cate/6754/0/newest/{page_num}"
    print(f"爬取頁面: {url}")
    
    try:
        crawler = AsyncWebCrawler()
        
        result = await crawler.arun(
            url=url,
            config=config
        )
        # 使用正則表達式匹配所有新聞URL
        pattern = r'https?://[^"\s)]+\.com/nba/story/\d+/\d+'
        matches = re.findall(pattern, result.markdown)
        
        # 去除重複URL
        unique_urls = list(set(matches))
        print(f"找到 {len(unique_urls)} 個唯一URL")
        
        return unique_urls
    except Exception as e:
        print(f"爬取頁面 {url} 時出錯: {e}")
        return []

def save_urls_to_mongodb(urls: List[str]) -> tuple:
    """
    將URL列表保存到MongoDB
    
    Args:
        urls: 要保存的URL列表
        
    Returns:
        (成功保存的URL數量, 總共的URL數量)
    """
    try:
        # 連接MongoDB
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        collection = db[URL_COLLECTION]
        
        # 檢查哪些URL已經存在
        existing_urls: Set[str] = set()
        for doc in collection.find({}, {"url": 1}):
            existing_urls.add(doc["url"])
        
        # 過濾出新URL
        new_urls = [url for url in urls if url not in existing_urls]
        
        # 準備要插入的文檔
        now = datetime.now()
        documents = []
        
        for url in new_urls:
            # 使用Pydantic模型創建文檔
            seed_url = SeedUrl(
                url=url,
                status="pending",
                created_at=now,
                updated_at=now
            )
            documents.append(seed_url.model_dump())
        
        # 批量插入
        if documents:
            collection.insert_many(documents)
            print(f"成功保存 {len(documents)} 個新URL到MongoDB")
        else:
            print("沒有新的URL需要保存")
        
        return len(documents), len(urls)
    
    except Exception as e:
        print(f"MongoDB操作出錯: {e}")
        return 0, len(urls)
    finally:
        if 'client' in locals():
            client.close()

def get_url_status_counts():
    """獲取各狀態URL的數量"""
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        collection = db[URL_COLLECTION]
        
        # 使用聚合查詢
        pipeline = [
            {"$group": {"_id": "$status", "count": {"$sum": 1}}}
        ]
        
        result = list(collection.aggregate(pipeline))
        status_counts = {item["_id"]: item["count"] for item in result}
        
        return status_counts
    except Exception as e:
        print(f"獲取URL狀態統計時出錯: {e}")
        return {}
    finally:
        if 'client' in locals():
            client.close()

async def main():
    """主函數：爬取多頁URL並保存"""
    try:
        # 爬取前3頁的URL (可調整頁數)
        all_urls = []
        for page in range(1, 4):
            urls = await get_seed_urls(page)
            all_urls.extend(urls)
            
            # 避免爬取太快
            if page < 3:
                await asyncio.sleep(1)
        
        # 保存到MongoDB
        saved_count, total_count = save_urls_to_mongodb(all_urls)
        print(f"總共爬取到 {total_count} 個URL，其中 {saved_count} 個是新URL")
        
        # 獲取URL狀態統計
        status_counts = get_url_status_counts()
        print("URL狀態統計:")
        for status, count in status_counts.items():
            print(f"  - {status}: {count}個")
        
    except Exception as e:
        print(f"執行過程中出錯: {e}")

if __name__ == "__main__":
    asyncio.run(main())