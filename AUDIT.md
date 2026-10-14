# Kiểm chứng: ZCleaner có làm đúng điều nó nói không?

Chính sách ở [PRIVACY.md](PRIVACY.md) hứa một số điều. Bảng dưới chỉ ra **đoạn code nào** liên quan đến từng lời hứa, để bạn tự đối chiếu. Các file trong `audit/` là bản trích **nguyên văn** từ mã nguồn thật; chúng không chạy độc lập và không đủ để xác minh toàn bộ mã nguồn hoặc bản ứng dụng đã đóng gói.

| Lời hứa | Nơi kiểm chứng |
|---|---|
| Không gửi tệp, tên tệp, đường dẫn đi đâu | `audit/telemetry.py`: tín hiệu thống kê chỉ gồm 5 trường ở hàm `payload()`; hàm gửi chỉ nhận **tên sự kiện** và không nhận được dữ liệu từ thư mục Zalo. `STATS_URL` mặc định để trống nên bản build không có endpoint thì **hoàn toàn offline** |
| Thống kê ẩn danh, tắt được, tắt xong thì xóa mã | `audit/telemetry.py`: mã ngẫu nhiên tạo bằng `secrets.token_hex` trên máy bạn và bị xóa khi tắt |
| Chỉ quét khi được phép, chỉ tìm đúng thư mục Zalo | `audit/discovery.py`: `candidate_bases` chỉ trả về thư mục thuộc Zalo, "never broad home or AppData roots" |
| Giao diện chỉ nói chuyện với máy của bạn (127.0.0.1) | `audit/server_safety_excerpt.py` dòng 214–222 và `audit/server_safety_excerpt.py` dòng 11–12 |
| Ứng dụng không tự xóa; chỉ xử lý thứ bạn chọn và xác nhận | `audit/server_safety_excerpt.py` dòng 67–76, `audit/server_safety_excerpt.py` dòng 99–132, `audit/server_safety_excerpt.py` dòng 135–166 |
| Tệp đã đổi từ lúc quét thì không bị xử lý nhầm | `audit/server_safety_excerpt.py` dòng 20–31 |
| Tệp được bảo vệ thì không dọn được | `audit/server_safety_excerpt.py` dòng 67–76 (`validated_selection` từ chối mọi tệp nằm trong danh sách bảo vệ, dòng 71–73); danh sách bảo vệ do dòng 34–35 và 53–64 quản lý |
| Ưu tiên Thùng rác, khôi phục được | `audit/server_safety_excerpt.py` dòng 79–96, `audit/server_safety_excerpt.py` dòng 174–211 |

## Chưa công khai

Giao diện, phần xử lý xem trước, gom ảnh gần giống và gợi ý dọn không nằm trong repo này. Bản chạy được phân phối dưới dạng ứng dụng đã build trong mục Releases.

## Ghi chú

Docstring của `audit/telemetry.py` nhắc tới `tests/test_telemetry.py`. File test đó thuộc phần chưa công khai.
