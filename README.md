1. cài đặt 
    Yêu cầu python 3.10+
        nhập lệnh bash:
            python -m pip install Pillow

2. Hướng dẫn sử dụng
2.1. Xử lý một ảnh đơn lẻ
    Chương trình sẽ tự động trích xuất thông tin kỹ thuật, sinh UUID, tính mã SHA-256, lưu ảnh vào data/, tạo link file:// và ghi file <file_id>.json cùng metadata_index.json ngay tại thư mục gọi lệnh:   Bashpython main.py ./input/img01.jpg
2.2. Xử lý cả thư mục ảnhXử lý toàn bộ các file trong thư mục đầu vào. 
    Nếu gặp file lỗi, chương trình ghi nhận lỗi, tiếp tục xử lý các file khác và in bảng tổng kết số lượng thành công/thất bại:   Bashpython main.py ./input/
2.3. Kiểm tra tính toàn vẹn file ảnh (verify_file)
    Kiểm tra đối chiếu mã SHA-256 giữa file ảnh thực tế trong data/ với trường checksum lưu trong file JSON:   Bashpython main.py --verify <file_id>.json
    Kết quả hiển thị:
    [MATCH]: Checksum trùng khớp hoàn toàn, ảnh toàn vẹn.
    [MISMATCH]: Checksum sai lệch (ảnh đã bị can thiệp/chỉnh sửa nội dung).
    [UNVERIFIED]: Không tìm thấy ảnh hoặc đường dẫn không truy cập được.
2.4. Tìm kiếm ảnh trong Metadata (Mở rộng C)
    Tìm kiếm theo từ khóa trên các trường: all, file_id, file_name, caption, tags, mime_type:  
        Bash# Tìm kiếm từ khóa xuất hiện ở bất kỳ trường nào
            python main.py --search "eduhub" all    

# Tìm kiếm theo caption
python main.py --search "Không có chú thích" caption

# Tìm kiếm theo mime_type
python main.py --search "image/png" mime_type

# Tìm kiếm theo file_name
python main.py --search "anh_the" file_name

3. Quy ước Data Link và Tái tạo liên kết
    Dạng liên kết: data_url sử dụng giao thức URI file:/// trỏ tới đường dẫn tuyệt đối của file ảnh trên máy tính thực thi.   
    Cách truy cập:
        Mở trực tiếp bằng trình duyệt Web (Chrome, Edge, Firefox) bằng cách copy chuỗi URI file:///... dán vào thanh địa chỉ.Khi đem bài sang máy tính khác chấm, do đường dẫn tuyệt đối thay đổi, người chấm có thể tái lập metadata hoặc chạy lại lệnh quét trên thư mục input/ để sinh lại link tương thích với máy chấm.    
4. Mô tả các trường Metadata bổ sung
    Ngoài 7 trường bắt buộc theo quy định (file_id, file_name, description, path, size, caption, data_url), chương trình bổ sung đầy đủ các trường kỹ thuật và toàn vẹn dữ liệu:
       1.extension: Phần mở rộng chuẩn của file (ví dụ: .jpg, .png).   
       2.mime_type: Kiểu MIME xác định loại nội dung nhị phân (ví dụ: image/jpeg).   
       3.width: Chiều rộng thực tế của ảnh (pixel).   
       4.height: Chiều cao thực tế của ảnh (pixel). 
       5.created_at: Thời gian tạo metadata định dạng chuẩn ISO 8601 kèm múi giờ (ví dụ: +07:00).   
       6.storage_type: Phương thức lưu trữ (local).
       7.checksum_algorithm: Thuật toán băm kiểm tra toàn vẹn (sha256).
       8.checksum: Giá trị băm SHA-256 tính từ nội dung nhị phân của ảnh.
       9.tags: Danh sách nhãn phân loại học liệu (dạng mảng JSON).
---
    