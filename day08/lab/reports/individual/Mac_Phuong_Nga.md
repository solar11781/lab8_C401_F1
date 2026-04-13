# Báo Cáo Cá Nhân — Lab Day 08: RAG Pipeline

**Họ và tên:** Mạc Phương Nga  
**Vai trò trong nhóm:** Tester
**Ngày nộp:** 13/04/2026  
**Độ dài yêu cầu:** 500–800 từ

---

## 1. Tôi đã làm gì trong lab này? (100-150 từ)

> Mô tả cụ thể phần bạn đóng góp vào pipeline:
> - Sprint chủ yếu làm: 2 & 3
> - Cụ thể: Đánh giá câu trả lời của baseline và variant, phân tích lỗi, đề xuất cải tiến.
> - Công việc chủ yếu gắn liền với việc đánh giá hệ thống retrieval và llm generation --> Chỉ ra các lỗi cụ thể đang gặp phải để nhóm có thể tập trung cải thiện.

_________________

---

## 2. Điều tôi hiểu rõ hơn sau lab này (100-150 từ)

> Chunking theo section cần lưu ý đến các phần general (không có section cụ thể trong document) vì có thể chứa thông tin quan trọng. Việc này giúp đảm bảo rằng không bỏ sót thông tin nào khi thực hiện retrieval.

> Không phải lúc nào việc retrieval bằng hybird cũng có kết quả tốt hơn BM25. Điều này phụ thuộc vào nhiều yếu tố như chất lượng dữ liệu, cách thiết kế prompt, và cách kết hợp giữa các phương pháp retrieval. Trong một số trường hợp, BM25 có thể hoạt động tốt hơn nếu dữ liệu có cấu trúc rõ ràng và không cần sự hiểu biết sâu sắc về ngữ cảnh. Ngược lại, hybrid retrieval có thể cải thiện hiệu suất khi cần hiểu ngữ cảnh phức tạp hoặc khi dữ liệu có nhiều thông tin không cấu trúc. Việc đánh giá kỹ lưỡng từng phương pháp trong từng tình huống cụ thể là rất quan trọng để đạt được kết quả tốt nhất.

_________________

---

## 3. Điều tôi ngạc nhiên hoặc gặp khó khăn (100-150 từ)

> Điều ngạc nhiên nhất là việc retrieval bằng hybrid không phải lúc nào cũng cho kết quả tốt hơn BM25. Tôi đã kỳ vọng rằng việc kết hợp nhiều phương pháp retrieval sẽ luôn cải thiện hiệu suất, nhưng thực tế lại không phải vậy. Điều này chỉ ra rằng việc lựa chọn phương pháp retrieval phù hợp phụ thuộc vào nhiều yếu tố như chất lượng dữ liệu, cách thiết kế prompt, và cách kết hợp giữa các phương pháp retrieval.

> Chỉnh sửa prompt để cải thiện các trường hợp thông tin để trả lời không có trong document. Việc đưa ra trả lời dạng "Tôi không có đủ tài liệu để trả lời" hơi cứng. Để hướng dẫn cụ thể hoặc gợi ý thì khó hơn nhiều. Việc này đòi hỏi phải có sự hiểu biết sâu sắc về cách thiết kế prompt và cách hệ thống llm hoạt động để có thể đưa ra các gợi ý hoặc hướng dẫn phù hợp mà không làm mất đi tính tự nhiên của câu trả lời.

> Tạo system prompt dạng few-shot để cải thiện khả năng trả lời của llm. Kết quả trên tập test cho thấy rằng việc sử dụng few-shot prompt có thể cải thiện hiệu suất của llm trong việc trả lời các câu hỏi phức tạp. Tuy nhiên, system prompt này cũng chưa được test thêm với nhiều câu dạng như vậy để đánh giá khái quát hơn.

_________________

---

## 4. Phân tích một câu hỏi trong scorecard (150-200 từ)

> Chọn 1 câu hỏi trong test_questions.json mà nhóm bạn thấy thú vị.
> Phân tích:
> - Baseline trả lời đúng hay sai? Điểm như thế nào?
> - Lỗi nằm ở đâu: indexing / retrieval / generation?
> - Variant có cải thiện không? Tại sao có/không?

**Câu hỏi:** ERR-403-AUTH là lỗi gì và cách xử lý?

**Phân tích:**

> Baseline trả lời đúng và đạt F/R/Rc/C = 5/2/5/4. Điểm số có sự mâu thuẫn lớn: Faithfulness đạt 5/5 nhưng Relevance lại bị đánh giá rất thấp (2/5).

> Lỗi ở đây nằm ở khâu Evaluation (AI chấm điểm). Khi một câu hỏi cố tình được đưa vào mà không có thông tin trong tài liệu, model RAG đã hành xử chính xác bằng cách từ chối trả lời (abstain) để tránh bịa đặt. Thế nhưng, AI Judge lại đánh giá thấp độ liên quan (Relevance), cho thấy tiêu chí chấm điểm đang bị sai lệch: nó trừng phạt model vì không trả lời được, thay vì khen ngợi model vì đã chống hallucination thành công.

> Variant cũng không cải thiện được điểm số. Vì câu hỏi này vốn không có trong document, việc cải thiện retrieval không giúp được gì. 

> Từ đó nhận thấy rằng: Prompt được sử dụng cho LLM chấm điểm đang gặp vấn đề trong việc đánh giá các câu trả lời dạng abstain. Điều này dẫn đến việc model bị phạt điểm Relevance một cách không công bằng, mặc dù nó đã thực hiện đúng nhiệm vụ của mình là tránh hallucination. Việc này cho thấy cần phải điều chỉnh lại prompt chấm điểm để có thể đánh giá chính xác hơn các trường hợp mà model không có đủ thông tin để trả lời, thay vì trừng phạt nó vì điều đó.
_________________

---

## 5. Nếu có thêm thời gian, tôi sẽ làm gì? (50-100 từ)

> 1-2 cải tiến cụ thể bạn muốn thử.
> Không phải "làm tốt hơn chung chung" mà phải là:
> "Tôi sẽ thử X vì kết quả eval cho thấy Y."

> Thử cập nhật lại System Prompt của AI Evaluator (Judge) vì kết quả eval cho thấy AI chấm điểm đang trừng phạt sai (chấm Relevance = 1 hoặc 2) khi hệ thống RAG từ chối trả lời (abstain) hợp lý ở câu q09.

> Áp dụng Query Transformation (HyDE hoặc Rewrite): thử đưa thêm bước Query Rewrite để viết lại câu hỏi rõ nghĩa hơn hoặc dùng HyDE (tạo câu trả lời giả định) trước khi Retrieval, giúp Vector Search bắt được các ngữ nghĩa sâu hơn thay vì chỉ dựa vào từ khóa bề mặt.
_________________

