"""
🧠 PROMPTS & SAFEGUARDS (Dành cho Role 3: Prompt & Safeguard Engineer)
Nơi cấu hình System Prompt và Phanh An Toàn (Guardrails) cho AI.
"""

# Baseline Chatbot Prompt (Chỉ dùng LLM thông thường, không có Tool)
# Đề tài: Trợ Lý Sàng Lọc Hồ Sơ Tuyển sinh cho chương trình Đào tạo nhân tài AI thực chiến
CHATBOT_BASELINE_PROMPT = """Bạn là một Chatbot tư vấn tuyển sinh cho chương trình Đào tạo nhân tài AI thực chiến.

## VỀ CHƯƠNG TRÌNH:
- Chương trình tuyển sinh ứng viên cho khóa học AI thực chiến
- Quy trình gồm: Đăng ký -> Sàng lọc CV -> Thi đầu vào -> Xét tuyển -> Thông báo kết quả
- Tiêu chí sàng lọc: GPA tối thiểu 7.0, kỹ năng lập trình Python, kinh nghiệm ít nhất 1 năm

## NGUYÊN TẮC TRẢ LỜI:
1. TRẢ LỜI CÁC CÂU HỎI LÝ THUYẾT: Về quy trình tuyển sinh, tiêu chí, thời hạn, v.v.
2. KHÔNG BỊA ĐẶT DỮ LIỆU: Không tự ý xác nhận điểm thi, trạng thái hồ sơ, hay kết quả tuyển sinh của bất kỳ ai
3. THỪA NHẬN GIỚI HẠN: Nếu câu hỏi đòi hỏi dữ liệu thực tế (điểm thi, trạng thái cụ thể), hãy thành thật:
   "Tôi không có quyền truy cập vào hệ thống dữ liệu tuyển sinh. Để biết kết quả cụ thể, bạn vui lòng liên hệ phòng tuyển sinh."
4. KHÔNG CAM KẾT: Không hứa hẹn kết quả tuyển sinh hay thời gian cụ thể

## VÍ DỤ CÂU TRẢ LỜI ĐÚNG:
- Câu hỏi: "Chương trình AI thực chiến yêu cầu gì?"
  → Trả lời được (dựa trên kiến thức có sẵn về tiêu chí)

- Câu hỏi: "Tôi đăng ký tháng trước, khi nào có kết quả?"
  → Thừa nhận giới hạn, không bịa đặt

## LƯU Ý QUAN TRỌNG:
- Baseline KHÔNG gọi được Tool, chỉ trả lời dựa trên kiến thức LLM có sẵn
- Câu trả lời có thể nghe mượt nhưng KHÔNG có bằng chứng thực tế
"""

# ReAct Agent Prompt (Ép LLM suy luận theo chuỗi Thought -> Action)
# Đề tài: Trợ Lý Sàng Lọc Hồ Sơ Tuyển sinh cho chương trình Đào tạo nhân tài AI thực chiến
REACT_SYSTEM_PROMPT = """Bạn là một ReAct Agent thông minh hỗ trợ quy trình tuyển sinh cho chương trình Đào tạo nhân tài AI thực chiến.

## DANH SÁCH CÔNG CỤ (TOOLS):
Bạn có quyền truy cập vào các công cụ sau. Mỗi công cụ có input/output cụ thể:

1. **register_applicant**[{name: str, email: str, phone: str, program: str, resume_url: str}]
   → Đăng ký thông tin ứng viên mới vào hệ thống
   → Trả về: applicant_id nếu thành công, hoặc thông báo lỗi chi tiết

2. **screen_resume_ai_program**[{applicant_id: str, criteria: dict}]
   → Sàng lọc CV của ứng viên theo tiêu chí chương trình AI
   → criteria mẫu: {min_gpa: float, required_skills: list, years_exp: int}
   → Trả về: Kết quả pass/fail kèm lý do

3. **send_entry_exam_invitation**[{applicant_ids: list, exam_date: str, exam_location: str}]
   → Gửi email mời ứng viên đã pass screening tham gia thi đầu vào
   → Trả về: Danh sách gửi thành công/thất bại

4. **get_exam_score**[{applicant_id: str, exam_session: str}]
   → Lấy điểm bài thi đầu vào của ứng viên
   → Trả về: Điểm số hoặc thông báo chưa có điểm

5. **rank_and_admit_candidates**[{applicant_ids: list, cutoff_score: float}]
   → Xếp hạng ứng viên theo điểm thi và chọn trúng tuyển theo điểm chuẩn
   → Trả về: Danh sách admitted/rejected kèm điểm cụ thể

6. **send_admission_notice**[{applicant_ids: list, admission_status: dict}]
   → Gửi thông báo kết quả tuyển sinh đến ứng viên
   → admission_status: {applicant_id: "admitted"|"rejected"|"waitlist"}
   → Trả về: Danh sách gửi thành công/thất bại

## QUY TRÌNH TUYỂN SINH CHUẨN:
1. register_applicant (Đăng ký)
2. screen_resume_ai_program (Sàng lọc CV)
3. send_entry_exam_invitation (Mời thi)
4. get_exam_score (Lấy điểm)
5. rank_and_admit_candidates (Xét tuyển)
6. send_admission_notice (Thông báo)

## QUY TẮC BẮT BUỘC - ĐỊNH DẠNG TRẢ LỜI:

### Khi cần gọi Tool:
Thought: Suy luận của bạn về bước tiếp theo cần làm. Giải thích TẠI SAO cần dùng tool này.
Action: tên_công_cụ[tham_số_json]
(Sau đó dừng lại chờ hệ thống trả về kết quả Observation)

### Khi đã có đủ thông tin:
Thought: Tôi đã có đủ thông tin để trả lời dựa trên kết quả từ [tên tool].
Final Answer: Câu trả lời hoàn chỉnh cuối cùng gửi cho người dùng.

## NGUYÊN TẮC XỬ LÝ LỖI:
- Nếu Tool trả về "LỖI: ..." → Đọc kỹ thông báo, xử lý theo hướng dẫn trong lỗi
- Nếu cần thông tin từ bước trước → Thông báo cho người dùng biết cần hoàn thành bước trước
- Không bịa đặt kết quả - chỉ trả lời dựa trên Observation thực tế

## VÍ DỤ MINH HỌA:

**Câu hỏi**: "Ứng viên ABC đã trúng tuyển chưa?"

Thought: Cần tra cứu điểm thi và trạng thái tuyển sinh của ứng viên ABC.
Action: get_exam_score[{"applicant_id": "ABC123", "exam_session": "2026-S1"}]
Observation: Điểm thi: 8.5/10

Thought: Điểm 8.5 cao hơn điểm chuẩn (7.0). Cần kiểm tra đã xét tuyển chưa.
Final Answer: Ứng viên ABC có điểm thi 8.5/10, cao hơn điểm chuẩn 7.0. Hồ sơ đã được xét tuyển thành công.

BẮT ĐẦU:
"""

# 🛡️ GUARDRAILS CONFIGURATION (PHANH AN TOÀN)
MAX_ITERATIONS = 3  # Giới hạn tối đa 3 vòng lặp Thought-Action để tránh lặp vô tận
TIMEOUT_SECONDS = 10  # Timeout cho mỗi lần gọi tool


# ═══════════════════════════════════════════════════════════════════════════════
# 📋 FAILURE MODES ANALYSIS - ROLE 3: PROMPT ENGINEER
# Mốc 1: Xác định các trường hợp tool có thể bị lỗi
# ═══════════════════════════════════════════════════════════════════════════════

"""
Phân tích các Failure Modes cho 6 tools trong hệ thống Tuyển sinh AI Program:
1. register_applicant      - Đăng ký thông tin ứng viên
2. screen_resume_ai_program - Sàng lọc CV theo tiêu chí
3. send_entry_exam_invitation - Gửi email mời thi đầu vào
4. get_exam_score          - Lấy điểm thi đầu vào
5. rank_and_admit_candidates - Xét tuyển theo điểm
6. send_admission_notice   - Gửi thông báo kết quả
"""

TOOL_FAILURE_MODES = """
# ═══════════════════════════════════════════════════════════════════════════════
# BẢNG PHÂN TÍCH FAILURE MODES CHO 6 TOOLS TUYỂN SINH
# ═══════════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────────┐
│ TOOL 1: register_applicant (Đăng ký thông tin ứng viên)                    │
├─────────────────────────────────────────────────────────────────────────────┤
│ INPUT: {name: str, email: str, phone: str, program: str, resume_url: str}  │
├─────────────────────────────────────────────────────────────────────────────┤
│ FAILURE MODES:                                                            │
│  • Lỗi validation: Email sai format → "LỖI: Email không hợp lệ"           │
│  • Lỗi validation: Số điện thoại sai format → "LỖI: Số điện thoại..."    │
│  • Lỗi nghiệp vụ: Email đã tồn tại → "LỖI: Ứng viên đã đăng ký"         │
│  • Lỗi nghiệp vụ: Chương trình không tồn tại → "LỖI: Chương trình..."    │
│  • Lỗi hệ thống: Database timeout → "LỖI: Không thể lưu, thử lại sau"    │
│  • LỖI CẦN AGENT XỬ LÝ: Trả về thông báo lỗi cụ thể để hướng dẫn sửa    │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ TOOL 2: screen_resume_ai_program (Sàng lọc CV theo tiêu chí AI Program)  │
├─────────────────────────────────────────────────────────────────────────────┤
│ INPUT: {applicant_id: str, criteria: dict}                                 │
│ CRITERIA MẪU: {min_gpa: float, required_skills: list, years_exp: int}     │
├─────────────────────────────────────────────────────────────────────────────┤
│ FAILURE MODES:                                                            │
│  • Lỗi input: applicant_id rỗng/null → "LỖI: Thiếu mã ứng viên"          │
│  • Lỗi input: criteria sai schema → "LỖI: Định dạng tiêu chí không..."    │
│  • Lỗi nghiệp vụ: Ứng viên chưa đăng ký → "LỖI: Không tìm thấy ứng..." │
│  • Lỗi nghiệp vụ: CV chưa upload → "LỖI: CV chưa được nộp"              │
│  • Lỗi hệ thống: AI screening service timeout → "LỖI: Dịch vụ sàng lọc..."│
│  • LỖI CẦN AGENT XỬ LÝ: Thông báo thiếu bước trước đó cần thực hiện    │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ TOOL 3: send_entry_exam_invitation (Gửi email mời đăng ký thi đầu vào)   │
├─────────────────────────────────────────────────────────────────────────────┤
│ INPUT: {applicant_ids: list, exam_date: str, exam_location: str}          │
├─────────────────────────────────────────────────────────────────────────────┤
│ FAILURE MODES:                                                            │
│  • Lỗi validation: exam_date sai format → "LỖI: Ngày thi không hợp lệ"   │
│  • Lỗi validation: Ngày thi đã qua → "LỖI: Ngày thi phải trong tương lai"│
│  • Lỗi input: applicant_ids rỗng → "LỖI: Danh sách ứng viên trống"        │
│  • Lỗi nghiệp vụ: Ứng viên chưa pass screening → "LỖI: Ứng viên chưa..." │
│  • Lỗi hệ thống: Email service down → "LỖI: Không gửi được email"        │
│  • Lỗi hệ thống: Một số email thất bại → "CẢNH BÁO: 2/10 email thất bại"│
│  • LỖI CẦN AGENT XỬ LÝ: Liệt kê cụ thể ứng viên nào thất bại           │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ TOOL 4: get_exam_score (Lấy điểm bài thi đầu vào)                        │
├─────────────────────────────────────────────────────────────────────────────┤
│ INPUT: {applicant_id: str, exam_session: str}                             │
├─────────────────────────────────────────────────────────────────────────────┤
│ FAILURE MODES:                                                            │
│  • Lỗi input: applicant_id không tồn tại → "LỖI: Không tìm thấy ứng viên"│
│  • Lỗi input: exam_session không tồn tại → "LỖI: Đợt thi không tồn tại"  │
│  • Lỗi nghiệp vụ: Ứng viên chưa thi → "LỖI: Chưa có điểm thi"           │
│  • Lỗi nghiệp vụ: Chưa nhận được điểm → "LỖI: Điểm chưa được cập nhật"  │
│  • Lỗi hệ thống: Exam system timeout → "LỖI: Không truy cập được điểm"   │
│  • LỖI CẦN AGENT XỬ LÝ: Hỏi người dùng xác nhận lại thông tin          │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ TOOL 5: rank_and_admit_candidates (Xét tuyển theo điểm)                   │
├─────────────────────────────────────────────────────────────────────────────┤
│ INPUT: {applicant_ids: list, cutoff_score: float}                          │
├─────────────────────────────────────────────────────────────────────────────┤
│ FAILURE MODES:                                                            │
│  • Lỗi input: cutoff_score không hợp lệ → "LỖI: Điểm chuẩn phải là số"  │
│  • Lỗi input: cutoff_score < 0 hoặc > 10 → "LỖI: Điểm chuẩn ngoài..."    │
│  • Lỗi input: applicant_ids rỗng → "LỖI: Danh sách trống"                  │
│  • Lỗi nghiệp vụ: Một số ứng viên chưa có điểm → "CẢNH BÁO: 3 ứng..."    │
│  • Lỗi nghiệp vụ: Không ai đạt điểm chuẩn → "THÔNG BÁO: Không ai trúng..."│
│  • Lỗi hệ thống: Database update fail → "LỖI: Không lưu được kết quả"     │
│  • LỖI CẦN AGENT XỬ LÝ: Trả về danh sách đạt/không đạt kèm điểm cụ thể │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ TOOL 6: send_admission_notice (Gửi thông báo kết quả tuyển sinh)          │
├─────────────────────────────────────────────────────────────────────────────┤
│ INPUT: {applicant_ids: list, admission_status: dict}                       │
│ STATUS: {applicant_id: "admitted"|"rejected"|"waitlist"}                   │
├─────────────────────────────────────────────────────────────────────────────┤
│ FAILURE MODES:                                                            │
│  • Lỗi input: admission_status rỗng → "LỖI: Danh sách kết quả trống"      │
│  • Lỗi input: Status không hợp lệ → "LỖI: Trạng thái phải là admitted/.."│
│  • Lỗi nghiệp vụ: Ứng viên chưa được xét tuyển → "LỖI: Chưa xét tuyển"  │
│  • Lỗi hệ thống: Email service down → "LỖI: Không gửi được thông báo"    │
│  • Lỗi hệ thống: Một số email thất bại → "CẢNH BÁO: 2/10 email thất bại"│
│  • LỖI CẦN AGENT XỬ LÝ: Trả về chi tiết ai thành công, ai thất bại      │
└─────────────────────────────────────────────────────────────────────────────┘

# ═══════════════════════════════════════════════════════════════════════════════
# TỔNG HỢP: CÁC FAILURE PATTERNS CHUNG & HƯỚNG DẪN XỬ LÝ CHO AGENT
# ═══════════════════════════════════════════════════════════════════════════════

PATTERN_ERROR_HANDLING = {
    "VALIDATION_ERROR": {
        "description": "Dữ liệu đầu vào không đúng định dạng",
        "agent_action": "Yêu cầu người dùng nhập lại với format đúng, cung cấp ví dụ mẫu"
    },
    "NOT_FOUND_ERROR": {
        "description": "Không tìm thấy dữ liệu liên quan",
        "agent_action": "Kiểm tra xem các bước trước đó đã hoàn thành chưa, thông báo cho người dùng"
    },
    "DUPLICATE_ERROR": {
        "description": "Dữ liệu đã tồn tại hoặc bị trùng lặp",
        "agent_action": "Thông báo rõ ràng dữ liệu nào đã tồn tại, đề xuất hành động tiếp theo"
    },
    "TIMEOUT_ERROR": {
        "description": "Dịch vụ không phản hồi trong thời gian cho phép",
        "agent_action": "Thử lại sau 5 giây, nếu vẫn lỗi thì thông báo và gợi ý thử lại sau"
    },
    "PARTIAL_FAILURE": {
        "description": "Một phần thao tác thành công, một phần thất bại",
        "agent_action": "Liệt kê cụ thể thành công/thất bại, không dừng hoàn toàn"
    }
}

SAFE_FALLBACK_MESSAGE = "Xin lỗi, tôi gặp sự cố khi xử lý yêu cầu này. Vui lòng kiểm tra lại thông tin hoặc thử lại sau."
"""
