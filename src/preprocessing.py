import json
import re
from pathlib import Path

from underthesea import word_tokenize


def lowercase_and_clean(text: str) -> str:
    """
    Chuyển toàn bộ văn bản về chữ thường, các ký tự đặc biệt, 
    dấu câu thừa và chuẩn hóa khoảng trắng thừa.
    """
    if not text:
        return ""
    # 1. Chuyển về chữ thường
    text = text.lower()
    # 2. Loại bỏ ký tự đặc biệt và dấu câu thừa 
    # (giữ lại các chữ cái, chữ số, khoảng trắng và ký tự tiếng Việt)
    text = re.sub(r"[^\w\sàáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ]", " ", text)
    # 3. Chuẩn hóa khoảng trắng thừa (nhiều khoảng trắng liên tiếp thành 1)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def tokenize_vietnamese(text: str) -> list[str]:
    """
    Tách từ tiếng Việt dựa trên từ điển và ngữ pháp sử dụng thư viện underthesea.
    Trả về danh sách các tokens (từ/cụm từ đã được tách).
    """
    if not text:
        return []
    
    # Dùng underthesea để tách từ, định dạng "text" sẽ nối các từ trong cụm từ cố định bằng dấu gạch dưới "_"
    # Sau đó dùng .split() để chuyển thành danh sách các token
    return word_tokenize(text, format="text").split()

# Định nghĩa danh sách từ dừng (stopwords) tiếng Việt phổ biến
VIETNAMESE_STOPWORDS = {
    "và", "của", "là", "có", "các", "cho", "trong", "những", "được",
    "với", "về", "đến", "theo", "tại", "này", "đã", "đang", "như",
    "hoặc", "nếu", "nhưng", "bởi", "vì", "để", "từ", "trên", "dưới"
}

def remove_stopwords(tokens: list[str], stopwords: set = VIETNAMESE_STOPWORDS) -> list[str]:
    """
    Loại bỏ các từ dừng (stopwords) khỏi danh sách các tokens tiếng Việt.
    """
    if not tokens:
        return []
    # Lọc giữ lại những token không nằm trong danh sách từ dừng
    filtered_tokens = [token for token in tokens if token.lower() not in stopwords]
    
    return filtered_tokens

def preprocess_chunk(chunk: dict) -> dict:
    # Sao chép bản ghi gốc để không làm thay đổi trực tiếp dữ liệu đầu vào
    processed_chunk = dict(chunk)
    
    raw_text = processed_chunk.get("text", "")
    
    # Bước 1: Lowercasing & Cleaning
    clean_text = lowercase_and_clean(raw_text)
    # Bước 2: Tokenization
    tokens = tokenize_vietnamese(clean_text)
    # Bước 3: Stopwords Removal
    filtered_tokens = remove_stopwords(tokens)
    # Chuỗi hoàn chỉnh sau khi xử lý (dùng để tạo vector sau này)
    processed_text = " ".join(filtered_tokens)
    # Cập nhật kết quả vào dictionary
    processed_chunk.update({
        "clean_text": clean_text,
        "tokens": tokens,
        "filtered_tokens": filtered_tokens,
        "processed_text": processed_text
    })
    
    return processed_chunk


def run_preprocessing() -> None:
    """
    Chạy toàn bộ pipeline xử lý dữ liệu cho từng chunk trong merged.json.
    Kết quả được lưu vào merged_preprocessed.json.
    """
    project_root = Path(__file__).resolve().parent.parent
    input_path = project_root / "Data" / "merged.json"
    output_path = project_root / "Data" / "merged_preprocessed.json"

    # Đọc dữ liệu từ merged.json
    with input_path.open("r", encoding="utf-8") as f:
        records = json.load(f)

    # Xử lý từng chunk
    processed_records = [preprocess_chunk(chunk) for chunk in records]

    # Lưu kết quả vào merged_preprocessed.json
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(processed_records, f, ensure_ascii=False, indent=4)

    print(f"Đã xử lý {len(processed_records)} chunk.")
    print(f"Kết quả: {output_path}")