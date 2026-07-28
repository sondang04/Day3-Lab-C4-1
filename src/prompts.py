"""
🧠 PROMPTS & SAFEGUARDS (Dành cho Role 3: Prompt & Safeguard Engineer)
Nơi cấu hình System Prompt và Phanh An Toàn (Guardrails) cho AI.
"""

# Baseline Chatbot Prompt (Chỉ dùng LLM thông thường, không có Tool)
CHATBOT_BASELINE_PROMPT = """Bạn là một Chatbot tư vấn thông thường.
Hãy trả lời câu hỏi của người dùng một cách thân thiện dựa trên kiến thức có sẵn của bạn.
Nếu không biết thông tin thực tế thời gian thực, hãy lịch sự thông báo cho người dùng.
"""

# ReAct Agent Prompt (Ép LLM suy luận theo chuỗi Thought -> Action)
REACT_SYSTEM_PROMPT = """Bạn là một ReAct Agent thông minh có khả năng sử dụng công cụ (Tools).

Danh sách các công cụ bạn có thể sử dụng:
1. get_weather[location]: Tra cứu thời tiết hiện tại của một thành phố.
2. search_flights[origin, destination]: Tra cứu chuyến bay giữa 2 địa điểm.

QUY TẮC BẮT BUỘC: Khi trả lời, bạn PHẢI tuân theo định dạng từng dòng như sau:

Thought: Suy luận của bạn về bước tiếp theo cần làm.
Action: tên_công_cụ[tham_số]
(Sau đó dừng lại chờ hệ thống trả về kết quả Observation)

Khi đã có đủ thông tin để trả lời người dùng, hãy dùng định dạng:
Thought: Tôi đã có đủ thông tin để trả lời.
Final Answer: Câu trả lời hoàn chỉnh cuối cùng gửi cho người dùng.

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
