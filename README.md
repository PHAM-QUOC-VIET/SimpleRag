# SimpleRag

## Expected Structure

```text
legal-rag-system/
├── .env.example                  # File mẫu lưu cấu hình môi trường
├── Dockerfile                    # Containerization cho production
├── docker-compose.yml            # Dựng services: VectorDB, Postgres, Redis...
├── pyproject.toml / requirements.txt
├── README.md
├── data/                         # Thư mục lưu dữ liệu cục bộ (ignored by Git)
│   ├── raw/                      # File .pdf, .docx luật thô
│   ├── parsed_json/              # File JSON sau khi bóc tách cấu trúc
│   └── embeddings/               # Cache local vector index (nếu có)
├── config/                       # Quản lý cấu hình dự án
│   ├── __init__.py
│   ├── settings.py               # Pydantic BaseSettings đọc từ .env
│   └── logging.py                # System logging config
├── src/                          # Source code chính của hệ thống
│   ├── __init__.py
│   ├── core/                     # Các module AI cốt lõi (LLM, Embedding, Prompts)
│   │   ├── llm.py                # Wrapper gọi OpenAI / Gemini / Ollama
│   │   ├── embedding.py          # Wrapper BGE-M3 / OpenAI Embeddings
│   │   └── prompts.py            # Quản lý prompt templates cho hệ thống luật
│   ├── ingestion/                # Pipeline 1: Tiền xử lý & indexing
│   │   ├── __init__.py
│   │   ├── pdf_extractor.py      # Đọc PDF/Word ra văn bản thô
│   │   ├── legal_parser.py       # Bóc tách thành JSON (Chương/Điều/Khoản)
│   │   ├── chunking.py           # Contextual chunking & parent-child splitter
│   │   └── indexer.py            # Đẩy JSON & vector vào Vector DB + Elastic
│   ├── retrieval/                # Pipeline 2: Tìm kiếm & truy xuất
│   │   ├── __init__.py
│   │   ├── hybrid_search.py      # Kết hợp dense vector + sparse (BM25)
│   │   ├── reranker.py           # Cross-encoder reranking
│   │   └── query_transform.py    # Rewrite câu hỏi, trích xuất mã điều luật
│   ├── services/                 # Business logic điều phối RAG
│   │   ├── __init__.py
│   │   ├── rag_service.py        # Query -> Search -> LLM -> Answer
│   │   └── document_service.py   # Xử lý upload và cập nhật tài liệu
│   ├── database/                 # Kết nối DB & ORM models
│   │   ├── vector_db.py          # Kết nối Qdrant/Milvus/Chroma
│   │   └── postgres.py           # Lưu lịch sử chat & metadata
│   └── api/                      # REST API endpoints (FastAPI)
│       ├── v1/
│       │   ├── endpoints/
│       │   │   ├── chat.py       # POST /api/v1/chat
│       │   │   ├── ingest.py     # POST /api/v1/ingest
│       │   │   └── health.py     # Healthcheck
│       │   └── router.py
│       └── app.py                # Khởi tạo FastAPI app
├── scripts/                      # Các script độc lập chạy batch job
│   ├── run_ingest.py             # Chạy tay để index lại toàn bộ database luật
│   └── eval_rag.py               # Đánh giá chất lượng RAG (RAGAS framework)
└── tests/                        # Unit tests & integration tests
    ├── test_legal_parser.py
    └── test_retrieval.py
```

## Notes

- `data/` nên được thêm vào `.gitignore`.
- Có thể tách phần `src/` thành các package nhỏ hơn nếu dự án mở rộng.
- Nếu muốn, mình có thể chỉnh tiếp README theo kiểu chuyên nghiệp hơn: thêm `Overview`, `Setup`, `Usage`, `API`, `Environment Variables`, `Project Layout`.
