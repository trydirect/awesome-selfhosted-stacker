# awesome-llm-apps — candidates for the catalog

Source: https://github.com/Shubhamsaboo/awesome-llm-apps (as of 2026-10-19).

**Nature of the source:** not a catalog of self-hosted products (unlike the
earlier oss-quick-deploy-targets), but a collection of tutorials/demos
(Streamlit scripts, agent skills, RAG examples). Most of it is not suitable
for Quick Deploy templates. The viable candidates are below.

No overlaps with the current catalog (290 projects).

## Tier A — packageable as products

| Project | Structure | What it is | Template plan |
|---|---|---|---|
| [ai-mcp-app-builder](https://github.com/Shubhamsaboo/awesome-llm-apps/tree/main/generative_ui_agents/ai-mcp-app-builder) | Dockerfile, pnpm monorepo, render.yaml | "Describe an MCP app — get a live sandboxed instance" | `app.type: custom` + its own Dockerfile; port from README; LLM key in .env |
| [Excaliflow](https://github.com/Shubhamsaboo/awesome-llm-apps/tree/main/advanced_llm_apps/excaliflow) | package.json, server.js, index.html | Excalidraw-style diagram editor with live animated flows | `app.type: node`; build from source |

## Tier B — packageable as python apps (LLM key in .env)

| Project | Structure | What it is | Template plan |
|---|---|---|---|
| [rag-as-a-service](https://github.com/Shubhamsaboo/awesome-llm-apps/tree/main/rag_tutorials/rag-as-a-service) | rag_app.py, requirements.txt | Production RAG service in under 50 lines | `app.type: python` + qdrant/pg |
| [local_chatgpt_with_memory](https://github.com/Shubhamsaboo/awesome-llm-apps/tree/main/advanced_llm_apps/llm_apps_with_memory_tutorials/local_chatgpt_with_memory) | local_chatgpt_memory.py, requirements.txt | Local chat with per-user memory | `app.type: python` + ollama-compatible endpoint |
| [always_on_hn_briefing_agent](https://github.com/Shubhamsaboo/awesome-llm-apps/tree/main/always_on_agents/always_on_hn_briefing_agent) | agent.py, scheduler_api.py, delivery.py | Scheduler: HN digest to Slack/email | `app.type: python` (API) + volume for state |

## Do not package (teaching material)

- **Agent Skills** (project-graveyard, first-reader, dependency-doctor, etc.) —
  coding-agent skills, not services; installed via `npx skills add`
- **RAG tutorials** (~20), **LLM optimization**, **fine-tuning**,
  **crash courses** — notebooks/scripts for learning
- **Chrome extensions** (Needle), **Google Docs add-on** (Ripple) — not
  server-side apps
- **Game-playing demos** (chess, tic-tac-toe, pygame) — demos, not products

## Status

Analysis complete; templates **not yet created** (awaiting a scope decision:
Tier A+B = 5 templates or Tier A only = 2).
