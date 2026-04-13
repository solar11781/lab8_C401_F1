"""
app.py — Giao diện Trợ lý Nội bộ (Phiên bản Dành cho Nhân viên)
Chạy lệnh: streamlit run app.py
"""

import streamlit as st
from rag_answer import rag_answer

# =============================================================================
# CẤU HÌNH TRANG & GIAO DIỆN CƠ BẢN
# =============================================================================
st.set_page_config(page_title="Trợ lý Nội bộ", page_icon="💬", layout="centered")

# Nhúng CSS tùy chỉnh để tối ưu thêm bảng màu
st.markdown("""
<style>
    /* Đổi màu viền và nền của thanh nhập liệu chat */
    .stChatInputContainer {
        border: 1px solid #86B6F6 !important;
        background-color: white !important;
    }
    /* Đổi màu viền của các thẻ Expander */
    .streamlit-expanderHeader {
        color: #176B87 !important;
        border-bottom: 1px solid #B4D4FF !important;
    }
    /* Tùy chỉnh màu chữ cho các đoạn chú thích (info/success) */
    .stAlert {
        background-color: white !important;
        border: 1px solid #B4D4FF !important;
        color: #176B87 !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("💬 Trợ lý Hành chính & IT")
st.markdown("*Xin chào! Mình ở đây để giúp bạn tra cứu nhanh các chính sách, quy trình và quy định nội bộ của công ty.*")

# =============================================================================
# SIDEBAR: TINH GỌN (CHỈ DÀNH CHO CÁC TÁC VỤ CƠ BẢN)
# =============================================================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712139.png", width=100) # Placeholder logo
    st.markdown("### 🏢 Cổng Thông Tin Nội Bộ")
    st.info("💡 **Mẹo:** Hãy đặt câu hỏi rõ ràng, có chứa từ khóa về chính sách hoặc quy trình bạn cần tìm.")
    
    st.divider()
    if st.button("🔄 Bắt đầu cuộc trò chuyện mới", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    # Giấu các thiết lập kỹ thuật vào một Expander dành riêng cho Admin/Dev test
    with st.expander("⚙️ Cấu hình hệ thống (Admin)"):
        retrieval_mode = st.selectbox("Thuật toán", ["hybrid", "dense", "sparse"])
        use_rerank = st.toggle("Dùng Rerank", value=True)
        top_k = st.number_input("Top K", value=3, min_value=1)

# =============================================================================
# KHỞI TẠO STATE
# =============================================================================
if "messages" not in st.session_state or not st.session_state.messages:
    st.session_state.messages = [
        {"role": "assistant", "content": "👋 Chào bạn! Mình có thể giúp gì cho bạn hôm nay? Bạn có thể hỏi mình về:\n- 🕒 Quy định nghỉ phép\n- 💻 Quy trình cấp quyền hệ thống\n- 🎫 SLA xử lý lỗi IT"}
    ]

# =============================================================================
# HIỂN THỊ LỊCH SỬ CHAT
# =============================================================================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# =============================================================================
# XỬ LÝ INPUT MỚI (TỪ NGƯỜI DÙNG)
# =============================================================================
if prompt := st.chat_input("Nhập câu hỏi của bạn (VD: Quy định nghỉ phép năm?)..."):
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Đang tra cứu thông tin trên hệ thống... 🔍"):
            try:
                # Gọi RAG Pipeline (Sử dụng tham số từ bảng Admin ẩn)
                result = rag_answer(
                    query=prompt,
                    retrieval_mode=retrieval_mode,
                    top_k_search=10,
                    top_k_select=top_k,
                    use_rerank=use_rerank,
                    verbose=False
                )
                
                raw_answer = result.get("answer", "")
                chunks_used = result.get("chunks_used", [])
                
                # --- XỬ LÝ KỊCH BẢN ---
                if "PIPELINE_NOT_IMPLEMENTED" in raw_answer or "ERROR" in raw_answer:
                    final_response = "Hệ thống đang được bảo trì hoặc gặp sự cố gián đoạn. Vui lòng thử lại sau."
                    st.markdown(final_response)
                    st.session_state.messages.append({"role": "assistant", "content": final_response})
                
                elif "Không tìm thấy thông tin" in raw_answer or "Không đủ dữ liệu" in raw_answer:
                    final_response = "Hệ thống chưa tìm thấy quy định cụ thể cho truy vấn này. Vui lòng sử dụng từ khóa khác hoặc liên hệ bộ phận chuyên trách."
                    st.markdown(final_response)
                    st.session_state.messages.append({"role": "assistant", "content": final_response})
                
                else:
                    # Hiển thị câu trả lời văn bản
                    st.markdown(raw_answer)
                    
                    # Khởi tạo giao diện nguồn tương tác (Clickable Sources)
                    if chunks_used:
                        st.markdown("---")
                        st.markdown("**Tài liệu tham khảo chi tiết:**")
                        
                        # Duyệt qua từng chunk và tạo một expander riêng biệt
                        for chunk in chunks_used:
                            meta = chunk.get('metadata', {})
                            source = meta.get('source', 'Không xác định')
                            section = meta.get('section', 'Không xác định')
                            
                            # Tiêu đề của expander đóng vai trò như một nút bấm (button)
                            with st.expander(f"Nguồn: {source} | Mục: {section}"):
                                st.info(chunk.get('text', ''))
                    
                    # Định dạng nội dung lưu vào lịch sử (chỉ lưu text tĩnh)
                    history_content = raw_answer
                    if chunks_used:
                        sources_list = [c.get('metadata', {}).get('source', '') for c in chunks_used]
                        unique_sources = list(set(filter(None, sources_list)))
                        history_content += f"\n\n---\n**Nguồn tham khảo:** {', '.join(unique_sources)}"
                        
                    st.session_state.messages.append({"role": "assistant", "content": history_content})
                
            except Exception as e:
                error_msg = (
                    "🚨 **Kết nối bị gián đoạn:**\n\n"
                    "Đường truyền đến máy chủ tra cứu đang gặp sự cố. Bạn vui lòng tải lại trang hoặc thử lại sau vài phút nhé."
                )
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})