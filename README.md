"# SimpleRag" 

## expected structure

legal-rag-system/
├── .env.example                  # File mẫu lưu cấu hình môi trường
├── Dockerfile                    # Containerization cho Production
├── docker-compose.yml            # Dựng Services: VectorDB, Postgres, Redis...
├── pyproject.toml / requirements.txt
├── README.md
│
├── data/                         # Thư mục lưu dữ liệu cục bộ (Ignored by Git)
│   ├── raw/                      # File .pdf, .docx luật thô
│   ├── parsed_json/              # File JSON sau khi bóc tách cấu trúc
│   └── embeddings/               # Cache local vector index (nếu có)
│
├── config/                       # Quản lý cấu hình dự án
│   ├── __init__.py
│   ├── settings.py               # Pydantic BaseSettings đọc từ .env
│   └── logging.py                # System logging config
│
├── src/                          # Source code chính của hệ thống
│   ├── __init__.py
│   │
│   ├── core/                     # Các module AI cốt lõi (LLM, Embedding, Prompts)
│   │   ├── llm.py                # Wrapper gọi OpenAI / Gemini / Ollama
│   │   ├── embedding.py          # Wrapper BGE-M3 / OpenAI Embeddings
│   │   └── prompts.py            # Quản lý Prompt templates cho hệ thống luật
│   │
│   ├── ingestion/                # PIPELINE 1: Tiền xử lý & Indexing
│   │   ├── __init__.py
│   │   ├── pdf_extractor.py      # Đọc PDF/Word ra văn bản thô
│   │   ├── legal_parser.py       # Script bóc tách thành JSON (Chương/Điều/Khoản)
│   │   ├── chunking.py           # Contextual Chunking & Parent-Child Splitter
│   │   └── indexer.py            # Đẩy JSON & Vector vào Vector DB + Elastic
│   │
│   ├── retrieval/                # PIPELINE 2: Tìm kiếm & Truy xuất
│   │   ├── __init__.py
│   │   ├── hybrid_search.py      # Kết hợp Dense Vector + Sparse (BM25)
│   │   ├── reranker.py           # Cross-Encoder Reranking
│   │   └── query_transform.py    # Rewrite câu hỏi người dùng, trích xuất mã Điều/Luật
│   │
│   ├── services/                 # Business Logic điều phối RAG
│   │   ├── __init__.py
│   │   ├── rag_service.py        # Pipeline hoàn chỉnh: Query -> Search -> LLM -> Answer
│   │   └── document_service.py   # Xử lý upload và cập nhật tài liệu
│   │
│   ├── database/                 # Kết nối DB & ORM Models
│   │   ├── vector_db.py          # Kết nối Qdrant/Milvus/Chroma
│   │   └── postgres.py           # Lưu lịch sử chat & metadata
│   │
│   └── api/                      # REST API Endpoints (FastAPI)
│       ├── v1/
│       │   ├── endpoints/
│       │   │   ├── chat.py       # Endpoint POST /api/v1/chat
│       │   │   ├── ingest.py     # Endpoint POST /api/v1/ingest
│       │   │   └── health.py     # Healthcheck
│       │   └── router.py
│       └── app.py                # Khởi tạo FastAPI App
│
├── scripts/                      # Các script độc lập chạy batch job
│   ├── run_ingest.py             # Script chạy bằng tay để index lại toàn bộ database luật
│   └── eval_rag.py               # Script đánh giá chất lượng RAG (RAGAS framework)
│
└── tests/                        # Unit tests & Integration tests
    ├── test_legal_parser.py
    └── test_retrieval.py