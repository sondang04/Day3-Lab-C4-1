"""
🛠️ TOOL REGISTRY & SCHEMAS - ĐỀ TÀI: TUYỂN SINH CHƯƠNG TRÌNH THỰC CHIẾN AI VINUNI
Dành cho Role 2: Tool & Spec Engineer (Chu Thành Dũng)

Quy trình tuyển sinh 5 bước:
1. register_applicant: Đăng ký thí sinh (Nộp thông tin & CV).
2. screen_resume_ai_program: Sàng lọc CV theo tiêu chí tuyển sinh AI VinUni.
3. send_entry_exam_invitation: Gửi email đăng ký bài thi Đánh Giá Năng Lực đầu vào (thang điểm 100).
4. get_exam_score: Tra cứu điểm thi Đánh Giá Năng Lực đầu vào của ứng viên.
5. rank_and_admit_candidates: Xét tuyển & Xếp hạng điểm từ cao xuống thấp (Tối đa 500 học viên/khóa).
6. send_admission_notice: Gửi email thông báo kết quả trúng tuyển chính thức.
"""

def register_applicant(fullname: str, email: str, phone: str, cv_link: str) -> str:
    """
    Bước 1: Đăng ký thí sinh mới tham gia Chương trình Thực chiến AI VinUni (Nộp thông tin & CV).
    
    Args:
        fullname (str): Họ và tên thí sinh (Ví dụ: 'Nguyễn Văn A')
        email (str): Địa chỉ Email (Ví dụ: 'anuyen@gmail.com')
        phone (str): Số điện thoại (Ví dụ: '0987654321')
        cv_link (str): Đường dẫn file CV (Ví dụ: 'drive.google.com/cv_a.pdf')
        
    Returns:
        str: Thông báo đăng ký thành công kèm Mã hồ sơ tuyển sinh (VIN-AI-2026-xxx)
    """
    if not fullname or not email or "@" not in email:
        return f"LỖI: Thông tin đăng ký không hợp lệ. Vui lòng cung cấp đầy đủ Họ tên và Email hợp lệ."
        
    import random
    app_id = f"VIN-AI-2026-{random.randint(100, 999)}"
    return (
        f"✅ ĐĂNG KÝ HỒ SƠ THÀNH CÔNG!\n"
        f"- Mã hồ sơ thí sinh: {app_id}\n"
        f"- Thí sinh: {fullname}\n"
        f"- Email: {email} | SĐT: {phone}\n"
        f"- Link CV: {cv_link}\n"
        f"- Trạng thái: Hồ sơ đã chuyển sang Bước 2 (Sàng lọc CV)."
    )


def screen_resume_ai_program(applicant_id_or_name: str) -> str:
    """
    Bước 2: Sàng lọc CV của thí sinh theo các tiêu chí của Chương trình Thực chiến AI VinUni 
    (Nền tảng Toán/Lập trình, Tư duy tư duy thuật toán, Động lực học tập).
    
    Args:
        applicant_id_or_name (str): Mã hồ sơ hoặc Họ tên thí sinh (Ví dụ: 'Nguyễn Văn A', 'VIN-AI-2026-101')
        
    Returns:
        str: Kết quả đánh giá CV, trạng thái ĐẠT / KHÔNG ĐẠT vòng CV
    """
    a_lower = applicant_id_or_name.lower()
    if "nguyễn văn a" in a_lower or "a" in a_lower or "101" in a_lower:
        return (
            f"📄 KẾT QUẢ SÀNG LỌC CV THÍ SINH: Nguyễn Văn A (Mã: VIN-AI-2026-101)\n"
            f"- Đánh giá nền tảng: Đã học Python, Nắm vững Đại số tuyến tính & Xác suất thống kê.\n"
            f"- Tiêu chí AI Readiness: 88/100 (Phù hợp với chương trình thực chiến).\n"
            f"- ĐÁNH GIÁ: ĐẠT VÒNG CV.\n"
            f"- Khuyến nghị: Đủ điều kiện nhận email đăng ký bài thi Đánh Giá Năng Lực đầu vào."
        )
    elif "trần thị b" in a_lower or "b" in a_lower or "102" in a_lower:
        return (
            f"📄 KẾT QUẢ SÀNG LỌC CV THÍ SINH: Trần Thị B (Mã: VIN-AI-2026-102)\n"
            f"- Đánh giá nền tảng: Chưa có nền tảng lập trình và toán tin.\n"
            f"- Tiêu chí AI Readiness: 42/100.\n"
            f"- ĐÁNH GIÁ: KHÔNG ĐẠT VÒNG CV."
        )
    else:
        return f"LỖI: Không tìm thấy hồ sơ của thí sinh '{applicant_id_or_name}' để sàng lọc CV."


def send_entry_exam_invitation(applicant_id_or_name: str) -> str:
    """
    Bước 3a: Gửi email đăng ký & lịch thi bài Đánh Giá Năng Lực đầu vào (thang điểm 100) cho ứng viên ĐẠT vòng CV.
    
    Args:
        applicant_id_or_name (str): Mã hồ sơ hoặc Họ tên thí sinh (Ví dụ: 'Nguyễn Văn A')
        
    Returns:
        str: Xác nhận đã gửi email lịch thi ĐGNL kèm mã dự thi
    """
    a_lower = applicant_id_or_name.lower()
    if "trần thị b" in a_lower:
        return f"THẤT BẠI: Thí sinh {applicant_id_or_name} chưa ĐẠT vòng CV, không thể gửi email thi ĐGNL."
    elif "nguyễn văn a" in a_lower or "a" in a_lower:
        return (
            f"📧 ĐÃ GỬI EMAIL MỜI THI ĐÁNH GIÁ NĂNG LỰC ĐẦU VÀO!\n"
            f"- Thí sinh: {applicant_id_or_name}\n"
            f"- Bài thi: Đánh Giá Năng Lực AI VinUni (Thang điểm: 100 điểm).\n"
            f"- Thời gian thi: 09:00 - 10:30 Chủ Nhật tuần này.\n"
            f"- Link làm bài thi Online: https://exam.vinuni.edu.vn/ai-entrance-test\n"
            f"- Trạng thái: Đã gửi mã dự thi vào email thí sinh."
        )
    else:
        return f"LỖI: Không tìm thấy ứng viên '{applicant_id_or_name}' để gửi email thi ĐGNL."


def get_exam_score(applicant_id_or_name: str) -> str:
    """
    Bước 3b: Tra cứu điểm bài thi Đánh Giá Năng Lực đầu vào của ứng viên (Thang điểm 100).
    
    Args:
        applicant_id_or_name (str): Mã hồ sơ hoặc Họ tên thí sinh (Ví dụ: 'Nguyễn Văn A')
        
    Returns:
        str: Điểm thi ĐGNL chính thức (thang điểm 100) và chi tiết các phần thi
    """
    a_lower = applicant_id_or_name.lower()
    if "nguyễn văn a" in a_lower or "a" in a_lower:
        return (
            f"📊 ĐIỂM THI ĐÁNH GIÁ NĂNG LỰC THÍ SINH: Nguyễn Văn A\n"
            f"- Điểm Tư duy Lập trình: 35/40\n"
            f"- Điểm Toán & Logic AI: 30/30\n"
            f"- Điểm Tiếng Anh & Đọc hiểu Paper: 25/30\n"
            f"- TỔNG ĐIỂM BÀI THI: 90 / 100 ĐIỂM."
        )
    elif "lê văn c" in a_lower or "c" in a_lower:
        return (
            f"📊 ĐIỂM THI ĐÁNH GIÁ NĂNG LỰC THÍ SINH: Lê Văn C\n"
            f"- TỔNG ĐIỂM BÀI THI: 82 / 100 ĐIỂM."
        )
    elif "trần thị b" in a_lower or "b" in a_lower:
        return f"THẤT BẠI: Thí sinh {applicant_id_or_name} chưa làm bài thi ĐGNL đầu vào."
    else:
        return f"LỖI: Không tìm thấy dữ liệu điểm thi của thí sinh '{applicant_id_or_name}'."


def rank_and_admit_candidates(batch_id: str = "Khoá 1 - 2026", limit: int = 500) -> str:
    """
    Bước 4: Xét tuyển & Xếp hạng danh sách thí sinh theo điểm thi ĐGNL từ cao xuống thấp, áp dụng chỉ tiêu tối đa 500 học viên/khóa.
    
    Args:
        batch_id (str): Tên khóa học (Mặc định: 'Khóa 1 - 2026')
        limit (int): Chỉ tiêu tuyển sinh tối đa (Mặc định: 500 học viên)
        
    Returns:
        str: Bảng xếp hạng điểm thi ĐGNL và danh sách trúng tuyển trong chỉ tiêu 500 học viên
    """
    return (
        f"🏆 BẢNG XẾP HẠNG VÀ XÉT TUYỂN CHƯƠNG TRÌNH THỰC CHIẾN AI VINUNI ({batch_id})\n"
        f"Chỉ tiêu tối đa: {limit} học viên/khóa.\n"
        f"1. Hạng 1 (Top 1): Nguyễn Văn A | Điểm ĐGNL: 90/100 -> TRÚNG TUYỂN CHÍNH THỨC (Suất Học bổng 100%)\n"
        f"2. Hạng 2 (Top 2): Lê Văn C     | Điểm ĐGNL: 82/100 -> TRÚNG TUYỂN CHÍNH THỨC\n"
        f"...\n"
        f"500. Hạng 500    : Pham Văn D   | Điểm ĐGNL: 65/100 -> TRÚNG TUYỂN CHÍNH THỨC (Điểm sàn trúng tuyển: 65/100)\n"
        f"501. Hạng 501    : Hoàng Văn E  | Điểm ĐGNL: 64/100 -> DANH SÁCH CHỜ (Dự bị)"
    )


def send_admission_notice(applicant_id_or_name: str) -> str:
    """
    Bước 5: Gửi email xác nhận trúng tuyển chính thức cho ứng viên đạt yêu cầu xét tuyển (Top 500).
    
    Args:
        applicant_id_or_name (str): Mã hồ sơ hoặc Họ tên thí sinh (Ví dụ: 'Nguyễn Văn A')
        
    Returns:
        str: Kết quả gửi email thư nhập học (Admission Offer Letter) và mã xác nhận nhập học
    """
    a_lower = applicant_id_or_name.lower()
    if "nguyễn văn a" in a_lower or "a" in a_lower:
        return (
            f"🎉 ĐÃ GỬI EMAIL XÁC NHẬN TRÚNG TUYỂN THÀNH CÔNG!\n"
            f"- Thí sinh: Nguyễn Văn A (Mã HS: VIN-AI-2026-101)\n"
            f"- Chương trình: Thực chiến AI VinUni (Khóa 1 - 2026)\n"
            f"- Trạng thái: TRÚNG TUYỂN CHÍNH THỨC (Xếp hạng 1/500).\n"
            f"- Nội dung Email: Thư mời nhập học (Admission Offer Letter) + Hướng dẫn làm thủ tục nhập học trước ngày 15/08/2026.\n"
            f"- Mã nhập học: VIN-OFFER-9981."
        )
    elif "trần thị b" in a_lower or "b" in a_lower:
        return f"THẤT BẠI: Thí sinh {applicant_id_or_name} không nằm trong danh sách trúng tuyển top 500."
    else:
        return f"LỖI: Không tìm thấy ứng viên '{applicant_id_or_name}' để gửi thông báo trúng tuyển."


# ---------------------------------------------------------
# DANH SÁCH CÁC TOOL ĐƯỢC ĐĂNG KÝ CHO REACT AGENT SỬ DỤNG
# ---------------------------------------------------------
AVAILABLE_TOOLS = {
    "register_applicant": register_applicant,
    "screen_resume_ai_program": screen_resume_ai_program,
    "send_entry_exam_invitation": send_entry_exam_invitation,
    "get_exam_score": get_exam_score,
    "rank_and_admit_candidates": rank_and_admit_candidates,
    "send_admission_notice": send_admission_notice,
}

if __name__ == "__main__":
    print("🧪 KIỂM THỬ ĐỘC LẬP 6 TOOLS TUYỂN SINH THỰC CHIẾN AI VINUNI...")
    print(register_applicant("Nguyễn Văn A", "anuyen@gmail.com", "0987654321", "drive.google.com/cv_a.pdf"))
    print("\n" + screen_resume_ai_program("Nguyễn Văn A"))
    print("\n" + send_entry_exam_invitation("Nguyễn Văn A"))
    print("\n" + get_exam_score("Nguyễn Văn A"))
    print("\n" + rank_and_admit_candidates("Khóa 1 - 2026", 500))
    print("\n" + send_admission_notice("Nguyễn Văn A"))
    print("\n✅ TẤT CẢ 6 TOOLS ĐÃ TEST THÀNH CÔNG!")
