# Báo Cáo Cá Nhân — Lab Day 08: RAG Pipeline

**Họ và tên:** Bùi Trần Gia Bảo
**Vai trò trong nhóm:** Retrieval Owner
**Ngày nộp:** 13/04/2026
**Độ dài yêu cầu:** 500–800 từ

---

## 1. Tôi đã làm gì trong lab này? (100-150 từ)

> Mô tả cụ thể phần bạn đóng góp vào pipeline:
>
> - Sprint nào bạn chủ yếu làm?
> - Cụ thể bạn implement hoặc quyết định điều gì?
> - Công việc của bạn kết nối với phần của người khác như thế nào?

Tôi chủ yếu làm ở Sprint 3 với vai trò Retrieval Owner. Phần tôi phụ trách tập trung vào cải thiện bước retrieve trước khi generate. Trong `rag_answer.py` tôi implemented `rerank()` bằng cross-encoder và cả LLM, `transform_query()` với ba strategies expansion, decomposition và hyde, và `compare_retrieval_strategies()` để so sánh dense, sparse và hybrid trên cùng một câu hỏi. Công việc này nối trực tiếp với Sprint 1 vì retrieval phụ thuộc vào chunk và metadata đã được index, và nối với Sprint 4 vì `eval.py` dùng chính `rag_answer()` để chạy baseline và variant. Ngoài ra tôi cũng hỗ trợ phần evaluation bằng cách đối chiếu kết quả scorecard để xem retrieval thay đổi có thật sự giúp hệ thống tốt hơn hay không.

---

---

## 2. Điều tôi hiểu rõ hơn sau lab này (100-150 từ)

> Chọn 1-2 concept từ bài học mà bạn thực sự hiểu rõ hơn sau khi làm lab.
> Ví dụ: chunking, hybrid retrieval, grounded prompt, evaluation loop.
> Giải thích bằng ngôn ngữ của bạn — không copy từ slide.

Sau lab này, tôi hiểu rõ hơn về hybrid retrieval và reranking. Trước đó, tôi nghĩ chỉ cần dense retrieval là đủ vì embedding đã nắm được ngữ nghĩa nhưng khi làm lab tôi thấy dense mạnh ở semantic matching chứ không phải lúc nào cũng tốt với keyword, alias hoặc mã lỗi. Hybrid retrieval giải quyết điểm này bằng cách kết hợp dense và BM25, tức là giữ được cả ngữ nghĩa lẫn exact term. Tôi cũng hiểu rõ hơn vai trò của reranking là retrieve ban đầu có thể lấy về đúng source nhưng thứ tự chunk chưa tối ưu nên cross-encoder hoặc LLM giúp chấm lại mức liên quan giữa query và từng chunk để chọn đúng vài đoạn tốt nhất để đưa vào prompt.

---

---

## 3. Điều tôi ngạc nhiên hoặc gặp khó khăn (100-150 từ)

> Điều gì xảy ra không đúng kỳ vọng?
> Lỗi nào mất nhiều thời gian debug nhất?
> Giả thuyết ban đầu của bạn là gì và thực tế ra sao?

Điều tôi thấy rõ nhất là phần evaluation mất nhiều thời gian hơn dự kiến. Buổi sáng nhóm đã xong Sprint 1 và Sprint 2, nhưng đến buổi chiều thì phần Sprint 4 phải làm khá gấp vì không chỉ chạy pipeline mà còn phải chấm bốn metric và phân tích A/B comparison. Lỗi mất nhiều thời gian debug nhất là conflict khi làm việc chung trên repo. Do chưa tách branch rõ từ đầu, việc push/pull dễ ghi đè lẫn nhau, đặc biệt ở các file như `rag_answer.py` và `eval.py`.
Ban đầu tôi nghĩ rằng nếu retrieval đạt Context Recall cao thì câu trả lời sẽ chính xác. Tuy nhiên thực tế không phải vậy. Có những câu vẫn đạt 5/5 nhưng Faithfulness thấp do model không sử dụng đúng ngữ cảnh và vẫn suy diễn thêm thông tin.

---

---

## 4. Phân tích một câu hỏi trong scorecard (150-200 từ)

> Chọn 1 câu hỏi trong test_questions.json mà nhóm bạn thấy thú vị.
> Phân tích:
>
> - Baseline trả lời đúng hay sai? Điểm như thế nào?
> - Lỗi nằm ở đâu: indexing / retrieval / generation?
> - Variant có cải thiện không? Tại sao có/không?

**Câu hỏi:** Escalation trong sự cố P1 diễn ra như thế nào?

**Phân tích:**
Ở baseline (dense-only), câu gq06 đạt điểm cao với Faithfulness = 5, Relevance = 5, Context Recall = 5 và Completeness = 4. Theo scorecard, câu trả lời phù hợp với ngữ cảnh và thông tin đều có bằng chứng từ tài liệu. Điều đó cho thấy retrieval đã lấy đúng source cần thiết và model sử dụng ngữ cảnh khá tốt.

Sang variant (hybrid + rerank), điểm số của gq06 vẫn giữ nguyên (5/5/5/4). Điều này cho thấy việc cải thiện retrieval bằng hybrid và rerank không tạo ra khác biệt rõ rệt cho câu hỏi này. Nguyên nhân là vì đây là câu hỏi tương đối “dễ” đối với hệ thống: thông tin escalation nằm rõ ràng trong một tài liệu SLA, nên dense retrieval đã đủ để tìm đúng chunk ngay từ đầu.

=> Improvement của variant phụ thuộc vào loại câu hỏi. Với các câu cần multi-document hoặc dễ bị nhiễu, hybrid + rerank giúp cải thiện rõ rệt. Tuy nhiên, với các câu có thông tin rõ ràng trong một source như gq06, baseline đã đạt gần tối ưu nên variant không mang lại lợi ích gì thêm.

---

## 5. Nếu có thêm thời gian, tôi sẽ làm gì? (50-100 từ)

> 1-2 cải tiến cụ thể bạn muốn thử.
> Không phải "làm tốt hơn chung chung" mà phải là:
> "Tôi sẽ thử X vì kết quả eval cho thấy Y."

Do nhóm sử dụng nhiều LLM provider khác nhau (OpenAI, Gemini, Ollama) nên xảy ra vấn đề không tương thích, đặc biệt ở embedding khi số chiề`pu vector output khác nhau (OpenAI ~1000, Gemini >3000). Điều này đã gây lỗi ở bước indexing phía sau. Nếu có thêm thời gian, tôi sẽ chuẩn hóa embedding bằng cách áp dụng PCA để giảm chiều vector của Gemini về cùng không gian với OpenAI và giúp hệ thống hoạt động ổn định và nhất quán hơn khi sử dụng nhiều providers.
