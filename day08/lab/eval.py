# """
# eval.py — Sprint 4: Evaluation & Scorecard
# ==========================================
# Mục tiêu Sprint 4 (60 phút):
#   - Chạy 10 test questions qua pipeline
#   - Chấm điểm theo 4 metrics: Faithfulness, Relevance, Context Recall, Completeness
#   - So sánh baseline vs variant
#   - Ghi kết quả ra scorecard

# Definition of Done Sprint 4:
#   ✓ Demo chạy end-to-end (index → retrieve → answer → score)
#   ✓ Scorecard trước và sau tuning
#   ✓ A/B comparison: baseline vs variant với giải thích vì sao variant tốt hơn

# A/B Rule (từ slide):
#   Chỉ đổi MỘT biến mỗi lần để biết điều gì thực sự tạo ra cải thiện.
#   Đổi đồng thời chunking + hybrid + rerank + prompt = không biết biến nào có tác dụng.
# """

# import json
# import csv
# from pathlib import Path
# from typing import List, Dict, Any, Optional
# from datetime import datetime
# from rag_answer import rag_answer

# # =============================================================================
# # CẤU HÌNH
# # =============================================================================

# TEST_QUESTIONS_PATH = Path(__file__).parent / "data" / "test_questions.json"
# RESULTS_DIR = Path(__file__).parent / "results"

# # Cấu hình baseline (Sprint 2)
# BASELINE_CONFIG = {
#     "retrieval_mode": "dense",
#     "top_k_search": 10,
#     "top_k_select": 3,
#     "use_rerank": False,
#     "label": "baseline_dense",
# }

# # Cấu hình variant (Sprint 3 — điều chỉnh theo lựa chọn của nhóm)
# # TODO Sprint 4: Cập nhật VARIANT_CONFIG theo variant nhóm đã implement
# VARIANT_CONFIG = {
#     "retrieval_mode": "hybrid",   # Hoặc "dense" nếu chỉ đổi rerank
#     "top_k_search": 10,
#     "top_k_select": 3,
#     "use_rerank": True,           # Hoặc False nếu variant là hybrid không rerank
#     "label": "variant_hybrid_rerank",
# }


# # =============================================================================
# # SCORING FUNCTIONS
# # 4 metrics từ slide: Faithfulness, Answer Relevance, Context Recall, Completeness
# # =============================================================================

# def score_faithfulness(
#     answer: str,
#     chunks_used: List[Dict[str, Any]],
# ) -> Dict[str, Any]:
#     """
#     Faithfulness: Câu trả lời có bám đúng chứng cứ đã retrieve không?
#     Câu hỏi: Model có tự bịa thêm thông tin ngoài retrieved context không?

#     Thang điểm 1-5:
#       5: Mọi thông tin trong answer đều có trong retrieved chunks
#       4: Gần như hoàn toàn grounded, 1 chi tiết nhỏ chưa chắc chắn
#       3: Phần lớn grounded, một số thông tin có thể từ model knowledge
#       2: Nhiều thông tin không có trong retrieved chunks
#       1: Câu trả lời không grounded, phần lớn là model bịa

#     TODO Sprint 4 — Có 2 cách chấm:

#     Cách 1 — Chấm thủ công (Manual, đơn giản):
#         Đọc answer và chunks_used, chấm điểm theo thang trên.
#         Ghi lý do ngắn gọn vào "notes".

#     Cách 2 — LLM-as-Judge (Tự động, nâng cao):
#         Gửi prompt cho LLM:
#             "Given these retrieved chunks: {chunks}
#              And this answer: {answer}
#              Rate the faithfulness on a scale of 1-5.
#              5 = completely grounded in the provided context.
#              1 = answer contains information not in the context.
#              Output JSON: {'score': <int>, 'reason': '<string>'}"

#     Trả về dict với: score (1-5) và notes (lý do)
#     """
#     # TODO Sprint 4: Implement scoring
#     # Tạm thời trả về None (yêu cầu chấm thủ công)
#     return {
#         "score": None,
#         "notes": "TODO: Chấm thủ công hoặc implement LLM-as-Judge",
#     }


# def score_answer_relevance(
#     query: str,
#     answer: str,
# ) -> Dict[str, Any]:
#     """
#     Answer Relevance: Answer có trả lời đúng câu hỏi người dùng hỏi không?
#     Câu hỏi: Model có bị lạc đề hay trả lời đúng vấn đề cốt lõi không?

#     Thang điểm 1-5:
#       5: Answer trả lời trực tiếp và đầy đủ câu hỏi
#       4: Trả lời đúng nhưng thiếu vài chi tiết phụ
#       3: Trả lời có liên quan nhưng chưa đúng trọng tâm
#       2: Trả lời lạc đề một phần
#       1: Không trả lời câu hỏi

#     TODO Sprint 4: Implement tương tự score_faithfulness
#     """
#     return {
#         "score": None,
#         "notes": "TODO: Implement score_answer_relevance",
#     }


# def score_context_recall(
#     chunks_used: List[Dict[str, Any]],
#     expected_sources: List[str],
# ) -> Dict[str, Any]:
#     """
#     Context Recall: Retriever có mang về đủ evidence cần thiết không?
#     Câu hỏi: Expected source có nằm trong retrieved chunks không?

#     Đây là metric đo retrieval quality, không phải generation quality.

#     Cách tính đơn giản:
#         recall = (số expected source được retrieve) / (tổng số expected sources)

#     Ví dụ:
#         expected_sources = ["policy/refund-v4.pdf", "sla-p1-2026.pdf"]
#         retrieved_sources = ["policy/refund-v4.pdf", "helpdesk-faq.md"]
#         recall = 1/2 = 0.5

#     TODO Sprint 4:
#     1. Lấy danh sách source từ chunks_used
#     2. Kiểm tra xem expected_sources có trong retrieved sources không
#     3. Tính recall score
#     """
#     if not expected_sources:
#         # Câu hỏi không có expected source (ví dụ: "Không đủ dữ liệu" cases)
#         return {"score": None, "recall": None, "notes": "No expected sources"}

#     retrieved_sources = {
#         c.get("metadata", {}).get("source", "")
#         for c in chunks_used
#     }

#     # TODO: Kiểm tra matching theo partial path (vì source paths có thể khác format)
#     found = 0
#     missing = []
#     for expected in expected_sources:
#         # Kiểm tra partial match (tên file)
#         expected_name = expected.split("/")[-1].replace(".pdf", "").replace(".md", "")
#         matched = any(expected_name.lower() in r.lower() for r in retrieved_sources)
#         if matched:
#             found += 1
#         else:
#             missing.append(expected)

#     recall = found / len(expected_sources) if expected_sources else 0

#     return {
#         "score": round(recall * 5),  # Convert to 1-5 scale
#         "recall": recall,
#         "found": found,
#         "missing": missing,
#         "notes": f"Retrieved: {found}/{len(expected_sources)} expected sources" +
#                  (f". Missing: {missing}" if missing else ""),
#     }


# def score_completeness(
#     query: str,
#     answer: str,
#     expected_answer: str,
# ) -> Dict[str, Any]:
#     """
#     Completeness: Answer có thiếu điều kiện ngoại lệ hoặc bước quan trọng không?
#     Câu hỏi: Answer có bao phủ đủ thông tin so với expected_answer không?

#     Thang điểm 1-5:
#       5: Answer bao gồm đủ tất cả điểm quan trọng trong expected_answer
#       4: Thiếu 1 chi tiết nhỏ
#       3: Thiếu một số thông tin quan trọng
#       2: Thiếu nhiều thông tin quan trọng
#       1: Thiếu phần lớn nội dung cốt lõi

#     TODO Sprint 4:
#     Option 1 — Chấm thủ công: So sánh answer vs expected_answer và chấm.
#     Option 2 — LLM-as-Judge:
#         "Compare the model answer with the expected answer.
#          Rate completeness 1-5. Are all key points covered?
#          Output: {'score': int, 'missing_points': [str]}"
#     """
#     return {
#         "score": None,
#         "notes": "TODO: Implement score_completeness (so sánh với expected_answer)",
#     }


# # =============================================================================
# # SCORECARD RUNNER
# # =============================================================================

# def run_scorecard(
#     config: Dict[str, Any],
#     test_questions: Optional[List[Dict]] = None,
#     verbose: bool = True,
# ) -> List[Dict[str, Any]]:
#     """
#     Chạy toàn bộ test questions qua pipeline và chấm điểm.

#     Args:
#         config: Pipeline config (retrieval_mode, top_k, use_rerank, ...)
#         test_questions: List câu hỏi (load từ JSON nếu None)
#         verbose: In kết quả từng câu

#     Returns:
#         List scorecard results, mỗi item là một row

#     TODO Sprint 4:
#     1. Load test_questions từ data/test_questions.json
#     2. Với mỗi câu hỏi:
#        a. Gọi rag_answer() với config tương ứng
#        b. Chấm 4 metrics
#        c. Lưu kết quả
#     3. Tính average scores
#     4. In bảng kết quả
#     """
#     if test_questions is None:
#         with open(TEST_QUESTIONS_PATH, "r", encoding="utf-8") as f:
#             test_questions = json.load(f)

#     results = []
#     label = config.get("label", "unnamed")

#     print(f"\n{'='*70}")
#     print(f"Chạy scorecard: {label}")
#     print(f"Config: {config}")
#     print('='*70)

#     for q in test_questions:
#         question_id = q["id"]
#         query = q["question"]
#         expected_answer = q.get("expected_answer", "")
#         expected_sources = q.get("expected_sources", [])
#         category = q.get("category", "")

#         if verbose:
#             print(f"\n[{question_id}] {query}")

#         # --- Gọi pipeline ---
#         try:
#             result = rag_answer(
#                 query=query,
#                 retrieval_mode=config.get("retrieval_mode", "dense"),
#                 top_k_search=config.get("top_k_search", 10),
#                 top_k_select=config.get("top_k_select", 3),
#                 use_rerank=config.get("use_rerank", False),
#                 verbose=False,
#             )
#             answer = result["answer"]
#             chunks_used = result["chunks_used"]

#         except NotImplementedError:
#             answer = "PIPELINE_NOT_IMPLEMENTED"
#             chunks_used = []
#         except Exception as e:
#             answer = f"ERROR: {e}"
#             chunks_used = []

#         # --- Chấm điểm ---
#         faith = score_faithfulness(answer, chunks_used)
#         relevance = score_answer_relevance(query, answer)
#         recall = score_context_recall(chunks_used, expected_sources)
#         complete = score_completeness(query, answer, expected_answer)

#         row = {
#             "id": question_id,
#             "category": category,
#             "query": query,
#             "answer": answer,
#             "expected_answer": expected_answer,
#             "faithfulness": faith["score"],
#             "faithfulness_notes": faith["notes"],
#             "relevance": relevance["score"],
#             "relevance_notes": relevance["notes"],
#             "context_recall": recall["score"],
#             "context_recall_notes": recall["notes"],
#             "completeness": complete["score"],
#             "completeness_notes": complete["notes"],
#             "config_label": label,
#         }
#         results.append(row)

#         if verbose:
#             print(f"  Answer: {answer[:100]}...")
#             print(f"  Faithful: {faith['score']} | Relevant: {relevance['score']} | "
#                   f"Recall: {recall['score']} | Complete: {complete['score']}")

#     # Tính averages (bỏ qua None)
#     for metric in ["faithfulness", "relevance", "context_recall", "completeness"]:
#         scores = [r[metric] for r in results if r[metric] is not None]
#         avg = sum(scores) / len(scores) if scores else None
#         print(f"\nAverage {metric}: {avg:.2f}" if avg else f"\nAverage {metric}: N/A (chưa chấm)")

#     return results


# # =============================================================================
# # A/B COMPARISON
# # =============================================================================

# def compare_ab(
#     baseline_results: List[Dict],
#     variant_results: List[Dict],
#     output_csv: Optional[str] = None,
# ) -> None:
#     """
#     So sánh baseline vs variant theo từng câu hỏi và tổng thể.

#     TODO Sprint 4:
#     Điền vào bảng sau để trình bày trong báo cáo:

#     | Metric          | Baseline | Variant | Delta |
#     |-----------------|----------|---------|-------|
#     | Faithfulness    |   ?/5    |   ?/5   |  +/?  |
#     | Answer Relevance|   ?/5    |   ?/5   |  +/?  |
#     | Context Recall  |   ?/5    |   ?/5   |  +/?  |
#     | Completeness    |   ?/5    |   ?/5   |  +/?  |

#     Câu hỏi cần trả lời:
#     - Variant tốt hơn baseline ở câu nào? Vì sao?
#     - Biến nào (chunking / hybrid / rerank) đóng góp nhiều nhất?
#     - Có câu nào variant lại kém hơn baseline không? Tại sao?
#     """
#     metrics = ["faithfulness", "relevance", "context_recall", "completeness"]

#     print(f"\n{'='*70}")
#     print("A/B Comparison: Baseline vs Variant")
#     print('='*70)
#     print(f"{'Metric':<20} {'Baseline':>10} {'Variant':>10} {'Delta':>8}")
#     print("-" * 55)

#     for metric in metrics:
#         b_scores = [r[metric] for r in baseline_results if r[metric] is not None]
#         v_scores = [r[metric] for r in variant_results if r[metric] is not None]

#         b_avg = sum(b_scores) / len(b_scores) if b_scores else None
#         v_avg = sum(v_scores) / len(v_scores) if v_scores else None
#         delta = (v_avg - b_avg) if (b_avg and v_avg) else None

#         b_str = f"{b_avg:.2f}" if b_avg else "N/A"
#         v_str = f"{v_avg:.2f}" if v_avg else "N/A"
#         d_str = f"{delta:+.2f}" if delta else "N/A"

#         print(f"{metric:<20} {b_str:>10} {v_str:>10} {d_str:>8}")

#     # Per-question comparison
#     print(f"\n{'Câu':<6} {'Baseline F/R/Rc/C':<22} {'Variant F/R/Rc/C':<22} {'Better?':<10}")
#     print("-" * 65)

#     b_by_id = {r["id"]: r for r in baseline_results}
#     for v_row in variant_results:
#         qid = v_row["id"]
#         b_row = b_by_id.get(qid, {})

#         b_scores_str = "/".join([
#             str(b_row.get(m, "?")) for m in metrics
#         ])
#         v_scores_str = "/".join([
#             str(v_row.get(m, "?")) for m in metrics
#         ])

#         # So sánh đơn giản
#         b_total = sum(b_row.get(m, 0) or 0 for m in metrics)
#         v_total = sum(v_row.get(m, 0) or 0 for m in metrics)
#         better = "Variant" if v_total > b_total else ("Baseline" if b_total > v_total else "Tie")

#         print(f"{qid:<6} {b_scores_str:<22} {v_scores_str:<22} {better:<10}")

#     # Export to CSV
#     if output_csv:
#         RESULTS_DIR.mkdir(parents=True, exist_ok=True)
#         csv_path = RESULTS_DIR / output_csv
#         combined = baseline_results + variant_results
#         if combined:
#             with open(csv_path, "w", newline="", encoding="utf-8") as f:
#                 writer = csv.DictWriter(f, fieldnames=combined[0].keys())
#                 writer.writeheader()
#                 writer.writerows(combined)
#             print(f"\nKết quả đã lưu vào: {csv_path}")


# # =============================================================================
# # REPORT GENERATOR
# # =============================================================================

# def generate_scorecard_summary(results: List[Dict], label: str) -> str:
#     """
#     Tạo báo cáo tóm tắt scorecard dạng markdown.

#     TODO Sprint 4: Cập nhật template này theo kết quả thực tế của nhóm.
#     """
#     metrics = ["faithfulness", "relevance", "context_recall", "completeness"]
#     averages = {}
#     for metric in metrics:
#         scores = [r[metric] for r in results if r[metric] is not None]
#         averages[metric] = sum(scores) / len(scores) if scores else None

#     timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

#     md = f"""# Scorecard: {label}
# Generated: {timestamp}

# ## Summary

# | Metric | Average Score |
# |--------|--------------|
# """
#     for metric, avg in averages.items():
#         avg_str = f"{avg:.2f}/5" if avg else "N/A"
#         md += f"| {metric.replace('_', ' ').title()} | {avg_str} |\n"

#     md += "\n## Per-Question Results\n\n"
#     md += "| ID | Category | Faithful | Relevant | Recall | Complete | Notes |\n"
#     md += "|----|----------|----------|----------|--------|----------|-------|\n"

#     for r in results:
#         md += (f"| {r['id']} | {r['category']} | {r.get('faithfulness', 'N/A')} | "
#                f"{r.get('relevance', 'N/A')} | {r.get('context_recall', 'N/A')} | "
#                f"{r.get('completeness', 'N/A')} | {r.get('faithfulness_notes', '')[:50]} |\n")

#     return md


# # =============================================================================
# # MAIN — Chạy evaluation
# # =============================================================================

# if __name__ == "__main__":
#     print("=" * 60)
#     print("Sprint 4: Evaluation & Scorecard")
#     print("=" * 60)

#     # Kiểm tra test questions
#     print(f"\nLoading test questions từ: {TEST_QUESTIONS_PATH}")
#     try:
#         with open(TEST_QUESTIONS_PATH, "r", encoding="utf-8") as f:
#             test_questions = json.load(f)
#         print(f"Tìm thấy {len(test_questions)} câu hỏi")

#         # In preview
#         for q in test_questions[:3]:
#             print(f"  [{q['id']}] {q['question']} ({q['category']})")
#         print("  ...")

#     except FileNotFoundError:
#         print("Không tìm thấy file test_questions.json!")
#         test_questions = []

#     # --- Chạy Baseline ---
#     print("\n--- Chạy Baseline ---")
#     print("Lưu ý: Cần hoàn thành Sprint 2 trước khi chạy scorecard!")
#     try:
#         baseline_results = run_scorecard(
#             config=BASELINE_CONFIG,
#             test_questions=test_questions,
#             verbose=True,
#         )

#         # Save scorecard
#         RESULTS_DIR.mkdir(parents=True, exist_ok=True)
#         baseline_md = generate_scorecard_summary(baseline_results, "baseline_dense")
#         scorecard_path = RESULTS_DIR / "scorecard_baseline.md"
#         scorecard_path.write_text(baseline_md, encoding="utf-8")
#         print(f"\nScorecard lưu tại: {scorecard_path}")

#     except NotImplementedError:
#         print("Pipeline chưa implement. Hoàn thành Sprint 2 trước.")
#         baseline_results = []

#     # --- Chạy Variant (sau khi Sprint 3 hoàn thành) ---
#     # TODO Sprint 4: Uncomment sau khi implement variant trong rag_answer.py
#     # print("\n--- Chạy Variant ---")
#     # variant_results = run_scorecard(
#     #     config=VARIANT_CONFIG,
#     #     test_questions=test_questions,
#     #     verbose=True,
#     # )
#     # variant_md = generate_scorecard_summary(variant_results, VARIANT_CONFIG["label"])
#     # (RESULTS_DIR / "scorecard_variant.md").write_text(variant_md, encoding="utf-8")

#     # --- A/B Comparison ---
#     # TODO Sprint 4: Uncomment sau khi có cả baseline và variant
#     # if baseline_results and variant_results:
#     #     compare_ab(
#     #         baseline_results,
#     #         variant_results,
#     #         output_csv="ab_comparison.csv"
#     #     )

#     print("\n\nViệc cần làm Sprint 4:")
#     print("  1. Hoàn thành Sprint 2 + 3 trước")
#     print("  2. Chấm điểm thủ công hoặc implement LLM-as-Judge trong score_* functions")
#     print("  3. Chạy run_scorecard(BASELINE_CONFIG)")
#     print("  4. Chạy run_scorecard(VARIANT_CONFIG)")
#     print("  5. Gọi compare_ab() để thấy delta")
#     print("  6. Cập nhật docs/tuning-log.md với kết quả và nhận xét")


"""
eval.py — Sprint 4: Evaluation & Scorecard
==========================================
Mục tiêu Sprint 4 (60 phút):
  - Chạy 10 test questions qua pipeline
  - Chấm điểm theo 4 metrics: Faithfulness, Relevance, Context Recall, Completeness
  - So sánh baseline vs variant
  - Ghi kết quả ra scorecard

Definition of Done Sprint 4:
  ✓ Demo chạy end-to-end (index → retrieve → answer → score)
  ✓ Scorecard trước và sau tuning
  ✓ A/B comparison: baseline vs variant với giải thích vì sao variant tốt hơn

A/B Rule (từ slide):
  Chỉ đổi MỘT biến mỗi lần để biết điều gì thực sự tạo ra cải thiện.
  Đổi đồng thời chunking + hybrid + rerank + prompt = không biết biến nào có tác dụng.
"""

import json
import csv
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from rag_answer import rag_answer

# =============================================================================
# CẤU HÌNH
# =============================================================================

TEST_QUESTIONS_PATH = Path(__file__).parent / "data" / "test_questions.json"
RESULTS_DIR = Path(__file__).parent / "results"

# Cấu hình baseline (Sprint 2)
BASELINE_CONFIG = {
    "retrieval_mode": "dense",
    "top_k_search": 10,
    "top_k_select": 3,
    "use_rerank": False,
    "label": "baseline_dense",
}

# Cấu hình variant (Sprint 3 — điều chỉnh theo lựa chọn của nhóm)
# TODO Sprint 4: Cập nhật VARIANT_CONFIG theo variant nhóm đã implement # cái này nhóm tự tính 
VARIANT_CONFIG = {
    "retrieval_mode": "hybrid",   # Hoặc "dense" nếu chỉ đổi rerank
    "top_k_search": 10,
    "top_k_select": 3,
    "use_rerank": True,           # Hoặc False nếu variant là hybrid không rerank
    "label": "variant_hybrid_rerank",
}


# =============================================================================
# SCORING FUNCTIONS
# 4 metrics từ slide: Faithfulness, Answer Relevance, Context Recall, Completeness
# =============================================================================

import json
import openai # Giả định bạn dùng OpenAI, có thể thay bằng LangChain/Cerebras tùy setup

def score_faithfulness(
    answer: str,
    chunks_used: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Đánh giá tính trung thực (Faithfulness) sử dụng LLM-as-Judge.
    """
    # 1. Chuẩn bị ngữ cảnh từ các chunks
    context = "\n---\n".join([
        f"Source: {c.get('metadata', {}).get('source', 'Unknown')}\nContent: {c.get('page_content', '')}" 
        for c in chunks_used
    ])

    # 2. Xây dựng System Prompt chuyên nghiệp
    system_prompt = """Bạn là một chuyên gia kiểm định chất lượng hệ thống AI (QA Auditor). 
Nhiệm vụ của bạn là đánh giá tính 'TRUNG THỰC' (Faithfulness) của một câu trả lời dựa trên ngữ cảnh cho trước.

QUY TẮC CHẤM ĐIỂM (Thang 1-5):
- Điểm 5: Hoàn hảo. Mọi khẳng định trong câu trả lời đều có bằng chứng trực tiếp trong ngữ cảnh.
- Điểm 4: Tốt. Hầu hết đều có bằng chứng, chỉ có 1 chi tiết rất nhỏ không quan trọng là suy luận thêm nhưng không sai lệch.
- Điểm 3: Trung bình. Có thông tin đúng nhưng model đưa thêm kiến thức bên ngoài vào (hallucination nhẹ).
- Điểm 2: Kém. Nhiều thông tin quan trọng không có trong ngữ cảnh.
- Điểm 1: Thất bại. Câu trả lời tự bịa (hallucination hoàn toàn) hoặc trái ngược hoàn toàn với ngữ cảnh.

YÊU CẦU ĐẦU RA: Trả về định dạng JSON duy nhất với cấu trúc:
{"score": <int>, "reason": "<phân tích ngắn gọn từng bước>"}"""

    user_prompt = f"""
NGỮ CẢNH (RETRIEVED CHUNKS):
{context}

CÂU TRẢ LỜI CỦA MODEL (ANSWER):
{answer}

Hãy thực hiện:
1. Liệt kê các thông tin chính trong câu trả lời.
2. So sánh từng thông tin với ngữ cảnh.
3. Chấm điểm dựa trên quy tắc.
"""

    try:
        # 3. Gọi LLM (Ví dụ dùng GPT-4o hoặc GPT-4o-mini để tiết kiệm chi phí)
        response = openai.chat.completions.create(
            model="gpt-4o-mini", # Hoặc model bạn đang dùng trong rag_answer.py
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={ "type": "json_object" },
            temperature=0 # Quan trọng: Giữ kết quả ổn định
        )

        # 4. Parse kết quả
        result = json.loads(response.choices[0].message.content)
        return {
            "score": result.get("score"),
            "notes": result.get("reason")
        }

    except Exception as e:
        return {
            "score": 1, 
            "notes": f"Lỗi khi gọi LLM Judge: {str(e)}"
        }



def score_answer_relevance(
    query: str,
    answer: str,
) -> Dict[str, Any]:
    """
    Answer Relevance: Đánh giá mức độ phù hợp và trực diện của câu trả lời đối với câu hỏi.
    Sử dụng LLM-as-Judge để phân tích ý định (intent) của người dùng.
    """

    system_prompt = """Bạn là một chuyên gia ngôn ngữ học và đánh giá chất lượng AI.
Nhiệm vụ của bạn là đánh giá xem câu trả lời có thực sự giải quyết được câu hỏi của người dùng hay không.

THANG ĐIỂM 1-5:
- 5 (Xuất sắc): Trả lời trực tiếp, đầy đủ và chính xác ý định của câu hỏi. Không thừa, không thiếu.
- 4 (Tốt): Trả lời đúng trọng tâm nhưng có thể thiếu một chi tiết phụ nhỏ hoặc hơi dài dòng.
- 3 (Trung bình): Trả lời có liên quan nhưng chưa đi thẳng vào vấn đề, hoặc trả lời quá chung chung.
- 2 (Kém): Câu trả lời chỉ chạm đến một phần nhỏ của câu hỏi, phần lớn là lạc đề.
- 1 (Thất bại): Câu trả lời hoàn toàn không liên quan, hoặc model trả lời "Tôi không biết" một cách không cần thiết khi câu hỏi rõ ràng.

YÊU CẦU ĐẦU RA: Trả về JSON duy nhất:
{"score": <int>, "reason": "<phân tích ngắn gọn về mức độ đáp ứng câu hỏi>"}"""

    user_prompt = f"""
CÂU HỎI (QUERY): {query}
CÂU TRẢ LỜI (ANSWER): {answer}

Hãy phân tích:
1. Ý định thực sự của người dùng trong câu hỏi là gì?
2. Câu trả lời có cung cấp đúng thông tin đó không?
3. Có thông tin thừa nào làm loãng câu trả lời không?
"""

    try:
        # Gọi LLM Judge (khuyến khích dùng temperature=0 để kết quả nhất quán)
        response = openai.chat.completions.create(
            model="gpt-4o-mini",  # Đảm bảo dùng model đủ thông minh để hiểu ngữ cảnh
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={ "type": "json_object" },
            temperature=0
        )

        result = json.loads(response.choices[0].message.content)
        
        return {
            "score": result.get("score"),
            "notes": result.get("reason")
        }

    except Exception as e:
        return {
            "score": 1,
            "notes": f"Lỗi hệ thống khi chấm điểm Relevance: {str(e)}"
        }



def score_context_recall(
    chunks_used: List[Dict[str, Any]],
    expected_sources: List[str],
) -> Dict[str, Any]:
    """
    Context Recall: Kiểm tra xem Retriever có tìm thấy đúng tài liệu chứa câu trả lời không.
    Thang điểm 1-5 được quy đổi từ tỷ lệ % nguồn tài liệu tìm thấy.
    """
    
    # Trường hợp câu hỏi không yêu cầu nguồn cụ thể (ví dụ: câu hỏi ngoài phạm vi)
    if not expected_sources:
        return {
            "score": 5, # Mặc định 5 nếu không có nguồn nào bị bỏ lỡ
            "recall": 1.0, 
            "found": 0,
            "missing": [],
            "notes": "No expected sources required for this query."
        }

    # 1. Trích xuất danh sách các nguồn mà Retriever đã tìm được
    # Sử dụng set để loại bỏ trùng lặp và tăng tốc độ tìm kiếm
    retrieved_sources = {
        c.get("metadata", {}).get("source", "").lower()
        for c in chunks_used
    }

    found_count = 0
    missing_sources = []

    # 2. Kiểm tra từng nguồn kỳ vọng (Expected Source)
    for expected in expected_sources:
        # Chuẩn hóa tên file: loại bỏ đường dẫn thư mục và phần mở rộng (.pdf, .txt, .md)
        # Ví dụ: "support/sla-p1-2026.pdf" -> "sla-p1-2026"
        clean_expected = expected.split("/")[-1].split(".")[0].lower()
        
        # Kiểm tra xem có bất kỳ nguồn retrieved nào chứa tên file này không
        is_matched = any(clean_expected in r for r in retrieved_sources)
        
        if is_matched:
            found_count += 1
        else:
            missing_sources.append(expected)

    # 3. Tính toán tỷ lệ Recall
    recall_rate = found_count / len(expected_sources)

    # 4. Quy đổi sang thang điểm 1-5
    # 1.0 (100%) -> 5 điểm
    # 0.0 (0%)   -> 1 điểm
    # Công thức: 1 + (recall * 4)
    display_score = round(1 + (recall_rate * 4))

    return {
        "score": display_score,
        "recall": round(recall_rate, 2),
        "found": found_count,
        "missing": missing_sources,
        "notes": f"Found {found_count}/{len(expected_sources)} sources. " + 
                 (f"Missing: {', '.join(missing_sources)}" if missing_sources else "All sources captured.")
    }

import json
import openai # Hoặc thư viện LLM bạn đang dùng

def score_completeness(
    query: str,
    answer: str,
    expected_answer: str,
) -> Dict[str, Any]:
    """
    Completeness: Đánh giá độ đầy đủ bằng cách so sánh Answer với Expected Answer.
    Sử dụng LLM-as-Judge để kiểm tra các ý chính (key points).
    """
    
    # Nếu không có đáp án mẫu, không thể chấm điểm tự động chính xác
    if not expected_answer:
        return {
            "score": 5, 
            "notes": "No expected answer provided for comparison."
        }

    system_prompt = """Bạn là một chuyên gia đánh giá dữ liệu (Data Auditor).
Nhiệm vụ của bạn là so sánh 'CÂU TRẢ LỜI CỦA MODEL' với 'ĐÁP ÁN CHUẨN' để đo lường độ đầy đủ (Completeness).

THANG ĐIỂM 1-5:
- 5 (Hoàn hảo): Bao phủ tất cả các ý chính, các bước và điều kiện có trong đáp án chuẩn.
- 4 (Tốt): Thiếu một chi tiết rất nhỏ, không ảnh hưởng đến nội dung tổng thể.
- 3 (Trung bình): Thiếu một ý quan trọng hoặc một bước trong quy trình.
- 2 (Kém): Chỉ trả lời được khoảng 50% các ý chính so với đáp án chuẩn.
- 1 (Thất bại): Thiếu phần lớn nội dung hoặc chỉ trả lời chung chung.

YÊU CẦU ĐẦU RA: Trả về JSON duy nhất:
{"score": <int>, "missing_points": ["ý 1", "ý 2"], "reason": "<phân tích tổng quát>"}"""

    user_prompt = f"""
CÂU HỎI: {query}
ĐÁP ÁN CHUẨN (EXPECTED): {expected_answer}
CÂU TRẢ LỜI CỦA MODEL (ANSWER): {answer}

Hãy thực hiện:
1. Trích xuất các ý chính (key points) từ Đáp án chuẩn.
2. Kiểm tra xem Câu trả lời của model đã bao phủ bao nhiêu ý trong số đó.
3. Liệt kê các ý còn thiếu (nếu có).
"""

    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={ "type": "json_object" },
            temperature=0
        )

        result = json.loads(response.choices[0].message.content)
        
        # Tạo ghi chú chi tiết từ kết quả của LLM
        missing = result.get("missing_points", [])
        notes = result.get("reason", "")
        if missing:
            notes += f" | Thiếu: {', '.join(missing)}"

        return {
            "score": result.get("score"),
            "notes": notes
        }

    except Exception as e:
        return {
            "score": 1,
            "notes": f"Lỗi chấm điểm Completeness: {str(e)}"
        }

# =============================================================================
# SCORECARD RUNNER
# =============================================================================

def run_scorecard(
    config: Dict[str, Any],
    test_questions: Optional[List[Dict]] = None,
    verbose: bool = True,
) -> List[Dict[str, Any]]:
    """
    Thực thi đánh giá hệ thống RAG theo cấu hình cụ thể.
    """
    if test_questions is None:
        try:
            with open(TEST_QUESTIONS_PATH, "r", encoding="utf-8") as f:
                test_questions = json.load(f)
        except Exception as e:
            print(f"❌ Lỗi khi load test questions: {e}")
            return []

    results = []
    label = config.get("label", "unnamed")

    print(f"\n{'='*80}")
    print(f"🚀 ĐANG CHẠY SCORECARD: {label.upper()}")
    print(f"⚙️  Config: {config}")
    print(f"{'='*80}")

    for q in test_questions:
        question_id = q["id"]
        query = q["question"]
        expected_answer = q.get("expected_answer", "")
        expected_sources = q.get("expected_sources", [])
        category = q.get("category", "General")

        if verbose:
            print(f"\n👉 [{question_id}] ({category}): {query}")

        # --- Bước 1: Gọi RAG Pipeline ---
        try:
            # Lưu ý: rag_answer phải được import từ rag_answer.py
            result = rag_answer(
                query=query,
                retrieval_mode=config.get("retrieval_mode", "dense"),
                top_k_search=config.get("top_k_search", 10),
                top_k_select=config.get("top_k_select", 3),
                use_rerank=config.get("use_rerank", False),
                verbose=False,
            )
            answer = result["answer"]
            chunks_used = result["chunks_used"]
        except Exception as e:
            print(f"  ⚠️ Lỗi Pipeline tại câu {question_id}: {e}")
            answer = f"ERROR_PIPELINE: {str(e)}"
            chunks_used = []
        
        # --- Bước 2: Chấm điểm bằng các hàm đã implement ---
        # Chúng ta dùng các hàm LLM-as-Judge và Logic đã viết ở các bước trước
        faith = score_faithfulness(answer, chunks_used)
        relevance = score_answer_relevance(query, answer)
        recall = score_context_recall(chunks_used, expected_sources)
        complete = score_completeness(query, answer, expected_answer)

        # --- Bước 3: Lưu trữ dữ liệu dòng ---
        row = {
            "id": question_id,
            "category": category,
            "query": query,
            "answer": answer,
            "expected_answer": expected_answer,
            "faithfulness": faith["score"],
            "faithfulness_notes": faith["notes"],
            "relevance": relevance["score"],
            "relevance_notes": relevance["notes"],
            "context_recall": recall["score"],
            "context_recall_notes": recall["notes"],
            "completeness": complete["score"],
            "completeness_notes": complete["notes"],
            "config_label": label,
        }
        results.append(row)

        if verbose:
            print(f"  📝 Answer: {answer[:120]}...")
            print(f"  📊 Scores -> F: {faith['score']} | R: {relevance['score']} | "
                  f"Rc: {recall['score']} | C: {complete['score']}")

    # --- Bước 4: Tính toán trung bình cộng (Final Stats) ---
    print(f"\n{'-'*30}")
    print(f"📈 KẾT QUẢ TỔNG HỢP: {label}")
    print(f"{'-'*30}")
    
    metrics = ["faithfulness", "relevance", "context_recall", "completeness"]
    summary_stats = {}
    
    for metric in metrics:
        valid_scores = [r[metric] for r in results if r[metric] is not None]
        avg_score = sum(valid_scores) / len(valid_scores) if valid_scores else None
        summary_stats[metric] = avg_score
        print(f"{metric}: {avg_score:.2f}")
    return results

# =============================================================================
# A/B COMPARISON
# =============================================================================

def compare_ab(
    baseline_results: List[Dict],
    variant_results: List[Dict],
    output_csv: Optional[str] = None,
) -> None:
    """
    So sánh baseline vs variant theo từng câu hỏi và tổng thể.

    TODO Sprint 4:
    Điền vào bảng sau để trình bày trong báo cáo:

    | Metric          | Baseline | Variant | Delta |
    |-----------------|----------|---------|-------|
    | Faithfulness    |   ?/5    |   ?/5   |  +/?  |
    | Answer Relevance|   ?/5    |   ?/5   |  +/?  |
    | Context Recall  |   ?/5    |   ?/5   |  +/?  |
    | Completeness    |   ?/5    |   ?/5   |  +/?  |

    Câu hỏi cần trả lời:
    - Variant tốt hơn baseline ở câu nào? Vì sao?
    - Biến nào (chunking / hybrid / rerank) đóng góp nhiều nhất?
    - Có câu nào variant lại kém hơn baseline không? Tại sao?
    """
    metrics = ["faithfulness", "relevance", "context_recall", "completeness"]

    print(f"\n{'='*70}")
    print("A/B Comparison: Baseline vs Variant")
    print('='*70)
    print(f"{'Metric':<20} {'Baseline':>10} {'Variant':>10} {'Delta':>8}")
    print("-" * 55)

    for metric in metrics:
        b_scores = [r[metric] for r in baseline_results if r[metric] is not None]
        v_scores = [r[metric] for r in variant_results if r[metric] is not None]

        b_avg = sum(b_scores) / len(b_scores) if b_scores else None
        v_avg = sum(v_scores) / len(v_scores) if v_scores else None
        delta = (v_avg - b_avg) if (b_avg and v_avg) else None

        b_str = f"{b_avg:.2f}" if b_avg else "N/A"
        v_str = f"{v_avg:.2f}" if v_avg else "N/A"
        d_str = f"{delta:+.2f}" if delta else "N/A"

        print(f"{metric:<20} {b_str:>10} {v_str:>10} {d_str:>8}")

    # Per-question comparison
    print(f"\n{'Câu':<6} {'Baseline F/R/Rc/C':<22} {'Variant F/R/Rc/C':<22} {'Better?':<10}")
    print("-" * 65)

    b_by_id = {r["id"]: r for r in baseline_results}
    for v_row in variant_results:
        qid = v_row["id"]
        b_row = b_by_id.get(qid, {})

        b_scores_str = "/".join([
            str(b_row.get(m, "?")) for m in metrics
        ])
        v_scores_str = "/".join([
            str(v_row.get(m, "?")) for m in metrics
        ])

        # So sánh đơn giản
        b_total = sum(b_row.get(m, 0) or 0 for m in metrics)
        v_total = sum(v_row.get(m, 0) or 0 for m in metrics)
        better = "Variant" if v_total > b_total else ("Baseline" if b_total > v_total else "Tie")

        print(f"{qid:<6} {b_scores_str:<22} {v_scores_str:<22} {better:<10}")

    # Export to CSV
    if output_csv:
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        csv_path = RESULTS_DIR / output_csv
        combined = baseline_results + variant_results
        if combined:
            with open(csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=combined[0].keys())
                writer.writeheader()
                writer.writerows(combined)
            print(f"\nKết quả đã lưu vào: {csv_path}")


# =============================================================================
# REPORT GENERATOR
# =============================================================================

from datetime import datetime

def generate_scorecard_summary(results: List[Dict], label: str) -> str:
    """
    Tạo báo cáo tóm tắt scorecard dạng Markdown chuyên nghiệp.
    Bổ sung biểu tượng cảm xúc và nhận xét tự động dựa trên điểm số.
    """
    metrics = ["faithfulness", "relevance", "context_recall", "completeness"]
    averages = {}
    
    for metric in metrics:
        scores = [r[metric] for r in results if r[metric] is not None]
        averages[metric] = sum(scores) / len(scores) if scores else None

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # Header & Metadata
    md = f"# 📊 RAG Evaluation Scorecard: {label.upper()}\n"
    md += f"- **Thời gian thực hiện:** {timestamp}\n"
    md += f"- **Số lượng mẫu thử:** {len(results)} câu hỏi\n\n"

    # Section 1: Summary Table
    md += "## 📈 Điểm số trung bình\n\n"
    md += "| Chỉ số (Metric) | Điểm trung bình | Đánh giá |\n"
    md += "| :--- | :---: | :--- |\n"
    
    for metric, avg in averages.items():
        if avg is None:
            status = "⚪ N/A"
            avg_str = "N/A"
        elif avg >= 4.5:
            status = "🟢 Xuất sắc"
            avg_str = f"**{avg:.2f}/5**"
        elif avg >= 3.5:
            status = "🟡 Khá"
            avg_str = f"{avg:.2f}/5"
        else:
            status = "🔴 Cần cải thiện"
            avg_str = f"_{avg:.2f}/5_"
            
        name = metric.replace('_', ' ').title()
        md += f"| {name} | {avg_str} | {status} |\n"

    # Section 2: Per-Question Details
    md += "\n## 📝 Chi tiết từng câu hỏi\n\n"
    md += "| ID | Phân loại | F | R | Rc | C | Ghi chú (Notes) |\n"
    md += "| :---: | :--- | :---: | :---: | :---: | :---: | :--- |\n"

    for r in results:
        # Rút ngắn note để bảng không bị quá rộng
        note = r.get('faithfulness_notes', '') or r.get('relevance_notes', '') or ""
        short_note = (note[:75] + '...') if len(note) > 75 else note
        
        md += (f"| {r['id']} | {r['category']} | "
               f"{r.get('faithfulness', '—')} | "
               f"{r.get('relevance', '—')} | "
               f"{r.get('context_recall', '—')} | "
               f"{r.get('completeness', '—')} | "
               f"{short_note} |\n")

    # Section 3: Legend (Giải thích ký hiệu)
    md += "\n--- \n"
    md += "**Ký hiệu:** \n"
    md += "- **F**: Faithfulness (Tính trung thực) \n"
    md += "- **R**: Relevance (Độ liên quan) \n"
    md += "- **Rc**: Context Recall (Khả năng tìm kiếm) \n"
    md += "- **C**: Completeness (Độ đầy đủ)"

    return md


# =============================================================================
# MAIN — Chạy evaluation
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("🚀 SPRINT 4: EVALUATION SYSTEM & SCORECARD GENERATOR")
    print("=" * 70)

    # 1. Khởi tạo và kiểm tra dữ liệu đầu vào
    print(f"\n🔍 Đang tải bộ câu hỏi kiểm thử: {TEST_QUESTIONS_PATH}")
    try:
        with open(TEST_QUESTIONS_PATH, "r", encoding="utf-8") as f:
            test_questions = json.load(f)
        
        num_q = len(test_questions)
        print(f"✅ Thành công: Tìm thấy {num_q} câu hỏi.")
        
        # In preview nhanh 3 câu đầu để kiểm tra format
        for q in test_questions[:3]:
            print(f"   • [{q['id']}] {q['question'][:60]}...")
    except FileNotFoundError:
        print(f"❌ Lỗi: Không tìm thấy file tại {TEST_QUESTIONS_PATH}. Vui lòng kiểm tra lại đường dẫn.")
        test_questions = []
    except json.JSONDecodeError:
        print(f"❌ Lỗi: File JSON không đúng định dạng.")
        test_questions = []

    # Nếu có câu hỏi, tiến hành chạy đánh giá
    if test_questions:
        # Đảm bảo thư mục lưu kết quả tồn tại
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        
        # --- PHẦN 1: CHẠY BASELINE (DENSE RETRIEVAL) ---
        print("\n" + "-"*30)
        print("🟢 GIAI ĐOẠN 1: CHẠY BASELINE SCORECARD")
        print("-"*30)
        
        baseline_results = []
        try:
            baseline_results = run_scorecard(
                config=BASELINE_CONFIG,
                test_questions=test_questions,
                verbose=True,
            )
            
            # Xuất báo cáo Markdown cho Baseline
            baseline_md = generate_scorecard_summary(baseline_results, "Baseline (Dense Only)")
            baseline_path = RESULTS_DIR / "scorecard_baseline.md"
            baseline_path.write_text(baseline_md, encoding="utf-8")
            print(f"📝 Đã lưu báo cáo Baseline tại: {baseline_path}")
            
        except Exception as e:
            print(f"⚠️ Lỗi khi chạy Baseline: {e}")

        # --- PHẦN 2: CHẠY VARIANT (HYBRID + RERANK) ---
        print("\n" + "-"*30)
        print("🔵 GIAI ĐOẠN 2: CHẠY VARIANT SCORECARD")
        print("-"*30)
        
        variant_results = []
        try:
            variant_results = run_scorecard(
                config=VARIANT_CONFIG,
                test_questions=test_questions,
                verbose=True,
            )
            
            # Xuất báo cáo Markdown cho Variant
            variant_md = generate_scorecard_summary(variant_results, VARIANT_CONFIG.get("label", "Variant"))
            variant_path = RESULTS_DIR / "scorecard_variant.md"
            variant_path.write_text(variant_md, encoding="utf-8")
            print(f"📝 Đã lưu báo cáo Variant tại: {variant_path}")
            
        except Exception as e:
            print(f"⚠️ Lỗi khi chạy Variant: {e}. Đảm bảo bạn đã implement Hybrid Search ở Sprint 3.")

        # --- PHẦN 3: SO SÁNH A/B & XUẤT DELTA ---
        if baseline_results and variant_results:
            print("\n" + "-"*30)
            print(" GIAI ĐOẠN 3: PHÂN TÍCH SO SÁNH A/B")
            print("-"*30)
            
            compare_ab(
                baseline_results,
                variant_results,
                output_csv="ab_comparison_report.csv"
            )
            print(f"✅ Hoàn tất so sánh. Kết quả đã được xuất ra CSV để vẽ biểu đồ.")
        else:
            print("\n💡 Lưu ý: Cần kết quả của cả Baseline và Variant để thực hiện so sánh A/B.")

    print("\n" + "=" * 70)
    print(" KẾT THÚC QUY TRÌNH ĐÁNH GIÁ SPRINT 4")
    print("Hành động tiếp theo:")
    print("1. Mở file 'results/scorecard_variant.md' để xem nhận xét từ LLM-as-Judge.")
    print("2. Kiểm tra 'ab_comparison_report.csv' để xem sự tăng trưởng (Delta) của các chỉ số.")
    print("3. Đưa các con số trung bình vào slide báo cáo Lab 8.")
    print("=" * 70)
