"""
🛠️ TOOL REGISTRY & SCHEMAS - ĐỀ TÀI: TRỢ LÝ TƯ VẤN & XÉT TUYỂN ĐẠI HỌC
Dành cho Role 2: Tool & Spec Engineer (Chu Thành Dũng)

Danh sách 6 công cụ (Tools):
1. get_admission_criteria: Tra cứu tiêu chuẩn & phương thức xét tuyển của ngành học.
2. lookup_student_profile: Tra cứu hồ sơ học tập thí sinh (điểm THPTQG, học bạ, ĐGNL, thư giới thiệu).
3. evaluate_admission_eligibility: Đánh giá khả năng trúng tuyển theo từng phương thức xét tuyển.
4. rank_applicant_profiles: Xếp hạng hồ sơ các thí sinh đăng ký vào ngành học.
5. check_counseling_slots: Kiểm tra ca tư vấn tuyển sinh 1-1 / phỏng vấn xét tuyển còn trống.
6. schedule_admission_counseling: Đặt lịch tư vấn tuyển sinh hoặc phỏng vấn xét tuyển cho thí sinh.
"""

def get_admission_criteria(major: str) -> str:
    """
    Tra cứu tiêu chuẩn, chỉ tiêu và các phương thức xét tuyển của một ngành học đại học.
    
    Args:
        position/major (str): Tên ngành học (Ví dụ: 'Khoa học Máy tính', 'Quản trị Kinh doanh', 'Trí tuệ Nhân tạo')
        
    Returns:
        str: Chi tiết tiêu chí xét tuyển (Điểm sàn THPTQG, Học bạ, ĐGNL, Thư giới thiệu)
    """
    m_lower = major.lower()
    if "máy tính" in m_lower or "khmt" in m_lower or "it" in m_lower or "trí tuệ nhân tạo" in m_lower:
        return (
            f"📋 TIÊU CHÍ XÉT TUYỂN NGHÀNH: Khoa học Máy tính / AI (Năm 2026)\n"
            f"- Phương thức 1 (Điểm THPTQG): Điểm sàn >= 26.5 điểm (Tổ hợp A00, A01, D07).\n"
            f"- Phương thức 2 (Xét Học bạ): Tổng điểm 3 môn tổ hợp lớp 12 >= 27.5 điểm + Hạnh kiểm Tốt.\n"
            f"- Phương thức 3 (Thi ĐGNL): Điểm ĐGNL ĐHQG >= 850/1200 điểm.\n"
            f"- Phương thức 4 (Xét tuyển kết hợp): Học bạ >= 25 điểm + Thư giới thiệu từ Giáo viên + Phỏng vấn."
        )
    elif "quản trị" in m_lower or "kinh doanh" in m_lower or "qtkd" in m_lower:
        return (
            f"📋 TIÊU CHÍ XÉT TUYỂN NGÀNH: Quản trị Kinh doanh (Năm 2026)\n"
            f"- Phương thức 1 (Điểm THPTQG): Điểm sàn >= 24.5 điểm (Tổ hợp A01, D01, D07).\n"
            f"- Phương thức 2 (Xét Học bạ): Điểm trung bình 3 năm THPT >= 8.0/10.\n"
            f"- Phương thức 3 (Thi ĐGNL): Điểm ĐGNL >= 750/1200 điểm.\n"
            f"- Phương thức 4 (Xét tuyển thẳng): Chứng chỉ IELTS >= 6.5 + Thư giới thiệu cá nhân."
        )
    else:
        return f"LỖI: Không tìm thấy thông tin tiêu chí xét tuyển cho ngành '{major}' trong hệ thống đại học."


def lookup_student_profile(student_id_or_name: str) -> str:
    """
    Tra cứu hồ sơ học tập và thành tích của thí sinh (Điểm THPTQG, Học bạ, ĐGNL, Thư giới thiệu).
    
    Args:
        student_id_or_name (str): Mã số báo danh hoặc Họ tên thí sinh (Ví dụ: 'Nguyễn Văn A', 'TS-2026-01')
        
    Returns:
        str: Chi tiết bảng điểm THPTQG, điểm học bạ, kết quả thi ĐGNL và trạng thái thư giới thiệu
    """
    s_lower = student_id_or_name.lower()
    if "nguyễn văn a" in s_lower or "a" in s_lower or "01" in s_lower:
        return (
            f"🎓 HỒ SƠ THÍ SINH: Nguyễn Văn A (Mã HS: TS-2026-01)\n"
            f"- Điểm THPTQG (Tổ hợp A00): Toán 9.2, Lý 8.8, Hóa 8.5 (Tổng: 26.5 điểm).\n"
            f"- Điểm Học bạ lớp 12: Toán 9.5, Lý 9.0, Hóa 9.2 (Trung bình: 9.23/10).\n"
            f"- Điểm Thi Đánh giá Năng lực (ĐGNL): 880 / 1200 điểm.\n"
            f"- Thư giới thiệu (Recommendation Letter): Đã nộp (Được xác nhận bởi Hiệu trưởng THPT Chuyên).\n"
            f"- Chứng chỉ Tiếng Anh: IELTS 7.0."
        )
    elif "trần thị b" in s_lower or "b" in s_lower or "02" in s_lower:
        return (
            f"🎓 HỒ SƠ THÍ SINH: Trần Thị B (Mã HS: TS-2026-02)\n"
            f"- Điểm THPTQG (Tổ hợp D01): Toán 7.5, Văn 8.0, Anh 8.2 (Tổng: 23.7 điểm).\n"
            f"- Điểm Học bạ lớp 12: Trung bình 8.1/10.\n"
            f"- Điểm Thi Đánh giá Năng lực (ĐGNL): 710 / 1200 điểm.\n"
            f"- Thư giới thiệu: Chưa nộp."
        )
    else:
        return f"LỖI: Không tìm thấy hồ sơ thí sinh '{student_id_or_name}' trong cơ sở dữ liệu tuyển sinh."


def evaluate_admission_eligibility(student_name: str, major: str, admission_method: str) -> str:
    """
    Đánh giá khả năng trúng tuyển của thí sinh vào ngành học theo phương thức xét tuyển lựa chọn.
    
    Args:
        student_name (str): Tên thí sinh (Ví dụ: 'Nguyễn Văn A')
        major (str): Ngành học đăng ký (Ví dụ: 'Khoa học Máy tính')
        admission_method (str): Phương thức xét tuyển ('THPTQG', 'Học bạ', 'ĐGNL', hoặc 'Kết hợp / Thư giới thiệu')
        
    Returns:
        str: Kết quả đánh giá chi tiết, cơ hội trúng tuyển (%) và khuyến nghị
    """
    s_lower = student_name.lower()
    m_lower = major.lower()
    method_lower = admission_method.lower()
    
    if "nguyễn văn a" in s_lower or "a" in s_lower:
        if "thpt" in method_lower:
            return (
                f"📊 ĐÁNH GIÁ XÉT TUYỂN: Thí sinh {student_name} -> Ngành {major} (Phương thức THPTQG)\n"
                f"- Điểm tổ hợp A00 của thí sinh: 26.5 điểm.\n"
                f"- Điểm sàn dự kiến ngành {major}: 26.5 điểm.\n"
                f"- Khả năng trúng tuyển: 85% (Cơ hội ĐẬU cao).\n"
                f"- Lời khuyên: Nên đặt nguyện vọng 1 vào ngành này."
            )
        elif "đgnl" in method_lower or "đánh giá năng lực" in method_lower:
            return (
                f"📊 ĐÁNH GIÁ XÉT TUYỂN: Thí sinh {student_name} -> Ngành {major} (Phương thức Thi ĐGNL)\n"
                f"- Điểm thi ĐGNL của thí sinh: 880/1200 điểm.\n"
                f"- Tiêu chuẩn ngành {major}: 850/1200 điểm.\n"
                f"- Khả năng trúng tuyển: 92% (RẤT CAO - Vượt tiêu chuẩn 30 điểm)."
            )
        else: # Học bạ / Kết hợp
            return (
                f"📊 ĐÁNH GIÁ XÉT TUYỂN: Thí sinh {student_name} -> Ngành {major} (Phương thức Xét Học bạ & Thư giới thiệu)\n"
                f"- Điểm Học bạ: 27.7 điểm + Thư giới thiệu Tốt từ THPT Chuyên + IELTS 7.0.\n"
                f"- Khả năng trúng tuyển: 95% (Đủ điều kiện XÉT TUYỂN THẲNG)."
            )
    elif "trần thị b" in s_lower or "b" in s_lower:
        return (
            f"📊 ĐÁNH GIÁ XÉT TUYỂN: Thí sinh {student_name} -> Ngành {major}\n"
            f"- Điểm THPTQG (23.7) & ĐGNL (710) chưa đạt điểm sàn dự kiến ngành {major} (26.5 điểm).\n"
            f"- Khả năng trúng tuyển: 35% (RỦI RO CAO).\n"
            f"- Lời khuyên: Thí sinh nên cân nhắc chọn ngành Quản trị Kinh doanh hoặc bổ sung Thư giới thiệu."
        )
    else:
        return f"LỖI: Không đủ dữ liệu để đánh giá xét tuyển cho thí sinh '{student_name}'."


def rank_applicant_profiles(applicant_list: str, major: str) -> str:
    """
    Xếp hạng danh sách thí sinh đăng ký vào ngành học theo thứ tự tổng điểm quy đổi từ cao xuống thấp.
    
    Args:
        applicant_list (str): Danh sách tên các thí sinh (Ví dụ: 'Nguyễn Văn A, Trần Thị B, Lê Văn C')
        major (str): Ngành học xét tuyển
        
    Returns:
        str: Bảng xếp hạng thứ tự xét tuyển kèm điểm số và trạng thái dự kiến trúng tuyển
    """
    if not applicant_list or "fake" in applicant_list.lower():
        return f"LỖI: Danh sách thí sinh '{applicant_list}' không hợp lệ."
        
    return (
        f"🏆 BẢNG XẾP HẠNG THÍ SINH ĐĂNG KÝ NGÀNH '{major}':\n"
        f"1. Hạng 1: Nguyễn Văn A | Điểm Quy Đổi: 95.5/100 (Học bạ 9.2, ĐGNL 880, Thư giới thiệu Xung phong) -> DỰ KIẾN TRÚNG TUYỂN (Học bổng)\n"
        f"2. Hạng 2: Lê Văn C     | Điểm Quy Đổi: 84.0/100 (THPTQG 25.8, ĐGNL 810) -> DỰ KIẾN TRÚNG TUYỂN\n"
        f"3. Hạng 3: Trần Thị B   | Điểm Quy Đổi: 71.5/100 -> DỰ KIẾN DỰ BỊ / NÊN ĐỔI NGÀNH"
    )


def check_counseling_slots(counselor_name: str, date: str) -> str:
    """
    Kiểm tra danh sách các ca tư vấn tuyển sinh 1-1 hoặc phỏng vấn xét tuyển còn trống trong ngày.
    
    Args:
        counselor_name (str): Tên Chuyên viên tư vấn / Giảng viên (Ví dụ: 'Thầy Hoàng - Ban Tuyển Sinh', 'Cô Hương - Trưởng khoa')
        date (str): Ngày tư vấn (Ví dụ: '29/07/2026')
        
    Returns:
        str: Danh sách ca tư vấn / phỏng vấn còn trống
    """
    if "31/02" in date or "32/" in date or "13/2026" in date:
        return f"LỖI: Ngày '{date}' không hợp lệ trên lịch làm việc của Ban tuyển sinh."
        
    c_lower = counselor_name.lower()
    if "hoàng" in c_lower or "tuyển sinh" in c_lower:
        return (
            f"📅 CA TƯ VẤN CÒN TRỐNG ({counselor_name} - Ngày {date}):\n"
            f"- Ca 1: 08:30 - 09:30 (Còn trống)\n"
            f"- Ca 2: 14:00 - 15:00 (Còn trống)\n"
            f"- Ca 3: 15:30 - 16:30 (Đã có phụ huynh đặt)"
        )
    elif "hương" in c_lower or "khoa" in c_lower:
        return (
            f"📅 CA TƯ VẤN CÒN TRỐNG ({counselor_name} - Ngày {date}):\n"
            f"- Ca 1: 09:30 - 10:30 (Còn trống)\n"
            f"- Ca 2: 15:00 - 16:00 (Còn trống)"
        )
    else:
        return f"LỖI: Không tìm thấy lịch trực tư vấn của cán bộ '{counselor_name}'."


def schedule_admission_counseling(student_name: str, counselor_name: str, time_slot: str, major: str) -> str:
    """
    Đặt lịch hẹn tư vấn tuyển sinh trực tiếp 1-1 hoặc phỏng vấn xét tuyển cho thí sinh và phụ huynh.
    
    Args:
        student_name (str): Tên thí sinh / Phụ huynh (Ví dụ: 'Nguyễn Văn A')
        counselor_name (str): Tên Cán bộ tư vấn (Ví dụ: 'Thầy Hoàng - Ban Tuyển Sinh')
        time_slot (str): Khung giờ & Ngày hẹn (Ví dụ: '08:30 ngày 29/07/2026')
        major (str): Ngành học quan tâm (Ví dụ: 'Khoa học Máy tính')
        
    Returns:
        str: Mã xác nhận lịch hẹn tư vấn, địa điểm phòng làm việc hoặc link tư vấn online
    """
    if "fake" in student_name.lower() or "chưa có" in time_slot.lower():
        return f"THẤT BẠI: Không thể đặt lịch tư vấn do thông tin thí sinh hoặc thời gian không hợp lệ."
        
    import random
    ticket_id = f"ADMIT-2026-{random.randint(1000, 9999)}"
    return (
        f"🎉 ĐẶT LỊCH TƯ VẤN / PHỎNG VẤN TUYỂN SINH THÀNH CÔNG!\n"
        f"- Mã phiếu hẹn: {ticket_id}\n"
        f"- Thí sinh / Phụ huynh: {student_name}\n"
        f"- Cán bộ tư vấn: {counselor_name}\n"
        f"- Ngành tư vấn: {major}\n"
        f"- Thời gian: {time_slot}\n"
        f"- Địa điểm: Phòng Tư vấn Tuyển sinh A102 hoặc Zoom Online: https://zoom.us/j/{random.randint(100000000, 999999999)}\n"
        f"- Đã gửi SMS & Email xác nhận phiếu hẹn kèm sơ đồ trường cho thí sinh."
    )


# ---------------------------------------------------------
# DANH SÁCH CÁC TOOL ĐƯỢC ĐĂNG KÝ CHO REACT AGENT SỬ DỤNG
# ---------------------------------------------------------
AVAILABLE_TOOLS = {
    "get_admission_criteria": get_admission_criteria,
    "lookup_student_profile": lookup_student_profile,
    "evaluate_admission_eligibility": evaluate_admission_eligibility,
    "rank_applicant_profiles": rank_applicant_profiles,
    "check_counseling_slots": check_counseling_slots,
    "schedule_admission_counseling": schedule_admission_counseling,
}

if __name__ == "__main__":
    print("🧪 KIỂM THỬ ĐỘC LẬP 6 TOOLS TUYỂN SINH ĐẠI HỌC...")
    print(get_admission_criteria("Khoa học Máy tính"))
    print("\n" + lookup_student_profile("Nguyễn Văn A"))
    print("\n" + evaluate_admission_eligibility("Nguyễn Văn A", "Khoa học Máy tính", "Học bạ"))
    print("\n" + rank_applicant_profiles("Nguyễn Văn A, Trần Thị B", "Khoa học Máy tính"))
    print("\n" + check_counseling_slots("Thầy Hoàng", "29/07/2026"))
    print("\n" + schedule_admission_counseling("Nguyễn Văn A", "Thầy Hoàng", "08:30 ngày 29/07/2026", "Khoa học Máy tính"))
    print("\n✅ TẤT CẢ 6 TOOLS ĐÃ TEST THÀNH CÔNG!")
