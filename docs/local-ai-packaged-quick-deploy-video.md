# Видеоролик: Quick Deploy local-ai-packaged (полный стек)

Назначение: 60-секундное демо для письма автору coleam00/local-ai-packaged
(YouTube-автор, смотрит видео, а не текст) + короткий GIF для README/лендинга.

Стек в кадре — **полный upstream**: n8n, Supabase, Ollama, Open WebUI, Flowise,
Qdrant, Neo4j, SearXNG, Langfuse, Caddy (28 сервисов, генерируется
`scripts/build-services.py`). План по RAM — 16 ГБ (7B-модель занимает 5–6 ГБ;
рекомендуемый cloud-размер — Hetzner cpx42, 8 vCPU / 16 ГБ).

**Вариант для слабого Managed-сервера (если тариф $26 меньше 16 ГБ):**
профиль без локальных моделей — в `.env`:
`OLLAMA_CPU_REPLICAS=0` (Ollama выключен, LLM через внешний API-ключ) либо
`OLLAMA_CPU_REPLICAS=0` + `COMPOSE_PROFILES=gpu-nvidia` на своём GPU-железе.
Такой профиль прямо называется в письме («full profile / no-local-models
profile»), чтобы не было расхождения с видео.

**Ссылка Quick Deploy** (из README проекта, baked-образ — все образы и модели
Ollama уже на сервере, свежие секреты при каждой установке):

```
https://try.direct/quick-deploy?source=github&repo=trydirect/awesome-selfhosted-stacker&path=stacker-projects/local-ai-packaged
```

## Этап 0 — подготовка (до записи)

1. Прогнать установку всухую (Quick Deploy или
   `stacker deploy --target cloud --force-new`), зафиксировать фактическое
   время: клик → все контейнеры healthy, и размер сервера в кадре.
2. Замерить и записать: размер Managed-сервера за $26 (если < 16 ГБ — видео
   снимать на no-local-models профиле или на cpx42), регион, время деплоя
   (секундомер), время первого ответа LLM (baked-модели уже на месте).
3. Подготовить demo: owner-аккаунт n8n, один наглядный workflow (вебхук →
   LLM → таблица/мессенджер); для no-local-models профиля — заранее вписать
   LLM-ключ в `.env` (ключ НЕ попадает в кадр).
4. Окружение записи: свежий профиль браузера, уведомления отключены, 1080p60,
   никаких паролей/токенов в кадре (подставлять редактируемые значения).
5. Для замеров держать под рукой: `docker ps`, `stacker agent health`.

## Сцена 1 — Quick Deploy (0:00–0:10)

1. Открыть страницу local-ai-packaged в каталоге TryDirect (или ссылку выше).
2. Клик **Quick Deploy** → экран Managed Server: регион, размер, домен →
   **Deploy**.
3. Таймлапс установки (ускорить x4–x8): статусы в UI — provision → Ansible →
   контейнеры; секундомер в углу. Из-за baked-образа тяжёлые pull почти не
   видны — это отдельно обыграть в письме.

## Сцена 2 — Проверка работоспособности (0:10–0:45)

Каждая проверка — короткий кадр с выводом. Команды на сервере (SSH) либо
открытые порты Caddy — через браузер:

1. `stacker agent health` (или Status Panel) — все сервисы green.
2. `docker ps --format 'table {{.Names}}\t{{.Status}}'` — все ~28 контейнеров
   Up (healthy) — в кадре прокрутить список.
3. Caddy-интерфейсы (публичные): `http://<host>:8001` n8n → `curl -fs
   http://localhost:8001/healthz` → `ok`; 8002 Open WebUI; 8003 Flowise; 8005
   Supabase Studio (вход `DASHBOARD_USERNAME`/`DASHBOARD_PASSWORD` из `.env`);
   8007 Langfuse; 8008 Neo4j Browser (`/browser/`).
4. Супервизор баз: `docker exec <qdrant> curl -s http://localhost:6333/healthz`
   → `{"status":"ok"}`; Supabase REST через Kong: `curl -fs http://localhost:8004/rest/v1/` →
   ответ/401 (норма — слушает); Neo4j: `curl -fs http://localhost:7687` не
   нужен — достаточно открыть 8008 и увидеть connect-экран.
5. Ollama (профиль с локальными моделями): `docker exec <ollama> ollama list`
   → `qwen2.5:7b-instruct-q4_K_M`, `nomic-embed-text` уже на месте (baked);
   `curl -fs http://localhost:11434/api/tags` изнутри сети → JSON со списком.
6. Сквозной тест ценности: в n8n открыть workflow с LLM-нодой → **Execute**
   → показать результат в кадре; для no-local-models профиля — ответ через
   внешний API.
7. Проверка периметра: `nc -zv <host> 8001` → открыт; `nc -zv <host> 5432`
   (и 11434/6333) → закрыт: наружу только 80/443/8001 по
   `public_ports`, остальное внутренний контур.

## Сцена 3 — Финал (0:45–1:00)

1. Кадр «Deployed in X мин» + карточка сервера (размер/регион/цена).
2. Ссылка Quick Deploy + CTA.
3. Отдельный 5-сек GIF (для README/письма): клик Deploy → «Deployed» →
   `healthz ok`.

## Замеры для письма (заполнить по факту прогона)

- Время: Quick Deploy клик → все контейнеры healthy: ____ мин
- Сервер: ____ (Managed $26/мес — если < 16 ГБ, в письме указать
  no-local-models профиль; эталон полного профиля — cpx42 8 vCPU/16 ГБ)
- Диск под образы/тома (baked + models): ____ ГБ
- Первый ответ LLM (модели уже на сервере): ____ сек
- Профиль в кадре: full / no-local-models (выбрать после замера Managed)
