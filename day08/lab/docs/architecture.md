# Architecture — RAG Pipeline (Day 08 Lab)

> Template: Điền vào các mục này khi hoàn thành từng sprint.
> Deliverable của Documentation Owner.

## 1. Tổng quan kiến trúc

```
[Raw Docs]
    ↓
[index.py: Preprocess → Chunk → Embed → Store]
    ↓
[ChromaDB Vector Store]
    ↓
[rag_answer.py: Query → Retrieve → Rerank → Generate]
    ↓
[Grounded Answer + Citation]
```

**Mô tả ngắn gọn:**
> Chatbot RAG giúp nhân viên công ty trả lời câu hỏi liên quan đến chính sách, quy trình dựa trên tài liệu nội bộ. Hệ thống gồm pipeline indexing để xử lý tài liệu và pipeline retrieval để tìm kiếm và tạo câu trả lời có trích dẫn nguồn.

---

## 2. Indexing Pipeline (Sprint 1)

### Tài liệu được index
| File | Nguồn | Department | Số chunk |
|------|-------|-----------|---------|
| `policy_refund_v4.txt` | policy/refund-v4.pdf | CS | 6 |
| `sla_p1_2026.txt` | support/sla-p1-2026.pdf | IT | 5 |
| `access_control_sop.txt` | it/access-control-sop.md | IT Security | 8 |
| `it_helpdesk_faq.txt` | support/helpdesk-faq.md | IT | 6 |
| `hr_leave_policy.txt` | hr/leave-policy-2026.pdf | HR | 5 |

### Quyết định chunking
| Tham số | Giá trị | Lý do |
|---------|---------|-------|
| Chunk size | 400 | Để đảm bảo mỗi chunk chứa đủ thông tin nhưng không quá dài |
| Overlap | 80 | Để giữ lại thông tin liên quan giữa các chunk |
| Chunking strategy | Heading-based | Tài liệu có cấu trúc rõ ràng, chia section cụ thể |
| Metadata fields | source, section, effective_date, department, access | Phục vụ filter, freshness, citation |

### Embedding model
- **Model**: OpenAI text-embedding-3-small
- **Vector store**: ChromaDB (PersistentClient)
- **Similarity metric**: Cosine

---

## 3. Retrieval Pipeline (Sprint 2 + 3)

### Baseline (Sprint 2)
| Tham số | Giá trị |
|---------|---------|
| Strategy | Dense (embedding similarity) |
| Top-k search | 10 |
| Top-k select | 3 |
| Rerank | Không |

### Variant (Sprint 3)
| Tham số | Giá trị | Thay đổi so với baseline |
|---------|---------|------------------------|
| Strategy | hybrid | Kết hợp dense và sparse sử dụng thuật toán RRF |
| Top-k search | 10 | Không đổi |
| Top-k select | 3 | Không đổi |
| Rerank | cross-encoder | Sử dụng mô hình Cross-encoder (ms-marco-MiniLM-L-6-v2) để chấm điểm lại top 10 trước khi lọc ra top 3. |
| Query transform | Không | Không đổi (Tập trung tối ưu Retriever và Reranker trong Sprint này). |

**Lý do chọn variant này:**

> Chọn Hybrid Search (Dense + Sparse) vì tài liệu nội bộ chứa đựng ngôn ngữ tự nhiên lẫn các thuật ngữ chuyên môn. Dense Retrieval giúp bắt được ngữ nghĩa, trong khi Sparse Retrieval (BM25) có thể bắt được các keyword quan trọng mà embedding có thể bỏ qua. Reranking bằng Cross-encoder giúp cải thiện độ chính xác của kết quả cuối cùng bằng cách đánh giá lại mức độ liên quan của từng candidate dựa trên query cụ thể.

> Bổ sung Cross-encoder vào pipeline giúp tăng khả năng phân biệt giữa các candidate có điểm embedding tương tự nhưng mức độ liên quan khác nhau. Điều này đặc biệt hữu ích khi top-k search trả về nhiều candidate có điểm số gần nhau, giúp cải thiện chất lượng câu trả lời cuối cùng.
---

## 4. Generation (Sprint 2)

### Grounded Prompt Template
```
Bạn là một AI Agent hỗ trợ CS Helpdesk và IT chuyên nghiệp, tận tâm. 
Nhiệm vụ của bạn là trả lời câu hỏi của người dùng DỰA VÀO DUY NHẤT Dữ liệu ngữ cảnh (Context) được cung cấp.

HƯỚNG DẪN CỐT LÕI:
1. CHỈ DÙNG BẰNG CHỨNG (EVIDENCE-ONLY): Chỉ sử dụng các thông tin được nêu rõ trong Context. Tuyệt đối không tự bịa ra hoặc suy đoán thông tin.
2. ĐỒNG BỘ NGÔN NGỮ (LANGUAGE MATCH): Bạn PHẢI phản hồi bằng đúng ngôn ngữ mà người dùng sử dụng trong câu hỏi.
3. ĐỊNH DẠNG (FORMATTING): Trình bày câu trả lời rõ ràng. Sử dụng gạch đầu dòng (bullet points) khi có nhiều ý hoặc các bước. Giữ câu trả lời luôn ngắn gọn, súc tích.
4. TRÍCH DẪN (CITATION): Luôn đính kèm chính xác Nguồn (Source) và Phần (Section) ở cuối mỗi thông tin được trích xuất.
   - Yêu cầu: Lấy thông tin từ phần tiêu đề của tài liệu và sử dụng đúng định dạng [Source: <tên file> | Section: <tên section>].

XỬ LÝ NGOẠI LỆ (ĐẶC BIỆT QUAN TRỌNG):
- KHỚP MỘT PHẦN (PARTIAL MATCH): Nếu người dùng hỏi về một trường hợp/điều kiện cụ thể (VD: chức vụ đặc biệt, tình huống hiếm) không được nhắc đến trong tài liệu, hãy nêu rõ rằng tài liệu không quy định về trường hợp ngoại lệ này, sau đó cung cấp chính sách/quy định chung.
- TỪ CHỐI & ĐIỀU HƯỚNG (ABSTAIN & ROUTE): Nếu context hoàn toàn không chứa thông tin để trả lời, hãy nói: "Tôi không tìm thấy thông tin trong tài liệu." Nếu câu hỏi liên quan đến một mã lỗi kỹ thuật hoặc sự cố hệ thống không có trong context, hãy hướng dẫn họ liên hệ với bộ phận IT Support/Helpdesk.

VÍ DỤ VỀ CÁCH TRẢ LỜI CHUẨN:

Question: Lỗi VPN-789-TIMEDOUT nghĩa là gì và làm sao để kết nối lại?
Context: (Không có thông tin liên quan)
Answer: Tôi không tìm thấy thông tin về mã lỗi VPN-789-TIMEDOUT trong tài liệu hiện tại. Đây có thể là lỗi kỹ thuật liên quan đến đường truyền mạng (VPN), vui lòng liên hệ trực tiếp bộ phận IT Helpdesk để được kiểm tra hệ thống.

Question: Nhân viên thực tập (Intern) có được cấp Macbook Pro để code không?
Context:
Tài liệu 1:
[Source: it-equipment-policy.pdf | Section: 2.1 | Date: 2026-02-15]
Nhân viên chính thức (Full-time) sau khi qua thử việc sẽ được cấp 01 laptop Windows tiêu chuẩn để làm việc.
Answer: Tài liệu không có quy định cụ thể về việc cấp phát thiết bị riêng cho nhân viên thực tập (Intern) hay cấp Macbook Pro. Theo quy định chung:
- Nhân viên chính thức sau khi qua thử việc sẽ được cấp laptop Windows tiêu chuẩn. [Source: it-equipment-policy.pdf | Section: 2.1]

---
CONTEXT:
{context_block}

QUESTION: {query}
ANSWER:
```

### LLM Configuration
| Tham số | Giá trị |
|---------|---------|
| Model | gpt-4o-mini |
| Temperature | 0 |
| Max tokens | 512 |

---

## 5. Failure Mode Checklist

> Dùng khi debug — kiểm tra lần lượt: index → retrieval → generation

| Failure Mode | Triệu chứng | Cách kiểm tra |
|-------------|-------------|---------------|
| Index lỗi | Retrieve về docs cũ / sai version | `inspect_metadata_coverage()` trong index.py |
| Chunking tệ | Chunk cắt giữa điều khoản | `list_chunks()` và đọc text preview |
| Retrieval lỗi | Không tìm được expected source | `score_context_recall()` trong eval.py |
| Generation lỗi | Answer không grounded / bịa | `score_faithfulness()` trong eval.py |
| Token overload | Context quá dài → lost in the middle | Kiểm tra độ dài context_block |

---

## 6. Diagram (tùy chọn)


```mermaid
graph LR
    A[User Query] --> B[Query Embedding]
    B --> C[ChromaDB Vector Search]
    C --> D[Top-10 Candidates]
    D --> E{Rerank?}
    E -->|Yes| F[Cross-Encoder]
    E -->|No| G[Top-3 Select]
    F --> G
    G --> H[Build Context Block]
    H --> I[Grounded Prompt]
    I --> J[LLM]
    J --> K[Answer + Citation]
```
