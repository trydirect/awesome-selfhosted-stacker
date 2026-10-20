# awesome-llm-apps — кандидаты для обогащения каталога

Источник: https://github.com/Shubhamsaboo/awesome-llm-apps (список от 2026-10-19).

**Природа источника:** не каталог self-hosted продуктов, а коллекция
туториалов/демо (Streamlit-скрипты, agent-skills, RAG-примеры). Бо́льшая часть
не пригодна для шаблонов Quick Deploy. Ниже — проверенные кандидаты.

Пересечений с текущим каталогом (290 проектов) нет.

## Tier A — упаковываются как продукты

| Проект | Структура | Что это | План шаблона |
|---|---|---|---|
| [ai-mcp-app-builder](https://github.com/Shubhamsaboo/awesome-llm-apps/tree/main/generative_ui_agents/ai-mcp-app-builder) | Dockerfile, pnpm-монорепо, render.yaml | «Описал MCP-приложение — получил живой sandbox-инстанс» | `app.type: custom` + готовый Dockerfile; порт из README; LLM-ключ в .env |
| [Excaliflow](https://github.com/Shubhamsaboo/awesome-llm-apps/tree/main/advanced_llm_apps/excaliflow) | package.json, server.js, index.html | Excalidraw-подобный редактор схем с живыми анимациями | `app.type: node`; сборка из исходников |

## Tier B — упаковываются как python-приложения (LLM-ключ в .env)

| Проект | Структура | Что это | План шаблона |
|---|---|---|---|
| [rag-as-a-service](https://github.com/Shubhamsaboo/awesome-llm-apps/tree/main/rag_tutorials/rag-as-a-service) | rag_app.py, requirements.txt | Production RAG-сервис <50 строк | `app.type: python` + qdrant/pg |
| [local_chatgpt_with_memory](https://github.com/Shubhamsaboo/awesome-llm-apps/tree/main/advanced_llm_apps/llm_apps_with_memory_tutorials/local_chatgpt_with_memory) | local_chatgpt_memory.py, requirements.txt | Локальный чат с памятью на пользователя | `app.type: python` + ollama-совместимый endpoint |
| [always_on_hn_briefing_agent](https://github.com/Shubhamsaboo/awesome-llm-apps/tree/main/always_on_agents/always_on_hn_briefing_agent) | agent.py, scheduler_api.py, delivery.py | Планировщик: дайджест HN в Slack/email | `app.type: python` (API) + volume для состояния |

## Не упаковывать (обучающий код)

- **Agent Skills** (project-graveyard, first-reader, dependency-doctor и т.д.) —
  скиллы для coding-агентов, не сервисы; ставятся через `npx skills add`
- **RAG-туториалы** (~20 шт.), **LLM-optimization**, **fine-tuning**,
  **crash-courses** — ноутбуки/скрипты для обучения
- **Chrome-расширения** (Needle), **Google Docs add-on** (Ripple) — не
  серверные приложения
- **Game-playing demos** (chess, tic-tac-toe, pygame) — демо без продукта

## Статус

Анализ согласован, шаблоны **не создавались** (ожидают подтверждения объёма:
Tier A+B = 5 шаблонов или только Tier A = 2).
