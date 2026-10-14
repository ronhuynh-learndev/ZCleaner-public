# ZCleaner

Công cụ **độc lập** giúp xem trước và dọn các tệp Zalo lưu trên máy Mac. Không cần đăng nhập Zalo. Không phải sản phẩm của Zalo.

**Dữ liệu của bạn ở trên máy bạn**: ZCleaner không gửi tên tệp, đường dẫn hay nội dung đi đâu. Ứng dụng không tự xóa gì; bạn chọn và xác nhận từng lần, ưu tiên chuyển vào Thùng rác.

## Tải ứng dụng

**Phiên bản hiện tại: ZCleaner Version 1.0.0 cho macOS.** Tải tại [Release v1.0.0](https://github.com/ronhuynh-learndev/ZCleaner-public/releases/tag/v1.0.0): có bản Apple Silicon và Intel. Chọn đúng bản cho chip của máy và đối chiếu SHA-256 trong file `.sha256` đi kèm. Bản Intel đã được thử dưới Rosetta; chưa thử trên Mac Intel vật lý. Ứng dụng chưa được Apple notarize.

## Kiểm chứng, không cần tin lời

Repo này công khai một phần mã nguồn để bạn đối chiếu các lời hứa về quyền riêng tư:

- [PRIVACY.md](PRIVACY.md): chính sách quyền riêng tư đầy đủ.
- [AUDIT.md](AUDIT.md): mỗi lời hứa được thực thi ở **đoạn code nào**, để bạn tự đọc và kiểm tra.
- [`audit/`](audit/): mã nguồn trích nguyên văn (thống kê ẩn danh, dò thư mục Zalo, các hàm quyết định cái gì được phép xóa).

Giao diện và các phần xử lý khác chưa công khai.
Vì mã nguồn và bản build đầy đủ chưa công khai, các đoạn trích này không đủ để kiểm chứng độc lập toàn bộ ứng dụng đã phát hành.

## English

ZCleaner Version 1.0.0 is an independent macOS tool to preview and clean Zalo files stored on your computer. It never uploads file names, paths or contents. This repository publishes only the parts that let you verify that claim (`audit/`, `AUDIT.md`, `PRIVACY.md`); the UI and remaining logic are not published. Not affiliated with Zalo.

## Giấy phép

[PolyForm Noncommercial License 1.0.0](LICENSE): được đọc, học và dùng cho mục đích **phi thương mại**. Không được bán, đóng gói lại hay dùng để làm sản phẩm thương mại khi chưa có sự đồng ý bằng văn bản.

Required Notice: Copyright 2026 Blossom Creative

Muốn dùng thương mại hoặc hợp tác? Liên hệ Ron Huỳnh (Blossom Creative):

- Email: ronhuynh.work@gmail.com
- LinkedIn: https://www.linkedin.com/in/ronhuynh-work/
