# AI Engineering Workspace

A collection of production-oriented AI applications built while exploring modern AI engineering concepts, backend architecture, and intelligent software systems.

The objective of this repository is to progressively build, improve, and productionize AI-powered applications by following an engineering-first approach rather than isolated tutorials.

> See [ARCHITECTURE.md](ARCHITECTURE.md) for the layered design shared across modules — layers, request flow, principles, and how to add new modules.

---

# Vision

Modern software is rapidly evolving from traditional CRUD applications into intelligent systems powered by Large Language Models (LLMs).

This repository documents that evolution.

Each milestone introduces one major AI engineering capability while reusing and improving the previous architecture, resulting in a collection of complete, production-inspired applications.

The long-term objective is to build systems that can:

- Understand natural language
- Retrieve and reason over private knowledge
- Interact with external tools and APIs
- Automate engineering workflows
- Scale using modern backend infrastructure
- Be deployed as production-ready services

---

# Engineering Principles

This workspace follows a few guiding principles.

- Build from first principles.
- Keep every milestone functional.
- Introduce only one major concept at a time.
- Reuse and refactor instead of rewriting.
- Design for maintainability.
- Follow clean software architecture.
- Treat AI models as backend services.
- Focus on production-oriented implementation.

---

# Roadmap

## Milestone 1 — CLI LLM Client

**Objective**

Build a lightweight terminal-based client capable of communicating with an LLM through its API.

### Topics

- API Integration
- Chat Completions
- Prompt Formatting
- Conversation History
- Roles
- System Prompts
- Configuration Management

### Deliverable

A terminal application capable of maintaining multi-turn conversations with an LLM.

---

## Milestone 2 — Prompt Engineering (`m2_prompt_studio`)

**Objective**

Improve response quality through structured prompt design — learned by
experimentation rather than feature-building. The deliverable is a **Prompt
Engineering Studio**: a terminal app that is really a menu of prompt
experiments over the *same* model.

### Topics

- Zero-shot prompting
- Few-shot prompting
- Structured outputs
- JSON responses
- Persona design
- Prompt templates

### Architecture

A one-way request pipeline where each layer has a single responsibility and
only talks to the layer below it:

```
main.py          orchestration — wires dependencies, runs the loop, dispatches
utils/menu.py    UI: render menu, read + validate the numeric choice
utils/printer.py UI: all terminal output (banner, message, error, success)
services/        business logic — build messages, call the LLM, return a reply
llm.py           the only module that knows Groq exists (messages → text)
config.py        settings + logging (single source of truth)
```

Guiding rules that keep it scalable: `main.py` holds no business/API/prompt
logic and no bare `print()`; UI modules never import AI code; prompt
construction lives in each service's `_build_messages()` — the seam where new
experiments plug in. Adding an experiment = one prompt file + one service +
one dispatch entry; no other file changes.

### Phases

| Phase | Experiment             | Concept              | Status |
| ----- | ---------------------- | -------------------- | ------ |
| 1     | Framework + Playground | Architecture         | ✅     |
| 2     | Explain Concepts       | System prompts       | ✅     |
| 3     | Backend Mentor         | Persona prompting    | ✅     |
| 4     | SQL Assistant          | Task prompting       | ✅     |
| 5     | Code Reviewer          | Instruction prompting| ✅     |
| 6     | Rewrite Assistant      | Style prompting      | ✅     |
| 7     | JSON Generator         | Structured output    | ✅     |
| 8     | Compare Prompt Styles  | Prompt evaluation    | ✅     |
| 9     | Playground Upgrade     | Free experimentation | ✅     |

**Current status: M2 complete (all 9 phases).** The framework runs end-to-end.
Working experiments:

- **Explain Concepts** (1) — *varies the system prompt* by audience (Student →
  Non-Technical), so the same topic yields different explanations.
- **Backend Mentor** (2) — *fixes* a single Senior Mentor persona and *varies
  the topic* (15 backend topics); the inverse lesson, demonstrating persona
  prompting.
- **SQL Assistant** (3) — capability-driven (Explain, Optimize, Suggest
  Indexes, SQL↔ORM, Query Plan, Performance) over a pasted query.
- **Code Reviewer** (4) — 7 reviewer personas sharing one fixed review
  structure; persona varies, structure is constant.
- **Rewrite Assistant** (5) — rewrites text in one of 7 styles (Professional,
  Documentation, ATS Resume, LinkedIn, Email, Simplified, Executive Summary).
- **JSON Generator** (6) — generates JSON from a request, then validates it
  with `json.loads()` and pretty-prints it (or reports the error).
- **Compare Prompt Styles** (7) — runs one question through 6 strategies in one
  action, reusing existing prompts, and prints the answers side by side.
- **Custom Playground** (8) — a stateful, configurable chat lab. A sub-menu
  supports multi-turn conversation history, a history on/off toggle, clearing
  history, a custom system prompt, and live control of temperature, max tokens,
  and model — plus a "view settings" view. Conversation state lives in
  `conversation.py`; only `llm.py` knows about temperature/max_tokens/model.

Menu-selectable choices share a `LabeledEnum` base (`enums.py`) so the
label/selection logic is written once.

### Deliverable

AI-powered text transformation tools such as resume improvement, email generation, and structured content generation.

---

## Milestone 3 — Semantic Search

**Objective**

Understand how machines compare meaning instead of keywords.

### Topics

- Embeddings
- Similarity Search
- Cosine Similarity
- Vector Representations

### Deliverable

Semantic search engine capable of retrieving related content based on meaning.

---

## Milestone 4 — Vector Database

**Objective**

Persist semantic knowledge using vector storage.

### Topics

- Indexing
- Metadata
- Chunking
- Retrieval
- Collections

### Deliverable

Knowledge search application backed by a vector database.

---

## Milestone 5 — Retrieval-Augmented Generation (RAG)

**Objective**

Combine retrieval with language models.

### Topics

- Document Processing
- PDF Parsing
- Embeddings
- Retrieval Pipeline
- Context Injection

### Deliverable

Document question-answering system capable of answering questions using uploaded PDFs.

---

## Milestone 6 — Tool / Function Calling

**Objective**

Allow language models to interact with external systems.

### Topics

- Function Calling
- Tool Selection
- External APIs
- Python Functions
- Structured Responses

### Deliverable

Personal AI assistant capable of interacting with backend services and external APIs.

---

## Milestone 7 — LangChain

**Objective**

Introduce orchestration frameworks for AI applications.

### Topics

- Chains
- Prompt Templates
- Memory
- Retrievers
- Output Parsers

### Deliverable

Advanced multi-document assistant built using LangChain.

---

## Milestone 8 — LangGraph

**Objective**

Build stateful AI workflows.

### Topics

- Graphs
- Nodes
- State
- Conditional Routing
- Workflow Design

### Deliverable

Autonomous research assistant capable of executing multi-step reasoning workflows.

---

## Milestone 9 — Multi-Agent Systems

**Objective**

Coordinate multiple specialized AI agents.

### Topics

- Agent Collaboration
- Planning
- Task Delegation
- Coordination
- Reflection

### Deliverable

Software engineering team simulator composed of multiple collaborating AI agents.

---

## Milestone 10 — AI DevOps Assistant

**Objective**

Build an engineering assistant capable of analyzing real production systems.

### Topics

- Log Analysis
- Deployment Diagnostics
- Infrastructure Awareness
- Monitoring
- Root Cause Analysis

### Deliverable

AI assistant capable of assisting software engineers during deployment and production incidents.

---

# Planned Technology Stack

## Backend

- Python
- FastAPI
- Django
- PostgreSQL
- Redis
- Docker

## AI

- Groq
- OpenAI
- Claude
- Gemini
- LangChain
- LangGraph
- MCP
- Embedding Models

## Data

- ChromaDB
- FAISS
- PostgreSQL

## Infrastructure

- Docker
- Docker Compose
- GitHub Actions
- AWS
- Nginx

## Observability

- Logging
- Monitoring
- Evaluation
- Prompt Versioning

---

# Repository Structure

```
AI/
│
├── README.md
├── requirements.txt
├── .env
├── docs/
├── shared/
│
└── src/
    ├── m1_cli_chat/
    ├── m2_prompt_studio/
    │   ├── main.py
    │   ├── config.py
    │   ├── llm.py
    │   ├── enums.py
    │   ├── conversation.py
    │   ├── prompts/
    │   ├── services/
    │   └── utils/
    ├── m3_semantic_search/
    ├── m4_vector_database/
    ├── m5_rag/
    ├── m6_function_calling/
    ├── m7_langchain/
    ├── m8_langgraph/
    ├── m9_multi_agent/
    └── m10_ai_devops/
```

---

# Long-Term Goal

The final objective is to evolve this workspace into a collection of production-grade AI systems demonstrating the complete lifecycle of modern AI engineering:

- LLM Integration
- Retrieval-Augmented Generation
- Agentic Workflows
- Backend Services
- Cloud Deployment
- Production Infrastructure
- Observability
- System Design

Rather than building isolated examples, each milestone extends previous work, gradually transforming simple applications into scalable, intelligent software systems.

---

# Status

| Milestone | Project | Status |
|-----------|----------|--------|
| M1 | CLI LLM Client | ✅ Complete |
| M2 | Prompt Engineering (Prompt Studio) | ✅ Complete |
| M3 | Semantic Search | ⏳ Planned |
| M4 | Vector Database | ⏳ Planned |
| M5 | RAG | ⏳ Planned |
| M6 | Function Calling | ⏳ Planned |
| M7 | LangChain | ⏳ Planned |
| M8 | LangGraph | ⏳ Planned |
| M9 | Multi-Agent Systems | ⏳ Planned |
| M10 | AI DevOps Assistant | ⏳ Planned |