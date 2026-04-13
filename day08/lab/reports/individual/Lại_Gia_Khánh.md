# Báo Cáo Cá Nhân — Lab Day 08: RAG Pipeline

**Họ và tên:** Lại Gia Khánh <br>
**Vai trò trong nhóm:** Retrieval Owner <br>
**Ngày nộp:** 13/04/2026 <br>
**Độ dài yêu cầu:** 500–800 từ

---

## 1. Tôi đã làm gì trong lab này? (100-150 từ)

> Mô tả cụ thể phần bạn đóng góp vào pipeline:
> - Sprint nào bạn chủ yếu làm?
> - Cụ thể bạn implement hoặc quyết định điều gì?
> - Công việc của bạn kết nối với phần của người khác như thế nào?

Chịu trách nhiệm làm Sprint 3, triển khai hybrid retrieval trong rag_answer.py. Cụ thể:
- Xử lý code cho retrieve_sparse() bằng cách load toàn bộ chunk từ ChromaDB, tiền xử lý/tokenize bằng regex, xây dựng chỉ mục BM25 và trả về các đoạn có điểm cao nhất để bắt chính xác thuật ngữ, mã lỗi và tên riêng.
- Xử lý code cho retrieve_hybrid() dùng Reciprocal Rank Fusion (RRF) để kết hợp kết quả dense và sparse, tính điểm RRF với trọng số điều chỉnh, xử lý trường hợp thiếu dữ liệu và chuẩn hoá metadata. <br>
--> Hai thành phần này tích hợp trực tiếp với pipeline chính (retrieve_dense(), module rerank và rag_answer()), giúp cải thiện recall cho queries chứa từ khóa exact đồng thời giữ được ngữ nghĩa của dense retrieval.

---

## 2. Điều tôi hiểu rõ hơn sau lab này (100-150 từ)

> Chọn 1-2 concept từ bài học mà bạn thực sự hiểu rõ hơn sau khi làm lab.
> Ví dụ: chunking, hybrid retrieval, grounded prompt, evaluation loop.
> Giải thích bằng ngôn ngữ của bạn — không copy từ slide.

Hybrid retrieval giúp hiểu rõ cách kết hợp hai thế mạnh: dense embedding cho khả năng bắt nghĩa và paraphrase, còn sparse/BM25 ghi nhận các từ khóa chính xác như mã lỗi, tên riêng hoặc điều khoản. Thực tế là không phải chọn một hay bỏ một — mà ghép chúng lại bằng phương pháp như Reciprocal Rank Fusion (RRF) để mỗi nguồn góp một phần điểm theo thứ hạng. Việc này cải thiện recall cho truy vấn lẫn lộn giữa ngữ nghĩa và từ khóa, đồng thời dễ điều chỉnh bằng trọng số (dense vs sparse) khi cân bằng precision/recall.

---

## 3. Điều tôi ngạc nhiên hoặc gặp khó khăn (100-150 từ)

> Điều gì xảy ra không đúng kỳ vọng?
> Lỗi nào mất nhiều thời gian debug nhất?
> Giả thuyết ban đầu của bạn là gì và thực tế ra sao?

- Sau khi nhóm chạy test question, một số câu trả lời được LLM đưa ra không đúng với tài liệu thực, thường bị thiếu thông tin hoặc tìm thấy thông tin nhưng trả lời không đúng trọng tâm.
- Lúc đầu chạy thì cá nhân em bị lỗi không tạo được collection trong chromadb nhưng sau khi clone lại repo thì đã chạy được.


---

## 4. Phân tích một câu hỏi trong scorecard (150-200 từ)

> Chọn 1 câu hỏi trong test_questions.json mà nhóm bạn thấy thú vị.
> Phân tích:
> - Baseline trả lời đúng hay sai? Điểm như thế nào?
> - Lỗi nằm ở đâu: indexing / retrieval / generation?
> - Variant có cải thiện không? Tại sao có/không?

**Câu hỏi:** Question 06: Escalation trong sự cố P1 diễn ra như nào?

**Phân tích:**
- Baseline trả lời đúng: "Escalation trong sự cố P1 chỉ áp dụng khi cần thay đổi quyền hệ thống ngoài quy trình thông thường."
- Điểm số được đánh giá qua 4 tiêu chí (Faithfulness, Relevance, Context Recall, Completeness) lần lượt là 5/4/5/1. Theo em, lỗi ở đây là do LLM đánh giá sai khi completeness chỉ được 1 dù câu trả lời đúng với nội dung câu hỏi.
- Variant không cải thiện mà còn đạt được điểm số thấp hơn 4/4/5/1.

---

## 5. Nếu có thêm thời gian, tôi sẽ làm gì? (50-100 từ)

> 1-2 cải tiến cụ thể bạn muốn thử.
> Không phải "làm tốt hơn chung chung" mà phải là:
> "Tôi sẽ thử X vì kết quả eval cho thấy Y."

Thêm bước rerank bằng cross-encoder để chấm lại top-10 và chọn top-3, vì đánh giá cho thấy retrieve_hybrid() tăng recall nhưng kéo theo nhiều chunk nhiễu làm giảm precision; rerank sẽ nâng precision mà vẫn giữ recall.

---

*Lưu file này với tên: `reports/individual/[ten_ban].md`*
*Ví dụ: `reports/individual/nguyen_van_a.md`*
