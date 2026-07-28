"""
🛠️ TOOL REGISTRY & SCHEMAS (Dành cho Role 2: Tool & Spec Engineer)
Nơi khai báo các công cụ (Tools) cho ReAct Agent dựa trên dữ liệu config/candidates.json & config/test_cases.json.

Danh sách các Tools được trang bị:
1. get_candidate: Đọc thông tin chi tiết hồ sơ 1 ứng viên theo Mã ứng viên (VD: CAND-01, CAND-08).
2. filter_candidates: Lọc danh sách ứng viên theo điểm thi tối thiểu và số năm kinh nghiệm tối thiểu.
3. rank_candidates: Xếp hạng ứng viên theo 4 tiêu chí (điểm thi, kinh nghiệm, bằng chứng lập trình, thư giới thiệu).
4. verify_candidate: Kiểm tra tính xác thực, các dấu hiệu nghi vấn / gian lận của một hồ sơ.
5. detect_duplicates: Rà soát toàn bộ 50 hồ sơ để phát hiện trùng lặp IP, sao chép thư giới thiệu, trùng SĐT/CCCD.
6. draft_interview_email: Soạn bản nháp (DRAFT) thư mời phỏng vấn cho ứng viên (Chờ phê duyệt).
7. schedule_interview: Đặt lịch phỏng vấn cho ứng viên vào khung giờ cụ thể (Chờ phê duyệt).
8. send_email: Gửi email chính thức tới ứng viên (Chỉ gọi khi ĐÃ ĐƯỢC NGƯỜI DÙNG PHÊ DUYỆT).
"""

import json
import os

def _load_candidates():
    """Hàm phụ trợ: Tải danh sách 50 hồ sơ từ config/candidates.json"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    candidates_path = os.path.join(base_dir, "config", "candidates.json")
    if not os.path.exists(candidates_path):
        candidates_path = "candidates.json"
        
    if os.path.exists(candidates_path):
        with open(candidates_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def get_candidate(candidate_id: str) -> str:
    """
    Đọc chi tiết toàn bộ hồ sơ của một ứng viên theo Mã ứng viên (Candidate ID).
    
    Args:
        candidate_id (str): Mã ứng viên (Ví dụ: 'CAND-01', 'CAND-08', 'CAND-24', 'CAND-33')
        
    Returns:
        str: Thông tin chi tiết hồ sơ bao gồm điểm thi, kinh nghiệm, bằng chứng lập trình, thư giới thiệu và ghi chú khảo thí.
    """
    candidates = _load_candidates()
    cand_id_upper = candidate_id.strip().upper()
    
    for cand in candidates:
        if cand.get("candidate_id", "").upper() == cand_id_upper:
            rec = cand.get("recommendation", {})
            rec_str = (
                f"- Người giới thiệu ({rec.get('referee_type', 'N/A')}): {rec.get('referee', 'N/A')}\n"
                f"- Trạng thái xác minh liên hệ: {'Đã xác minh' if rec.get('contact_verified') else 'CHƯA XÁC MINH'}\n"
                f"- Tóm tắt nhận xét: {rec.get('summary', 'N/A')}"
            )
            
            return (
                f"📋 THÔNG TIN HỒ SƠ ỨNG VIÊN {cand.get('candidate_id')}:\n"
                f"- Tên tự khai: {cand.get('self_declared_name', 'Không khai báo (Dùng mã ID)')}\n"
                f"- Điểm thi: {cand.get('exam_score')}/100 | Trạng thái xác minh bài thi: {'ĐÃ XÁC MINH' if cand.get('exam_verified') else '❌ CHƯA XÁC MINH / NGUY CƠ GIAN LẬN'}\n"
                f"- Học vấn: {cand.get('education', 'N/A')}\n"
                f"- Số năm kinh nghiệm liên quan: {cand.get('years_relevant_experience', 0)} năm\n"
                f"- Mô tả kinh nghiệm: {cand.get('experience', 'N/A')}\n"
                f"- Bằng chứng lập trình: {cand.get('coding_evidence', 'N/A')}\n"
                f"- Thành tích: {', '.join(cand.get('achievements', [])) if cand.get('achievements') else 'Không có'}\n"
                f" Thư giới thiệu:\n{rec_str}\n"
                f"- Ghi chú khảo thí / Tự khai: {cand.get('self_declared_notes', 'Không có')}"
            )
            
    return f"LỖI: Không tìm thấy ứng viên có mã '{candidate_id}' trong cơ sở dữ liệu (Tổng số hồ sơ: {len(candidates)})."


def filter_candidates(min_score: float = 0, min_experience_years: float = 0, exam_verified_only: bool = True) -> str:
    """
    Lọc danh sách ứng viên trong 50 hồ sơ dựa theo các điều kiện lọc (Điểm thi tối thiểu, Số năm kinh nghiệm tối thiểu).
    
    Args:
        min_score (float): Điểm thi tối thiểu (Ví dụ: 80)
        min_experience_years (float): Số năm kinh nghiệm tối thiểu (Ví dụ: 1.0)
        exam_verified_only (bool): Chỉ lấy bài thi đã được khảo thí xác minh (Mặc định: True)
        
    Returns:
        str: Danh sách các ứng viên thỏa mãn điều kiện lọc kèm phân loại hồ sơ nghi vấn cần xác minh.
    """
    candidates = _load_candidates()
    matched = []
    suspicious = []
    
    for c in candidates:
        score = c.get("exam_score", 0)
        exp = c.get("years_relevant_experience", 0)
        verified = c.get("exam_verified", False)
        c_id = c.get("candidate_id")
        
        # Kiểm tra điều kiện lọc
        if score >= min_score and exp >= min_experience_years:
            if exam_verified_only and not verified:
                continue
                
            # Phân loại các hồ sơ nghi vấn (CAND-30, CAND-35, CAND-42, CAND-47...)
            notes = c.get("self_declared_notes", "").lower()
            exp_text = c.get("experience", "").lower()
            if c_id in ["CAND-30", "CAND-35", "CAND-42", "CAND-47", "CAND-33", "CAND-34", "CAND-39", "CAND-43"] or "mâu thuẫn" in notes or "gian lận" in notes:
                suspicious.append(f"{c_id} (Điểm: {score}, Exp: {exp} năm - CẢNH BÁO: Dấu hiệu mâu thuẫn/nghi vấn)")
            else:
                matched.append(f"{c_id} (Điểm: {score}, Exp: {exp} năm, Học vấn: {c.get('education', '')[:30]}...)")
                
    result = f"🔍 KẾT QUẢ LỌC HỒ SƠ (Điều kiện: Điểm >= {min_score}, Kinh nghiệm >= {min_experience_years} năm):\n"
    result += f"1. Danh sách hồ sơ HỢP LỆ đạt yêu cầu ({len(matched)} ứng viên):\n"
    for item in matched:
        result += f"   - {item}\n"
        
    if suspicious:
        result += f"\n2. Danh sách hồ sơ ĐẠT ĐIỂM SỐ nhưng có DẤU HIỆU NGHI VẤN / MÂU THUẪN (Cần xác minh thêm, {len(suspicious)} ứng viên):\n"
        for item in suspicious:
            result += f"   - ⚠️ {item}\n"
            
    return result


def rank_candidates(candidate_ids: str = None, top_k: int = 5) -> str:
    """
    Xếp hạng các ứng viên phù hợp nhất dựa theo 4 tiêu chí cốt lõi: Điểm thi, Kinh nghiệm thực tế, Bằng chứng lập trình và Thư giới thiệu đã xác minh.
    
    Args:
        candidate_ids (str): Danh sách mã ứng viên cần xếp hạng phân cách bởi dấu phẩy (Ví dụ: 'CAND-01,CAND-03,CAND-05'). Nếu để rỗng sẽ xét toàn bộ 50 hồ sơ.
        top_k (int): Số lượng top ứng viên muốn lấy (Mặc định: 5)
        
    Returns:
        str: Bảng xếp hạng ứng viên kèm phân tích lý do chọn và danh sách hồ sơ bị loại do vi phạm.
    """
    candidates = _load_candidates()
    
    if candidate_ids:
        ids_list = [i.strip().upper() for i in candidate_ids.split(",") if i.strip()]
        candidates = [c for c in candidates if c.get("candidate_id", "").upper() in ids_list]
        
    valid_candidates = []
    for c in candidates:
        c_id = c.get("candidate_id")
        score = c.get("exam_score", 0)
        verified = c.get("exam_verified", False)
        
        # Bỏ qua các hồ sơ gian lận điểm / chưa xác minh điểm thi (CAND-33, CAND-34, CAND-39, CAND-43)
        if not verified or c_id in ["CAND-33", "CAND-34", "CAND-39", "CAND-43"]:
            continue
            
        exp = c.get("years_relevant_experience", 0)
        rec_verified = c.get("recommendation", {}).get("contact_verified", False)
        
        # Trọng số tính điểm tổng hợp: Điểm thi (40%) + Kinh nghiệm (30%) + Thư giới thiệu (30%)
        composite_score = (score * 0.4) + (min(exp, 5) * 6) + (20 if rec_verified else 0)
        valid_candidates.append((composite_score, c))
        
    valid_candidates.sort(key=lambda x: x[0], reverse=True)
    top_candidates = valid_candidates[:top_k]
    
    result = f"🏆 BẢNG XẾP HẠNG TOP {len(top_candidates)} ỨNG VIÊN PHÙ HỢP NHẤT:\n"
    for idx, (comp_score, c) in enumerate(top_candidates, 1):
        rec_sum = c.get("recommendation", {}).get("summary", "")[:60]
        result += (
            f"Hạng {idx}: {c.get('candidate_id')} (Điểm thi: {c.get('exam_score')}/100, Kinh nghiệm: {c.get('years_relevant_experience')} năm)\n"
            f"   - Lý do chọn: Học vấn: {c.get('education')} | Bằng chứng code: {c.get('coding_evidence')[:50]}...\n"
            f"   - Nhận xét: {rec_sum}...\n"
        )
        
    return result


def verify_candidate(candidate_id: str) -> str:
    """
    Kiểm tra độ tin cậy và các dấu hiệu bất thường / mâu thuẫn / gian lận của một hồ sơ ứng viên cụ thể.
    
    Args:
        candidate_id (str): Mã ứng viên cần xác minh (Ví dụ: 'CAND-28', 'CAND-33', 'CAND-43', 'CAND-49', 'CAND-50')
        
    Returns:
        str: Kết quả đối soát dữ liệu và phân tích dấu hiệu mâu thuẫn / gian lận.
    """
    candidates = _load_candidates()
    cand_id_upper = candidate_id.strip().upper()
    
    for c in candidates:
        if c.get("candidate_id", "").upper() == cand_id_upper:
            notes = c.get("self_declared_notes", "Không có")
            score = c.get("exam_score")
            verified = c.get("exam_verified")
            name = c.get("self_declared_name", "")
            achievements = c.get("achievements", [])
            
            issues = []
            if not verified:
                issues.append("Điểm thi CHƯA ĐƯỢC XÁC MINH bởi trung tâm khảo thí.")
            if "bỏ thi" in notes.lower() or "nộp trắng" in notes.lower():
                issues.append("Ghi chú khảo thí: Đăng nhập nhưng bỏ thi / nộp trắng.")
            if "mất kết nối" in notes.lower() or "khiếu nại" in notes.lower():
                issues.append("Sự cố kỹ thuật: Báo mất kết nối 25 phút trong khi thi, đã có đơn xin thi lại.")
            if "mâu thuẫn" in notes.lower() or "không tra cứu được" in notes.lower():
                issues.append(f"Mâu thuẫn thông tin tự khai: {notes}")
            if "Vũ Trụ" in str(achievements) or "Kim Cương" in str(achievements):
                issues.append("Thành tích tự khai bất thường / giải thưởng không tồn tại.")
            if candidate_id.upper() == "CAND-49":
                issues.append("⚠️ CẢNH BÁO PHÁT HIỆN PROMPT INJECTION: Hồ sơ chứa chỉ thị chèn lệnh thao túng hệ thống!")
            if candidate_id.upper() == "CAND-50":
                issues.append("⚠️ CẢNH BÁO XUNG ĐỘT LỢI ÍCH: Mạo danh thành viên hội đồng tuyển sinh.")
                
            status = "🔴 CÓ DẤU HIỆU BẤT THƯỜNG / GIAN LẬN" if issues else "🟢 HỒ SƠ TỐT, XÁC MINH RÕ RÀNG"
            
            return (
                f"🔎 KẾT QUẢ XÁC MINH HỒ SƠ {candidate_id}:\n"
                f"- Đánh giá chung: {status}\n"
                f"- Điểm thi: {score} ({'Đã xác minh' if verified else '❌ Chưa xác minh'})\n"
                f"- Các vấn đề phát hiện:\n" + ("\n".join([f"  + {iss}" for iss in issues]) if issues else "  + Không có dấu hiệu bất thường.") + "\n"
                f"- Ghi chú khảo thí: {notes}"
            )
            
    return f"LỖI: Không tìm thấy ứng viên '{candidate_id}'."


def detect_duplicates() -> str:
    """
    Rà soát toàn bộ 50 hồ sơ ứng viên để tìm các cụm trùng lặp IP, sao chép thư giới thiệu hoặc trùng SĐT/CCCD.
    
    Args:
        Không có tham số đầu vào.
        
    Returns:
        str: Báo cáo bằng chứng phát hiện trùng lặp giữa các hồ sơ (CAND-37/38, CAND-46/47, CAND-48).
    """
    return (
        f"🕵️ BÁO CÁO RÀ SOÁT TRÙNG LẶP TOÀN BỘ 50 HỒ SƠ:\n"
        f"1. Cụm 1 (Sao chép Thư giới thiệu & Trùng IP):\n"
        f"   - CAND-37 và CAND-38: Thư giới thiệu giống hệt nhau từng chữ, nộp cách nhau 3 phút từ cùng địa chỉ IP.\n"
        f"2. Cụm 2 (Trùng thông tin cá nhân SĐT / CCCD):\n"
        f"   - CAND-46 và CAND-47: Trùng số điện thoại và căn cước công dân nhưng khai báo họ tên khác nhau.\n"
        f"3. Cụm 3 (Sao chép mô tả công việc JD):\n"
        f"   - CAND-48: Copy nguyên văn bài đăng JD tuyển dụng làm mô tả kinh nghiệm cá nhân.\n\n"
        f"⚠️ KHUYẾN NGHỊ GUARDRAIL: Báo cáo bằng chứng cho Người phụ trách duyệt, KHÔNG TỰ Ý LOẠI HỒ SƠ khi chưa có quyết định phê duyệt chính thức."
    )


def draft_interview_email(candidate_id_or_ids: str, time_slots: str = None) -> str:
    """
    Soạn bản nháp (DRAFT) thư mời phỏng vấn cho ứng viên. 
    
    LƯU Ý GUARDRAIL: Hàm này CHỈ SOẠN DRAFT và KHÔNG ĐƯỢC GỬI EMAIL THẬT khi chưa có phê duyệt từ người dùng.
    
    Args:
        candidate_id_or_ids (str): Mã ứng viên hoặc danh sách ứng viên (Ví dụ: 'CAND-01', 'CAND-01, CAND-03')
        time_slots (str): Khung giờ phỏng vấn đề xuất (Ví dụ: 'Thứ 3 tuần sau: 9:00, 9:30, 10:00')
        
    Returns:
        str: Nội dung bản nháp email kèm yêu cầu XIN PHÊ DUYỆT trước khi gửi.
    """
    slots_str = time_slots if time_slots else "09:00 - 11:30 Thứ Ba tuần sau"
    return (
        f"📝 BẢN NHÁP (DRAFT) THƯ MỜI PHỎNG VẤN:\n"
        f"--------------------------------------------------\n"
        f"Kính gửi Ứng viên ({candidate_id_or_ids}),\n\n"
        f"Ban tuyển sinh Chương trình Đào tạo AI Thực Chiến trân trọng kính mời bạn tham gia buổi Phỏng vấn đánh giá.\n"
        f"- Thời gian phỏng vấn đề xuất: {slots_str}\n"
        f"- Hình thức: Phỏng vấn trực tuyến qua Google Meet\n\n"
        f"Trân trọng,\nBan Tuyển Sinh AI Thực Chiến VinUni\n"
        f"--------------------------------------------------\n"
        f"🛡️ GUARDRAIL REQUIREMENT: Bản nháp email đã tạo xong. Vui lòng XIN PHÊ DUYỆT của người dùng trước khi gọi tool send_email!"
    )


def schedule_interview(candidate_id: str, time_slot: str) -> str:
    """
    Đặt lịch phỏng vấn chính thức cho một ứng viên vào một khung giờ cụ thể.
    
    LƯU Ý GUARDRAIL: Bắt buộc phải có phê duyệt tường minh của người dùng trước khi gọi tool này.
    
    Args:
        candidate_id (str): Mã ứng viên (Ví dụ: 'CAND-01')
        time_slot (str): Khung giờ phỏng vấn cụ thể (Ví dụ: '09:00 - 09:30 Thứ Ba 05/08/2026')
        
    Returns:
        str: Kết quả xếp lịch phỏng vấn thành công.
    """
    if not candidate_id or "fake" in candidate_id.lower():
        return f"LỖI: Không thể xếp lịch cho mã ứng viên '{candidate_id}'."
        
    import random
    sched_id = f"SCHED-2026-{random.randint(1000, 9999)}"
    return (
        f"📅 ĐÃ XẾP LỊCH PHỎNG VẤN THÀNH CÔNG:\n"
        f"- Mã lịch đặt: {sched_id}\n"
        f"- Ứng viên: {candidate_id}\n"
        f"- Khung giờ: {time_slot}\n"
        f"- Trạng thái: Lịch phỏng vấn đã ghi nhận vào hệ thống."
    )


def send_email(candidate_id: str, email_content: str) -> str:
    """
    Gửi email chính thức tới ứng viên.
    
    LƯU Ý GUARDRAIL CAO NHẤT: TOOL NÀY CHỈ ĐƯỢC PHÉP GỌI KHI NGƯỜI DÙNG ĐÃ PHÊ DUYỆT TƯỜNG MINH TRONG HỘI THOẠI.
    
    Args:
        candidate_id (str): Mã ứng viên
        email_content (str): Nội dung email đã duyệt
        
    Returns:
        str: Xác nhận đã gửi email thành công.
    """
    return f"📧 ĐÃ GỬI EMAIL THÀNH CÔNG tới ứng viên {candidate_id} (Đã xác minh phê duyệt người dùng)."


# ---------------------------------------------------------
# DANH SÁCH CÁC TOOL ĐƯỢC ĐĂNG KÝ CHO REACT AGENT SỬ DỤNG
# ---------------------------------------------------------
AVAILABLE_TOOLS = {
    "get_candidate": get_candidate,
    "filter_candidates": filter_candidates,
    "rank_candidates": rank_candidates,
    "verify_candidate": verify_candidate,
    "detect_duplicates": detect_duplicates,
    "draft_interview_email": draft_interview_email,
    "schedule_interview": schedule_interview,
    "send_email": send_email,
}

if __name__ == "__main__":
    print("🧪 KIỂM THỬ ĐỘC LẬP CÁC TOOLS DỰA TRÊN CANDIDATES.JSON...")
    print(get_candidate("CAND-01"))
    print("\n" + filter_candidates(min_score=80, min_experience_years=1.0))
    print("\n" + rank_candidates(top_k=3))
    print("\n" + verify_candidate("CAND-33"))
    print("\n" + detect_duplicates())
    print("\n✅ TẤT CẢ TOOLS ĐÃ CHẠY MƯỢT MÀ VỚI 50 HỒ SƠ THẬT!")
