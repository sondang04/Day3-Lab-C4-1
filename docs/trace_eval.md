# 📊 BÁO CÁO GIÁM SÁT & ĐÁNH GIÁ (OBSERVABILITY TRACE LOGS)
*Dành cho Role 5: Observability & Reviewer*

---

## 🎯 1. BẢNG CHẤM ĐIỂM AGENTIC FIT (SCORING MATRIX)

| Tiêu chí | Điểm (1-5) | Lý do đánh giá |
| :--- | :---: | :--- |
| 🧠 **Multi-step Reasoning** | `5/5` | Agent phải suy luận qua một chuỗi nghiệp vụ nhiều lớp: lọc ứng viên đạt ngưỡng → xếp hạng theo 4 tiêu chí → xác thực hồ sơ của (các) ứng viên top đầu → chỉ soạn thư mời phỏng vấn nếu hồ sơ hợp lệ → dừng lại chờ phê duyệt trước khi gửi email chính thức. Không phải một câu trả lời một bước mà là cả một quy trình ra quyết định tuyển sinh. |
| 🛠️ **Tool Interaction** | `5/5` | Cần phối hợp 8 tool với vai trò khác nhau: đọc dữ liệu (`get_candidate`), lọc (`filter_candidates`), xếp hạng đa tiêu chí (`rank_candidates`), kiểm tra gian lận cá nhân (`verify_candidate`) và trên toàn bộ 50 hồ sơ (`detect_duplicates`), soạn nháp (`draft_interview_email`, `schedule_interview`), và hành động gửi thật (`send_email`). LLM thuần không thể tự tra cứu, tính toán hay gửi email. |
| 🔀 **Dynamic Decision** | `5/5` | Kết quả mỗi bước rẽ nhánh hành động tiếp theo rõ rệt: `verify_candidate`/`detect_duplicates` phát hiện nghi vấn → Agent phải loại ứng viên khỏi danh sách mời, **không** gọi `draft_interview_email`; ngược lại hồ sơ sạch mới soạn thư; và quan trọng nhất — `draft_interview_email`/`schedule_interview` luôn ở trạng thái "Chờ phê duyệt", Agent **tuyệt đối không được tự ý gọi `send_email`** cho đến khi nhận được xác nhận rõ ràng từ người dùng. Đây là ví dụ Dynamic Decision gắn liền với Guardrail rất chuẩn. |
| ⏳ **Long Horizon** | `5/5` | `detect_duplicates` yêu cầu quét toàn bộ 50 hồ sơ để so sánh chéo (IP, thư giới thiệu, SĐT/CCCD trùng lặp) — một tác vụ ở cấp độ tập dữ liệu chứ không phải 1 ứng viên đơn lẻ. Cộng với quy trình có điểm dừng chờ con người phê duyệt (draft → chờ duyệt → gửi), toàn bộ chuỗi kéo dài qua nhiều lượt tương tác chứ không kết thúc trong 1-2 bước. |
| **TỔNG ĐIỂM FIT** | **20/20** | **KẾT LUẬN: BÀI TOÁN CỰC KỲ PHÙ HỢP DÙNG REACT AGENT.** Đặc biệt, cơ chế "DRAFT → chờ phê duyệt → SEND" là ví dụ mẫu mực cho phần **Guardrails & Safeguards** của bài Lab: Agent được phép suy luận và chuẩn bị hành động, nhưng hành động có hệ quả không thể hoàn tác (gửi email thật) bắt buộc phải có con người xác nhận trước. |

---

## 🔍 2. SO SÁNH PHẢN HỒI (TEST CASE #3)

**Câu hỏi**: *"Thời tiết ở Hà Nội hôm nay thế nào và tôi nên mặc gì đi chơi?"*

### 🤖 Chatbot Baseline:
* **Phản hồi**: *"Tôi không có truy cập Internet thời gian thực nên không biết thời tiết hôm nay ở Hà Nội."*
* **Nhận xét**: An toàn nhưng không giải quyết được nhu cầu thực tế của người dùng.

### 🧠 ReAct Agent:
* **Thought 1**: Cần tra cứu thời tiết Hà Nội.
* **Action 1**: `get_weather['Hà Nội']`
* **Observation 1**: `Thời tiết Hà Nội: 28°C, Nắng nhẹ, Độ ẩm 65%.`
* **Thought 2**: Đã có thông tin 28°C nắng nhẹ, đưa ra lời khuyên trang phục.
* **Final Answer**: *"Thời tiết Hà Nội hôm nay 28°C, nắng nhẹ. Bạn nên mặc quần áo thoáng mát!"*
* **Nhận xét**: Hoàn thành xuất sắc nhiệm vụ nhờ sự kết hợp giữa suy luận và công cụ.