import hashlib
import shutil
import json
from pathlib import Path

def calculate_sha256(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def save_image_local(source_path, file_id, extension):
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

    dest_path = data_dir / f"{file_id}{extension}"
    shutil.copy2(source_path, dest_path)

    return {
        "path": str(dest_path),
        "data_url": f"file://{dest_path.absolute()}",
        "storage_type": "local",
        "checksum": calculate_sha256(dest_path),
        "checksum_algorithm": "sha256"
    }

def verify_file(json_path):
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
    except FileNotFoundError:
        return "Không thể kiểm tra: Không tìm thấy file metadata JSON."

    img_path = Path(metadata.get("path"))
    if not img_path.exists():
        return "Không thể kiểm tra: Ảnh gốc không tồn tại hoặc mất quyền truy cập."

    if calculate_sha256(img_path) == metadata.get("checksum"):
        return "Khớp: Dữ liệu ảnh toàn vẹn."
    return "Không khớp: Ảnh đã bị thay đổi sau khi lưu."