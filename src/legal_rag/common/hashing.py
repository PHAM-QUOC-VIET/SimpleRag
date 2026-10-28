"""Hashing and fingerprinting utilities for version tracking."""

import hashlib
from pathlib import Path


def compute_file_hash(file_path: Path) -> str:
    """Tính toán SHA-256 hash của một file bất biến."""
    hasher = hashlib.sha256() # tạo đối tượng tính hash
    with open(file_path, "rb") as f: # mở file chế độ đọc nhị phân
        while chunk := f.read(65536): # đọc từng khối 65.536 bytes
            hasher.update(chunk) # cập nhật hash với khối dữ liệu vừa đọc
    return hasher.hexdigest() # trả về giá trị hash dưới dạng chuỗi hex


def compute_text_hash(text: str) -> str:
    """Tính toán SHA-256 hash của một chuỗi text."""
    # str.encode(): Chuyển đổi chuỗi thành bytes, sử dụng mã hóa UTF-8.
    # Lý do: hàm băm sha256 yêu cầu dữ liệu đầu vào là bytes, không phải chuỗi
    return hashlib.sha256(text.strip().encode("utf-8")).hexdigest()


def compute_version_fingerprint(*components: str) -> str:
    """Tạo fingerprint định danh phiên bản kết hợp nhiều thành phần (vd: source_hash + parser_version)."""
    hasher = hashlib.sha256()
    for comp in components:
        hasher.update(comp.encode("utf-8"))
    return hasher.hexdigest()[:16]
