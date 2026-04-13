# Báo Cáo Cá Nhân — Lab Day 08: RAG Pipeline

**Họ và tên:** Lê Duy Anh
**Vai trò trong nhóm:** Tech Lead
**Ngày nộp:** 13/04/2026
**Độ dài yêu cầu:** 500–800 từ

---

## 1. Tôi đã làm gì trong lab này? (100-150 từ)

> Trong lab này, em tập trung vào sprint 1 và 2, chịu trách nhiệm xây dựng RAG index và Baseline RAG. Em thực hiện chỉnh sửa 1 chút phần tiền xử lý, đồng thời đưa ra lựa chọn sử dụng OpenAI Embeddings để vector hóa dữ liệu. Ngoài ra, em còn triển khai grounded prompt và call_llm để đưa ra được câu trả lời mong muốn. 

> Phần triển khai của em là tiền đề để các thành viên khác thực hiện yêu cầu của sprint 3 và 4.
_________________

---

## 2. Điều tôi hiểu rõ hơn sau lab này (100-150 từ)

> Qua bài lab này, em đã hiểu rõ hơn phần Grounded prompt. Khi thực hiện triển khai prompt, em nhận thấy grounded prompt là yếu tố vô cùng quan trọng. Thay vì để LLM tự đưa ra nội dung trả lời, grounded prompt sẽ ràng buộc câu trả lời của nó vào đúng những đoạn dữ liệu (chunks) mình vừa tìm ra. Hiểu nôm na là em nhét thêm context vào prompt, kèm theo lệnh: "1. CHỈ DÙNG BẰNG CHỨNG (EVIDENCE-ONLY): Chỉ sử dụng các thông tin được nêu rõ trong Context. Tuyệt đối không tự bịa ra hoặc suy đoán thông tin.". Việc này giúp hệ thống không tự ý bịa thông tin.
_________________

---

## 3. Điều tôi ngạc nhiên hoặc gặp khó khăn (100-150 từ)

> Trong quá trình thực hiện lab, thách thức lớn nhất mà em đối mặt lại nằm ở khâu thiết lập grounded_prompt. Ban đầu, em đặt giả thuyết rằng việc áp dụng các ràng buộc thật nghiêm ngặt sẽ triệt tiêu hoàn toàn hiện tượng "ảo giác" (hallucination) và bảo đảm tính chính xác tuyệt đối cho hệ thống. Tuy nhiên, thực tế triển khai lại phát sinh vấn đề ngoài kỳ vọng: đầu ra của mô hình không đạt được sự mượt mà cần thiết (ví dụ như câu 09 và 10 của test_questions).

> Do các chỉ thị trong prompt gò ép quá chặt, một số câu trả lời do LLM sinh ra trở nên vô cùng cứng nhắc và máy móc. Việc ép mô hình bám sát từng câu chữ trong ngữ cảnh (context) khiến đầu ra mất đi sự linh hoạt khi tổng hợp thông tin. Em đã phải tiêu tốn khá nhiều thời gian debug và tinh chỉnh lại câu lệnh để tìm ra điểm cân bằng giữa việc tuân thủ nghiêm ngặt dữ liệu gốc và khả năng diễn đạt ngôn ngữ tự nhiên.
_________________

---

## 4. Phân tích một câu hỏi trong scorecard (150-200 từ)

> **Câu hỏi:** Question 07: Approval Matrix để cấp quyền hệ thống là tài liệu nào?

> **Phân tích:** Baseline trả lời đúng. Câu trả lời là: "Tài liệu về Approval Matrix để cấp quyền hệ thống trước đây có tên là \"Approval Matrix for System Access\" và hiện tại được ghi chú trong tài liệu có tên \"it/access-control-sop.md\". [Source: it/access-control-sop.md | Section: General]". Câu này được chấm điểm theo 4 tiêu chí lần lượt là 5/5/5/3. Variant không cải thiện. Vì câu trả lời của baseline đã chính xác do phần chunk được sử dụng để trả lời là 1 chunk riêng và chưa đủ thông tin cho baseline có thể dễ dàng truy vấn.

_________________

---

## 5. Nếu có thêm thời gian, tôi sẽ làm gì? (50-100 từ)

> Nếu có thêm thời gian, em sẽ thử thay đổi chunk strategy. Em muốn so sánh thử xem việc chunk theo format file (do file này có format rõ ràng) so với việc sử dụng các thuật toán chia cắt theo chunk size như sliding window và chia theo recursive có tạo ra kết quả khác biệt nhau không.

_________________

---

*Lưu file này với tên: `reports/individual/[ten_ban].md`*
*Ví dụ: `reports/individual/nguyen_van_a.md`*
