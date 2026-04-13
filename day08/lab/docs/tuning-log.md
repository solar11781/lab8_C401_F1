# Tuning Log — RAG Pipeline (Day 08 Lab)

> Template: Ghi lại mỗi thay đổi và kết quả quan sát được.
> A/B Rule: Chỉ đổi MỘT biến mỗi lần.

---

## Baseline (Sprint 2)

**Ngày:** 13/4/2026 
**Config:**
```
retrieval_mode = "dense"
chunk_size = _400 tokens
overlap = 80 tokens
top_k_search = 10
top_k_select = 3
use_rerank = False
llm_model = gpt-4o-mini
```

**Scorecard Baseline:**
| Metric | Average Score |
|--------|--------------|
| Faithfulness | 4.5 /5 |
| Answer Relevance | 4.6 /5 |
| Context Recall | 5/5 |
| Completeness | 4 /5 |

**Câu hỏi yếu nhất (điểm thấp):**
> TODO: Liệt kê 2-3 câu hỏi có điểm thấp nhất và lý do tại sao.
> Ví dụ: "q07 (Approval Matrix) - context recall = 1/5 vì dense bỏ lỡ alias."

**Giả thuyết nguyên nhân (Error Tree):**
- [ ] Indexing: Chunking cắt giữa điều khoản
- [ ] Indexing: Metadata thiếu effective_date
- [ ] Retrieval: Dense bỏ lỡ exact keyword / alias
- [ ] Retrieval: Top-k quá ít → thiếu evidence
- [ ] Generation: Prompt không đủ grounding
- [ ] Generation: Context quá dài → lost in the middle

---

## Variant 1 (Sprint 3)

**Ngày:** 13/4/2026
**Biến thay đổi:** Chuyển `retrieval_mode` từ `"dense"` → `"hybrid"`

### Lý do chọn biến này:
* **Cơ chế:** Trong `rag_answer.py` đã implement hàm `retrieve_hybrid()` kết hợp Dense (Vector Similarity) + Sparse (BM25) bằng thuật toán Reciprocal Rank Fusion (RRF).
* **Vấn đề của Baseline:** Baseline chỉ dùng Dense retrieval thường dễ bỏ lỡ các query chứa keyword kỹ thuật cụ thể như `"ERR-403"`, `"P1"`, hoặc các danh từ riêng trong chính sách.
* **Kỳ vọng:** Hybrid giúp giữ vững khả năng hiểu ngữ nghĩa (semantic matching) và cải thiện việc tìm kiếm từ khóa chính xác (exact keyword matching), cực kỳ phù hợp với corpus chứa cả văn bản chính sách lẫn mã lỗi hệ thống.

### Cấu hình (Config):
```python
retrieval_mode = "hybrid"

**Scorecard Variant 1:**
| Metric | Baseline | Variant 1 | Delta |
|--------|----------|-----------|-------|
| Faithfulness | 4.5/5 | 4.3/5 | -0.2 |
| Answer Relevance | 4.6/5 | 4.6/5 | 0 |
| Context Recall | 5/5 | 5/5 | 0 |
| Completeness | 4/5 | 4/5 | 0 |

**Nhận xét:**
>  Variant 1 không cải thiện rõ rệt so với baseline.
Cụ thể, Answer Relevance, Context Recall và Completeness giữ nguyên (delta = 0), cho thấy hybrid retrieval không mang thêm thông tin mới đáng kể so với dense trong các test cases hiện tại.
Tuy nhiên, Faithfulness giảm nhẹ từ 4.5 → 4.3 (-0.2). Điều này cho thấy ở một số câu hỏi, hybrid đã retrieve thêm các chunk có liên quan về keyword nhưng kém chính xác về ngữ nghĩa, khiến model dễ đưa vào câu trả lời những chi tiết không hoàn toàn grounded.
Không có câu nào cải thiện rõ rệt, nhưng có một số câu bị giảm nhẹ về chất lượng do noise từ sparse retrieval.

**Kết luận:**
> Variant 1 không tốt hơn baseline.
> Bằng chứng: Faithfulness giảm (-0.2), trong khi các metric còn lại không cải thiện. Điều này cho thấy hybrid retrieval trong trường hợp này không mang lại lợi ích rõ ràng, thậm chí còn introduce thêm noise làm giảm độ chính xác của câu trả lời

---

## Variant 2 (nếu có thời gian)

**Biến thay đổi:** Bật use_rerank = True (Sử dụng Cross-Encoder Rerank)
**Config:**
```retrieval_mode = "hybrid"
use_rerank = True
```

**Scorecard Variant 2:**
| Metric | Baseline | Variant 1 | Variant 2 | Best |
|--------|----------|-----------|-----------|------|
| Faithfulness | 4.5/5 | 4.3/5 | 4.6/5 | 4.6/5 (Variant 2) |
| Answer Relevance | 4.6/5 | 4.6/5 | 4.5/5 | 4.6/5 (Baseline + Variant 1) |
| Context Recall | 5/5 | 5/5 | 5/5 | 5/5 |
| Completeness | 4/5 | 4/5 | 3.5/5 | 4.5 (Baseline + Variant 1) |
> Variant 2 cho thấy sự cải thiện rõ rệt về độ tin cậy nhưng lại đánh đổi bằng độ đầy đủ của thông tin. Cụ thể, Faithfulness đạt mức cao nhất trong các phiên bản (4.6/5), chứng minh rằng bước Reranking (Cross-Encoder) đã hoạt động hiệu quả trong việc lọc bỏ các đoạn văn bản gây nhiễu và chỉ giữ lại những nội dung có độ liên quan cao nhất để trả lời.
- Ngược lại, điểm Completeness sụt giảm đáng kể xuống còn 3.5/5 (giảm 0.5 so với baseline). Điều này cho thấy cơ chế Rerank khi giới hạn số lượng chunk trả về (top_k_select) đã vô tình loại bỏ các "minor chunks" — những đoạn chứa thông tin bổ trợ hoặc các ý phụ cần thiết để tạo nên một câu trả lời toàn diện. Chỉ số Answer Relevance cũng giảm nhẹ (4.5/5) do câu trả lời quá tập trung vào tính chính xác mà thiếu đi sự bao quát ý định người dùng.
 - Variant 2 tốt hơn về tính an toàn (Faithfulness) nhưng kém hơn về hiệu suất tổng thể (Overall Performance).

>Bằng chứng: Mặc dù giúp hệ thống đạt điểm trung thực cao nhất, nhưng việc đánh đổi quá nhiều điểm Completeness khiến Variant 2 chưa phải là cấu hình tối ưu. Đây là minh chứng cho thấy Reranker đang bị "lọc quá đà" (aggressive filtering). Để khắc phục, nhóm cần điều chỉnh tăng số lượng chunk được chọn sau khi rerank hoặc hạ ngưỡng lọc để giữ lại các thông tin bổ trợ.

## Variant 3
> Biến thay đổi: Query Transformation (Query Expansion) trước khi Retrieval.
**Config:** : # Transform query trước khi retrieve
queries = transform_query(query, strategy="expansion")
# Retrieve cho từng query sau đó merge kết quả
---Scorecard Variant 3:
| Metric | Baseline | Variant 1 | Variant 2 | Variant 3 | Best |
|--------|----------|-----------|-----------|------|------|
| Faithfulness | 4.5/5 | 4.3/5 | 4.6/5 | 4.7/5 | 4.7/5 (Variant 3) |
| Answer Relevance | 4.6/5 | 4.6/5 | 4.5/5 | 4.5/5 | 4.6/5 (Baseline + Variant 1) |
| Context Recall | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 |
| Completeness | 4/5 | 4/5 | 3.5/5 | 3.7/5 | 4/5 (Baseline + Variant 1) |
> Variant 3 ghi nhận mức điểm Faithfulness cao nhất trong tất cả các phiên bản (4.7/5). Việc sử dụng Query Expansion giúp mô hình tiếp cận vấn đề từ nhiều góc độ diễn đạt khác nhau, từ đó tìm được những dẫn chứng (chunks) khớp chính xác hơn với ý định thực sự của người dùng, giúp câu trả lời được củng cố vững chắc trên dữ liệu nguồn. Tuy nhiên, mức độ liên quan (Answer Relevance) vẫn duy trì ở mức 4.5/5, cho thấy việc tạo ra quá nhiều biến thể truy vấn đôi khi làm câu trả lời hơi lan man, không đi thẳng vào trọng tâm như mong đợi.


> Kết luận : Variant 3 là phiên bản tốt nhất về tính xác thực thông tin (Faithfulness).
Bằng chứng: Với mức điểm 4.7/5, Variant 3 vượt qua cả Variant 2 nhờ khả năng "hiểu" câu hỏi sâu sắc hơn thông qua các biến thể ngôn ngữ. Tuy nhiên, đây chưa phải là phiên bản hoàn hảo nhất về độ bao phủ thông tin. Variant 3 sẽ cực kỳ hiệu quả trong các hệ thống đòi hỏi độ chính xác tuyệt đối và xử lý tốt các câu hỏi dùng thuật ngữ không đồng nhất, nhưng cần tinh chỉnh thêm ở bước tổng hợp câu trả lời để khôi phục lại điểm số Completeness.
## Tóm tắt học được

> TODO (Sprint 4): Điền sau khi hoàn thành evaluation.

1. **Lỗi phổ biến nhất trong pipeline này là gì?**
   > Sự hạn chế của Dense Retrieval: Bỏ lỡ các từ khóa (keyword) quan trọng mang tính kỹ thuật (mã lỗi, tên riêng của chính sách), dẫn đến điểm Context Recall bị thấp dù câu trả lời nghe có vẻ trôi chảy.

2. **Biến nào có tác động lớn nhất tới chất lượng?**
   > Retrieval Strategy: Việc chuyển đổi từ dense sang hybrid có tác động lớn nhất vì nó thay đổi trực tiếp chất lượng của ngữ cảnh (context) đầu vào cho LLM. Nếu context sai, các bước sau đều vô nghĩa.

3. **Nếu có thêm 1 giờ, nhóm sẽ thử gì tiếp theo?**
   >Thử kết hợp cả 3: hybrid + rerank + query expansion để tối ưu cả recall và precision.
