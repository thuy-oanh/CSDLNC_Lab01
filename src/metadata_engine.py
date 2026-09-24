import hashlib
import json
import mimetypes
from datetime import datetime, timezone
from pathlib import Path
import uuid
from PIL import Image


def validate_image(image_path: Path) -> bool:
  """Kiểm tra file có tồn tại và thực sự là một file ảnh mở được hay không."""
  if not image_path.is_file():
    return False
  try:
    # Lần mở 1: verify() kiểm tra cấu trúc file có toàn vẹn không
    with Image.open(image_path) as img:
      img.verify()
    # Lần mở 2 (BẮT BUỘC): sau verify(), object ảnh không dùng lại được nữa,
    # nên phải mở lại và .load() để ép Pillow giải mã HẾT dữ liệu pixel.
    # Đây là bước bắt được các ảnh bị CẮT CỤT (truncated) mà verify() bỏ sót.
    with Image.open(image_path) as img:
      img.load()
    return True
  except Exception:
    return False


def compute_checksum(image_path: Path) -> str:
  """Tính mã băm SHA-256 (dấu vân tay) của file ảnh."""
  sha256 = hashlib.sha256()
  with open(image_path, "rb") as f:
    for block in iter(lambda: f.read(65536), b""):
      sha256.update(block)
  return sha256.hexdigest()


def generate_metadata(
    image_path_str: str,
    description: str,
    caption: str,
    author: str = "Nguyen Le Thuy Oanh",
    tags: list = None,
) -> dict:
  """Trích xuất toàn bộ thông số kỹ thuật thật từ ảnh."""
  path_obj = Path(image_path_str).resolve()

  # 1. Bắt lỗi file giả mạo hoặc file hỏng
  if not validate_image(path_obj):
    raise ValueError(
        f"Tệp '{path_obj.name}' bị hỏng hoặc không phải là hình ảnh hợp lệ!"
    )

  # 1b. Bắt lỗi description/caption rỗng — đây là quy định bắt buộc của đề bài
  if description is None or not description.strip():
    raise ValueError("description không được để trống")
  if caption is None or not caption.strip():
    raise ValueError("caption không được để trống")

  # 2. Sinh UUID ngẫu nhiên duy nhất
  file_id = str(uuid.uuid4())

  # 3. Đo chiều rộng và chiều cao thật (pixel)
  with Image.open(path_obj) as img:
    width, height = img.size
    pil_format = img.format  # ví dụ "JPEG", "PNG" - lấy từ chính nội dung ảnh

  # 4. Đo kích thước dung lượng thật (bytes) và lấy định dạng chuẩn
  file_size = path_obj.stat().st_size
  mime_type, _ = mimetypes.guess_type(path_obj)
  if mime_type is None and pil_format:
    # Nếu đoán theo đuôi file thất bại, dùng định dạng thật Pillow đọc được
    mime_type = f"image/{pil_format.lower()}"

  # 5. Thời điểm tạo chuẩn ISO 8601 có múi giờ
  created_at = datetime.now(timezone.utc).astimezone().isoformat()

  # 6. Tính checksum SHA-256
  checksum = compute_checksum(path_obj)

  metadata = {
      "file_id": file_id,
      "file_name": path_obj.name,
      "description": description,
      "caption": caption,
      "author": author,
      "size": file_size,
      "extension": path_obj.suffix.lower(),
      "mime_type": mime_type,
      "width": width,
      "height": height,
      "created_at": created_at,
      "checksum_algorithm": "sha256",
      "checksum": checksum,
      "tags": tags if tags is not None else ["lab01", "eduhub", "ca_nhan"],
  }
  return metadata


if __name__ == "__main__":
  from pathlib import Path as P
  folder = P("input")
  thanh_cong, that_bai = 0, 0
  for img_path in sorted(folder.iterdir()):
    print(f"\n===== {img_path.name} =====")
    try:
      meta = generate_metadata(
          str(img_path),
          description=f"Ảnh học liệu: {img_path.stem}",
          caption="Tư liệu học liệu EduHub",
      )
      thanh_cong += 1
      print(json.dumps(meta, ensure_ascii=False, indent=2))
    except Exception as e:
      that_bai += 1
      print(f"Lỗi: {e}")
  print(f"\nTổng kết: {thanh_cong} thành công, {that_bai} thất bại")