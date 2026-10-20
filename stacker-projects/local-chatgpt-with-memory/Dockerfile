# Local ChatGPT clone with per-user memory (mem0 + qdrant + ollama) at a
# pinned upstream commit. The upstream config hardcodes localhost for the
# qdrant/ollama endpoints; the sed below retargets them to compose service
# names so the app can reach its sidecars.

FROM python:3.12-slim

RUN apt-get update \
 && apt-get install -y --no-install-recommends git \
 && rm -rf /var/lib/apt/lists/*

ARG REF=874bc13a57aa2ba1266a84f2444808ce3093efb6
RUN git init /src \
 && git -C /src remote add origin https://github.com/Shubhamsaboo/awesome-llm-apps.git \
 && git -C /src fetch --depth 1 origin ${REF} \
 && git -C /src checkout FETCH_HEAD

WORKDIR /src/advanced_llm_apps/llm_apps_with_memory_tutorials/local_chatgpt_with_memory

RUN sed -i 's/"host": "localhost"/"host": "qdrant"/' local_chatgpt_memory.py \
 && sed -i 's|http://localhost:11434|http://ollama:11434|g' local_chatgpt_memory.py

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8501

CMD ["streamlit", "run", "local_chatgpt_memory.py", "--server.port=8501", "--server.address=0.0.0.0"]
