# Architecture

This document describes the engineering architecture shared across the modules
in this repository — the layers, why each exists, how a request flows through
them, the principles that keep it maintainable, and how to add new work without
breaking the design.

The reference implementation is [`src/m2_prompt_studio`](src/m2_prompt_studio):
it is the most mature module and every layer below points at real files there.
Earlier and later modules follow the same shape.

---

## Repository layout

```
AI/
├── README.md              # roadmap, milestones, status
├── ARCHITECTURE.md        # this document
├── requirements.txt       # shared dependencies
├── .env                   # shared secrets (GROQ_API_KEY, optional overrides)
├── .venv/                 # shared virtualenv for all modules
├── docs/                  # long-form notes
└── src/
    ├── m1_cli_chat/       # M1 — CLI LLM client
    ├── m2_prompt_studio/  # M2 — prompt engineering studio (reference module)
    └── ...                # later milestones
```

Configuration is **shared at the root** (`.env`, `.venv`, `requirements.txt`)
and reused by every module. A module is a self-contained package under `src/`
that is run from inside its own directory (`cd src/m2_prompt_studio && python main.py`).

---

## The layers

Each module is built as a one-way pipeline. A layer only ever calls the layer
below it, never above or sideways.

```
main.py            orchestration — wire dependencies, run the loop, dispatch
   │
utils/menu.py      UI: render menus, read + validate input
utils/printer.py   UI: all terminal output
   │
services/          business logic — build messages, call the LLM, return a reply
   │
prompts/           content — pure functions returning prompt strings
   │
llm.py             provider boundary — the only code that knows Groq exists
   │
config.py          settings + logging (single source of truth)
   │
Groq API           via the OpenAI-compatible SDK
```

### Why each layer exists

| Layer | File(s) | Single responsibility | What breaks if merged away |
|-------|---------|-----------------------|----------------------------|
| Config | [config.py](src/m2_prompt_studio/config.py) | Load env, expose an immutable `Settings`, configure logging, raise `ConfigError` early | Config reads scatter; changing the model means grepping the codebase |
| Provider | [llm.py](src/m2_prompt_studio/llm.py) | Turn chat messages into model text; the **only** file importing `openai` | Swapping providers touches every service |
| Prompts | [prompts/](src/m2_prompt_studio/prompts) | Pure functions returning prompt strings — no I/O, no logic | Prompt wording gets tangled in control flow; non-engineers can't tune it |
| Services | [services/](src/m2_prompt_studio/services) | Own business logic: choose prompt, build messages, call the LLM | `main` learns message formats and bloats with every feature |
| UI — input | [utils/menu.py](src/m2_prompt_studio/utils/menu.py) | Render menus, validate input, never return a bad value | `main` fills with `while`/`try` input-parsing noise |
| UI — output | [utils/printer.py](src/m2_prompt_studio/utils/printer.py) | All terminal formatting in one place | Output style drifts; UI changes ripple everywhere |
| Orchestration | [main.py](src/m2_prompt_studio/main.py) | Wire the pieces, run the loop, dispatch, own I/O bookends | It becomes a god-file and the layering collapses |

---

## Request flow

Using Explain Concepts (menu option 1) as the example:

1. **`main`** reads the menu choice from `menu.get_choice()`.
2. It dispatches to `_run_explain`, which reads the **Topic** and shows the
   **Audience** sub-menu via `menu.choose(title, options)`.
3. `main` converts the UI integer to a domain type with `Audience.from_choice()`
   — UI numbers stop at the orchestrator's edge.
4. **`ExplainService.run(topic, audience)`** selects the audience's system
   prompt from `prompts/explain.py` and assembles `system` + `user` messages.
5. **`LLMClient.get_reply(messages)`** calls Groq and returns text, or `None`
   on failure (logged, not raised).
6. `main` passes the reply to `printer` — a friendly error if `None`, else the
   message — and loops back to the menu.

The rule that makes this readable: **input and output (I/O) live at the edges**
(`main` reads lines, `printer` writes them). Services are pure logic — a topic
and audience in, a reply out — and never call `input()` or `print()`.

---

## Design principles

- **Single Responsibility Principle.** Each file has one reason to change. A
  prompt tweak touches `prompts/`; a formatting change touches `printer.py`.
- **Separation of concerns.** UI code never imports AI code; AI code never
  prints. The boundaries are enforced, not just suggested.
- **Dependency injection.** `main` builds one `LLMClient` and hands it to every
  service (`ExplainService(llm)`). Services never construct their own client,
  which makes them testable with a fake and keeps one connection config.
- **Provider isolation.** `openai` is imported in exactly one file (`llm.py`).
  Changing model providers is a one-file change.
- **Fail fast on config.** `get_settings()` validates and raises `ConfigError`
  at startup; `main` catches it and exits cleanly. No half-configured runs.
- **Modular prompts.** Prompts are content, expressed as pure functions in
  `prompts/`. The service's `_build_messages()` is the single seam where a
  prompt enters the pipeline.
- **Stateless provider client.** `LLMClient` holds no conversation history.
  Any state (multi-turn memory) belongs in a service, not the client.
- **DRY, but earned.** Shared logic is extracted when the second caller appears
  (e.g. `menu.choose`, `main._print_reply`) — not speculatively.
- **YAGNI.** Abstractions are introduced when the data justifies them. A lookup
  table replaces `if/elif` only once branches are genuinely distinct (see the
  prompt-builder dict in `explain_service.py` vs. the still-simple menu dispatch
  in `main.py`).

---

## How to add a new **feature** to an existing module

Adding an experiment (e.g. a new menu option in `m2_prompt_studio`) should
touch a predictable, small set of files — the architecture stays fixed:

1. **`prompts/<feature>.py`** — add pure functions returning the prompt
   string(s). No I/O, no logic.
2. **`services/<feature>_service.py`** — add a `<Feature>Service` that takes an
   injected `LLMClient`, maps inputs to a prompt, builds messages in
   `_build_messages()`, and returns `str | None`. Put any domain enums here.
3. **`main.py`** — instantiate the service once, add a dispatch branch and a
   small `_run_<feature>` I/O helper (read input → call service → `_print_reply`).
4. **`utils/menu.py`** — only if the feature needs a new sub-menu; reuse
   `choose(title, options)` rather than writing a new validation loop.

You should **not** need to touch `llm.py`, `config.py`, or `printer.py` to add a
feature. If you do, question whether the responsibility is landing in the right
layer.

## How to add a new **module** (milestone)

1. Create `src/m<N>_<name>/` as a self-contained package.
2. Reuse the root `.env` / `.venv` / `requirements.txt`; add new dependencies to
   the shared `requirements.txt`.
3. Start from the same layer skeleton: `config.py`, `llm.py` (or a shared client
   if one is later extracted), `main.py`, and `prompts/` / `services/` / `utils/`
   as needed.
4. Reuse patterns from the reference module rather than inventing new ones;
   improve the shared design rather than forking it.
5. Update [README.md](README.md) (roadmap + status) and this document if the
   architecture itself evolves.
