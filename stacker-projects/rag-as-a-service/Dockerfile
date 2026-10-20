# Streamlit app from the upstream rag-as-a-service tutorial, pinned commit.

FROM python:3.12-slim

RUN apt-get update \
 && apt-get install -y --no-install-recommends git \
 && rm -rf /var/lib/apt/lists/*

ARG REF=874bc13a57aa2ba1266a84f2444808ce3093efb6
RUN git init /src \
 && git -C /src remote add origin https://github.com/Shubhamsaboo/awesome-llm-apps.git \
 && git -C /src fetch --depth 1 origin ${REF} \
 && git -C /src checkout FETCH_HEAD

WORKDIR /src/rag_tutorials/rag-as-a-service
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8501

CMD ["streamlit", "run", "rag_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
