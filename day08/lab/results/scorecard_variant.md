# 📊 RAG Evaluation Scorecard: VARIANT_HYBRID_RERANK
- **Thời gian thực hiện:** 2026-04-13 17:20
- **Số lượng mẫu thử:** 10 câu hỏi

## 📈 Điểm số trung bình

| Chỉ số (Metric) | Điểm trung bình | Đánh giá |
| :--- | :---: | :--- |
| Faithfulness | 4.00/5 | 🟡 Khá |
| Relevance | **4.50/5** | 🟢 Xuất sắc |
| Context Recall | **5.00/5** | 🟢 Xuất sắc |
| Completeness | 4.10/5 | 🟡 Khá |

## 📝 Chi tiết từng câu hỏi

| ID | Phân loại | F | R | Rc | C | Ghi chú (Notes) |
| :---: | :--- | :---: | :---: | :---: | :---: | :--- |
| gq01 | SLA | 5 | 5 | 5 | 4 | Câu trả lời của model hoàn toàn chính xác và có bằng chứng trực tiếp trong ... |
| gq02 | Cross-Document | 5 | 5 | 5 | 4 | Câu trả lời của model nêu rõ yêu cầu sử dụng VPN khi làm việc remote và giớ... |
| gq03 | Refund | 5 | 5 | 5 | 4 | Câu trả lời của model hoàn toàn chính xác và có bằng chứng trực tiếp trong ... |
| gq04 | Refund | 1 | 5 | 5 | 4 | Câu trả lời của model hoàn toàn bịa đặt thông tin. Ngữ cảnh không cung cấp ... |
| gq05 | Access Control | 4 | 3 | 5 | 2 | Câu trả lời của model nêu rõ quy trình cấp quyền Admin Access cho nhân viên... |
| gq06 | Cross-Document | 5 | 5 | 5 | 4 | Câu trả lời của model hoàn toàn phù hợp với ngữ cảnh. Mọi thông tin trong c... |
| gq07 | Insufficient Context | 4 | 2 | 5 | 5 | Câu trả lời của model nêu rõ rằng không có thông tin về mức phạt trong tài ... |
| gq08 | HR Policy | 5 | 5 | 5 | 5 | Câu trả lời của model hoàn toàn chính xác và có bằng chứng trực tiếp trong ... |
| gq09 | IT Helpdesk | 5 | 5 | 5 | 4 | Câu trả lời của model hoàn toàn chính xác và có bằng chứng trực tiếp trong ... |
| gq10 | Refund | 1 | 5 | 5 | 5 | Câu trả lời của model hoàn toàn sai lệch với ngữ cảnh. Ngữ cảnh không cung ... |

--- 
**Ký hiệu:** 
- **F**: Faithfulness (Tính trung thực) 
- **R**: Relevance (Độ liên quan) 
- **Rc**: Context Recall (Khả năng tìm kiếm) 
- **C**: Completeness (Độ đầy đủ)