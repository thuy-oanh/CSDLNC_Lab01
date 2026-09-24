TRẢ LỜI CÂU HỎI
1.Metadata là gì? Trong bài làm, trường nào mô tả nội dung, trường nào mô tả dữ liệu
kỹ thuật?

Metadata là dữ liệu về dữ liệu, không phải bản thân ảnh, mà là thông tin mô tả, phân loại, định vị và đảm bảo toàn vẹn cho ảnh đó.

Mô tả nội dung (người dùng nhập): description, caption, tags, author, file_name.
Mô tả kỹ thuật (tự động sinh trong generate_metadata() và save_image_local()): file_id, size, extension, mime_type, width, height, created_at, checksum_algorithm, checksum, storage_type, path, data_url.

2.So sánh lưu ảnh trong CSDL với tách ảnh ra File/Object Storage. Mỗi cách phù hợp
với tình huống nào?

BLOB trong CSDL: ảnh nằm ngay trong bảng dưới dạng nhị phân.
    +Ưu điểm: toàn vẹn giao dịch (transaction), backup 1 lần đồng bộ. 
    +Nhược điểm: DB phình to nhanh, đọc/ghi chậm, khó dùng CDN.
    + Phù hợp: BLOB hợp hệ thống nhỏ cần transaction chặt (hồ sơ pháp lý...)
Tách ảnh ra storage, DB/JSON chỉ giữ metadata (cách bài làm chọn): ảnh phục vụ trực tiếp qua path/URL, storage scale riêng rẻ hơn, DB/metadata nhẹ, dễ index. 
    +Nhược điểm: phải tự lo đồng bộ ảnh–metadata.
    +Phù hợp: tách rời hợp hệ thống nhiều ảnh, cần tốc độ đọc cao — như EduHub.

3.File Storage, Object Storage và Database Storage khác nhau như thế nào?

File Storage: tổ chức theo cây thư mục, truy cập bằng path (bài dùng cách này: thư mục data/).
Object Storage (MinIO/S3): namespace phẳng theo bucket + object key, truy cập qua HTTP API, hỗ trợ presigned URL, scale ngang rất lớn.
Database Storage: dữ liệu quản lý trong DBMS, có SQL/NoSQL, transaction, index, ACID.

4.file_id có vai trò gì? Vì sao dùng UUID thay cho tên file gốc?

file_id (sinh bằng uuid.uuid4()) là khóa duy nhất liên kết ảnh vật lý (data/<file_id>.ext), file JSON (<file_id>.json) và mục chỉ mục tìm kiếm. Dùng UUID vì tên file gốc dễ trùng — chính bài test có case test_trung_ten/hoc_lieu.jpg để kiểm tra hai ảnh khác nhau cùng tên gốc; 
UUID đảm bảo không ghi đè, xác suất trùng gần như bằng 0, và không lộ tên file gốc khi public URL.

5.path khác data_url như thế nào? Vì sao object key chưa phải là URL truy cập?

path là vị trí lưu trên hệ lưu trữ, trong bài là đường dẫn tương đối data/<file_id>.ext.
data_url là liên kết dùng để truy cập được nội dung, trong bài là file:// và thêm đường dẫn tuyệt đối (dest_path.absolute()).
Object key chỉ là "địa chỉ nội bộ" trong bucket, muốn thành URL truy cập được cần ghép thêm endpoint/scheme, và nếu bucket private còn cần chữ ký (presigned URL) — nếu không có các bước đó, phần mềm ngoài không lấy được ảnh chỉ từ object key.

6.Checksum dùng để làm gì? verify_file() xử lí thế nào khi ảnh bị sửa, bị xóa hoặc
không thể truy cập?

Checksum (SHA-256, tính trên dữ liệu nhị phân ảnh) dùng để phát hiện ảnh có bị sửa đổi/hỏng sau khi lưu hay không. verify_file() trả về đúng 3 trạng thái:

Không tìm thấy JSON → "Không thể kiểm tra: Không tìm thấy file metadata JSON."
Ảnh không tồn tại/mất quyền → "Không thể kiểm tra: Ảnh gốc không tồn tại hoặc mất quyền truy cập."
So khớp SHA-256 → "Khớp: Dữ liệu ảnh toàn vẹn." hoặc "Không khớp: Ảnh đã bị thay đổi sau khi lưu."

7.MinIO khác một thư mục thông thường ở những điểm nào? Presigned URL là gì và
điều gì xảy ra khi hết hạn?

MinIO là object storage tương thích S3 API: namespace phẳng (bucket + key), truy cập qua HTTP thay vì filesystem path, hỗ trợ versioning, policy phân quyền theo bucket, presigned URL, scale phân tán nhiều node — điều mà một thư mục thường trên 1 máy không có.
Presigned URL là URL có chữ ký, cấp quyền truy cập tạm thời vào object private trong thời gian giới hạn mà không cần chia sẻ access key/secret key. Khi hết hạn, URL bị từ chối (403) dù object vẫn còn trong bucket — phải cấp lại URL mới.

8.Nếu quản lí 10 triệu ảnh, cần thay đổi gì về tổ chức metadata, chỉ mục tìm kiếm, phân
quyền, sao lưu và tính nhất quán giữa ảnh với metadata?

Metadata: hàng triệu file .json rời trong 1 thư mục phẳng sẽ rất chậm/giới hạn OS → cần metadata DB thật, hoặc phân tầng thư mục theo prefix UUID nếu vẫn dùng file.
Chỉ mục tìm kiếm: metadata_index.json + duyệt tuyến tính (linear scan) như hàm search_images() hiện tại không kham nổi quy mô này → cần search engine (Elasticsearch/OpenSearch) hoặc index DB trên các trường tra cứu.
Phân quyền: access control chi tiết theo bucket/prefix, presigned URL thời hạn ngắn, audit log.
Sao lưu: backup tự động, incremental, replicate đa vùng, bật versioning trên object storage.
Tính nhất quán ảnh–metadata: cần cơ chế đối chiếu định kỳ (reconciliation job) phát hiện ảnh "mồ côi" (không có metadata) hoặc metadata "mồ côi" (thiếu ảnh), dùng pattern transaction-outbox/queue để đảm bảo eventual consistency.

MÔ TẢ 2 PHẦN MỞ RỘNG

C – Tìm kiếm ảnh: tìm trong metadata theo file_id, file_name, caption, tags và
mime_type; trả về định danh và data link phù hợp.

Cài đặt bằng hàm search_images(keyword) trong main.py, gọi qua tham số dòng lệnh -s/--search.
Cách hoạt động: hàm đọc metadata_index.json để lấy danh sách metadata_path của tất cả ảnh đã xử lý, sau đó mở từng file <file_id>.json tương ứng. Với mỗi ảnh, chương trình gộp các trường file_id, file_name, caption, tags và mime_type thành một chuỗi văn bản duy nhất (không phân biệt hoa thường), rồi kiểm tra từ khóa người dùng nhập có xuất hiện trong chuỗi đó không (keyword in search_text). Nếu khớp, in ra file_id và data_url để có thể truy cập ảnh ngay.

Ví dụ chạy:
    python main.py -s "phong-may"
    python main.py -s "hoc_lieu"
Nếu chưa có metadata_index.json (chưa xử lý ảnh nào), hoặc không có kết quả khớp, chương trình báo rõ ràng thay vì lỗi ngầm.

E – Chỉ mục metadata: tạo metadata_index.json trong thư mục hiện hành, gồm
file_id, file_name và metadata_path trỏ tới <file_id>.json. Thêm ảnh mới không
làm mất các mục cũ.

Cài đặt bằng hàm update_metadata_index() trong main.py, được gọi tự động sau mỗi lần ghi file <file_id>.json thành công trong process_single_image().

Cách hoạt động: hàm đọc metadata_index.json hiện có tại thư mục làm việc (Path.cwd()) nếu tồn tại — nếu file lỗi hoặc trống thì bỏ qua chứ không làm crash chương trình. Sau đó, nối thêm một bản ghi mới gồm file_id, file_name và metadata_path (đường dẫn tới file JSON chi tiết vừa tạo) vào danh sách, rồi ghi đè lại toàn bộ file dưới dạng mảng JSON (UTF-8, ensure_ascii=False). Vì luôn đọc trước rồi nối thêm (append), việc xử lý ảnh mới không làm mất các mục đã có từ trước — đúng theo yêu cầu đề bài.

metadata_index.json chính là "chỉ mục" trung tâm mà chức năng tìm kiếm (C) sử dụng để biết cần mở những file JSON nào, nên hai phần mở rộng này hoạt động phối hợp trực tiếp với nhau
