# AgentScout (always-on HN briefing) scheduler API at a pinned upstream commit.

FROM python:3.12-slim

RUN apt-get update \
 && apt-get install -y --no-install-recommends git \
 && rm -rf /var/lib/apt/lists/*

ARG REF=874bc13a57aa2ba1266a84f2444808ce3093efb6
RUN git init /src \
 && git -C /src remote add origin https://github.com/Shubhamsaboo/awesome-llm-apps.git \
 && git -C /src fetch --depth 1 origin ${REF} \
 && git -C /src checkout FETCH_HEAD

WORKDIR /src/always_on_agents/always_on_hn_briefing_agent

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "scheduler_api:app", "--host", "0.0.0.0", "--port", "8000"]
