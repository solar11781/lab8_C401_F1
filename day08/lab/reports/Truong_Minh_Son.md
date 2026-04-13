# Báo Cáo Cá Nhân — Lab Day 08: RAG Pipeline

**Họ và tên:** Truong Minh Son
**Vai trò trong nhóm:** Tech Lead / Eval Owner / Documentation Owner  
**Ngày nộp:** 13/4/2026
**Độ dài yêu cầu:** 500–800 từ

---

## 1. Tôi đã làm gì trong lab này? (100-150 từ)
>Trong lab này, em đảm nhận vai trò chính là Eval Owner và Documentation Owner, tập trung toàn bộ nguồn lực vào Sprint 4. Sau khi các thành viên khác hoàn thiện phần Indexing và Retrieval, em đã tiếp nhận hệ thống để thực hiện đo lường chất lượng.

>Công việc cụ thể của em bao gồm: thiết kế bộ câu hỏi kiểm thử test_questions.json với các kịch bản khó (như câu hỏi bẫy, câu hỏi dùng từ đồng nghĩa), thực thi file eval.py để lấy số liệu thực tế cho 3 phiên bản (Baseline, Variant 1, Variant 2). Sau đó, em chịu trách nhiệm phân tích các chỉ số Faithfulness, Relevance, Recall và Completeness để tìm ra nguyên nhân gốc rễ của các lỗi Hallucination. Cuối cùng, em là người tổng hợp toàn bộ tri thức thu được để viết tài liệu tuning-log.md và các báo cáo phân tích cho nhóm.

_________________

---

## 2. Điều tôi hiểu rõ hơn sau lab này (100-150 từ)

>Điều em hiểu rõ nhất sau lab này chính là tầm quan trọng của vòng lặp đánh giá (Evaluation Loop). Trước đây, em nghĩ phát triển AI chỉ là viết code và chạy thử vài câu hỏi thấy ổn là xong. Tuy nhiên, khi trực tiếp quản lý Sprint 4, em nhận ra rằng nếu không có các con số định lượng, chúng ta sẽ không bao giờ biết được việc nâng cấp hệ thống (như thêm Rerank hay Hybrid) thực sự có lợi hay đang làm hỏng các chỉ số khác.

>Em cũng thấu hiểu sâu sắc về chỉ số Faithfulness (tính trung thực). Qua việc chấm điểm, em thấy rằng một mô hình có điểm Recall rất cao (tìm đúng tài liệu) vẫn có thể có điểm Faithfulness thấp nếu Prompt không đủ chặt chẽ, dẫn đến việc mô hình tự ý suy diễn ngoài ngữ cảnh. Việc tối ưu hóa RAG thực chất là một bài toán tìm điểm cân bằng giữa các chỉ số đối nghịch nhau.
_________________

---

## 3. Điều tôi ngạc nhiên hoặc gặp khó khăn (100-150 từ)

>Điều khiến em ngạc nhiên nhất là hiện tượng "càng tối ưu càng thiếu ý". Khi em thử nghiệm Variant 2 (Hybrid + Rerank), điểm Faithfulness tăng lên rất đẹp nhưng điểm Completeness lại sụt giảm nghiêm trọng. Em đã mất khá nhiều thời gian để debug và nhận ra rằng Reranker đang làm việc quá "khắt khe", nó lọc bỏ hết các thông tin bổ trợ và chỉ để lại những gì quan trọng nhất, khiến câu trả lời bị thiếu đi sự toàn diện.

>Khó khăn lớn nhất là việc thiết kế bộ câu hỏi kiểm thử sao cho đủ "khó". Em đã phải giả định mình là một người dùng không chuyên, sử dụng các thuật ngữ sai lệch so với tài liệu để kiểm tra xem hệ thống có thực sự bền bỉ (robust) hay không. Việc phân tích tại sao cùng một câu hỏi mà mỗi Variant lại cho ra một điểm số khác nhau đòi hỏi em phải đọc kỹ từng dòng context được truy xuất, đây là công việc tốn khá nhiều thời gian và sự tỉ mỉ.

_________________

---

## 4. Phân tích một câu hỏi trong scorecard (150-200 từ)

**Câu hỏi**: "Approval Matrix để cấp quyền hệ thống là tài liệu nào?" (Câu q07 trong bộ test)

**Phân tích**:
- Đây là một câu hỏi thú vị vì nó sử dụng tên cũ của tài liệu ("Approval Matrix"), trong khi tài liệu thực tế đã được đổi tên thành "Access Control SOP".

- Baseline (Dense): Trả lời đúng một phần nhưng điểm Relevance không cao vì embedding của từ "Approval Matrix" không hoàn toàn khớp với nội dung mới trong file .txt.

- Lỗi nằm ở: Retrieval. Dense retrieval đôi khi quá tập trung vào ngữ nghĩa chung mà bỏ qua sự thay đổi về thuật ngữ chuyên biệt (alias).

Variant 2 & 3 có cải thiện rõ rệt. Đặc biệt là ở Variant 1 và 2 khi có thêm Hybrid Retrieval (BM25). Nhờ khả năng bắt từ khóa (keyword matching), hệ thống đã tìm thấy các đoạn văn bản có nhắc đến tên cũ trong phần lịch sử thay đổi của tài liệu, giúp mô hình trả lời chính xác tên file hiện tại là access-control-sop.md.

Kết quả: Điểm Context Recall đạt tuyệt đối 5/5 ở các bản Hybrid, giúp khẳng định rằng đối với các doanh nghiệp thường xuyên thay đổi tên gọi quy trình, Hybrid Retrieval là một sự nâng cấp bắt buộc so với Dense truyền thống.


_________________

---

## 5. Nếu có thêm thời gian, tôi sẽ làm gì? (50-100 từ)

> Nếu có thêm thời gian, em sẽ tập trung cải thiện điểm Completeness vốn đang bị thấp ở các bản nâng cao. Em sẽ thử thay đổi tham số top_k_select sau bước Rerank, tăng từ 3 lên 5 hoặc 7 chunks. Em tin rằng việc cung cấp thêm "không gian" cho các thông tin bổ trợ sẽ giúp LLM tổng hợp câu trả lời đầy đủ hơn mà không làm ảnh hưởng đến độ trung thực trong khi Rerank sẽ cho các chunks đều có sự liên quan.


_________________

---

*Lưu file này với tên: `reports/individual/[ten_ban].md`*
*Ví dụ: `reports/individual/nguyen_van_a.md`*
