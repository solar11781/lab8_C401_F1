# 📊 RAG Evaluation Scorecard: VARIANT_HYBRID_RERANK
- **Thời gian thực hiện:** 2026-04-13 17:40
- **Số lượng mẫu thử:** 10 câu hỏi

## 📈 Điểm số trung bình

| Chỉ số (Metric) | Điểm trung bình | Đánh giá |
| :--- | :---: | :--- |
| Faithfulness | 4.30/5 | 🟡 Khá |
| Relevance | 4.30/5 | 🟡 Khá |
| Context Recall | **5.00/5** | 🟢 Xuất sắc |
| Completeness | 3.60/5 | 🟡 Khá |

## 📝 Chi tiết từng câu hỏi

| ID | Phân loại | F | R | Rc | C | Ghi chú (Notes) |
| :---: | :--- | :---: | :---: | :---: | :---: | :--- |
| q01 | SLA | 5 | 5 | 5 | 4 | Câu trả lời của model liệt kê chính xác các thông tin về SLA xử lý ticket P... |
| q02 | Refund | 5 | 5 | 5 | 5 | Câu trả lời của model khẳng định rằng khách hàng có thể yêu cầu hoàn tiền t... |
| q03 | Access Control | 5 | 5 | 5 | 5 | Câu trả lời của model hoàn toàn chính xác và có bằng chứng trực tiếp trong ... |
| q04 | Refund | 5 | 5 | 5 | 5 | Câu trả lời của model khẳng định rằng sản phẩm thuộc danh mục hàng kỹ thuật... |
| q05 | IT Helpdesk | 5 | 5 | 5 | 5 | Câu trả lời của model hoàn toàn chính xác và có bằng chứng trực tiếp trong ... |
| q06 | SLA | 5 | 5 | 5 | 3 | Câu trả lời của model hoàn toàn phù hợp với ngữ cảnh. Mọi thông tin được li... |
| q07 | Access Control | 5 | 4 | 5 | 3 | Câu trả lời của model hoàn toàn chính xác và có bằng chứng trực tiếp trong ... |
| q08 | HR Policy | 1 | 5 | 5 | 3 | Câu trả lời hoàn toàn không có bằng chứng trong ngữ cảnh. Ngữ cảnh không đề... |
| q09 | Insufficient Context | 5 | 1 | 5 | 1 | Câu trả lời của model hoàn toàn phản ánh thông tin trong ngữ cảnh. Nó cung ... |
| q10 | Refund | 2 | 3 | 5 | 2 | Câu trả lời đề cập đến quy trình hoàn tiền nhưng không có thông tin cụ thể ... |

--- 
**Ký hiệu:** 
- **F**: Faithfulness (Tính trung thực) 
- **R**: Relevance (Độ liên quan) 
- **Rc**: Context Recall (Khả năng tìm kiếm) 
- **C**: Completeness (Độ đầy đủ)