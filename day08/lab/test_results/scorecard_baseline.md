# 📊 RAG Evaluation Scorecard: BASELINE (DENSE ONLY)
- **Thời gian thực hiện:** 2026-04-13 17:38
- **Số lượng mẫu thử:** 10 câu hỏi

## 📈 Điểm số trung bình

| Chỉ số (Metric) | Điểm trung bình | Đánh giá |
| :--- | :---: | :--- |
| Faithfulness | **4.50/5** | 🟢 Xuất sắc |
| Relevance | **4.50/5** | 🟢 Xuất sắc |
| Context Recall | **5.00/5** | 🟢 Xuất sắc |
| Completeness | 4.10/5 | 🟡 Khá |

## 📝 Chi tiết từng câu hỏi

| ID | Phân loại | F | R | Rc | C | Ghi chú (Notes) |
| :---: | :--- | :---: | :---: | :---: | :---: | :--- |
| q01 | SLA | 5 | 5 | 5 | 4 | Câu trả lời của model liệt kê chính xác các thông tin về SLA xử lý ticket P... |
| q02 | Refund | 5 | 5 | 5 | 5 | Câu trả lời của model hoàn toàn chính xác và có bằng chứng trực tiếp trong ... |
| q03 | Access Control | 5 | 5 | 5 | 5 | Câu trả lời liệt kê chính xác các cá nhân cần phê duyệt để cấp quyền Level ... |
| q04 | Refund | 5 | 5 | 5 | 5 | Câu trả lời của model hoàn toàn chính xác và có bằng chứng trực tiếp trong ... |
| q05 | IT Helpdesk | 5 | 5 | 5 | 5 | Câu trả lời của model hoàn toàn chính xác và có bằng chứng trực tiếp trong ... |
| q06 | SLA | 5 | 5 | 5 | 4 | Câu trả lời của model hoàn toàn chính xác và có bằng chứng trực tiếp trong ... |
| q07 | Access Control | 5 | 5 | 5 | 3 | Câu trả lời khẳng định rằng tài liệu 'Approval Matrix for System Access' tr... |
| q08 | HR Policy | 1 | 5 | 5 | 3 | Câu trả lời hoàn toàn bịa đặt vì không có thông tin nào trong ngữ cảnh đề c... |
| q09 | Insufficient Context | 5 | 2 | 5 | 4 | Câu trả lời của model nêu rõ rằng không tìm thấy thông tin về mã lỗi ERR-40... |
| q10 | Refund | 4 | 3 | 5 | 3 | Câu trả lời cung cấp quy trình hoàn tiền chung cho khách hàng, bao gồm các ... |

--- 
**Ký hiệu:** 
- **F**: Faithfulness (Tính trung thực) 
- **R**: Relevance (Độ liên quan) 
- **Rc**: Context Recall (Khả năng tìm kiếm) 
- **C**: Completeness (Độ đầy đủ)