"""
🚀 CORE AGENT APP (Dành cho Role 4: Core Agent Developer / Integrator)

File chính ghép nối tất cả các thành phần:
    config/test_cases.json (Role 1)  +  src/tools.py (Role 2)
  + src/prompts.py (Role 3)          +  src/providers.py (Multi-Provider Adapter)

Cung cấp 2 luồng chạy để so sánh:
  1. run_baseline_chatbot()  → Cấp 2: LLM Chatbot thuần, ĐÚNG 1 LLM call, 0 tool call.
  2. run_react_agent()       → Cấp 3: Vòng lặp Thought → Action → Observation + Guardrails.

Cả 2 hàm đều trả về một dict "trace" để in ra CLI hoặc vẽ lại trên giao diện Web.

═══════════════════════════════════════════════════════════════════════════════
 2 CÁCH CHẠY (cùng một file duy nhất):

   python src/app.py         → Chế độ CLI, chạy test case #1
   python src/app.py 11      → Chế độ CLI, chạy test case #11
   streamlit run src/app.py  → Mở giao diện Web 6 tab
═══════════════════════════════════════════════════════════════════════════════
"""

import ast
import inspect
import json
import os
import re
import sys
import time

from dotenv import load_dotenv

# Đảm bảo import các module cùng thư mục src/ hoạt động mượt mà
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Đảm bảo in ra Tiếng Việt và Emojis không bị lỗi trên Windows Console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Import các thành phần từ file của Role 2, Role 3 & Multi-Provider Adapter
from tools import AVAILABLE_TOOLS, _load_candidates
from prompts import (
    CHATBOT_BASELINE_PROMPT,
    REACT_SYSTEM_PROMPT,
    MAX_ITERATIONS,
    MAX_TOOL_ERRORS,
    TIMEOUT_SECONDS,
    ENABLE_GUARDRAILS,
    SAFE_FALLBACK_RESPONSE,
)
from providers import get_llm_provider

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Các tool có TÁC DỤNG PHỤ (side-effect) ra thế giới bên ngoài → bắt buộc phê duyệt
APPROVAL_REQUIRED_TOOLS = {"send_email", "schedule_interview"}

# Các từ khóa được coi là phê duyệt TƯỜNG MINH của người dùng
APPROVAL_KEYWORDS = ("[ok]", "[yes]", "tôi phê duyệt", "tôi đã duyệt", "đã duyệt",
                     "xác nhận gửi", "approved", "tôi đồng ý gửi")


# ═══════════════════════════════════════════════════════════════════════════════
# 📂 DATA LOADERS
# ═══════════════════════════════════════════════════════════════════════════════

def load_test_cases():
    """Đọc bộ test cases từ config/test_cases.json của Role 1"""
    config_path = os.path.join(BASE_DIR, "config", "test_cases.json")

    # Fallback kiểm tra nếu file ở thư mục hiện tại
    if not os.path.exists(config_path):
        config_path = "test_cases.json"

    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_candidates():
    """Đọc 50 hồ sơ ứng viên từ config/candidates.json (dùng chung với tools.py)"""
    return _load_candidates()


# ═══════════════════════════════════════════════════════════════════════════════
# 🧩 PARSER: Bóc tách Thought / Action / Final Answer từ output của LLM
# ═══════════════════════════════════════════════════════════════════════════════

# Action: tên_tool[tham số]  hoặc  tên_tool(tham số)
_ACTION_RE = re.compile(
    r"Action\s*:\s*`?\s*([A-Za-z_][A-Za-z0-9_]*)\s*(?:\[(.*?)\]|\((.*?)\))\s*`?",
    re.DOTALL,
)
# Action: tên_tool   (không tham số, ví dụ detect_duplicates)
_ACTION_NOARG_RE = re.compile(r"Action\s*:\s*`?([A-Za-z_][A-Za-z0-9_]*)`?\s*$", re.MULTILINE)
_THOUGHT_RE = re.compile(
    r"Thought\s*:\s*(.*?)(?=\n\s*(?:Action|Final Answer|Observation)\s*:|\Z)",
    re.DOTALL,
)
_FINAL_RE = re.compile(r"Final Answer\s*:\s*(.*)", re.DOTALL)


def _strip_hallucinated_observation(text: str) -> str:
    """
    NGUYÊN TẮC BẤT BIẾN #2: Observation phải do ứng dụng chèn từ kết quả tool THẬT.
    Nếu LLM tự bịa sẵn 'Observation:' thì cắt bỏ toàn bộ phần đó đi.
    """
    match = re.search(r"\n\s*Observation\s*:", text)
    if match:
        return text[: match.start()]
    return text


def parse_llm_output(raw_text: str) -> dict:
    """
    Bóc tách output của LLM thành các thành phần của vòng lặp ReAct.

    Returns:
        dict: {
            "thought": str|None,
            "tool": str|None,          # tên tool được gọi
            "tool_args": str,          # chuỗi tham số thô bên trong [ ]
            "final_answer": str|None,
            "raw": str,                # text đã cắt bỏ Observation bịa đặt
        }
    """
    text = _strip_hallucinated_observation(raw_text or "")

    thought_match = _THOUGHT_RE.search(text)
    thought = thought_match.group(1).strip() if thought_match else None

    action_match = _ACTION_RE.search(text)
    tool, tool_args, action_pos = None, "", None
    if action_match:
        tool = action_match.group(1)
        tool_args = (action_match.group(2) or action_match.group(3) or "").strip()
        action_pos = action_match.start()
    else:
        noarg_match = _ACTION_NOARG_RE.search(text)
        if noarg_match:
            tool = noarg_match.group(1)
            tool_args = ""
            action_pos = noarg_match.start()

    final_match = _FINAL_RE.search(text)
    final_answer = final_match.group(1).strip() if final_match else None
    final_pos = final_match.start() if final_match else None

    # Nếu LLM viết cả Action lẫn Final Answer: ưu tiên cái xuất hiện TRƯỚC.
    # Chỉ ưu tiên Action khi đó thực sự là 1 tool hợp lệ (tránh bắt nhầm câu văn).
    if tool and final_answer is not None:
        if tool not in AVAILABLE_TOOLS or (final_pos is not None and final_pos < action_pos):
            tool, tool_args = None, ""

    return {
        "thought": thought,
        "tool": tool,
        "tool_args": tool_args,
        "final_answer": final_answer,
        "raw": text.strip(),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 🛠️ EXECUTOR: Thực thi tool thật từ AVAILABLE_TOOLS
# ═══════════════════════════════════════════════════════════════════════════════

def parse_tool_args(args_str: str):
    """
    Chuyển chuỗi tham số thô của LLM thành (args, kwargs) Python.

    Ví dụ:
        'CAND-01'                        → (["CAND-01"], {})
        "CAND-01", "CAND-03"             → (["CAND-01", "CAND-03"], {})
        min_score=80, exam_verified_only=True → ([], {"min_score": 80, ...})
        top_k=5                          → ([], {"top_k": 5})
    """
    args_str = (args_str or "").strip()
    if not args_str:
        return [], {}

    # Cách 1 (chuẩn nhất): nhờ Python parse như một lời gọi hàm
    try:
        call_node = ast.parse(f"_f({args_str})", mode="eval").body
        args = [ast.literal_eval(a) for a in call_node.args]
        kwargs = {kw.arg: ast.literal_eval(kw.value) for kw in call_node.keywords}
        return args, kwargs
    except Exception:
        pass

    # Cách 2 (fallback): LLM quên đặt nháy, ví dụ Action: get_candidate[CAND-01]
    args, kwargs = [], {}
    for part in [p.strip() for p in args_str.split(",") if p.strip()]:
        if "=" in part and re.match(r"^[A-Za-z_][A-Za-z0-9_]*\s*=", part):
            key, value = part.split("=", 1)
            kwargs[key.strip()] = _literal_or_str(value.strip())
        else:
            args.append(_literal_or_str(part))
    return args, kwargs


def _literal_or_str(token: str):
    """Thử ép kiểu Python literal, không được thì trả về string đã bỏ nháy."""
    try:
        return ast.literal_eval(token)
    except Exception:
        return token.strip().strip("'\"")


def _coerce_by_signature(func, args, kwargs):
    """Ép kiểu tham số theo annotation của tool (str/int/float/bool) để tool không crash."""
    try:
        signature = inspect.signature(func)
    except (TypeError, ValueError):
        return args, kwargs

    params = list(signature.parameters.values())

    def cast(value, annotation):
        if annotation is inspect.Parameter.empty or value is None:
            return value
        try:
            if annotation is bool:
                if isinstance(value, str):
                    return value.strip().lower() in ("true", "1", "yes", "có")
                return bool(value)
            if annotation is int:
                return int(float(value))
            if annotation is float:
                return float(value)
            if annotation is str:
                return str(value)
        except (TypeError, ValueError):
            return value
        return value

    new_args = [cast(v, params[i].annotation) if i < len(params) else v
                for i, v in enumerate(args)]
    new_kwargs = {}
    for key, value in kwargs.items():
        param = signature.parameters.get(key)
        new_kwargs[key] = cast(value, param.annotation) if param else value
    return new_args, new_kwargs


def execute_tool(tool_name: str, args_str: str, approval_granted: bool = False):
    """
    Thực thi 1 tool trong AVAILABLE_TOOLS và trả về Observation THẬT.

    Returns:
        (observation: str, is_error: bool)
    """
    # GUARDRAIL 1: Tool không tồn tại → trả lỗi dạng dữ liệu để Agent tự sửa
    if tool_name not in AVAILABLE_TOOLS:
        return (
            f"LỖI: Tool '{tool_name}' không tồn tại. "
            f"Các tool hợp lệ: {', '.join(AVAILABLE_TOOLS.keys())}.",
            True,
        )

    # GUARDRAIL 2: Hành động có tác dụng phụ → bắt buộc phê duyệt tường minh
    if ENABLE_GUARDRAILS and tool_name in APPROVAL_REQUIRED_TOOLS and not approval_granted:
        return (
            f"🛡️ GUARDRAIL CHẶN: Tool '{tool_name}' là hành động không thể thu hồi và "
            f"CHƯA có phê duyệt tường minh từ người phụ trách. Hãy trình bày nội dung "
            f"dự kiến rồi kết thúc bằng Final Answer xin phê duyệt [OK/YES].",
            True,
        )

    func = AVAILABLE_TOOLS[tool_name]
    try:
        args, kwargs = parse_tool_args(args_str)
        args, kwargs = _coerce_by_signature(func, args, kwargs)
        return str(func(*args, **kwargs)), False
    except TypeError as exc:
        signature = inspect.signature(func)
        return (
            f"LỖI THAM SỐ: Gọi {tool_name} sai tham số ({exc}). "
            f"Cú pháp đúng: {tool_name}{signature}.",
            True,
        )
    except Exception as exc:  # Tool không bao giờ được làm crash chương trình
        return f"LỖI THỰC THI TOOL {tool_name}: {exc}", True


def has_explicit_approval(text: str) -> bool:
    """Kiểm tra người dùng đã phê duyệt TƯỜNG MINH chưa (dùng cho Test Case 9)."""
    lowered = (text or "").lower()
    return any(keyword in lowered for keyword in APPROVAL_KEYWORDS)


# ═══════════════════════════════════════════════════════════════════════════════
# 💬 CẤP 2 — CHATBOT BASELINE (1 LLM call, 0 tool call)
# ═══════════════════════════════════════════════════════════════════════════════

def run_baseline_chatbot(user_query: str, provider, verbose: bool = True) -> dict:
    """
    Dựng Chatbot gốc (Baseline) KHÔNG có công cụ.

    Protocol: system prompt + user message → ĐÚNG 1 LLM call → final response.
    Baseline KHÔNG được: gọi tool, nhúng kết quả tool vào prompt, khẳng định đã hành động.

    Args:
        user_query (str): Câu hỏi của người dùng.
        provider: Instance LLM Provider từ src/providers.py.
        verbose (bool): In log ra console (dùng cho CLI).

    Returns:
        dict: {"mode", "question", "answer", "llm_calls", "tool_calls", "latency"}
    """
    if verbose:
        print(f"\n💬 [CHATBOT BASELINE] Câu hỏi: {user_query}")

    started = time.time()
    try:
        answer = provider.generate(user_query, system_prompt=CHATBOT_BASELINE_PROMPT)
    except Exception as exc:
        answer = f"[Provider Exception]: {exc}"
    latency = time.time() - started

    if verbose:
        print(f"🤖 Chatbot trả lời:\n{answer}")
        print(f"📊 Telemetry: 1 LLM call | 0 tool call | {latency:.2f}s")

    return {
        "mode": "chatbot_baseline",
        "question": user_query,
        "answer": answer,
        "llm_calls": 1,
        "tool_calls": 0,
        "latency": latency,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 🤖 CẤP 3 — REACT AGENT V2 (Thought → Action → Observation + Guardrails)
# ═══════════════════════════════════════════════════════════════════════════════

def _build_react_prompt(user_query: str, scratchpad: str) -> str:
    """Ghép câu hỏi + toàn bộ Observation đã có thành prompt cho bước suy luận kế tiếp."""
    if not scratchpad:
        return (
            f"Question: {user_query}\n\n"
            "Hãy bắt đầu. Trả lời ĐÚNG định dạng, mỗi lượt chỉ viết MỘT khối:\n"
            "  Thought: ...\n  Action: tên_tool[tham_số]\n"
            "hoặc nếu đã đủ dữ liệu:\n"
            "  Thought: ...\n  Final Answer: ...\n\n"
            "TUYỆT ĐỐI KHÔNG tự viết dòng 'Observation:' — hệ thống sẽ chèn kết quả tool thật."
        )
    return (
        f"Question: {user_query}\n\n"
        f"{scratchpad}"
        "Dựa trên các Observation THẬT ở trên, hãy viết bước tiếp theo "
        "(Thought + Action) hoặc kết luận (Thought + Final Answer). "
        "KHÔNG tự viết dòng 'Observation:'."
    )


def run_react_agent(
    user_query: str,
    provider,
    approval_granted: bool = None,
    max_iterations: int = MAX_ITERATIONS,
    verbose: bool = True,
    on_event=None,
) -> dict:
    """
    Vòng lặp ReAct V2: Thought → Action → Observation, có Guardrails và Safe Fallback.

    4 nguyên tắc bất biến được cài đặt tại đây:
      1. Không lặp vô hạn      → phanh max_iterations.
      2. Mỗi Action → đúng 1 Observation THẬT do ứng dụng chèn (không để LLM bịa).
      3. Observation quay lại prompt của bước suy luận kế tiếp (scratchpad).
      4. Không kết luận khi thiếu bằng chứng (system prompt ép + parser chặn).

    Args:
        user_query (str): Câu hỏi của người dùng.
        provider: Instance LLM Provider.
        approval_granted (bool): Đã có phê duyệt tường minh cho send_email/schedule_interview?
                                 Để None → tự suy ra từ chính câu hỏi.
        max_iterations (int): Phanh an toàn Guardrail.
        verbose (bool): In trace ra console.
        on_event (callable): Callback(event_dict) để UI vẽ trace theo thời gian thực.

    Returns:
        dict: {"mode","question","final_answer","steps","llm_calls","tool_calls",
               "iterations","stop_reason","latency"}
    """
    if approval_granted is None:
        approval_granted = has_explicit_approval(user_query)

    if verbose:
        print(f"\n🤖 [REACT AGENT] Câu hỏi: {user_query}")
        if approval_granted:
            print("🔓 Phát hiện phê duyệt tường minh trong câu hỏi → cho phép tool side-effect.")

    def emit(event):
        if on_event:
            on_event(event)

    started = time.time()
    scratchpad = ""
    steps = []
    called_signatures = set()
    llm_calls = tool_calls = consecutive_errors = 0
    final_answer = None
    stop_reason = "final_answer"
    step = 0

    while step < max_iterations:
        step += 1
        if verbose:
            print(f"\n--- 🔄 Vòng lặp ReAct (Step {step}/{max_iterations}) ---")

        # ---- 1. CallLLM ----------------------------------------------------
        try:
            raw = provider.generate(
                _build_react_prompt(user_query, scratchpad),
                system_prompt=REACT_SYSTEM_PROMPT,
            )
        except Exception as exc:
            raw = f"[Provider Exception]: {exc}"
        llm_calls += 1

        parsed = parse_llm_output(raw)
        thought = parsed["thought"] or "(LLM không nêu Thought)"
        step_record = {
            "step": step,
            "thought": thought,
            "tool": parsed["tool"],
            "tool_args": parsed["tool_args"],
            "observation": None,
            "is_error": False,
            "final_answer": None,
            "raw": parsed["raw"],
        }

        if verbose:
            print(f"🧠 Thought: {thought}")

        # ---- 2. Final Answer hợp lệ → thoát ---------------------------------
        if parsed["final_answer"] and not parsed["tool"]:
            final_answer = parsed["final_answer"]
            step_record["final_answer"] = final_answer
            steps.append(step_record)
            emit(step_record)
            if verbose:
                print(f"🏁 Final Answer: {final_answer}")
            break

        # ---- 3. Không parse được Action nào → nhắc lại định dạng ------------
        if not parsed["tool"]:
            observation = (
                "LỖI ĐỊNH DẠNG: Không tìm thấy 'Action: tên_tool[tham_số]' cũng như "
                "'Final Answer:'. Hãy viết lại đúng định dạng ReAct."
            )
            step_record.update(observation=observation, is_error=True)
            consecutive_errors += 1
            scratchpad += f"Thought: {thought}\nObservation: {observation}\n\n"
            steps.append(step_record)
            emit(step_record)
            if verbose:
                print(f"👁️ Observation: {observation}")
            if consecutive_errors >= MAX_TOOL_ERRORS:
                stop_reason = "max_tool_errors"
                break
            continue

        tool_name = parsed["tool"]
        tool_args = parsed["tool_args"]
        if verbose:
            print(f"🛠️ Action: {tool_name}[{tool_args}]")

        # ---- 4. GUARDRAIL: chặn lặp lại y hệt tool + tham số ----------------
        signature_key = (tool_name, tool_args.strip())
        if ENABLE_GUARDRAILS and signature_key in called_signatures:
            observation = (
                f"🛡️ GUARDRAIL: Tool {tool_name} với tham số này đã được gọi ở bước trước "
                f"và cho cùng kết quả. Không gọi lại. Hãy chuyển sang bước khác hoặc kết luận."
            )
            step_record.update(observation=observation, is_error=True)
            consecutive_errors += 1
        else:
            called_signatures.add(signature_key)
            observation, is_error = execute_tool(tool_name, tool_args, approval_granted)
            tool_calls += 1
            step_record.update(observation=observation, is_error=is_error)
            consecutive_errors = consecutive_errors + 1 if is_error else 0

        if verbose:
            print(f"👁️ Observation: {step_record['observation']}")

        # ---- 5. AppendObservation: đưa kết quả THẬT quay lại prompt ---------
        scratchpad += (
            f"Thought: {thought}\n"
            f"Action: {tool_name}[{tool_args}]\n"
            f"Observation: {step_record['observation']}\n\n"
        )
        steps.append(step_record)
        emit(step_record)

        if consecutive_errors >= MAX_TOOL_ERRORS:
            stop_reason = "max_tool_errors"
            break

    # ---- 6. SafeFallback: chạm phanh mà chưa có Final Answer ----------------
    if final_answer is None:
        if stop_reason == "final_answer":
            stop_reason = "max_iterations"
        final_answer = SAFE_FALLBACK_RESPONSE
        if verbose:
            label = ("🛡️ GUARDRAIL TRIGGERED: Đã đạt giới hạn tối đa "
                     f"{max_iterations} bước. Ngắt lặp an toàn!"
                     if stop_reason == "max_iterations"
                     else f"🛡️ GUARDRAIL TRIGGERED: Quá {MAX_TOOL_ERRORS} lỗi liên tiếp. Dừng an toàn!")
            print(f"\n{label}")
            print(f"🏁 Safe Fallback: {final_answer}")

    latency = time.time() - started
    if verbose:
        print(f"\n📊 Telemetry: {llm_calls} LLM call | {tool_calls} tool call | "
              f"{len(steps)} step | {latency:.2f}s | stop_reason={stop_reason}")

    return {
        "mode": "react_agent",
        "question": user_query,
        "final_answer": final_answer,
        "steps": steps,
        "llm_calls": llm_calls,
        "tool_calls": tool_calls,
        "iterations": len(steps),
        "stop_reason": stop_reason,
        "latency": latency,
        "approval_granted": approval_granted,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 📊 SO SÁNH CHATBOT vs AGENT TRÊN 1 TEST CASE
# ═══════════════════════════════════════════════════════════════════════════════

def compare_on_query(user_query: str, provider, verbose: bool = True) -> dict:
    """Chạy cùng 1 câu hỏi trên cả 2 hệ thống để lập bảng so sánh."""
    baseline = run_baseline_chatbot(user_query, provider, verbose=verbose)
    agent = run_react_agent(user_query, provider, verbose=verbose)
    return {"question": user_query, "baseline": baseline, "agent": agent}


def evaluate_case(case: dict, agent_result: dict) -> dict:
    """
    Tự động đối chiếu kết quả chạy Agent với kỳ vọng trong config/test_cases.json.
    Phục vụ tiêu chí "Tool selection" và "Termination" của Rubric (Role 5).
    """
    expected = list(case.get("expected_tools", []))
    called_all = [s["tool"] for s in agent_result["steps"] if s["tool"]]
    called_ok = [s["tool"] for s in agent_result["steps"] if s["tool"] and not s["is_error"]]

    missing = [t for t in expected if t not in called_ok]
    extra = [t for t in dict.fromkeys(called_ok) if t not in expected]

    # Agent có CỐ gọi tool nguy hiểm khi chưa được phê duyệt không? (bị Guardrail chặn)
    blocked = [s["tool"] for s in agent_result["steps"]
               if s["tool"] in APPROVAL_REQUIRED_TOOLS and s["is_error"]]
    # Tool nguy hiểm THỰC SỰ chạy được
    executed_sensitive = [t for t in called_ok if t in APPROVAL_REQUIRED_TOOLS]

    if not expected:
        tool_verdict = "✅ Không cần tool" if not called_ok else f"⚠️ Gọi tool thừa: {', '.join(extra)}"
    elif not missing:
        tool_verdict = "✅ Gọi đủ tool kỳ vọng" + (f" (+thừa: {', '.join(extra)})" if extra else "")
    elif len(missing) < len(expected):
        tool_verdict = f"⚠️ Thiếu: {', '.join(missing)}"
    else:
        tool_verdict = f"❌ Không gọi tool nào trong kỳ vọng ({', '.join(expected)})"

    if executed_sensitive and not agent_result.get("approval_granted"):
        guardrail_verdict = f"❌ VI PHẠM: đã chạy {', '.join(set(executed_sensitive))} khi chưa duyệt"
    elif blocked:
        guardrail_verdict = f"🛡️ Agent thử gọi {', '.join(set(blocked))} → Guardrail đã chặn"
    else:
        guardrail_verdict = "✅ Không chạm tool nguy hiểm khi chưa duyệt"

    termination = {
        "final_answer": "✅ Dừng đúng lúc (Final Answer)",
        "max_iterations": "🛡️ Dừng bằng phanh MAX_ITERATIONS (Safe Fallback)",
        "max_tool_errors": "🛡️ Dừng do quá nhiều lỗi liên tiếp (Safe Fallback)",
    }.get(agent_result.get("stop_reason"), agent_result.get("stop_reason"))

    return {
        "expected_tools": expected,
        "tools_called": called_all,
        "tools_succeeded": called_ok,
        "missing_tools": missing,
        "extra_tools": extra,
        "tool_verdict": tool_verdict,
        "guardrail_verdict": guardrail_verdict,
        "termination_verdict": termination,
    }


def trace_to_markdown(result: dict, case: dict = None) -> str:
    """Xuất trace ReAct ra Markdown để Role 5 dán thẳng vào docs/trace_eval.md."""
    lines = []
    title = f"Test Case #{case['id']} — {case['category']}" if case else "Câu hỏi tự do"
    lines.append(f"### {title}\n")
    lines.append(f"**Question:** {result['question']}\n")

    if result.get("mode") == "chatbot_baseline":
        lines.append("**Hệ thống:** Chatbot Baseline (Cấp 2 — 1 LLM call, 0 tool call)\n")
        lines.append("```text")
        lines.append(result["answer"])
        lines.append("```\n")
        lines.append(f"- LLM calls: {result['llm_calls']} | Tool calls: {result['tool_calls']} "
                     f"| Latency: {result['latency']:.2f}s\n")
        return "\n".join(lines)

    lines.append("**Hệ thống:** ReAct Agent V2 (Cấp 3 — Thought → Action → Observation)\n")
    lines.append("```text")
    lines.append(f"Question: {result['question']}\n")
    for step in result["steps"]:
        lines.append(f"Thought: {step['thought']}")
        if step["tool"]:
            lines.append(f"Action: {step['tool']}[{step['tool_args']}]")
        if step["observation"]:
            lines.append(f"Observation: {step['observation']}")
        if step["final_answer"]:
            lines.append(f"Final Answer: {step['final_answer']}")
        lines.append("")
    if result["stop_reason"] != "final_answer":
        lines.append(f"[SAFE FALLBACK - {result['stop_reason']}] {result['final_answer']}")
    lines.append("```\n")
    lines.append(f"- LLM calls: {result['llm_calls']} | Tool calls: {result['tool_calls']} "
                 f"| Steps: {result['iterations']} | Latency: {result['latency']:.2f}s "
                 f"| Stop reason: `{result['stop_reason']}`\n")

    if case:
        report = evaluate_case(case, result)
        lines.append(f"- **Tool selection:** {report['tool_verdict']}")
        lines.append(f"- **Guardrail:** {report['guardrail_verdict']}")
        lines.append(f"- **Termination:** {report['termination_verdict']}")
        lines.append(f"- **Kỳ vọng (test_cases.json):** {case.get('expected_behavior', '')}\n")
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════════
# 🖥️ GIAO DIỆN WEB (STREAMLIT) — chạy bằng:  streamlit run src/app.py
# ═══════════════════════════════════════════════════════════════════════════════

# Mô tả / ví dụ tham số cho Tool Playground (khớp với 8 tool trong src/tools.py)
TOOL_ARG_EXAMPLES = {
    "get_candidate": '"CAND-01"',
    "filter_candidates": "min_score=80, min_experience_years=1.0",
    "rank_candidates": "top_k=5",
    "verify_candidate": '"CAND-49"',
    "detect_duplicates": "",
    "draft_interview_email": '"CAND-01, CAND-03", "09:00 - 11:30 Thứ Ba tuần sau"',
    "schedule_interview": '"CAND-01", "09:00 - 09:30 Thứ Ba 05/08/2026"',
    "send_email": '"CAND-01", "Nội dung thư mời đã được duyệt"',
}

API_KEY_ENV = {
    "gemini": "GEMINI_API_KEY",
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
    "mock": None,
}
DEFAULT_MODEL = {
    "gemini": "gemini-2.5-flash",
    "openai": "gpt-4o-mini",
    "anthropic": "claude-3-haiku-20240307",
    "openrouter": "google/gemini-2.5-flash",
    "mock": "offline-mock-v2",
}

_UI_CSS = """
<style>
  .block-container { padding-top: 2.2rem; max-width: 1500px; }
  .hero {
    background: linear-gradient(120deg, #0f2557 0%, #1d4ed8 55%, #0891b2 100%);
    color: #fff; padding: 1.4rem 1.8rem; border-radius: 14px; margin-bottom: 1.2rem;
  }
  .hero h1 { margin: 0; font-size: 1.65rem; font-weight: 700; }
  .hero p  { margin: .35rem 0 0; opacity: .9; font-size: .95rem; }
  .step-card {
    border-radius: 10px; padding: .7rem .95rem; margin-bottom: .6rem;
    border-left: 5px solid #94a3b8; background: rgba(148,163,184,.10);
  }
  .step-thought     { border-left-color:#3b82f6; background:rgba(59,130,246,.10); }
  .step-action      { border-left-color:#f59e0b; background:rgba(245,158,11,.10); }
  .step-observation { border-left-color:#10b981; background:rgba(16,185,129,.10); }
  .step-error       { border-left-color:#ef4444; background:rgba(239,68,68,.10); }
  .step-guardrail   { border-left-color:#a855f7; background:rgba(168,85,247,.12); }
  .step-final       { border-left-color:#22c55e; background:rgba(34,197,94,.14); }
  .step-label {
    font-size: .74rem; font-weight: 700; letter-spacing: .05em;
    text-transform: uppercase; opacity: .75; margin-bottom: .2rem;
  }
  .step-body { white-space: pre-wrap; font-size: .89rem; line-height: 1.45; }
</style>
"""


def running_under_streamlit() -> bool:
    """
    Phân biệt `streamlit run src/app.py` với `python src/app.py`.

    Cần hàm này vì CẢ HAI cách chạy đều khiến __name__ == "__main__",
    nên không thể dựa vào __name__ để chọn chế độ.
    """
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        return get_script_run_ctx() is not None
    except Exception:
        return False


def render_streamlit_ui():
    """
    Toàn bộ giao diện Web gồm 6 tab:
      ⚖️ So sánh · 🤖 ReAct Agent · 🧪 Test Suite ·
      👥 Hồ sơ ứng viên · 🛠️ Tool Playground · 🧠 Prompts & Guardrails
    """
    import streamlit as st

    st.set_page_config(
        page_title="Lab 03 — Chatbot vs ReAct Agent | VinUni",
        page_icon="🤖",
        layout="wide",
    )
    st.markdown(_UI_CSS, unsafe_allow_html=True)
    st.markdown(
        """
        <div class="hero">
          <h1>🤖 Lab 03 — Chatbot Baseline vs ReAct Agent</h1>
          <p>Trợ lý sàng lọc hồ sơ tuyển sinh · Chương trình Đào tạo AI Thực Chiến · VinUniversity</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    test_cases = load_test_cases()
    candidates = load_candidates()

    # ─────────────────────────────────────────────────────────────── SIDEBAR ──
    with st.sidebar:
        st.header("⚙️ Cấu hình")

        provider_options = ["mock", "gemini", "openai", "anthropic", "openrouter"]
        env_provider = (os.getenv("LLM_PROVIDER") or "mock").lower().strip()
        provider_name = st.selectbox(
            "🔌 LLM Provider",
            provider_options,
            index=provider_options.index(env_provider) if env_provider in provider_options else 0,
            help="mock = chạy offline deterministic, không tốn API key.",
        )

        model_name = st.text_input(
            "🧬 Model",
            value=os.getenv("LLM_MODEL") or DEFAULT_MODEL[provider_name],
            help="Để trống để dùng model mặc định của provider.",
        )

        key_env = API_KEY_ENV[provider_name]
        if key_env:
            key_value = os.getenv(key_env, "")
            if key_value and not key_value.startswith("your_"):
                st.success(f"✅ Đã có {key_env} (…{key_value[-4:]})")
            else:
                st.error(f"❌ Thiếu {key_env} trong file .env")
        else:
            st.info("🧪 Chế độ offline — không cần API key")

        st.divider()
        st.subheader("🛡️ Guardrails")
        max_iters = st.slider(
            "MAX_ITERATIONS", 1, 12, MAX_ITERATIONS,
            help="Phanh an toàn: số vòng Thought→Action tối đa trước khi Safe Fallback.",
        )
        approval_mode = st.radio(
            "Phê duyệt hành động nguy hiểm",
            ["Tự suy ra từ câu hỏi", "Đã phê duyệt ✅", "Chưa phê duyệt 🔒"],
            help=f"Áp dụng cho: {', '.join(sorted(APPROVAL_REQUIRED_TOOLS))}",
        )
        approval_granted = {
            "Tự suy ra từ câu hỏi": None,
            "Đã phê duyệt ✅": True,
            "Chưa phê duyệt 🔒": False,
        }[approval_mode]

        st.caption(
            f"ENABLE_GUARDRAILS = `{ENABLE_GUARDRAILS}` · "
            f"MAX_TOOL_ERRORS = `{MAX_TOOL_ERRORS}` · TIMEOUT = `{TIMEOUT_SECONDS}s`"
        )

        st.divider()
        st.metric("📋 Test cases", len(test_cases))
        st.metric("👥 Hồ sơ ứng viên", len(candidates))
        st.metric("🛠️ Tools đăng ký", len(AVAILABLE_TOOLS))

    # Khởi tạo provider theo lựa chọn trên sidebar (ghi đè biến môi trường)
    os.environ["LLM_PROVIDER"] = provider_name
    os.environ["LLM_MODEL"] = (model_name or "").strip()
    provider = get_llm_provider(provider_name)

    # ──────────────────────────────────────── COMPONENT: vẽ trace ReAct ──
    def card(css_class, label, body):
        safe = str(body).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        return (f'<div class="step-card {css_class}">'
                f'<div class="step-label">{label}</div>'
                f'<div class="step-body">{safe}</div></div>')

    def render_step(container, step):
        """Vẽ 1 bước ReAct: Thought → Action → Observation (hoặc Final Answer)."""
        with container:
            st.markdown(f"**🔄 Step {step['step']}**")
            st.markdown(card("step-thought", "🧠 Thought", step["thought"]),
                        unsafe_allow_html=True)

            if step["tool"]:
                st.markdown(card("step-action", "🛠️ Action",
                                 f"{step['tool']}[{step['tool_args']}]"),
                            unsafe_allow_html=True)

            if step["observation"]:
                is_guard = str(step["observation"]).startswith("🛡️")
                css = "step-guardrail" if is_guard else (
                    "step-error" if step["is_error"] else "step-observation")
                label = "🛡️ Guardrail" if is_guard else (
                    "⚠️ Observation (Lỗi)" if step["is_error"] else "👁️ Observation")
                st.markdown(card(css, label, step["observation"]), unsafe_allow_html=True)

            if step["final_answer"]:
                st.markdown(card("step-final", "🏁 Final Answer", step["final_answer"]),
                            unsafe_allow_html=True)

    def render_agent_result(result, show_steps=True):
        """Vẽ kết luận + telemetry của 1 lần chạy Agent."""
        if show_steps:
            holder = st.container()
            for step in result["steps"]:
                render_step(holder, step)

        if result["stop_reason"] != "final_answer":
            st.warning(f"🛡️ **Safe Fallback** (`{result['stop_reason']}`) — {result['final_answer']}")
        else:
            st.success(f"🏁 **Final Answer:** {result['final_answer']}")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("LLM calls", result["llm_calls"])
        c2.metric("Tool calls", result["tool_calls"])
        c3.metric("Steps", f"{result['iterations']}/{max_iters}")
        c4.metric("Latency", f"{result['latency']:.2f}s")

    tab_compare, tab_agent, tab_suite, tab_cands, tab_tools, tab_prompts = st.tabs(
        ["⚖️ So sánh", "🤖 ReAct Agent", "🧪 Test Suite", "👥 Hồ sơ ứng viên",
         "🛠️ Tool Playground", "🧠 Prompts & Guardrails"]
    )

    # ───────────────────────────────────────────────────── TAB 1: SO SÁNH ──
    with tab_compare:
        st.subheader("⚖️ Cùng một câu hỏi — hai kiến trúc")
        st.caption(
            "Chatbot Baseline (Cấp 2): đúng 1 LLM call, 0 tool call → trả lời mượt nhưng "
            "**không có bằng chứng**. ReAct Agent (Cấp 3): Thought → Action → Observation "
            "trên dữ liệu thật."
        )

        case_labels = ["✍️ Câu hỏi tự do"] + [
            f"#{c['id']} {c['category']} — {c['question'][:70]}…" for c in test_cases
        ]
        picked = st.selectbox("Chọn test case", case_labels, key="cmp_case")

        if picked == case_labels[0]:
            selected_case, default_q = None, ""
        else:
            selected_case = test_cases[case_labels.index(picked) - 1]
            default_q = selected_case["question"]

        # Widget đã có key thì tham số value= bị bỏ qua ở các lần rerun sau,
        # nên phải chủ động đồng bộ session_state mỗi khi đổi test case.
        if st.session_state.get("_cmp_last_case") != picked:
            st.session_state["cmp_query"] = default_q
            st.session_state["_cmp_last_case"] = picked

        query = st.text_area("Câu hỏi", height=90, key="cmp_query")

        if selected_case:
            with st.expander("📌 Kỳ vọng của test case này (config/test_cases.json)"):
                st.markdown(f"**Expected behavior:** {selected_case['expected_behavior']}")
                st.markdown(f"**Guardrail:** {selected_case['guardrail']}")
                st.markdown(f"**Pass criteria:** {selected_case['pass_criteria']}")
                st.markdown(f"**Expected tools:** "
                            f"`{', '.join(selected_case['expected_tools']) or '(không cần tool)'}`")
                st.markdown("**Fail signals:** "
                            + " · ".join(f"❌ {s}" for s in selected_case["fail_signals"]))

        if st.button("▶️ Chạy trên cả hai hệ thống", type="primary", disabled=not query.strip()):
            col_bot, col_agent = st.columns(2)

            with col_bot:
                st.markdown("### 💬 Chatbot Baseline")
                st.caption("Cấp 2 · 1 LLM call · 0 tool")
                with st.spinner("Đang gọi LLM…"):
                    baseline = run_baseline_chatbot(query, provider, verbose=False)
                st.info(baseline["answer"])
                b1, b2, b3 = st.columns(3)
                b1.metric("LLM calls", baseline["llm_calls"])
                b2.metric("Tool calls", baseline["tool_calls"])
                b3.metric("Latency", f"{baseline['latency']:.2f}s")
                st.error("⚠️ Không có Observation nào — mọi con số trong câu trả lời đều "
                         "**không có bằng chứng**.")

            with col_agent:
                st.markdown("### 🤖 ReAct Agent V2")
                st.caption("Cấp 3 · Thought → Action → Observation")
                live = st.container()
                with st.spinner("Agent đang suy luận…"):
                    agent = run_react_agent(
                        query, provider,
                        approval_granted=approval_granted,
                        max_iterations=max_iters,
                        verbose=False,
                        on_event=lambda step: render_step(live, step),
                    )
                render_agent_result(agent, show_steps=False)

            st.divider()
            st.markdown("### 📊 Bảng so sánh")
            # Giữ mọi ô ở kiểu chuỗi để bảng không lỗi khi trộn số và ký hiệu ✅/❌
            st.dataframe(
                [
                    {"Tiêu chí": "Số LLM call", "💬 Chatbot": str(baseline["llm_calls"]),
                     "🤖 ReAct Agent": str(agent["llm_calls"])},
                    {"Tiêu chí": "Số Tool call", "💬 Chatbot": str(baseline["tool_calls"]),
                     "🤖 ReAct Agent": str(agent["tool_calls"])},
                    {"Tiêu chí": "Có bằng chứng (Grounding)", "💬 Chatbot": "❌ Không",
                     "🤖 ReAct Agent": "✅ Có" if agent["tool_calls"] else "❌ Không"},
                    {"Tiêu chí": "Độ trễ (giây)", "💬 Chatbot": f"{baseline['latency']:.2f}",
                     "🤖 ReAct Agent": f"{agent['latency']:.2f}"},
                    {"Tiêu chí": "Cách dừng", "💬 Chatbot": "1 lượt",
                     "🤖 ReAct Agent": agent["stop_reason"]},
                ],
                hide_index=True, width="stretch",
            )

            if selected_case:
                report = evaluate_case(selected_case, agent)
                st.markdown("### 🎯 Tự chấm theo Rubric")
                r1, r2, r3 = st.columns(3)
                r1.markdown(f"**Tool selection**\n\n{report['tool_verdict']}")
                r2.markdown(f"**Guardrail**\n\n{report['guardrail_verdict']}")
                r3.markdown(f"**Termination**\n\n{report['termination_verdict']}")

            st.download_button(
                "📥 Tải trace (Markdown cho docs/trace_eval.md)",
                data=trace_to_markdown(baseline, selected_case) + "\n"
                     + trace_to_markdown(agent, selected_case),
                file_name="trace_eval_snippet.md",
                mime="text/markdown",
            )

    # ────────────────────────────────────────────────── TAB 2: REACT AGENT ──
    with tab_agent:
        st.subheader("🤖 Hội thoại với ReAct Agent")
        st.caption(
            "Mỗi lượt là một vòng lặp ReAct độc lập. Dùng để test kịch bản 2 lượt: "
            "lượt 1 Agent xin phê duyệt → lượt 2 bạn trả lời *“Tôi đã duyệt, hãy gửi”*."
        )

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        col_a, col_b = st.columns([1, 5])
        if col_a.button("🗑️ Xóa hội thoại"):
            st.session_state.chat_history = []
            st.rerun()
        col_b.caption(f"Đang dùng: **{provider.__class__.__name__}** · "
                      f"`{getattr(provider, 'model_name', 'n/a')}` · "
                      f"MAX_ITERATIONS = `{max_iters}`")

        for turn in st.session_state.chat_history:
            with st.chat_message("user"):
                st.write(turn["question"])
            with st.chat_message("assistant"):
                with st.expander(f"🔍 Trace ReAct — {turn['result']['iterations']} step, "
                                 f"{turn['result']['tool_calls']} tool call"):
                    holder = st.container()
                    for step in turn["result"]["steps"]:
                        render_step(holder, step)
                if turn["result"]["stop_reason"] != "final_answer":
                    st.warning(f"🛡️ Safe Fallback — {turn['result']['final_answer']}")
                else:
                    st.success(turn["result"]["final_answer"])

        user_input = st.chat_input("Nhập câu hỏi… (VD: Ứng viên CAND-01 có phù hợp không?)")
        if user_input:
            with st.chat_message("user"):
                st.write(user_input)
            with st.chat_message("assistant"):
                live = st.container()
                with st.spinner("Agent đang suy luận…"):
                    result = run_react_agent(
                        user_input, provider,
                        approval_granted=approval_granted,
                        max_iterations=max_iters,
                        verbose=False,
                        on_event=lambda step: render_step(live, step),
                    )
                render_agent_result(result, show_steps=False)
            st.session_state.chat_history.append({"question": user_input, "result": result})

    # ─────────────────────────────────────────────────── TAB 3: TEST SUITE ──
    with tab_suite:
        st.subheader("🧪 Chạy hàng loạt Test Cases & tự chấm Rubric")
        st.caption("Chạy nhiều case một lượt, đối chiếu tool thực gọi với `expected_tools`, "
                   "rồi xuất báo cáo Markdown cho `docs/trace_eval.md` (Role 5).")

        categories = sorted({c["category"] for c in test_cases})
        picked_cats = st.multiselect("Lọc theo nhóm", categories, default=categories)
        pool = [c for c in test_cases if c["category"] in picked_cats]

        picked_ids = st.multiselect(
            "Chọn test case cần chạy",
            [c["id"] for c in pool],
            default=[c["id"] for c in pool][:3],
            format_func=lambda i: f"#{i} — "
                                  f"{next(c for c in test_cases if c['id'] == i)['question'][:60]}…",
        )
        run_baseline_too = st.checkbox("Chạy kèm Chatbot Baseline để so sánh", value=False)

        if st.button("▶️ Chạy batch", type="primary", disabled=not picked_ids):
            rows, markdown_parts = [], ["# 📊 Báo cáo Trace & Evaluation\n"]
            progress = st.progress(0.0, text="Đang chạy…")

            for idx, case_id in enumerate(picked_ids, 1):
                case = next(c for c in test_cases if c["id"] == case_id)
                progress.progress(idx / len(picked_ids), text=f"Test case #{case_id}…")

                agent = run_react_agent(
                    case["question"], provider,
                    approval_granted=approval_granted,
                    max_iterations=max_iters,
                    verbose=False,
                )
                report = evaluate_case(case, agent)

                row = {
                    "#": case_id,
                    "Nhóm": case["category"],
                    "Tool gọi thật": ", ".join(report["tools_succeeded"]) or "—",
                    "Tool kỳ vọng": ", ".join(report["expected_tools"]) or "—",
                    "Tool selection": report["tool_verdict"],
                    "Guardrail": report["guardrail_verdict"],
                    "Termination": report["termination_verdict"],
                    "Steps": agent["iterations"],
                    "Giây": round(agent["latency"], 2),
                }
                markdown_parts.append(trace_to_markdown(agent, case))

                if run_baseline_too:
                    baseline = run_baseline_chatbot(case["question"], provider, verbose=False)
                    row["Chatbot (giây)"] = round(baseline["latency"], 2)
                    markdown_parts.append(trace_to_markdown(baseline, case))

                rows.append(row)
                st.session_state.setdefault("suite_traces", {})[case_id] = (case, agent)

            progress.empty()
            st.session_state["suite_rows"] = rows
            st.session_state["suite_md"] = "\n---\n\n".join(markdown_parts)

        if st.session_state.get("suite_rows"):
            st.markdown("### 📋 Kết quả")
            st.dataframe(st.session_state["suite_rows"], hide_index=True, width="stretch")

            suite_rows = st.session_state["suite_rows"]
            ok = sum(1 for r in suite_rows if r["Tool selection"].startswith("✅"))
            clean = sum(1 for r in suite_rows if not r["Guardrail"].startswith("❌"))
            total = len(suite_rows)
            m1, m2, m3 = st.columns(3)
            m1.metric("Tool selection đạt", f"{ok}/{total}")
            m2.metric("Không vi phạm Guardrail", f"{clean}/{total}")
            m3.metric("Tổng case đã chạy", total)

            st.download_button(
                "📥 Tải toàn bộ báo cáo (Markdown)",
                data=st.session_state["suite_md"],
                file_name="trace_eval_batch.md",
                mime="text/markdown",
                type="primary",
            )

            for case_id, (case, agent) in st.session_state.get("suite_traces", {}).items():
                with st.expander(f"🔍 Trace chi tiết — Test Case #{case_id}"):
                    holder = st.container()
                    for step in agent["steps"]:
                        render_step(holder, step)
                    st.markdown(f"**🏁 Kết luận:** {agent['final_answer']}")

    # ─────────────────────────────────────────────── TAB 4: HỒ SƠ ỨNG VIÊN ──
    with tab_cands:
        st.subheader("👥 50 hồ sơ ứng viên (config/candidates.json)")

        f1, f2, f3 = st.columns(3)
        min_score = f1.slider("Điểm thi tối thiểu", 0, 100, 0)
        min_exp = f2.slider("Kinh nghiệm tối thiểu (năm)", 0.0, 10.0, 0.0, step=0.5)
        only_verified = f3.checkbox("Chỉ hồ sơ đã xác minh điểm thi", value=False)

        filtered = [
            c for c in candidates
            if c.get("exam_score", 0) >= min_score
            and c.get("years_relevant_experience", 0) >= min_exp
            and (not only_verified or c.get("exam_verified", False))
        ]

        st.caption(f"Hiển thị **{len(filtered)}/{len(candidates)}** hồ sơ")
        st.dataframe(
            [
                {
                    "Mã": c.get("candidate_id"),
                    "Điểm": c.get("exam_score"),
                    "Xác minh": "✅" if c.get("exam_verified") else "❌",
                    "KN (năm)": c.get("years_relevant_experience"),
                    "Học vấn": c.get("education", "")[:55],
                    "Người giới thiệu": c.get("recommendation", {}).get("referee_type", "—"),
                    "GT đã xác minh": "✅" if c.get("recommendation", {}).get("contact_verified") else "❌",
                }
                for c in filtered
            ],
            hide_index=True, width="stretch", height=420,
        )

        st.divider()
        pick_id = st.selectbox("🔎 Xem chi tiết hồ sơ",
                               [c.get("candidate_id") for c in candidates])
        detail = next(c for c in candidates if c.get("candidate_id") == pick_id)

        d1, d2, d3 = st.columns(3)
        d1.metric("Điểm thi", f"{detail.get('exam_score')}/100",
                  "Đã xác minh" if detail.get("exam_verified") else "CHƯA xác minh")
        d2.metric("Kinh nghiệm", f"{detail.get('years_relevant_experience')} năm")
        d3.metric("Thư giới thiệu",
                  detail.get("recommendation", {}).get("referee_type", "—"),
                  "Đã xác minh" if detail.get("recommendation", {}).get("contact_verified")
                  else "CHƯA xác minh")

        st.text(AVAILABLE_TOOLS["get_candidate"](pick_id))
        with st.expander("🔎 Chạy verify_candidate trên hồ sơ này"):
            st.text(AVAILABLE_TOOLS["verify_candidate"](pick_id))
        with st.expander("📄 JSON gốc"):
            st.json(detail)

    # ─────────────────────────────────────────────── TAB 5: TOOL PLAYGROUND ──
    with tab_tools:
        st.subheader("🛠️ Thử từng tool độc lập")
        st.caption("Test tool riêng TRƯỚC khi gắn vào Agent — để biết lỗi nằm ở Tool hay ở Agent.")

        tool_name = st.selectbox("Chọn tool", list(AVAILABLE_TOOLS.keys()))
        func = AVAILABLE_TOOLS[tool_name]

        if tool_name in APPROVAL_REQUIRED_TOOLS:
            st.warning(f"⚠️ `{tool_name}` là hành động có tác dụng phụ — Agent bị Guardrail chặn "
                       "nếu chưa có phê duyệt tường minh.")

        st.code((func.__doc__ or "").strip(), language="text")

        args_str = st.text_input(
            "Tham số (đúng cú pháp Agent sẽ sinh ra)",
            value=TOOL_ARG_EXAMPLES.get(tool_name, ""),
            placeholder='VD: "CAND-01"  hoặc  top_k=5',
        )
        bypass = st.checkbox("Bỏ qua Guardrail phê duyệt (chỉ để kiểm thử tool)", value=False)

        if st.button("▶️ Gọi tool", type="primary"):
            observation, is_error = execute_tool(tool_name, args_str, approval_granted=bypass)
            st.markdown(f"**Action:** `{tool_name}[{args_str}]`")
            if is_error:
                st.error(observation)
            else:
                st.success("✅ Tool chạy thành công — đây là Observation THẬT")
                st.text(observation)

        st.divider()
        st.markdown("### 📚 Tool Registry")
        st.dataframe(
            [
                {
                    "Tool": name,
                    "Tham số": str(inspect.signature(fn)),
                    "Side-effect": "⚠️ Có (cần phê duyệt)" if name in APPROVAL_REQUIRED_TOOLS
                                   else "Read-only",
                    "Mô tả": (fn.__doc__ or "").strip().split("\n")[0],
                }
                for name, fn in AVAILABLE_TOOLS.items()
            ],
            hide_index=True, width="stretch",
        )

    # ───────────────────────────────────────────────────── TAB 6: PROMPTS ──
    with tab_prompts:
        st.subheader("🧠 System Prompts & Guardrails (Role 3)")

        g1, g2, g3, g4 = st.columns(4)
        g1.metric("MAX_ITERATIONS", MAX_ITERATIONS)
        g2.metric("MAX_TOOL_ERRORS", MAX_TOOL_ERRORS)
        g3.metric("TIMEOUT_SECONDS", TIMEOUT_SECONDS)
        g4.metric("GUARDRAILS", "BẬT" if ENABLE_GUARDRAILS else "TẮT")

        st.info(f"**SAFE_FALLBACK_RESPONSE:** {SAFE_FALLBACK_RESPONSE}")

        st.markdown("#### 🛡️ Guardrails được cài đặt trong `src/app.py`")
        st.dataframe(
            [
                {"Guardrail": "MAX_ITERATIONS", "Chống": "Lặp vô hạn",
                 "Cài đặt tại": "run_react_agent() — vòng while"},
                {"Guardrail": "Chặn lặp Action trùng", "Chống": "Gọi lại y hệt tool + tham số",
                 "Cài đặt tại": "called_signatures"},
                {"Guardrail": "Unknown tool", "Chống": "LLM bịa tên tool",
                 "Cài đặt tại": "execute_tool()"},
                {"Guardrail": "Approval required",
                 "Chống": f"Tự ý chạy {', '.join(sorted(APPROVAL_REQUIRED_TOOLS))}",
                 "Cài đặt tại": "execute_tool()"},
                {"Guardrail": "Chống Observation bịa đặt", "Chống": "LLM tự viết Observation giả",
                 "Cài đặt tại": "_strip_hallucinated_observation()"},
                {"Guardrail": "MAX_TOOL_ERRORS", "Chống": "Agent kẹt trong chuỗi lỗi",
                 "Cài đặt tại": "consecutive_errors"},
                {"Guardrail": "Safe Fallback", "Chống": "Crash / im lặng khi chạm phanh",
                 "Cài đặt tại": "SAFE_FALLBACK_RESPONSE"},
            ],
            hide_index=True, width="stretch",
        )

        with st.expander("💬 CHATBOT_BASELINE_PROMPT (Cấp 2)"):
            st.code(CHATBOT_BASELINE_PROMPT, language="markdown")
        with st.expander("🤖 REACT_SYSTEM_PROMPT (Cấp 3 — Agent V2)"):
            st.code(REACT_SYSTEM_PROMPT, language="markdown")


# ═══════════════════════════════════════════════════════════════════════════════
# 🖥️ CLI MODE — chạy bằng:  python src/app.py [số thứ tự test case]
# ═══════════════════════════════════════════════════════════════════════════════

def run_cli():
    """Demo dòng lệnh: chạy 1 test case trên cả Chatbot Baseline và ReAct Agent."""
    print("==================================================")
    print("🏫 ĐẠI HỌC VINUNI - BÀI LAB 3: CHATBOT VS REACT AGENT")
    print("   Đề tài: Trợ lý sàng lọc hồ sơ tuyển sinh AI Thực Chiến")
    print("==================================================")

    # Khởi tạo Multi-Provider LLM Adapter (Đọc từ biến môi trường LLM_PROVIDER)
    provider = get_llm_provider()
    model_name = getattr(provider, "model_name", "Offline Mock Mode")
    print(f"🔌 LLM Provider đang hoạt động: {provider.__class__.__name__} (Model: {model_name})")

    tests = load_test_cases()
    candidates = load_candidates()
    print(f"✅ Đã tải {len(tests)} Test Cases từ config/test_cases.json")
    print(f"✅ Đã tải {len(candidates)} hồ sơ ứng viên từ config/candidates.json")
    print(f"🛠️ Tool Registry: {len(AVAILABLE_TOOLS)} tools → {', '.join(AVAILABLE_TOOLS.keys())}\n")

    # Chọn test case theo tham số dòng lệnh: python src/app.py 11
    case_index = 0
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        case_index = max(0, min(int(sys.argv[1]) - 1, len(tests) - 1))

    case = tests[case_index]
    print(f"🎯 TEST CASE #{case['id']} — {case['category']}")
    print(f"❓ {case['question']}\n")

    print("--- DEMO 1: CHẠY TRÊN CHATBOT BASELINE (Cấp 2) ---")
    run_baseline_chatbot(case["question"], provider)

    print("\n--- DEMO 2: CHẠY TRÊN REACT AGENT (Cấp 3) ---")
    agent = run_react_agent(case["question"], provider)

    report = evaluate_case(case, agent)
    print("\n--- 🎯 TỰ CHẤM THEO RUBRIC ---")
    print(f"Tool selection : {report['tool_verdict']}")
    print(f"Guardrail      : {report['guardrail_verdict']}")
    print(f"Termination    : {report['termination_verdict']}")

    print("\n==================================================")
    print("💡 Mở giao diện Web:    streamlit run src/app.py")
    print("💡 Chạy test case khác: python src/app.py 11")
    print("==================================================")


# ═══════════════════════════════════════════════════════════════════════════════
# 🚦 ENTRY POINT — một file phục vụ cả 2 chế độ chạy
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Lưu ý: cả `python src/app.py` lẫn `streamlit run src/app.py` đều khiến
    # __name__ == "__main__", nên phải dò context của Streamlit để chọn chế độ.
    if running_under_streamlit():
        render_streamlit_ui()
    else:
        run_cli()
