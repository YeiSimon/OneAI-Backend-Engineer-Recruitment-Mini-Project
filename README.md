# NBA 新聞網站資料庫系統

基於 FastAPI + PostgreSQL + Alembic 的 NBA 新聞網站資料庫系統，使用 Docker 容器化部署。

## 功能特性

- 完整的新聞資料庫設計，支援新聞、分類、標籤、實體、熱度指標等功能
- 使用 Alembic 進行資料庫版本控制
- Docker 容器化部署，便於環境一致性
- RESTful API 支援各種查詢操作
- 完整的種子資料，便於快速啟動和測試

## 快速開始

### 前置需求

- Docker 和 Docker Compose
- Git

### 安裝步驟

1. 克隆此倉庫
```bash
git clone https://github.com/your-username/nba-news-db.git
cd nba-news-db
```

2. 啟動 Docker 容器
```bash
docker-compose up -d
```

3. 系統將自動執行以下操作:
   - 創建 PostgreSQL 資料庫
   - 使用 Alembic 進行資料庫遷移
   - 載入初始資料
   - 啟動 FastAPI 伺服器

4. API 服務將在以下地址運行:
```
http://localhost:8000
```

5. 可以訪問 API 文檔:
```
http://localhost:8000/docs
```

## API 端點

系統提供以下主要 API 端點:

- `GET /news/` - 獲取新聞列表
- `GET /news/hot/` - 獲取熱門新聞
- `GET /news/featured/` - 獲取精選新聞
- `GET /news/{slug}` - 獲取特定新聞詳情
- `GET /categories/{category_slug}/news/` - 獲取特定分類的新聞
- `GET /tags/{tag_slug}/news/` - 獲取特定標籤的新聞
- `GET /search/` - 搜索新聞
- `POST /news/` - 添加新聞
- `POST /news/{news_id}/entity/` - 向新聞添加實體關聯
- `GET /entities/{entity_type}/` - 獲取特定類型的實體列表
- `GET /entities/{entity_type}/{name}/news/` - 獲取與特定實體相關的新聞

## 資料庫結構

系統包含以下主要表格:

- `news` - 存儲新聞文章
- `categories` - 存儲新聞分類
- `tags` - 存儲標籤信息
- `news_tags` - 新聞和標籤的多對多關聯
- `news_metrics` - 追蹤新聞的瀏覽量等指標
- `entities` - 存儲 NBA 相關實體如球隊、球員等
- `news_entities` - 新聞和實體的多對多關聯

## 開發

### 目錄結構

```
.
├── alembic/              # Alembic 遷移文件
│   ├── versions/         # 遷移版本
│   └── env.py            # Alembic 環境設定
├── app/                  # API 應用程式
│   ├── __init__.py
│   ├── main.py           # FastAPI 應用
│   ├── database.py       # 資料庫連接設定
│   ├── models.py         # SQLAlchemy 模型
│   ├── schemas.py        # Pydantic 模型/驗證
│   └── crud.py           # 資料庫操作函數
├── scripts/              # 輔助腳本
│   ├── init.sh           # 初始化腳本
│   └── seed_data.py      # 種子資料腳本
├── docker-compose.yml    # Docker Compose 設定
├── Dockerfile            # Docker 映像檔設定
└── requirements.txt      # Python 依賴
```

### Alembic 命令

```bash
# 創建新的遷移文件
docker-compose exec web alembic revision --autogenerate -m "描述"

# 升級到最新版本
docker-compose exec web alembic upgrade head

# 降級到特定版本
docker-compose exec web alembic downgrade <版本號>
```

## 擴展建議

- 添加用戶評論功能
- 實現新聞搜索功能的全文檢索
- 添加球隊和球員專頁
- 實現新聞推薦系統
- 添加 Redis 緩存層提高性能
- 實現爬蟲系統自動抓取新聞

## 注意事項

- 確保在生產環境中更改預設的資料庫密碼
- 根據流量需求適當調整 PostgreSQL 和 FastAPI 的配置
- 定期備份資料庫
