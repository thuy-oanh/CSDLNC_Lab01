import argparse
import json
import sys
from pathlib import Path

# Giả sử file của Thành viên 1 là metadata_engine.py và của bạn là storage_engine.py nằm trong thư mục src/
# from src.metadata_engine import validate_and_extract_metadata, build_final_metadata
# from src.storage_engine import save_image_local

def process_single_image(file_path, args):
    """Hàm xử lý một file ảnh đơn lẻ, ráp nối các module."""
    path_obj = Path(file_path)
    
    if not path_obj.is_file():
        raise FileNotFoundError(f"Không tìm thấy file: {file_path}")

    # Bước 1: Gọi TV1 để validate ảnh, lấy thông số cơ bản và sinh UUID (file_id)
    # is_valid, base_meta, file_id = validate_and_extract_metadata(path_obj)
    # if not is_valid:
    #     raise ValueError(f"File {file_path} không hợp lệ hoặc bị hỏng.")

    # Mô phỏng file_id từ TV1 để chạy demo:
    import uuid
    file_id = str(uuid.uuid4())
    extension = path_obj.suffix

    # Bước 2: Gọi TV2 (Hàm của BẠN) để copy ảnh an toàn và sinh data_url
    # storage_info = save_image_local(path_obj, file_id, extension)
    
    # Mô phỏng kết quả trả về từ hàm của bạn:
    storage_info = {
        "path": f"data/{file_id}{extension}",
        "data_url": f"file://.../data/{file_id}{extension}",
        "storage_type": "local",
        "checksum": "mock_sha256_hash",
        "checksum_algorithm": "SHA-256"
    }

    # Bước 3: Gộp thông tin từ CLI (description, caption, tags)
    user_inputs = {
        "description": args.description,
        "caption": args.caption,
        "tags": args.tags.split(',') if args.tags else []
    }

    # Bước 4: Gọi TV1 lần cuối để đóng gói dict JSON hoàn chỉnh
    # final_metadata = build_final_metadata(base_meta, storage_info, user_inputs)
    
    # Mô phỏng dict cuối cùng:
    final_metadata = {
        "file_id": file_id,
        "file_name": path_obj.name,
        **user_inputs,
        **storage_info
    }

    # Bước 5: Ghi file JSON tại thư mục làm việc hiện hành (Quy tắc bắt buộc)
    current_cwd = Path.cwd()
    json_path = current_cwd / f"{file_id}.json"
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(final_metadata, f, ensure_ascii=False, indent=4)

    # In log theo yêu cầu bắt buộc (file_id, path, data_url, json_path)
    print(f"\n[THÀNH CÔNG] Xử lý xong: {path_obj.name}")
    print(f" - File ID: {file_id}")
    print(f" - Nơi lưu ảnh: {storage_info['path']}")
    print(f" - Data URL: {storage_info['data_url']}")
    print(f" - File JSON: {json_path}")
    
    return True

def main():
    parser = argparse.ArgumentParser(description="EduHub Image Ingestion System")
    parser.add_argument("input_path", help="Đường dẫn đến 1 file ảnh hoặc 1 thư mục chứa ảnh")
    parser.add_argument("-d", "--description", type=str, default="Không có mô tả", help="Mô tả ảnh")
    parser.add_argument("-c", "--caption", type=str, default="Không có chú thích", help="Chú thích ảnh")
    parser.add_argument("-t", "--tags", type=str, default="", help="Các thẻ tag, cách nhau bởi dấu phẩy")
    
    args = parser.parse_args()
    input_path = Path(args.input_path)

    success_count = 0
    fail_count = 0
    skipped_count = 0

    if input_path.is_file():
        try:
            process_single_image(input_path, args)
            success_count += 1
        except Exception as e:
            print(f"[LỖI] Xử lý {input_path.name} thất bại: {e}")
            fail_count += 1
            
    elif input_path.is_dir():
        print(f"Bắt đầu quét thư mục: {input_path}")
        for file_item in input_path.iterdir():
            if file_item.is_file():
                try:
                    # Chạy try/except từng file để lỗi 1 file không làm sập chương trình
                    process_single_image(file_item, args)
                    success_count += 1
                except Exception as e:
                    print(f"[LỖI] Xử lý {file_item.name} thất bại: {e}")
                    fail_count += 1
            else:
                skipped_count += 1
    else:
        print("Đường dẫn đầu vào không tồn tại.")
        sys.exit(1)

    # Thống kê cuối cùng
    print("\n--- TỔNG KẾT ---")
    print(f"Thành công: {success_count}")
    print(f"Thất bại: {fail_count}")
    print(f"Bỏ qua: {skipped_count}")

if __name__ == "__main__":
    main()