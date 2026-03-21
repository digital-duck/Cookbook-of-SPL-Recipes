# Chapter 5.1 — RAG Query

*"Knowledge is not what you have in your head, but knowing where to find it."*

---

## The Pattern

LLMs are brilliant, but they have a "Knowledge Cutoff." They only know what they were trained on. If you ask a model about a private document, a recent news event, or your own internal company data, it will either admit ignorance or, worse, hallucinate a plausible-sounding lie.

**RAG (Retrieval-Augmented Generation)** is the industry-standard solution. Instead of relying on the model's memory, you provide it with the relevant "background reading" alongside your question. You fetch the right information, inject it into the prompt, and ask the model to synthesize an answer based *only* on that context.

The SQL analogy is a **JOIN against an external table** or a **Subquery**:

```sql
SELECT answer 
FROM (
    SELECT content FROM documents 
    ORDER BY similarity(content, :question) DESC 
    LIMIT 3
) AS background
WHERE question = :question;
```

You aren't querying the model; you are querying a "table" of your own data and joining it with the model's reasoning capabilities.

The RAG Query recipe (Recipe 08) demonstrates the simplest possible RAG implementation in SPL. It uses the built-in `rag.query` function to perform a semantic search against a local vector database and feeds the results directly into the prompt.

---

## The SPL Approach

This recipe introduces the `rag` namespace, which provides high-level access to the SPL runtime's integrated vector store.

---

## The .spl File (Annotated)

```sql
-- Recipe 08: RAG Query
-- Retrieval-augmented generation over indexed documents.

PROMPT rag_answer                             -- (1) name the prompt block
SELECT
    system_role('You are a knowledgeable assistant. Use the provided context to answer accurately.'),
                                             -- (2) context-aware instruction
    rag.query(context.question, top_k=3) AS background,
                                             -- (3) The Semantic Join
    context.question AS question             -- (4) The user's query
GENERATE answer(question)                    -- (5) Grounded generation
```

### (1) `PROMPT rag_answer`

Even though RAG sounds complex, the execution flow is still a single model call. The "retrieval" happens during the `SELECT` phase, just like a SQL join happens before the final result set is produced.

### (2) `system_role(...)`

It is crucial to tell the model that it *has* context and that it should use it. This prevents the model from ignoring the retrieved data in favor of its own pre-trained weights.

### (3) `rag.query(context.question, top_k=3) AS background`

This is the heart of RAG in SPL. 
- **`rag.query`**: A built-in function that takes a string, converts it into a vector (an embedding), and searches the local FAISS index for the 3 most similar chunks of text.
- **`top_k=3`**: We only want the most relevant information. Too much context can "drown" the model or exceed its token limit.

SQL Analogy: A **Vector Similarity Search**. You are ordering your "documents" table by how closely they match the meaning of the question.

### (4) & (5) `question` and `GENERATE`

We bind the question and the retrieved background to the context row. When `GENERATE` fires, the model sees the question *and* the relevant evidence side-by-side. The resulting answer is "grounded" in your data.

---

## Running It

RAG requires a one-time setup to index your data:

```bash
# 1. Install dependencies
pip install numpy faiss-cpu sentence-transformers

# 2. Add a document to the index
# This chunks the file into paragraphs and stores their embeddings locally.
spl2 rag add /path/to/your/document.md
```

Now, run the query:

```bash
spl2 run cookbook/08_rag_query/rag_query.spl --adapter ollama \
    question="What is the main argument of this document?"
```

---

## What Just Happened

**LLM calls: 1.**
**Vector Search calls: 1.**

The "Conductor" (SPL Runtime) managed the retrieval:
1.  Calculated the embedding for the `question`.
2.  Searched the local `.spl/vectors.faiss` file for matches.
3.  Fetched the corresponding text from the `.spl/vectors_meta.db` database.
4.  Injected the found text into the `background` column.
5.  Passed the complete, grounded context to the model for the final answer.

---

## Reproducibility Note

RAG adds a layer of complexity to reproducibility: the **Embedding Model**. 
SPL defaults to `all-MiniLM-L6-v2`, a small but efficient model that runs on your CPU. If you change your embedding model, your search results will change, which will change the model's answer.

On a **GTX 1080 Ti**, the vector search takes **less than 50ms** for an index of thousands of paragraphs. The bottleneck remains the LLM generation time.

---

## When to Use This Pattern

Use the **RAG Query** pattern when:
- **Private Data**: You need to query documents that were never part of a public training set.
- **Up-to-Date Info**: You need the model to know about events that happened after its knowledge cutoff.
- **Fact-Checking**: You want to reduce hallucinations by forcing the model to cite its sources from the provided context.

---

## Exercises

1.  **Inspect the Retrieval.** Run `spl2 rag query "your question" --top-k 5` from the command line. This shows you exactly what the model will see *before* it generates an answer. This is the "EXPLAIN" plan for your RAG query.
2.  **Filter by Metadata.** (Advanced) Research how to add metadata to your documents (e.g., `author`, `date`) and filter your `rag.query` to only search specific files.
3.  **No-Grounding Test.** Run the recipe *before* you index any documents. Observe how the model handles the empty context. Does it admit it doesn't know, or does it try to guess? This is a great way to test the "honesty" of a model.
