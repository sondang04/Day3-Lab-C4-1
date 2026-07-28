# 📊 BÁO CÁO GIÁM SÁT & ĐÁNH GIÁ (OBSERVABILITY TRACE LOGS)
*Dành cho Role 5: Observability & Reviewer*

---

## 🎯 1. BẢNG CHẤM ĐIỂM AGENTIC FIT (SCORING MATRIX)

| Tiêu chí | Điểm (1-5) | Lý do đánh giá |
| :--- | :---: | :--- |
| 🧠 **Multi-step Reasoning** | `5/5` | Agent phải suy luận qua nhiều bước liên tiếp: trích xuất thông tin từ CV → đối chiếu với tiêu chí đầu vào chương trình → xác định ứng viên có đủ điều kiện dự thi đánh giá năng lực hay không → tổng hợp điểm CV + điểm thi → đưa ra khuyến nghị tuyển sinh cuối cùng. |
| 🛠️ **Tool Interaction** | `5/5` | Cần gọi nhiều tool khác nhau: `parse_cv()` (đọc & trích xuất dữ liệu từ hồ sơ), `score_cv()` (chấm điểm hồ sơ theo rubric), `check_test_schedule()` / `book_aptitude_test()` (tra cứu, xếp lịch thi), `get_test_result()` (lấy điểm thi đánh giá năng lực), `calculate_final_score()` (tính điểm xét tuyển tổng hợp). Không thể trả lời chính xác nếu chỉ dựa vào kiến thức tĩnh của LLM. |
| 🔀 **Dynamic Decision** | `5/5` | Kết quả của bước trước quyết định trực tiếp hành động tiếp theo: nếu điểm CV dưới ngưỡng tối thiểu → Agent từ chối ngay, không cần gọi tool xếp lịch thi; nếu đạt ngưỡng → mới tiến hành mời thi và tra cứu kết quả; nếu điểm thi biên giới (borderline) → đề xuất phỏng vấn bổ sung thay vì kết luận ngay. |
| ⏳ **Long Horizon** | `4/5` | Quy trình xét tuyển trải qua nhiều giai đoạn nối tiếp trong cùng một phiên làm việc (nộp hồ sơ → xét CV → (có thể) mời thi → chấm & tổng hợp điểm → ra quyết định), dài hơn hẳn một tác vụ tra cứu đơn lẻ, nhưng vẫn nằm trong một luồng hội thoại/phiên xử lý duy nhất chứ chưa đòi hỏi Agent tự vận hành qua nhiều ngày (đó là lý do chưa chấm tuyệt đối 5/5). |
| **TỔNG ĐIỂM FIT** | **19/20** | **KẾT LUẬN: BÀI TOÁN RẤT NÊN DÙNG REACT AGENT** (và là ứng viên tốt để thử nghiệm mở rộng lên Autonomous Agent Cấp 4 ở phần Bonus — ví dụ thêm Memory để nhớ hồ sơ ứng viên qua nhiều lượt hỏi, hoặc Planning để tự phân rã quy trình xét tuyển nhiều bước). |

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