# m3_semantic_search

An in-memory **semantic search engine built from first principles** — no vector
database, no LangChain, no RAG, no external embedding API. The goal of Milestone
3 is to understand embeddings and similarity by implementing the pieces by hand.

## Status

**Complete.** Loads a document corpus, generates real local embeddings, indexes
them once, and serves interactive semantic search ranked by cosine similarity,
with an evaluation harness and a test suite.

## Features

- Document loader (`.txt` → `Document` models, ids + titles assigned)
- In-memory `DocumentStore` with id/title lookups (no database)
- Local embeddings via `sentence-transformers` (`all-MiniLM-L6-v2`, 384-dim),
  behind an `EmbeddingClient` abstraction so another provider can be plugged in
- Cosine similarity implemented from scratch (pure Python, no sklearn/numpy)
- Top-K ranking with a configurable minimum-score threshold
- Interactive CLI search loop with graceful empty/no-match handling
- Evaluation harness reporting Top-1 accuracy over predefined queries
- Lightweight test suite runnable without pytest
- Clean logging: query, timing, and result counts

## Architecture

Text becomes a vector, vectors are compared, and the closest documents win:

```
Document  →  Embedding  →  Vector  →  Similarity  →  Ranking  →  Top Results
 (text)      (model)      (384 nums)  (cosine)      (sort+top-k)  (SearchResult)
```

The app is a one-way pipeline; each layer has a single responsibility and only
depends on the layer below it.

```
main.py                 orchestration — bootstrap + interactive loop
   │
bootstrap.py            wires corpus → store → embeddings → search (shared setup)
   │
services/search_service business logic — embed query, rank, threshold, Top-K
services/embedding_service  turn documents/queries into vectors
   │
embedding_client.py     EmbeddingClient interface + sentence-transformers impl
similarity/cosine.py    pure cosine-similarity math
storage/document_store  in-memory document storage
utils/loader.py         read the corpus     utils/printer.py  terminal output
   │
models.py               Document, DocumentEmbedding, SearchResult (dataclasses)
config.py               logging + constants (EMBEDDING_MODEL, DEFAULT_TOP_K, MIN_SCORE)
```

## Project flow

```
Startup:   load documents → store → embed all docs ONCE → cache index
Search:    query → embed query → cosine vs each cached vector
           → keep score ≥ MIN_SCORE → sort desc → take Top-K → SearchResult[]
Display:   printer renders ranked results (or a friendly message)
```

## Folder structure

```
m3_semantic_search/
├── main.py                 # interactive search CLI (orchestrator)
├── bootstrap.py            # shared "build a ready SearchService" factory
├── config.py               # logging + constants
├── models.py               # Document, DocumentEmbedding, SearchResult
├── embedding_client.py     # EmbeddingClient ABC + SentenceTransformer impl
├── evaluation.py           # accuracy harness over predefined queries
├── tests.py                # no-pytest test suite
├── services/
│   ├── embedding_service.py
│   └── search_service.py
├── similarity/
│   └── cosine.py
├── storage/
│   └── document_store.py
├── utils/
│   ├── loader.py
│   └── printer.py
└── documents/              # the corpus (docker, django, redis, python, fastapi)
```

## How it works

1. **Embed documents once.** At startup every document is embedded and the
   vectors are cached in the `SearchService`. Documents are never re-embedded.
2. **Embed the query.** Each search embeds the query into the *same* 384-dim
   space with the same model, so the vectors are comparable.
3. **Compare with cosine similarity.** The query vector is compared against
   every cached document vector; cosine measures *direction* (meaning), ignoring
   length.
4. **Threshold + rank.** Results below `MIN_SCORE` (0.30) are discarded; the
   rest are sorted by score and the Top-K are returned as `SearchResult`
   objects.

## How to run

Run from inside this directory (absolute imports assume it is on the path):

```bash
cd src/m3_semantic_search
python main.py          # interactive search  (add 2>/dev/null to hide model bars)
python evaluation.py    # accuracy report over predefined queries
python tests.py         # test suite (exit code 0 = all passed)
```

## Example searches

```
Search > web framework          → Django, FastAPI
Search > cache database         → Redis
Search > python programming     → Python
Search > containerization       → Docker      (no shared keyword — pure meaning)
Search > exit                   → quits
```

## Future improvements

- **Chunking:** the embedding model truncates input to ~256 tokens, so long
  documents are represented only by their opening. Splitting documents into
  passages and embedding each would sharpen relevance (and recover the ~2 eval
  queries whose relevant content sits deep in the document).
- **Persistence / vector store** (Milestone 4): cache embeddings to disk or a
  vector database so startup does not re-embed.
- **Pluggable API embeddings:** implement an OpenAI-compatible `EmbeddingClient`
  behind the existing interface.
- **Query expansion / hybrid search:** combine keyword and vector scoring.
