"""
rag_answer.py — Sprint 2 + Sprint 3: Retrieval & Grounded Answer
================================================================
Sprint 2 (60 phút): Baseline RAG
  - Dense retrieval từ ChromaDB
  - Grounded answer function với prompt ép citation
  - Trả lời được ít nhất 3 câu hỏi mẫu, output có source

Sprint 3 (60 phút): Tuning tối thiểu
  - Thêm hybrid retrieval (dense + sparse/BM25)
  - Hoặc thêm rerank (cross-encoder)
  - Hoặc thử query transformation (expansion, decomposition, HyDE)
  - Tạo bảng so sánh baseline vs variant

Definition of Done Sprint 2:
  ✓ rag_answer("SLA ticket P1?") trả về câu trả lời có citation
  ✓ rag_answer("Câu hỏi không có trong docs") trả về "Không đủ dữ liệu"

Definition of Done Sprint 3:
  ✓ Có ít nhất 1 variant (hybrid / rerank / query transform) chạy được
  ✓ Giải thích được tại sao chọn biến đó để tune
"""

import os
from typing import List, Dict, Any, Optional, Tuple
from dotenv import load_dotenv
from sentence_transformers import CrossEncoder

load_dotenv()

# =============================================================================
# CẤU HÌNH
# =============================================================================

TOP_K_SEARCH = 10    # Số chunk lấy từ vector store trước rerank (search rộng)
TOP_K_SELECT = 3     # Số chunk gửi vào prompt sau rerank/select (top-3 sweet spot)

LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")


# =============================================================================
# RETRIEVAL — DENSE (Vector Search)
# =============================================================================

def retrieve_dense(query: str, top_k: int = TOP_K_SEARCH) -> List[Dict[str, Any]]:
    """
    Dense retrieval: tìm kiếm theo embedding similarity trong ChromaDB.
    """
    import chromadb
    from index import get_embedding, CHROMA_DB_DIR

    # Khởi tạo client và collection
    client = chromadb.PersistentClient(path=str(CHROMA_DB_DIR))
    collection = client.get_collection("rag_lab")

    # Embed query
    query_embedding = get_embedding(query)

    # Truy vấn
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )

    # Format lại kết quả
    chunks = []
    if results["documents"]:
        for i in range(len(results["documents"][0])):
            chunks.append({
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "score": 1 - results["distances"][0][i]  # Cosine similarity
            })
    
    return chunks


# =============================================================================
# RETRIEVAL — SPARSE / BM25 (Keyword Search)
# Dùng cho Sprint 3 Variant hoặc kết hợp Hybrid
# =============================================================================

def retrieve_sparse(query: str, top_k: int = TOP_K_SEARCH) -> List[Dict[str, Any]]:
    """
    Sparse retrieval: tìm kiếm theo keyword (BM25).

    Mạnh ở: exact term, mã lỗi, tên riêng (ví dụ: "ERR-403", "P1", "refund")
    Hay hụt: câu hỏi paraphrase, đồng nghĩa

    TODO Sprint 3 (nếu chọn hybrid):
    1. Cài rank_bm25: pip install rank-bm25
    2. Load tất cả chunks từ ChromaDB (hoặc rebuild từ docs)
    3. Tokenize và tạo BM25Index
    4. Query và trả về top_k kết quả

    Gợi ý:
        from rank_bm25 import BM25Okapi
        corpus = [chunk["text"] for chunk in all_chunks]
        tokenized_corpus = [doc.lower().split() for doc in corpus]
        bm25 = BM25Okapi(tokenized_corpus)
        tokenized_query = query.lower().split()
        scores = bm25.get_scores(tokenized_query)
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
    """
    # TODO Sprint 3: Implement BM25 search
    from rank_bm25 import BM25Okapi
    import chromadb
    from index import CHROMA_DB_DIR
    import re

    # Load all chunks from the Chroma collection
    client = chromadb.PersistentClient(path=str(CHROMA_DB_DIR))
    collection = client.get_collection("rag_lab")

    try:
        results = collection.get(include=["documents", "metadatas"])
    except Exception:
        # Some chroma versions require explicit limit; try with a large limit as fallback
        results = collection.get(limit=10000, include=["documents", "metadatas"])

    docs = results.get("documents", [])
    metadatas = results.get("metadatas", [])

    if not docs:
        return []

    # Tokenize using simple word regex (better than split for punctuation)
    tokenized_corpus = [re.findall(r"\w+", d.lower()) for d in docs]
    bm25 = BM25Okapi(tokenized_corpus)

    tokenized_query = re.findall(r"\w+", query.lower())
    scores = bm25.get_scores(tokenized_query)

    # Get top_k indices by score
    top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]

    results_list: List[Dict[str, Any]] = []
    for idx in top_indices:
        score = float(scores[idx])
        meta = metadatas[idx] if idx < len(metadatas) else {}
        results_list.append({
            "text": docs[idx],
            "metadata": meta,
            "score": score,
        })

    return results_list


# =============================================================================
# RETRIEVAL — HYBRID (Dense + Sparse với Reciprocal Rank Fusion)
# =============================================================================

def retrieve_hybrid(
    query: str,
    top_k: int = TOP_K_SEARCH,
    dense_weight: float = 0.6,
    sparse_weight: float = 0.4,
) -> List[Dict[str, Any]]:
    """
    Hybrid retrieval: kết hợp dense và sparse bằng Reciprocal Rank Fusion (RRF).

    Mạnh ở: giữ được cả nghĩa (dense) lẫn keyword chính xác (sparse)
    Phù hợp khi: corpus lẫn lộn ngôn ngữ tự nhiên và tên riêng/mã lỗi/điều khoản

    Args:
        dense_weight: Trọng số cho dense score (0-1)
        sparse_weight: Trọng số cho sparse score (0-1)

    TODO Sprint 3 (nếu chọn hybrid):
    1. Chạy retrieve_dense() → dense_results
    2. Chạy retrieve_sparse() → sparse_results
    3. Merge bằng RRF:
       RRF_score(doc) = dense_weight * (1 / (60 + dense_rank)) +
                        sparse_weight * (1 / (60 + sparse_rank))
       60 là hằng số RRF tiêu chuẩn
    4. Sort theo RRF score giảm dần, trả về top_k

    Khi nào dùng hybrid (từ slide):
    - Corpus có cả câu tự nhiên VÀ tên riêng, mã lỗi, điều khoản
    - Query như "Approval Matrix" khi doc đổi tên thành "Access Control SOP"
    """
    # TODO Sprint 3: Implement hybrid RRF
    try:
        dense_results = retrieve_dense(query, top_k=top_k) or []
    except NotImplementedError:
        dense_results = []
    except Exception:
        dense_results = []

    try:
        sparse_results = retrieve_sparse(query, top_k=top_k) or []
    except NotImplementedError:
        sparse_results = []
    except Exception:
        sparse_results = []

    if not dense_results and not sparse_results:
        return []

    def _key_for_chunk(chunk: Dict[str, Any]) -> str:
        meta = chunk.get("metadata", {}) or {}
        source = meta.get("source", "")
        text_snip = (chunk.get("text", "") or "")[:200]
        return f"{source}||{text_snip}"

    # Build map of candidate -> ranks
    candidates: Dict[str, Dict[str, Any]] = {}

    for i, c in enumerate(dense_results):
        k = _key_for_chunk(c)
        if k not in candidates:
            candidates[k] = {
                "text": c.get("text", ""),
                "metadata": c.get("metadata", {}),
                "dense_rank": i + 1,
                "sparse_rank": None,
            }
        else:
            candidates[k]["dense_rank"] = i + 1

    for i, c in enumerate(sparse_results):
        k = _key_for_chunk(c)
        if k not in candidates:
            candidates[k] = {
                "text": c.get("text", ""),
                "metadata": c.get("metadata", {}),
                "dense_rank": None,
                "sparse_rank": i + 1,
            }
        else:
            candidates[k]["sparse_rank"] = i + 1

    # Compute RRF score and collect
    merged: List[Dict[str, Any]] = []
    for v in candidates.values():
        dr = v.get("dense_rank")
        sr = v.get("sparse_rank")
        score = 0.0
        if dr:
            score += dense_weight * (1.0 / (60.0 + float(dr)))
        if sr:
            score += sparse_weight * (1.0 / (60.0 + float(sr)))

        merged.append({
            "text": v.get("text", ""),
            "metadata": v.get("metadata", {}),
            "score": score,
        })

    # Sort by RRF score descending and return top_k
    merged_sorted = sorted(merged, key=lambda x: x.get("score", 0.0), reverse=True)
    return merged_sorted[:top_k]


# =============================================================================
# RERANK (Sprint 3 alternative)
# Cross-encoder để chấm lại relevance sau search rộng
# =============================================================================

rerank_model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
def rerank(
    query: str,
    candidates: List[Dict[str, Any]],
    top_k: int = TOP_K_SELECT,
) -> List[Dict[str, Any]]:
    """
    Rerank các candidate chunks bằng cross-encoder.

    Cross-encoder: chấm lại "chunk nào thực sự trả lời câu hỏi này?"
    MMR (Maximal Marginal Relevance): giữ relevance nhưng giảm trùng lặp

    Funnel logic (từ slide):
      Search rộng (top-20) → Rerank (top-6) → Select (top-3)

    TODO Sprint 3 (nếu chọn rerank):
    Option A — Cross-encoder:
        from sentence_transformers import CrossEncoder
        model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
        pairs = [[query, chunk["text"]] for chunk in candidates]
        scores = model.predict(pairs)
        ranked = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)
        return [chunk for chunk, _ in ranked[:top_k]]

    Option B — Rerank bằng LLM (đơn giản hơn nhưng tốn token):
        Gửi list chunks cho LLM, yêu cầu chọn top_k relevant nhất

    Khi nào dùng rerank:
    - Dense/hybrid trả về nhiều chunk nhưng có noise
    - Muốn chắc chắn chỉ 3-5 chunk tốt nhất vào prompt
    """
    # TODO Sprint 3: Implement rerank
    if not candidates:
        return []
    
    # Option A — Cross-encoder (use a CrossEncoder model to score each (query, passage) pair)
    pairs = [[query, chunk.get("text", "")] for chunk in candidates]
    scores = rerank_model.predict(pairs)

    ranked = sorted(
        zip(candidates, scores),
        key=lambda x: x[1],
        reverse=True
    )
    return [chunk for chunk, _ in ranked[:top_k]]

    # Option B — LLM-based rerank
    # import json
    # prompt_lines = [
    #     "You are a relevance rater. Given a query and a list of passages, return a JSON array of relevance scores (floats between 0 and 1) corresponding to each passage in the SAME ORDER.",
    #     f"Query: {query}",
    #     "Passages:"
    # ]
    # for i, c in enumerate(candidates, 1):
    #     text = c.get("text", "").strip()
    #     prompt_lines.append(f"[{i}] {text}")
    # prompt = "\n\n".join(prompt_lines)
    # response = call_llm(prompt)
    # # Expect response like: [0.1, 0.9, 0.3]
    # scores = json.loads(response)
    # scored = []
    # for c, s in zip(candidates, scores):
    #     c_copy = dict(c)
    #     c_copy["score"] = float(s)
    #     scored.append(c_copy)
    # scored_sorted = sorted(scored, key=lambda x: x["score"], reverse=True)
    # return scored_sorted[:top_k]


# =============================================================================
# QUERY TRANSFORMATION (Sprint 3 alternative)
# =============================================================================

def transform_query(query: str, strategy: str = "expansion") -> List[str]:
    """
    Biến đổi query để tăng recall.

    Strategies:
      - "expansion": Thêm từ đồng nghĩa, alias, tên cũ
      - "decomposition": Tách query phức tạp thành 2-3 sub-queries
      - "hyde": Sinh câu trả lời giả (hypothetical document) để embed thay query

    TODO Sprint 3 (nếu chọn query transformation):
    Gọi LLM với prompt phù hợp với từng strategy.

    Ví dụ expansion prompt:
        "Given the query: '{query}'
         Generate 2-3 alternative phrasings or related terms in Vietnamese.
         Output as JSON array of strings."

    Ví dụ decomposition:
        "Break down this complex query into 2-3 simpler sub-queries: '{query}'
         Output as JSON array."

    Khi nào dùng:
    - Expansion: query dùng alias/tên cũ (ví dụ: "Approval Matrix" → "Access Control SOP")
    - Decomposition: query hỏi nhiều thứ một lúc
    - HyDE: query mơ hồ, search theo nghĩa không hiệu quả
    """
    # TODO Sprint 3: Implement query transformation
    import json

    if strategy == "expansion":
        prompt = f"""Given the query: '{query}'
        Generate 2-3 alternative phrasings or related terms in Vietnamese.
        Output a JSON array of strings only, for example: ["alt1", "alt2"].
        Do not add any extra explanation or text."""
    elif strategy == "decomposition":
        prompt = f"""Break down this complex query into 2-3 simpler sub-queries in Vietnamese: '{query}'
        Output a JSON array of strings only, for example: ["sub1", "sub2"].
        Do not add any extra explanation or text."""
    elif strategy == "hyde":
        prompt = f"""Generate a concise hypothetical supporting document or short answer for the query '{query}' in Vietnamese.
        Treat the output as a short document suitable for embedding.
        Output a JSON array with a single string (the hypothetical document), for example: ["..."]
        Do not add any extra explanation or text."""
    else:
        raise ValueError(f"Unknown strategy: {strategy}")

    response = call_llm(prompt)
    return json.loads(response)


# =============================================================================
# GENERATION — GROUNDED ANSWER FUNCTION
# =============================================================================

def build_context_block(chunks: List[Dict[str, Any]]) -> str:
    """
    Đóng gói chunks kèm metadata (source, section, eff_date) để model dễ trích dẫn.
    """
    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        meta = chunk.get("metadata", {})
        source = meta.get("source", "unknown")
        section = meta.get("section", "")
        eff_date = meta.get("effective_date", "unknown")
        text = chunk.get("text", "")

        header = f"SOURCE: {source} | SECTION: {section} | DATE: {eff_date}"
        context_parts.append(f"{header}\n{text}")

    return "\n\n".join(context_parts)


def build_grounded_prompt(query: str, context_block: str) -> str:
    """
    Xây dựng grounded prompt tối ưu:
    - Evidence-only, Citation, Concise, Abstain, Language Match.
    """
    prompt = f"""Answer the question using ONLY the provided Context below.

REQUIREMENTS:
1. EVIDENCE-ONLY: Chỉ lấy thông tin từ Context. Tuyệt đối không dùng kiến thức ngoài hoặc tự bịa thông tin.
2. CITATION: Phải trích dẫn nguồn trực tiếp ngay sau mỗi thông tin quan trọng bằng định dạng [Tên file | Section] (hoặc format tương ứng có trong Context).
3. CONCISE: Trả lời ngắn gọn, đi thẳng vào trọng tâm (tối đa 2-3 câu). Không giải thích dông dài.
4. ABSTAIN: Nếu Context không chứa đủ thông tin để trả lời, phải nói rõ: "Tôi không tìm thấy thông tin trong tài liệu."
5. LANGUAGE MATCH: Luôn phản hồi bằng cùng ngôn ngữ với Câu hỏi.

Question: {query}

Context:
{context_block}

Answer:"""
    return prompt


def call_llm(prompt: str) -> str:
    """
    Gọi LLM để sinh câu trả lời sử dụng OpenAI.
    """
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,     # temperature=0 để output ổn định, dễ đánh giá
        max_tokens=512,
    )
    return response.choices[0].message.content


def rag_answer(
    query: str,
    retrieval_mode: str = "dense",
    top_k_search: int = TOP_K_SEARCH,
    top_k_select: int = TOP_K_SELECT,
    use_rerank: bool = False,
    verbose: bool = False,
) -> Dict[str, Any]:
    """
    Pipeline RAG hoàn chỉnh: query → retrieve → (rerank) → generate.

    Args:
        query: Câu hỏi
        retrieval_mode: "dense" | "sparse" | "hybrid"
        top_k_search: Số chunk lấy từ vector store (search rộng)
        top_k_select: Số chunk đưa vào prompt (sau rerank/select)
        use_rerank: Có dùng cross-encoder rerank không
        verbose: In thêm thông tin debug

    Returns:
        Dict với:
          - "answer": câu trả lời grounded
          - "sources": list source names trích dẫn
          - "chunks_used": list chunks đã dùng
          - "query": query gốc
          - "config": cấu hình pipeline đã dùng

    TODO Sprint 2 — Implement pipeline cơ bản:
    1. Chọn retrieval function dựa theo retrieval_mode
    2. Gọi rerank() nếu use_rerank=True
    3. Truncate về top_k_select chunks
    4. Build context block và grounded prompt
    5. Gọi call_llm() để sinh câu trả lời
    6. Trả về kết quả kèm metadata

    TODO Sprint 3 — Thử các variant:
    - Variant A: đổi retrieval_mode="hybrid"
    - Variant B: bật use_rerank=True
    - Variant C: thêm query transformation trước khi retrieve
    """
    config = {
        "retrieval_mode": retrieval_mode,
        "top_k_search": top_k_search,
        "top_k_select": top_k_select,
        "use_rerank": use_rerank,
    }

    # --- Bước 1: Retrieve ---
    if retrieval_mode == "dense":
        candidates = retrieve_dense(query, top_k=top_k_search)
    elif retrieval_mode == "sparse":
        candidates = retrieve_sparse(query, top_k=top_k_search)
    elif retrieval_mode == "hybrid":
        candidates = retrieve_hybrid(query, top_k=top_k_search)
    else:
        raise ValueError(f"retrieval_mode không hợp lệ: {retrieval_mode}")

    if verbose:
        print(f"\n[RAG] Query: {query}")
        print(f"[RAG] Retrieved {len(candidates)} candidates (mode={retrieval_mode})")
        for i, c in enumerate(candidates[:3]):
            print(f"  [{i+1}] score={c.get('score', 0):.3f} | {c['metadata'].get('source', '?')}")

    # --- Bước 2: Rerank (optional) ---
    if use_rerank:
        candidates = rerank(query, candidates, top_k=top_k_select)
    else:
        candidates = candidates[:top_k_select]

    if verbose:
        print(f"[RAG] After select: {len(candidates)} chunks")

    # --- Bước 3: Build context và prompt ---
    context_block = build_context_block(candidates)
    prompt = build_grounded_prompt(query, context_block)

    if verbose:
        print(f"\n[RAG] Prompt:\n{prompt[:500]}...\n")

    # --- Bước 4: Generate ---
    answer = call_llm(prompt)

    # --- Bước 5: Extract sources ---
    sources = list({
        c["metadata"].get("source", "unknown")
        for c in candidates
    })

    return {
        "query": query,
        "answer": answer,
        "sources": sources,
        "chunks_used": candidates,
        "config": config,
    }


# =============================================================================
# SPRINT 3: SO SÁNH BASELINE VS VARIANT
# =============================================================================

def compare_retrieval_strategies(query: str) -> None:
    """
    So sánh các retrieval strategies với cùng một query.

    TODO Sprint 3:
    Chạy hàm này để thấy sự khác biệt giữa dense, sparse, hybrid.
    Dùng để justify tại sao chọn variant đó cho Sprint 3.

    A/B Rule (từ slide): Chỉ đổi MỘT biến mỗi lần.
    """
    print(f"\n{'='*60}")
    print(f"Query: {query}")
    print('='*60)

    strategies = ["dense", "hybrid"]  # Thêm "sparse" sau khi implement

    for strategy in strategies:
        print(f"\n--- Strategy: {strategy} ---")
        try:
            result = rag_answer(query, retrieval_mode=strategy, verbose=False)
            print(f"Answer: {result['answer']}")
            print(f"Sources: {result['sources']}")
        except NotImplementedError as e:
            print(f"Chưa implement: {e}")
        except Exception as e:
            print(f"Lỗi: {e}")


# =============================================================================
# MAIN — Demo và Test
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Sprint 2 + 3: RAG Answer Pipeline")
    print("=" * 60)

    # Test queries từ data/test_questions.json
    test_queries = [
        "SLA xử lý ticket P1 là bao lâu?",
        "Khách hàng có thể yêu cầu hoàn tiền trong bao nhiêu ngày?",
        "Ai phải phê duyệt để cấp quyền Level 3?",
        "ERR-403-AUTH là lỗi gì?",  # Query không có trong docs → kiểm tra abstain
    ]

    print("\n--- Sprint 2: Test Baseline (Dense) ---")
    for query in test_queries:
        print(f"\nQuery: {query}")
        try:
            result = rag_answer(query, retrieval_mode="dense", verbose=False)
            print(f"Answer: {result['answer']}")
            print(f"Sources: {result['sources']}")
        except Exception as e:
            print(f"Lỗi: {e}")

    # Uncomment sau khi Sprint 3 hoàn thành:
    # print("\n--- Sprint 3: So sánh strategies ---")
    # compare_retrieval_strategies("Approval Matrix để cấp quyền là tài liệu nào?")
    # compare_retrieval_strategies("ERR-403-AUTH")

    print("\n\nViệc cần làm Sprint 2:")
    print("  1. Implement retrieve_dense() — query ChromaDB")
    print("  2. Implement call_llm() — gọi OpenAI hoặc Gemini")
    print("  3. Chạy rag_answer() với 3+ test queries")
    print("  4. Verify: output có citation không? Câu không có docs → abstain không?")

    print("\nViệc cần làm Sprint 3:")
    print("  1. Chọn 1 trong 3 variants: hybrid, rerank, hoặc query transformation")
    print("  2. Implement variant đó")
    print("  3. Chạy compare_retrieval_strategies() để thấy sự khác biệt")
    print("  4. Ghi lý do chọn biến đó vào docs/tuning-log.md")
