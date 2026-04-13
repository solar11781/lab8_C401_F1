# Báo Cáo Nhóm — Lab Day 08: Full RAG Pipeline

**Tên nhóm:** C401_F1
**Thành viên:**
| Tên | Vai trò | Email |
|-----|---------|-------|
| Lê Duy Anh | Tech Lead | leduyanh2k3@gmail.com |
| Bùi Trần Gia Bảo, Lại Gia Khánh | Retrieval Owner | billxd04@gmail.com |
| Trương Minh Sơn | Eval Owner | ___ |
| Mạc Phương Nga | Tester | mpnga03@gmail.com |
| Nguyễn Phạm Trà My | Documentation Owner | ___ |

**Ngày nộp:** 13/04/2026
**Repo:** (https://github.com/solar11781/lab8_C401_F1.git)
**Độ dài khuyến nghị:** 600–900 từ

---

> **Hướng dẫn nộp group report:**
>
> - File này nộp tại: `reports/group_report.md`
> - Deadline: Được phép commit **sau 18:00** (xem SCORING.md)
> - Tập trung vào **quyết định kỹ thuật cấp nhóm** — không trùng lặp với individual reports
> - Phải có **bằng chứng từ code, scorecard, hoặc tuning log** — không mô tả chung chung

---

## 1. Pipeline nhóm đã xây dựng (150–200 từ)

Nhóm đã xây dựng một hệ thống RAG (Retrieval-Augmented Generation) hoàn chỉnh phục vụ tra cứu chính sách nội bộ với các thành phần chính sau:

**Chunking decision:**
Nhóm sử dụng chiến lược chunking lai (Hybrid Chunking) với `chunk_size=400` tokens và `overlap=80` tokens. Quy trình thực hiện qua hai bước: đầu tiên tách tài liệu theo các section headers tự nhiên (`=== Section ... ===`) để giữ tính toàn vẹn của điều khoản, sau đó nếu các section vẫn quá dài, hệ thống sẽ tự động tách nhỏ hơn theo paragraph để đảm bảo không vượt quá giới hạn token nhưng vẫn duy trì được ngữ cảnh nhờ phần overlap.

**Embedding model:**
Hệ thống sử dụng model `text-embedding-3-small` của OpenAI. Để tăng cường khả năng tìm kiếm, nhóm triển khai kỹ thuật **Context-Enriched Embedding**: chèn thêm metadata (source, section) vào văn bản trước khi embed, giúp vector hóa cả thông tin định danh của tài liệu.

**Retrieval variant (Sprint 3):**
Nhóm chọn variant **Hybrid Retrieval (Dense + Sparse) kết hợp Reranking**. Kết quả từ Vector Search (Dense) và BM25 (Sparse) được gộp lại bằng thuật toán Reciprocal Rank Fusion (RRF). Sau đó, top 10 candidates sẽ được đưa qua model `cross-encoder/ms-marco-MiniLM-L-6-v2` để chấm điểm lại mức độ phù hợp thực tế với câu hỏi trước khi chọn top 3 gửi vào Prompt.

---

## 2. Quyết định kỹ thuật quan trọng nhất (200–250 từ)

**Quyết định:** Nâng cấp từ Dense Retrieval nguyên bản lên Hybrid Retrieval phối hợp với Cross-Encoder Reranking.

**Bối cảnh vấn đề:**
Ở phiên bản Baseline (Sprint 2), hệ thống chỉ sử dụng Dense Retrieval. Qua đánh giá scorecard, nhóm nhận thấy hệ thống gặp vấn đề nghiêm trọng với các truy vấn chứa từ khóa kỹ thuật hoặc mã lỗi (như gq02 về số thiết bị VPN, gq09 về Password SSO). Đặc biệt, model thường xuyên xảy ra tình trạng "hallucination" (bịa đặt thông tin) khi retrieve sai context nhưng vẫn cố gắng trả lời (Faithfulness score chỉ đạt 3.50/5).

**Các phương án đã cân nhắc:**

| Phương án | Ưu điểm | Nhược điểm |
|-----------|---------|-----------|
| Dense Only (Baseline) | Tốc độ nhanh, hiểu được ngữ nghĩa câu hỏi. | Hay bỏ lỡ từ khóa chính xác (exact term), dễ retrieve nhầm context tương tự. |
| Hybrid (Dense + BM25) | Cân bằng giữa ngữ nghĩa và từ khóa. | Vẫn có thể bị noise từ các đoạn văn bản có nhiều từ khóa trùng lặp nhưng không chứa câu trả lời. |
| Hybrid + Rerank (Selected) | Độ chính xác Retrieval cực cao, lọc được noise hiệu quả. | Tăng độ trễ (latency) của hệ thống do thêm bước reranking. |

**Phương án đã chọn và lý do:**
Nhóm chọn **Hybrid + Rerank** vì ưu tiên hàng đầu của một hệ thống trợ lý chính sách là sự chính xác và trung thực. Reranking giúp hệ thống thẩm định lại một lần nữa các chunk văn bản, đảm bảo LLM chỉ nhận được dữ liệu "sạch" nhất.

**Bằng chứng từ scorecard/tuning-log:**
Theo `scorecard_variant.md`, chỉ số **Faithfulness** đã tăng từ **3.50 lên 4.00** (+0.50). Các câu hỏi về IT Helpdesk (gq09) đã đạt điểm tuyệt đối 5/5 về tính trung thực thay vì bịa đặt như bản baseline.

---

## 3. Kết quả grading questions (100–150 từ)

Sau khi chạy pipeline với 10 câu hỏi kiểm thử:

**Ước tính điểm raw:** 82 / 98

**Câu tốt nhất:** ID: gq08 (HR Policy) — Lý do: Đây là câu hỏi về chính sách làm việc remote. Tài liệu có cấu trúc rõ ràng, chunking giữ nguyên được điều khoản, và model retrieve chính xác đoạn văn bản chứa con số "3 ngày", dẫn đến câu trả lời hoàn hảo.

**Câu fail:** Không có

**Câu gq07 (abstain):** Pipeline xử lý rất tốt. Model nhận diện được câu hỏi "Mức phạt vi phạm SLA" không có trong docs và phản hồi đúng theo hướng dẫn: "Tôi không tìm thấy thông tin trong tài liệu... chỉ đề cập quy trình xử lý không có hình phạt."

---

## 4. A/B Comparison — Baseline vs Variant (150–200 từ)

Dựa vào `docs/tuning-log.md` và các scorecard tương ứng:

**Biến đã thay đổi (chỉ 1 biến):** Cấu hình Retrieval (Mode: Hybrid, Rerank: Enable).

| Metric | Baseline | Variant | Delta |
|--------|---------|---------|-------|
| Faithfulness | 3.50 | 4.00 | +0.50 |
| Relevance | 4.60 | 4.50 | -0.10 |
| Context Recall | 5.00 | 5.00 | 0.00 |
| Completeness | 4.10 | 4.10 | 0.00 |

**Kết luận:**
Variant mang lại kết quả tốt hơn hẳn về tính an toàn và tin cậy. Dù chỉ số Relevance giảm nhẹ (do reranking đôi khi ưu tiên các đoạn văn bản khô khan, súc tích hơn), nhưng việc tăng điểm Faithfulness là minh chứng cho việc hệ thống đã bớt "bịa đặt" hơn trước.

---

## 5. Phân công và đánh giá nhóm (100–150 từ)

> Đánh giá trung thực về quá trình làm việc nhóm.

**Phân công thực tế:**

| Thành viên | Phần đã làm | Sprint |
|------------|-------------|--------|
| Lê Duy Anh | Chunking + Tech Lead | 1, 2 |
| Bùi Trần Gia Bảo, Lại Gia Khánh | Retrieval +Rerank | 1, 3 |
| Trương Minh Sơn | Evaluation + tuning-log | 3, 4 |
| Mạc Phương Nga | Testing + Documentation | 2, 4 |
| Nguyễn Phạm Trà My | Documentation + UI/UX Design | 2, 4 |

**Điều nhóm làm tốt:**
- Triển khai thành công Hybrid Retrieval và Reranking trong thời gian ngắn.

- Xử lý tốt metadata giúp citation cực kỳ chính xác.

**Điều nhóm làm chưa tốt:**

- Latency còn hơi cao khi dùng Reranking model local.

- Prompt cho AI chấm điểm chưa được tối ưu.
---

## 6. Nếu có thêm 1 ngày, nhóm sẽ làm gì? (50–100 từ)

Nhóm sẽ tập trung vào:
1. **Prompt Engineering:** Thêm kỹ thuật `Chain-of-Thought` kết hợp với `Self-Correction` trong prompt để ép LLM kiểm tra lại con số trước khi trả lời, nhằm triệt tiêu lỗi gq04.
2. **Metadata Filtering:** Áp dụng filtering theo department ngay từ bước retrieval để thu hẹp phạm vi tìm kiếm và loại bỏ nhiễu hoàn toàn.


