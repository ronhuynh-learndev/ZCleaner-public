# Quyền riêng tư của ZCleaner

**Dữ liệu của bạn ở trên máy bạn.**

ZCleaner là công cụ độc lập để xem và dọn các tệp Zalo lưu trên thiết bị. Ứng dụng không yêu cầu đăng nhập Zalo.

## 01. Chỉ quét khi được phép

Mỗi lần mở app, bạn chọn phạm vi, đánh dấu đồng ý và bấm “Quét tệp Zalo”. Trước thao tác đó, app không tự dò thư mục hay đọc nội dung tệp Zalo; nếu bạn chủ động chọn thư mục, app chỉ kiểm tra thư mục được chọn có hợp lệ. Bạn có thể quét các thư mục Zalo ứng dụng tự tìm cùng thư mục bổ sung, hoặc chỉ thư mục đã chọn. Có thể hủy trong lúc lập danh mục; kết quả quét dở sẽ bị bỏ. Danh mục và bản xem trước chỉ mở trong phiên đã cho phép.

## 02. Không gửi tệp đi

Tên, dung lượng, định dạng, nội dung xem trước và danh sách chọn được xử lý trong ứng dụng trên máy. Giao diện chỉ kết nối với dịch vụ cục bộ tại 127.0.0.1; phiên bản này không có tài khoản hay quảng cáo. Việc đếm người dùng ẩn danh được nêu riêng ở mục 05.

## 03. Bạn kiểm soát việc dọn

Ứng dụng không tự xóa tệp sau khi quét. Danh sách dọn hiển thị cả tệp đang nằm ngoài bộ lọc. Bạn có thể bảo vệ tệp; các đường dẫn cùng trỏ tới tệp đó sẽ không thể dọn cho đến khi bỏ bảo vệ. Chỉ các đường dẫn bạn chọn và xác nhận mới được xử lý. Bạn có thể chuyển vào Thùng rác để khôi phục, hoặc chọn xóa vĩnh viễn với cảnh báo riêng. Xóa vĩnh viễn không thể hoàn tác trong ứng dụng và không thể khôi phục từ Thùng rác; bản sao lưu ngoài ứng dụng có thể vẫn còn.

## 04. Dữ liệu lưu cục bộ

Đường dẫn của các tệp đã chọn và được bảo vệ, kết quả lần quét gần nhất (tên, đường dẫn, dung lượng và ngày của tệp, để lần sau mở lại không cần quét), bản xem trước tạm thời và nhật ký dọn tệp được lưu trong thư mục dữ liệu ZaloCleaner của tài khoản máy này; bản xem trước tạm được giữ dưới khoảng 500 MB. Nút “Xóa dữ liệu tạm” trong Cài đặt xóa lựa chọn, kết quả quét đã lưu và cache do app tạo; danh sách bảo vệ, nhật ký dọn và tệp gốc vẫn được giữ. Nếu bạn mở bản sao bằng ứng dụng khác, ứng dụng đó có thể xử lý tệp theo chính sách riêng.

## 05. Thống kê ẩn danh

Khi bản bạn cài có bật tính năng này, app gửi một tín hiệu nhỏ qua kết nối bảo mật (HTTPS) mỗi lần mở app, một lần khi bạn quét xong lần đầu và một lần khi bạn dọn tệp lần đầu. Tín hiệu chỉ gồm: mã ngẫu nhiên tạo trên máy bạn, phiên bản app, hệ điều hành (ví dụ macOS 15) và loại chip. Không bao giờ gửi tên tệp, đường dẫn, số lượng, dung lượng, tên cuộc trò chuyện hay nội dung từ thư mục Zalo. Tính năng được bật sẵn; bạn có thể tắt ở màn hình bắt đầu hoặc trong Cài đặt, khi đó mã ngẫu nhiên bị xóa khỏi máy. Nếu mục này không hiện công tắc trong ứng dụng, bản của bạn không gửi gì.

---

Tệp đã dọn có thể không còn hiển thị trong cuộc trò chuyện Zalo. Một số định dạng mã hoá hoặc hỏng không thể xem trước; ứng dụng sẽ cho biết khi không nhận diện được.
