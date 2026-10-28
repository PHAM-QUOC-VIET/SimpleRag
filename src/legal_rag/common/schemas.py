"""Core data contracts and Pydantic schemas for Legal RAG system."""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DocumentType(str, Enum):
    """Phân loại văn bản quy phạm pháp luật Việt Nam."""
    LUAT = "luat"                  # Luật / Bộ luật
    NGHI_DINH = "nghi_dinh"        # Nghị định
    THONG_TU = "thong_tu"          # Thông tư
    VBHN = "vbhn"                  # Văn bản hợp nhất
    QUYET_DINH = "quyet_dinh"      # Quyết định
    OTHER = "other"


class DocumentStatus(str, Enum):
    """Trạng thái hiệu lực của văn bản."""
    ACTIVE = "active"              # Còn hiệu lực
    EXPIRED = "expired"            # Hết hiệu lực
    PARTIALLY_EXPIRED = "partial"  # Hết hiệu lực một phần / sửa đổi bổ sung
    UNKNOWN = "unknown"


class LegalMetadata(BaseModel):
    """
    Metadata pháp lý của văn bản.

    Attributes:
        doc_code (Optional[str]): Số hiệu văn bản, ví dụ: 45/2013/QH13
        title (str): Tên gọi văn bản, ví dụ: Luật Đất đai 2013
        doc_type (DocumentType): Loại văn bản
        issuing_body (Optional[str]): Cơ quan ban hành, ví dụ: Quốc hội
        issue_date (Optional[str]): Ngày ban hành (YYYY-MM-DD)
        effective_date (Optional[str]): Ngày có hiệu lực (YYYY-MM-DD)
        status (DocumentStatus): Tình trạng hiệu lực
        extra (Dict[str, Any]): Thông tin bổ sung khác
    """
    doc_code: Optional[str] = Field(None, description="Số hiệu văn bản, ví dụ: 45/2013/QH13")
    title: str = Field(..., description="Tên gọi văn bản, ví dụ: Luật Đất đai 2013")
    doc_type: DocumentType = Field(DocumentType.LUAT, description="Loại văn bản")
    issuing_body: Optional[str] = Field(None, description="Cơ quan ban hành, ví dụ: Quốc hội")
    issue_date: Optional[str] = Field(None, description="Ngày ban hành (YYYY-MM-DD)")
    effective_date: Optional[str] = Field(None, description="Ngày có hiệu lực (YYYY-MM-DD)")
    status: DocumentStatus = Field(DocumentStatus.ACTIVE, description="Tình trạng hiệu lực")
    extra: Dict[str, Any] = Field(default_factory=dict)


class RawDocument(BaseModel):
    """
    Văn bản thô sau khi load từ file PDF/DOCX.
    
    Attributes:
        doc_id (str): ID duy nhất của văn bản
        file_name (str): Tên file gốc
        file_path (str): Đường dẫn file gốc
        source_hash (str): Hash của file gốc để kiểm tra thay đổi
        raw_text (str): Nội dung văng bản thô
        page_count (int): Số trang của văn bản
        metadata (LegalMetadata): Metadata pháp lý của văn bản
    """
    doc_id: str
    file_name: str
    file_path: str
    source_hash: str
    raw_text: str
    page_count: int
    metadata: LegalMetadata


class LegalUnit(BaseModel):
    """
    Đơn vị pháp lý bóc tách được từ văn bản (Chương, Mục, Điều, Khoản, Điểm).
    
    Attributes:
        doc_id (str): ID của văn bản 
        chapter_num (Optional[str]): Số chương, ví dụ: "Chương II"
        chapter_title (Optional[str]): Tên chương, ví dụ: "Quyền sử dụng đất"
        section_num (Optional[str]): Số mục, ví dụ: "Mục 1"
        section_title (Optional[str]): Tên mục, ví dụ: "Các loại đất"
        article_num (str): Số điều, ví dụ: "Điều 10"
        article_title (Optional[str]): Tên điều, ví dụ: "Phân loại đất"
        clause_num (Optional[str]): Số khoản, ví dụ: "1" hoặc "Khoản 1"
        point_id (Optional[str]): ID điểm, ví dụ: "a" hoặc "Điểm a"
        content (str): Nội dung của điều/khoản/điểm
        page_number (Optional[int]): Số trang chứa đơn vị pháp lý
    """
    doc_id: str
    chapter_num: Optional[str] = None
    chapter_title: Optional[str] = None
    section_num: Optional[str] = None
    section_title: Optional[str] = None
    article_num: str = Field(..., description="Ví dụ: 'Điều 10'")
    article_title: Optional[str] = Field(None, description="Ví dụ: 'Phân loại đất'")
    clause_num: Optional[str] = Field(None, description="Ví dụ: '1' hoặc 'Khoản 1'")
    point_id: Optional[str] = Field(None, description="Ví dụ: 'a' hoặc 'Điểm a'")
    content: str = Field(..., description="Nội dung điều/khoản/điểm")
    page_number: Optional[int] = None


class LegalChunk(BaseModel):
    """
    Đơn vị chunking chuẩn phục vụ indexing & retrieval.

    Attributes:
        chunk_id (str): ID duy nhất của chunk
        doc_id (str): ID của văn bản chứa chunk
        doc_title (str): Tên văn bản chứa chunk
        doc_code (Optional[str]): Số hiệu văn bản chứa chunk
        article_num (str): Số điều chứa chunk
        article_title (Optional[str]): Tên điều chứa chunk
        clause_num (Optional[str]): Số khoản chứa chunk
        header_path (str): Đường dẫn phân cấp đầy đủ, ví dụ: 'Luật Đất đai > Chương II > Điều 10. Phân loại đất > Khoản 1'
        content (str): Nội dung cốt lõi của chunk
        contextual_text (str): Nội dung đã gắn tiền tố ngữ cảnh phân cấp dùng cho dense embedding và reranking
        metadata (Dict[str, Any]): Thông tin bổ sung khác
        chunk_version (str): Phiên bản định nghĩa chunk, mặc định là "v1"
    """
    chunk_id: str
    doc_id: str
    doc_title: str
    doc_code: Optional[str] = None
    article_num: str
    article_title: Optional[str] = None
    clause_num: Optional[str] = None
    header_path: str = Field(
        ...,
        description="Đường dẫn phân cấp đầy đủ, ví dụ: 'Luật Đất đai > Chương II > Điều 10. Phân loại đất > Khoản 1'"
    )
    content: str = Field(..., description="Nội dung cốt lõi của chunk")
    contextual_text: str = Field(
        ...,
        description="Nội dung đã gắn tiền tố ngữ cảnh phân cấp dùng cho dense embedding và reranking"
    )
    metadata: Dict[str, Any] = Field(default_factory=dict)
    chunk_version: str = "v1"


class RetrievalResult(BaseModel):
    """
    Kết quả truy xuất tài liệu từ hệ thống tìm kiếm.
    
    Attributes:
        chunk (LegalChunk): Chunk được truy xuất
        score (float): Điểm tương đồng hoặc độ tin cậy của kết quả
        rank (int): Thứ hạng của kết quả trong danh sách trả về
        source_engine (str): Nguồn engine truy xuất
    """
    chunk: LegalChunk
    score: float
    rank: int = 0
    source_engine: str = Field("hybrid", description="dense | sparse | hybrid | rerank")


class Citation(BaseModel):
    """
    Căn cứ trích dẫn nguồn gốc của câu trả lời.
    
    Attributes:
        doc_title (str): Tên văn bản chứa căn cứ
        doc_code (Optional[str]): Số hiệu văn bản chứa căn cứ
        article_num (str): Số điều chứa căn cứ
        clause_num (Optional[str]): Số khoản chứa căn cứ
        point_id (Optional[str]): ID điểm chứa căn cứ
        snippet (str): Trích đoạn nội dung căn cứ
    """
    doc_title: str
    doc_code: Optional[str] = None
    article_num: str
    clause_num: Optional[str] = None
    point_id: Optional[str] = None
    snippet: str


class AnswerResponse(BaseModel):
    """
    Câu trả lời hoàn chỉnh trả về cho người dùng.
    
    Attributes:
        query (str): Câu hỏi người dùng gửi lên
        answer (str): Câu trả lời được sinh ra từ mô hình
        citations (List[Citation]): Danh sách căn cứ trích dẫn
        evidence_chunks (List[LegalChunk]): Danh sách các chunk pháp lý liên quan
        is_refusal (bool): Cờ từ chối trả lời nếu không có thông tin
        refusal_reason (Optional[str]): Lý do từ chối trả lời
        model_name (str): Tên mô hình LLM được sử dụng
        latency_ms (float): Thời gian xử lý câu hỏi (ms)
    """
    query: str
    answer: str
    citations: List[Citation] = Field(default_factory=list)
    evidence_chunks: List[LegalChunk] = Field(default_factory=list)
    is_refusal: bool = False
    refusal_reason: Optional[str] = None
    model_name: str
    latency_ms: float = 0.0
