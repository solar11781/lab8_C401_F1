# Báo Cáo Cá Nhân — Lab Day 08: RAG Pipeline

**Họ và tên:** Nguyễn Phạm Trà My 
**Vai trò trong nhóm:** UI + test
**Ngày nộp:** 13/4/2026 
**Độ dài yêu cầu:** 500–800 từ

---

## 1. Tôi đã làm gì trong lab này? (100-150 từ)

> Mô tả cụ thể phần bạn đóng góp vào pipeline:
> - Sprint nào bạn chủ yếu làm?
> - Cụ thể bạn implement hoặc quyết định điều gì?
> - Công việc của bạn kết nối với phần của người khác như thế nào?
Trong lab08, chủ yếu em đã đảm nhận vai trò làm một giao diện thân thiện để giúp kết nối người dùng với hệ thống (vì thầy có bảo nếu làm UI thì cũng tốt ạ). Cụ thể, em đã tạo file app.py, thiết lập cơ chế quản lý trạng thái phiên (st.session_state) để lưu trữ lịch sử trò chuyện. Cụ thể hơn, em đã import hàm rag_answer từ module rag_answer.py (do Tech Lead viết) để làm API xử lý logic truy vấn. Cùng với đó là mapping các tham số như retrieval_mode, use_rerank sang UI để vai trò admin có thể điều chỉnh các tham số trực tiếp ngay trên màn hình UI. Đây cũng là công việc vừa đòi hỏi thẩm mĩ cao nhưng cũng cần sự chính xác thì mới có thể show được kết quả cho người dùng trong tương lai, còn hiện tại thì UI này đã giúp nhóm không cần tưởng tượng ra sẽ giao tiếp với người dùng như nào mà có thể nhìn vào đó và điều chỉnh, khi test cũng sẽ tiện hơn rất nhiều.
_________________

---

## 2. Điều tôi hiểu rõ hơn sau lab này (100-150 từ)

> Chọn 1-2 concept từ bài học mà bạn thực sự hiểu rõ hơn sau khi làm lab.
> Ví dụ: chunking, hybrid retrieval, grounded prompt, evaluation loop.
> Giải thích bằng ngôn ngữ của bạn — không copy từ slide.

Tuy trong bài lab này, nhiệm vụ chính của em là làm giao diện, nhưng em vẫn học hỏi được rất nhiều những kiến thức, và 2 thứ khiến em cảm thấy bản thân mình đã vững vàng hơn sau lab này là hybird retrieval và grounded prompt. 
- Hybird retrieval theo em nghĩ là một khái niệm khá phức tạp và đi kèm với nó là 2 công thức khá khó nhớ (Reciprocal Rank Fusion - RRF và Alpha/Weighted Combination), ban đầu em ngộ nhận rằng AI chỉ cần chunking phù hợp là có thể dễ dàng trả lời được các câu hỏi của người dùng.
- Grounded prompt: giúp AI có những câu trả lời thực tế hơn, tránh gặp ảo giác, điều này giúp người dùng có được những thông tin chính xác, nhất là với những câu hỏi về thông tin nội bộ. Và hơn hết là nếu câu trả lời không có trong dữ liệu thì AI sẽ không bịa mà sẽ thừa nhận những thiếu sót đó.
_________________

---

## 3. Điều tôi ngạc nhiên hoặc gặp khó khăn (100-150 từ)

> Điều gì xảy ra không đúng kỳ vọng?
> Lỗi nào mất nhiều thời gian debug nhất?
> Giả thuyết ban đầu của bạn là gì và thực tế ra sao?
Khó khăn tốn nhiều thời gian xử lý nhất là các lỗi phát sinh khi xây dựng giao diện bằng thư viện Streamlit. Thứ nhất, khi bổ sung tính năng xem chi tiết nguồn tài liệu (st.expander), thao tác lồng ghép mã đã phá vỡ cấu trúc try-except gốc, dẫn đến lỗi cú pháp (SyntaxError). Lỗi này làm đóng băng toàn bộ giao diện thay vì chỉ ghi nhận lỗi trên console. Giả thuyết ban đầu là việc tích hợp giao diện bằng công cụ này sẽ đơn giản và mã nguồn thực thi mượt mà.

_________________

---

## 4. Phân tích một câu hỏi trong scorecard (150-200 từ)

> Chọn 1 câu hỏi trong test_questions.json mà nhóm bạn thấy thú vị.
> Phân tích:
> - Baseline trả lời đúng hay sai? Điểm như thế nào?
> - Lỗi nằm ở đâu: indexing / retrieval / generation?
> - Variant có cải thiện không? Tại sao có/không?

**Câu hỏi:** (Câu 8 - q08) Nhân viên được làm remote tối đa mấy ngày mỗi tuần?

**Phân tích:**
Truy vấn này đánh giá khả năng trích xuất thông tin có điều kiện của hệ thống RAG. Kết quả thực nghiệm cho thấy biến thể (Variant) kết hợp Hybrid Retrieval đã đạt điểm số tuyệt đối 5/5 trên cả bốn phương thức đo lường: Faithfulness, Relevance, Context Recall và Completeness.

Quá trình truy xuất (Retrieval) hoạt động chính xác khi chỉ số Context Recall đạt 5/5, thu thập thành công phân mảnh chứa thông tin từ tài liệu "hr/leave-policy-2026.pdf". Điểm đáng chú ý nằm ở pha tạo sinh (Generation). Hệ thống LLM không chỉ trích xuất con số "2 ngày/tuần" mà còn nhận diện và tổng hợp đầy đủ các điều kiện ràng buộc đi kèm, bao gồm "sau probation period" và "được Team Lead phê duyệt". Khả năng xử lý ngữ cảnh này giúp điểm Completeness và Relevance đạt mức tối đa. Đồng thời, do mô hình tuân thủ nghiêm ngặt cấu trúc Grounded Prompt, không có thông tin ngoại lai hay kiến thức nền nào được chèn vào câu trả lời, đảm bảo chỉ số Faithfulness tuyệt đối.

Kết quả này chứng minh rằng khi kết hợp thuật toán truy xuất lai nhằm đảm bảo cung cấp đủ ngữ cảnh với hệ thống prompt được thiết lập giới hạn chặt chẽ, mô hình có khả năng tổng hợp và suy luận các điều khoản nội bộ với độ chính xác và tính toàn vẹn thông tin cao.
_________________

---

## 5. Nếu có thêm thời gian, tôi sẽ làm gì? (50-100 từ)

> 1-2 cải tiến cụ thể bạn muốn thử.
> Không phải "làm tốt hơn chung chung" mà phải là:
> "Tôi sẽ thử X vì kết quả eval cho thấy Y."

Cải tiến 1, em sẽ thử áp dụng kỹ thuật làm nổi bật văn bản (Text Highlighting) bằng cách sử dụng Regex để bôi đậm các từ khóa quan trọng hoặc các cụm từ khớp với truy vấn của người dùng bên trong các chunk. Điều này giúp nhân viên tra cứu nhanh chóng xác minh được tại sao hệ thống lại chọn đoạn văn bản đó để làm cơ sở cho câu trả lời.
Cải tiến 2, em sẽ triển khai tính năng thu thập phản hồi người dùng (Feedback Loop) ngay trên giao diện bằng hai nút thumbs-up/thumbs-down dưới mỗi câu trả lời. Em muốn thử cải tiến này vì hiện tại kết quả eval.py chỉ đo lường trên một tập dữ liệu test tĩnh (10 câu hỏi), trong khi đó chất lượng RAG thực tế cần được đánh giá liên tục qua tương tác thực của người dùng.
_________________

---

