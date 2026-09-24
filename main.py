import argparse
import json
import sys
from pathlib import Path

from src.metadata_engine import generate_metadata
from src.storage_engine import save_image_local, verify_file

# Hàm cập nhật chỉ mục (Mở rộng E)
INDEX_FILE = "metadata_index.json"

def update_metadata_index(file_id, file_name, json_path):
    """Mở rộng E: Lưu chỉ mục metadata."""
    index_path = Path.cwd() / INDEX_FILE
    index_data = []
    
    if index_path.exists():
        try:
            with open(index_path, 'r', encoding='utf-8') as f:
                index_data = json.load(f)
        except json.JSONDecodeError:
            pass # Bỏ qua nếu file đang lỗi hoặc trống
            
    # Nối thêm thông tin ảnh mới vào danh sách
    index_data.append({
        "file_id": file_id,
        "file_name": file_name,
        "metadata_path": str(json_path)
    })
    
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, ensure_ascii=False, indent=4)

# Hàm tìm kiếm ảnh (Mở rộng C)
def search_images(keyword):
    """Mở rộng C: Tìm kiếm ảnh theo từ khóa."""
    index_path = Path.cwd() / INDEX_FILE
    if not index_path.exists():
        print("Chưa có cơ sở dữ liệu chỉ mục để tìm kiếm.")
        return

    with open(index_path, 'r', encoding='utf-8') as f:
        index_data = json.load(f)

    print(f"\n--- KẾT QUẢ TÌM KIẾM CHO: '{keyword}' ---")
    keyword = keyword.lower()
    found = False

    for entry in index_data:
        meta_path = Path(entry["metadata_path"])
        if meta_path.exists():
            with open(meta_path, 'r', encoding='utf-8') as mf:
                meta = json.load(mf)
            
            # Gom các trường cần tìm kiếm thành một chuỗi duy nhất để kiểm tra
            tags_str = " ".join(meta.get('tags', []))
            search_text = f"{meta.get('file_id', '')} {meta.get('file_name', '')} {meta.get('caption', '')} {tags_str} {meta.get('mime_type', '')}".lower()
            
            if keyword in search_text:
                print(f"- File ID: {meta.get('file_id')}")
                print(f"  Data URL: {meta.get('data_url')}\n")
                found = True
                
    if not found:
        print("Không có kết quả phù hợp.")

def process_single_image(file_path, args):
    """Hàm xử lý một file ảnh đơn lẻ, ráp nối các module."""
    path_obj = Path(file_path)

    if not path_obj.is_file():
        raise FileNotFoundError(f"Không tìm thấy file: {file_path}")

    # Chuẩn bị tags từ tham số dòng lệnh (vd: -t hoc-lieu,phong-may)
    tags_list = args.tags.split(',') if args.tags else None

    # Bước 1+2: Gọi TV1 (metadata_engine) - validate ảnh THẬT, sinh UUID,
    # tính toàn bộ thuộc tính kỹ thuật (size, width, height, checksum...)
    meta = generate_metadata(
        str(path_obj),
        description=args.description,
        caption=args.caption,
        tags=tags_list,
    )

    # Bước 3+4: Gọi TV2 (storage_engine) - copy ảnh THẬT vào data/,
    # sinh path/data_url/checksum thật (không còn "mock_sha256_hash" nữa)
    storage_info = save_image_local(path_obj, meta["file_id"], meta["extension"])

    # Bước 5: Gộp metadata kỹ thuật (TV1) + thông tin lưu trữ (TV2) làm 1 dict duy nhất
    final_metadata = {**meta, **storage_info}

    # Bước 6: Ghi file JSON tại thư mục làm việc hiện hành (Path.cwd()) - quy tắc bắt buộc
    current_cwd = Path.cwd()
    json_path = current_cwd / f"{meta['file_id']}.json"

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(final_metadata, f, ensure_ascii=False, indent=4)

    update_metadata_index(meta["file_id"], path_obj.name, json_path)

    # In log theo yêu cầu bắt buộc (file_id, path, data_url, json_path)
    print(f"\n[THÀNH CÔNG] Xử lý xong: {path_obj.name}")
    print(f" - File ID: {meta['file_id']}")
    print(f" - Nơi lưu ảnh: {storage_info['path']}")
    print(f" - Data URL: {storage_info['data_url']}")
    print(f" - File JSON: {json_path}")

    return True

def main():
    parser = argparse.ArgumentParser(description="EduHub Image Ingestion System")
    # Thêm nargs='?' để input_path không bắt buộc khi dùng lệnh search/verify
    parser.add_argument("input_path", nargs='?', help="Đường dẫn đến 1 file ảnh hoặc 1 thư mục chứa ảnh")
    parser.add_argument("-d", "--description", type=str, default="Không có mô tả", help="Mô tả ảnh")
    parser.add_argument("-c", "--caption", type=str, default="Không có chú thích", help="Chú thích ảnh")
    parser.add_argument("-t", "--tags", type=str, default="", help="Các thẻ tag, cách nhau bởi dấu phẩy")

    # Mở rộng C: Thêm tham số tìm kiếm
    parser.add_argument("-s", "--search", type=str, help="Tìm kiếm ảnh theo từ khóa")

    # Thêm tham số verify - gọi verify_file() từ storage_engine.py
    parser.add_argument("-v", "--verify", type=str, help="Đường dẫn file JSON cần kiểm tra toàn vẹn (checksum)")

    args = parser.parse_args()

    # Nếu người dùng chạy lệnh tìm kiếm, thực thi hàm và kết thúc luôn
    if args.search:
        search_images(args.search)
        sys.exit(0)

    # Nếu người dùng chạy lệnh verify, thực thi hàm và kết thúc luôn
    if args.verify:
        print(verify_file(args.verify))
        sys.exit(0)

    # Chặn lỗi nếu không nhập thư mục và cũng không tìm kiếm/verify
    if not args.input_path:
        print("Lỗi: Vui lòng cung cấp đường dẫn ảnh/thư mục.")
        sys.exit(1)

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
