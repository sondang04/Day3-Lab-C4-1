# 🏫 BÀI LAB 3: CHATBOT VS REACT AGENT - TỪ Ý TƯỞNG ĐẾN THỰC THI

---

### 💡 1. LỜI NÓI ĐẦU & NỀN TẢNG LÝ THUYẾT (4 CẤP ĐỘ AI HỘI THOẠI)

Bài Lab giúp bạn hiểu rõ sự tiến hóa qua 4 cấp độ của hệ thống AI:

| Cấp độ | Loại hệ thống | Đặc điểm chính | Sự xuất hiện trong Bài Lab |
| :---: | :--- | :--- | :--- |
| **Cấp 1** | **Rule-Based Bot** | Khớp từ khóa if/else cố định, không có LLM | *Minh họa lịch sử* |
| **Cấp 2** | **LLM Chatbot** | Dùng LLM sinh text mượt, nhưng không gọi được Tool | **Chatbot Baseline** (Phần thực hành 1) |
| **Cấp 3** | **Reactive Agent** | Suy luận `Thought -> Action -> Observation` & gọi Tool | **ReAct Agent Loop** (Trọng tâm Bài Lab) |
| **Cấp 4** | **Autonomous Agent** | Tự rã mục tiêu (Planning), tự đánh giá & có Memory | 🎁 **Phần Bonus Nâng cao (+10%)** |

* 🤖 **Chatbot thông thường (Cấp 2)**: Giống như một **chuyên gia lý thuyết** — chỉ trả lời dựa trên kiến thức tĩnh có sẵn trong LLM, không thể tra cứu số liệu thực tế hay tự thực hiện thao tác.
* 🧠 **ReAct Agent (Cấp 3)**: Giống như một **trợ lý thực hành** — vừa biết suy nghĩ (**Thought**), vừa biết chủ động dùng công cụ (**Action**) như phần mềm tra cứu/tính toán, và quan sát kết quả (**Observation**) để giải quyết các bài toán thực tế.

---

### 📂 2. CẤU TRÚC THƯ MỤC DỰ ÁN

```text
📁 Day-3-Lab-Chatbot-vs-react-agent-E402/
├── 📄 README.md                 <-- 📘 Tổng quan bài Lab & Thang điểm
├── 📄 .env.example              <-- 🔑 File mẫu API Key
├── 📄 requirements.txt          <-- 📦 Thư viện cần cài đặt
│
├── 📁 config/                   <-- 🛠️ CẤU HÌNH & DỮ LIỆU
│   └── 📄 test_cases.json       <-- 🟢 [Role 1] Bộ đề 5 Test Cases thử thách AI
│
├── 📁 src/                      <-- 💻 MÃ NGUỒN PYTHON (BOILERPLATE)
│   ├── 📄 tools.py              <-- 🛠️ [Role 2] Khai báo các công cụ (Tools)
│   ├── 📄 prompts.py            <-- 🧠 [Role 3] ReAct System Prompt & Guardrails
│   ├── 📄 providers.py          <-- 🔌 Multi-Provider LLM Adapter (Gemini/OpenAI/Anthropic/Mock)
│   └── 📄 app.py                <-- 🚀 [Role 4] Core App: ReAct Loop + Giao diện Web (1 file)
│
└── 📁 docs/                     <-- 📚 TÀI LIỆU HƯỚNG DẪN & BÁO CÁO
    ├── 📄 CODELAB.md            <-- 🎓 [LMS Format] Hướng dẫn thực hành từng bước Codelab
    ├── 📄 PHAN_CONG_CONG_VIEC.md <-- 📋 [BẮT ĐẦU TẠI ĐÂY] Sổ tay thực hành & Checklist 5 Roles
    ├── 📄 DANH_SACH_DE_TAI.md    <-- 💡 Danh sách 10 chủ đề gợi ý
    └── 📄 trace_eval.md          <-- 📊 [Role 5] Báo cáo Log Trace & Đánh giá Agentic Fit
```

---

### ▶️ 2.1. CÁCH CHẠY DỰ ÁN

```bash
# 1. Cài môi trường
python -m venv .venv
.venv\Scripts\Activate.ps1        # Windows PowerShell (macOS/Linux: source .venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env            # rồi điền API key vào .env

# 2. Chạy bằng dòng lệnh (CLI)
python src/app.py                 # chạy test case #1
python src/app.py 11              # chạy test case #11 (bẫy Guardrail)

# 3. Chạy giao diện Web (khuyên dùng khi demo) — vẫn là file app.py đó
streamlit run src/app.py
```

> 📌 Cả CLI lẫn giao diện Web đều nằm trong **một file `src/app.py`**. File tự nhận biết
> đang được gọi bằng `python` hay bằng `streamlit run` (hàm `running_under_streamlit()`)
> để chọn chế độ tương ứng.

> 💡 **Chạy offline không cần API key**: đặt `LLM_PROVIDER=mock` trong `.env`
> (hoặc chọn `mock` ở sidebar của giao diện Web). Mock Provider mô phỏng đúng
> định dạng ReAct nên toàn bộ vòng lặp, tool và Guardrails vẫn chạy thật.

**6 tab của giao diện Web (`streamlit run src/app.py`)**

| Tab | Chức năng |
| :-- | :-- |
| ⚖️ **So sánh** | Chạy cùng 1 câu hỏi trên Chatbot Baseline và ReAct Agent, hiện bảng đối chiếu + tự chấm Rubric |
| 🤖 **ReAct Agent** | Hội thoại nhiều lượt, xem trace `Thought → Action → Observation` theo thời gian thực |
| 🧪 **Test Suite** | Chạy hàng loạt 15 test cases, đối chiếu `expected_tools`, xuất báo cáo Markdown cho `docs/trace_eval.md` |
| 👥 **Hồ sơ ứng viên** | Tra cứu & lọc 50 hồ sơ trong `config/candidates.json` |
| 🛠️ **Tool Playground** | Gọi thử từng tool độc lập (kiểm thử Tool contract trước khi gắn Agent) |
| 🧠 **Prompts & Guardrails** | Xem System Prompt và bảng 7 Guardrails đang hoạt động |

---

### ⏱️ 3. LỘ TRÌNH THỰC HÀNH (4 MỐC / 150 PHÚT)

```mermaid
timeline
    title ⏱️ KỊCH BẢN THỰC HÀNH LAB 3 (Tổng thời lượng: 150 phút)
    Mốc 1 (20 phút) : Định hình & Đánh giá Agentic Fit : Chọn bài toán & Lập bảng chấm điểm Scoring Matrix
    Mốc 2 (30 phút) : Baseline Chatbot & Khai báo Tool : Dựng Chatbot gốc & Viết Tool Specs + 5 Test Cases
    Mốc 3 (60 phút) : ReAct Loop & Safeguards : Viết Prompt, lắp Agent, cài Phanh Guardrails & Chạy Test
    Mốc 4 (40 phút) : Tương tác liên nhóm & Hybrid Pattern : Cross-Audit (Tấn công/Phòng thủ) & Vẽ Flowchart
```

---

### 💯 4. CƠ CHẾ CHẤM ĐIỂM  (SCORING RUBRIC)

| Tiêu chí                                |  Trọng số  | Mô tả chi tiết                                                                                                             | Bằng chứng kiểm tra (Artifacts)                                        |
| :---------------------------------------- | :-----------: | :---------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------ |
| **1. Agentic Fit & Test Design**    | **20%** | Phân tích đúng 4 tiêu chí Agentic Fit cho chủ đề tự chọn. Bộ test cases đủ góc cạnh (đơn giản, multi-step, edge cases). | Bảng chấm điểm (`docs/trace_eval.md`) + `config/test_cases.json`. |
| **2. ReAct Implementation & Tools** | **30%** | Tool description rõ ràng. Vòng lặp ReAct chạy đúng chuẩn `Thought -> Action -> Observation`.                         | Code trong `src/tools.py` + `src/app.py`.                              |
| **3. Guardrails & Observability**   | **20%** | Bắt được lỗi loop, có max iterations (Guardrail). Trích xuất được ít nhất 1 Trace log hoàn chỉnh.                     | File `src/prompts.py` + Log trong `docs/trace_eval.md`.                |
| **4. Inter-group Attack & Defense** | **20%** | Phản biện tốt khi gọi ngẫu nhiên hoặc cử 1 bạn đi chấm chéo (+10đ). Agent chống đỡ tốt / fallback chuẩn (+10đ).        | Biên bản Cross-Audit / Trả lời phản biện.                             |
| **5. Hybrid Decision Flowchart**    | **10%** | Sơ đồ thể hiện rõ khi nào đi Chatbot path, khi nào đi ReAct Agent path.                                             | Sơ đồ Flowchart (`docs/hybrid_flowchart.mermaid`).                   |
| 🎁 **BONUS: Autonomous Agent**     | **+10%**| Thử nghiệm tính năng Planning (tự chia nhỏ mục tiêu) hoặc Memory cho Agent (Cấp 4).                                  | Demo code trong `src/app.py` hoặc giải trình trong report.           |

---

> 🚀 **BẮT ĐẦU LÀM BÀI**:
> Vui lòng mở sổ tay thực hành 👉 **[PHAN_CONG_CONG_VIEC.md](file:///c:/Users/Admin/Documents/VinUni/LabCoachVin/LabKeyCoach/Day-3-Lab-Chatbot-vs-react-agent-E402/docs/PHAN_CONG_CONG_VIEC.md)** để xem phân vai và checklist công việc cụ thể cho từng thành viên!
